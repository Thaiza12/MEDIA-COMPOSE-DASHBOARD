"""
ETL — consome a fila Redis `etl:eventos` e persiste no PostgreSQL.

Tabelas criadas automaticamente:
  • usuarios  (id, nome, criado_em)
  • projetos  (id, nome, usuario_id, criado_em)
  • eventos   (id, tipo, arquivo, caminho, projeto_id, usuario_id, timestamp)
"""

import json
import logging
import os
import time

import psycopg2
import psycopg2.extras
import redis

# ─── CONFIG ────────────────────────────────────────────────────────────────────
REDIS_HOST  = os.getenv("REDIS_HOST",  "localhost")
REDIS_PORT  = int(os.getenv("REDIS_PORT", 6379))
REDIS_DB    = int(os.getenv("REDIS_DB",   0))
REDIS_QUEUE = "etl:eventos"

PG_DSN = (
    f"host={os.getenv('PG_HOST', 'localhost')} "
    f"port={os.getenv('PG_PORT', '5432')} "
    f"dbname={os.getenv('PG_DB', 'etl_db')} "
    f"user={os.getenv('PG_USER', 'postgres')} "
    f"password={os.getenv('PG_PASSWORD', 'postgres')}"
)

BLPOP_TIMEOUT = 5   # segundos de espera bloqueante no Redis

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [ETL] %(levelname)s %(message)s",
    datefmt="%Y-%m-%d %H:%M:%S",
)
log = logging.getLogger(__name__)


# ─── DDL ───────────────────────────────────────────────────────────────────────
DDL = """
CREATE TABLE IF NOT EXISTS usuarios (
    id         SERIAL PRIMARY KEY,
    nome       TEXT UNIQUE NOT NULL,
    criado_em  TIMESTAMPTZ DEFAULT NOW()
);

CREATE TABLE IF NOT EXISTS projetos (
    id          SERIAL PRIMARY KEY,
    nome        TEXT NOT NULL,
    usuario_id  INT  NOT NULL REFERENCES usuarios(id),
    criado_em   TIMESTAMPTZ DEFAULT NOW(),
    UNIQUE (nome, usuario_id)
);

CREATE TABLE IF NOT EXISTS eventos (
    id          SERIAL PRIMARY KEY,
    tipo        TEXT NOT NULL,
    arquivo     TEXT NOT NULL,
    caminho     TEXT,
    pasta       TEXT,
    usuario_id  INT  REFERENCES usuarios(id),
    projeto_id  INT  REFERENCES projetos(id),
    ocorrido_em TIMESTAMPTZ NOT NULL,
    inserido_em TIMESTAMPTZ DEFAULT NOW()
);
"""


def criar_tabelas(conn):
    with conn.cursor() as cur:
        cur.execute(DDL)
    conn.commit()
    log.info("Tabelas verificadas/criadas com sucesso.")


# ─── UPSERT HELPERS ────────────────────────────────────────────────────────────
def upsert_usuario(cur, nome: str) -> int:
    """Insere o usuário se não existir e devolve o id."""
    cur.execute(
        """
        INSERT INTO usuarios (nome)
        VALUES (%s)
        ON CONFLICT (nome) DO UPDATE SET nome = EXCLUDED.nome
        RETURNING id
        """,
        (nome,),
    )
    return cur.fetchone()[0]


def upsert_projeto(cur, nome: str, usuario_id: int) -> int:
    """Insere o projeto se não existir e devolve o id."""
    cur.execute(
        """
        INSERT INTO projetos (nome, usuario_id)
        VALUES (%s, %s)
        ON CONFLICT (nome, usuario_id) DO UPDATE SET nome = EXCLUDED.nome
        RETURNING id
        """,
        (nome, usuario_id),
    )
    return cur.fetchone()[0]


def inserir_evento(cur, payload: dict, usuario_id: int, projeto_id: int):
    cur.execute(
        """
        INSERT INTO eventos
            (tipo, arquivo, caminho, pasta, usuario_id, projeto_id, ocorrido_em)
        VALUES
            (%s, %s, %s, %s, %s, %s, %s::timestamptz)
        """,
        (
            payload["tipoEvento"],
            payload["arquivo"],
            payload.get("caminho"),
            payload.get("pasta"),
            usuario_id,
            projeto_id,
            payload["timestamp"],
        ),
    )


# ─── TRANSFORMAÇÃO ETL ─────────────────────────────────────────────────────────
def transformar(payload: dict) -> dict:
    """
    Normaliza o payload vindo do watchdog.
    O watchdog já resolveu usuario e projeto — aqui fazemos limpeza adicional.
    """
    usuario = (payload.get("usuario") or "").strip().title()
    projeto = (payload.get("projeto") or "").strip().title()

    if not usuario:
        raise ValueError(f"Payload sem usuario: {payload}")
    if not projeto:
        raise ValueError(f"Payload sem projeto: {payload}")

    return {**payload, "usuario": usuario, "projeto": projeto}


# ─── LOOP PRINCIPAL ────────────────────────────────────────────────────────────
def processar_mensagem(conn, payload_raw: str):
    try:
        payload = json.loads(payload_raw)
        payload = transformar(payload)
    except (json.JSONDecodeError, ValueError) as e:
        log.error(f"Mensagem inválida descartada: {e} | raw={payload_raw[:200]}")
        return

    usuario = payload["usuario"]
    projeto = payload["projeto"]

    log.info(f"→ {payload['tipoEvento']:10} | {payload['arquivo']}")
    log.info(f"  usuario={usuario} | projeto={projeto}")

    try:
        with conn.cursor() as cur:
            uid = upsert_usuario(cur, usuario)
            pid = upsert_projeto(cur, projeto, uid)
            inserir_evento(cur, payload, uid, pid)
        conn.commit()
        log.info(f"  ✓ Gravado no PostgreSQL (usuario_id={uid}, projeto_id={pid})")
    except Exception as e:
        conn.rollback()
        log.error(f"  ✗ Erro ao gravar no PostgreSQL: {e}")
        raise


def main():
    log.info(f"Conectando ao Redis {REDIS_HOST}:{REDIS_PORT} ...")
    r = redis.Redis(host=REDIS_HOST, port=REDIS_PORT, db=REDIS_DB,
                    decode_responses=True)
    r.ping()
    log.info("Redis OK.")

    log.info(f"Conectando ao PostgreSQL ...")
    conn = psycopg2.connect(PG_DSN)
    log.info("PostgreSQL OK.")

    criar_tabelas(conn)

    log.info(f"ETL aguardando mensagens na fila '{REDIS_QUEUE}' ...\n")

    while True:
        try:
            resultado = r.blpop(REDIS_QUEUE, timeout=BLPOP_TIMEOUT)
            if resultado is None:
                continue   # timeout — nenhuma mensagem, aguarda mais
            _, payload_raw = resultado
            processar_mensagem(conn, payload_raw)

        except redis.ConnectionError as e:
            log.error(f"Redis desconectado: {e}. Reconectando em 5s...")
            time.sleep(5)
            r = redis.Redis(host=REDIS_HOST, port=REDIS_PORT, db=REDIS_DB,
                            decode_responses=True)

        except psycopg2.OperationalError as e:
            log.error(f"PostgreSQL desconectado: {e}. Reconectando em 5s...")
            time.sleep(5)
            conn = psycopg2.connect(PG_DSN)

        except KeyboardInterrupt:
            log.info("ETL encerrado pelo usuário.")
            break

    conn.close()


if __name__ == "__main__":
    main()