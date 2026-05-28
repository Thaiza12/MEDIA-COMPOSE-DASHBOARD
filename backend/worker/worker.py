"""
Worker ETL — consome "eventos_watchdog" no Redis e persiste no PostgreSQL.

Regra de finalização:
  Se o caminho do arquivo contém /final/ → projeto marcado como concluído
"""

import json
import time
import logging
import os
import psycopg2
import redis as redis_lib

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [WORKER] %(levelname)s %(message)s",
    datefmt="%Y-%m-%d %H:%M:%S",
)
log = logging.getLogger(__name__)

REDIS_QUEUE    = "eventos_watchdog"
PASTA_FINAL    = "final"   # nome da subpasta que sinaliza conclusão


def conectar_redis():
    while True:
        try:
            r = redis_lib.Redis(
                host=os.getenv("REDIS_HOST", "redis"),
                port=int(os.getenv("REDIS_PORT", 6379)),
                decode_responses=True
            )
            r.ping()
            log.info("Redis conectado.")
            return r
        except Exception as e:
            log.warning(f"Redis indisponível: {e}. Tentando em 3s...")
            time.sleep(3)


def conectar_postgres():
    while True:
        try:
            conn = psycopg2.connect(
                host=os.getenv("DB_HOST", "postgres"),
                port=int(os.getenv("DB_PORT", 5432)),
                database=os.getenv("DB_NAME", "globo2_db"),
                user=os.getenv("DB_USER", "globo_user"),
                password=os.getenv("DB_PASSWORD", "123456")
            )
            log.info("PostgreSQL conectado.")
            return conn
        except Exception as e:
            log.warning(f"PostgreSQL indisponível: {e}. Tentando em 3s...")
            time.sleep(3)


DDL = """
CREATE TABLE IF NOT EXISTS usuarios (
    id        SERIAL PRIMARY KEY,
    nome      TEXT UNIQUE NOT NULL,
    criado_em TIMESTAMPTZ DEFAULT NOW()
);

CREATE TABLE IF NOT EXISTS projetos (
    id          SERIAL PRIMARY KEY,
    nome        TEXT        NOT NULL,
    usuario_id  INT         NOT NULL REFERENCES usuarios(id),
    status      TEXT        NOT NULL DEFAULT 'em_andamento',
    concluido_em TIMESTAMPTZ,
    criado_em   TIMESTAMPTZ DEFAULT NOW(),
    UNIQUE (nome, usuario_id)
);

CREATE TABLE IF NOT EXISTS eventos (
    id          SERIAL PRIMARY KEY,
    tipo        TEXT        NOT NULL,
    caminho     TEXT,
    arquivo     TEXT        NOT NULL,
    pasta       TEXT,
    is_final    BOOLEAN     DEFAULT FALSE,
    usuario_id  INT         REFERENCES usuarios(id),
    projeto_id  INT         REFERENCES projetos(id),
    ocorrido_em TIMESTAMPTZ NOT NULL,
    inserido_em TIMESTAMPTZ DEFAULT NOW()
);

CREATE TABLE IF NOT EXISTS edicoes (
    id                 SERIAL PRIMARY KEY,
    editor             TEXT,
    arquivo            TEXT,
    projeto            TEXT,
    inicio_edicao      TIMESTAMPTZ,
    fim_edicao         TIMESTAMPTZ,
    duracao_segundos   INT,
    tamanho_arquivo_mb FLOAT,
    inserido_em        TIMESTAMPTZ DEFAULT NOW()
);
"""


def criar_tabelas(conn):
    with conn.cursor() as cur:
        cur.execute(DDL)
        # Migração segura: adiciona colunas novas se já existia tabela antiga
        cur.execute("""
            ALTER TABLE projetos
                ADD COLUMN IF NOT EXISTS status TEXT NOT NULL DEFAULT 'em_andamento',
                ADD COLUMN IF NOT EXISTS concluido_em TIMESTAMPTZ;
        """)
        cur.execute("""
            ALTER TABLE eventos
                ADD COLUMN IF NOT EXISTS is_final BOOLEAN DEFAULT FALSE;
        """)
    conn.commit()
    log.info("Tabelas criadas/verificadas.")


# ── helpers ───────────────────────────────────────────────────────────────────

def eh_evento_final(caminho: str) -> bool:
    """Retorna True se o arquivo está dentro da subpasta 'final'."""
    partes = caminho.replace("\\", "/").lower().split("/")
    return PASTA_FINAL in partes


def upsert_usuario(cur, nome: str) -> int:
    cur.execute(
        "INSERT INTO usuarios (nome) VALUES (%s) "
        "ON CONFLICT (nome) DO UPDATE SET nome = EXCLUDED.nome "
        "RETURNING id",
        (nome,),
    )
    return cur.fetchone()[0]


def upsert_projeto(cur, nome: str, usuario_id: int) -> int:
    cur.execute(
        "INSERT INTO projetos (nome, usuario_id) VALUES (%s, %s) "
        "ON CONFLICT (nome, usuario_id) DO UPDATE SET nome = EXCLUDED.nome "
        "RETURNING id",
        (nome, usuario_id),
    )
    return cur.fetchone()[0]


def concluir_projeto(cur, projeto_id: int, timestamp: str):
    """Marca o projeto como concluído."""
    cur.execute(
        "UPDATE projetos SET status = 'concluido', concluido_em = %s::timestamptz "
        "WHERE id = %s AND status != 'concluido'",
        (timestamp, projeto_id),
    )
    afetadas = cur.rowcount
    return afetadas > 0   # True se realmente mudou (não estava já concluído)


def insert_evento(cur, evento: dict, usuario_id, projeto_id, is_final: bool):
    cur.execute(
        "INSERT INTO eventos "
        "(tipo, caminho, arquivo, pasta, is_final, usuario_id, projeto_id, ocorrido_em) "
        "VALUES (%s, %s, %s, %s, %s, %s, %s, %s::timestamptz)",
        (
            evento["tipoEvento"],
            evento.get("caminho"),
            evento["arquivo"],
            evento.get("pasta", ""),
            is_final,
            usuario_id,
            projeto_id,
            evento["timestamp"],
        ),
    )


def upsert_edicao(cur, evento: dict):
    editor  = evento.get("usuario", "")
    arquivo = evento.get("arquivo", "")
    projeto = evento.get("projeto", "")
    ts      = evento["timestamp"]

    cur.execute(
        "SELECT id FROM edicoes "
        "WHERE editor = %s AND arquivo = %s AND fim_edicao IS NULL "
        "ORDER BY inicio_edicao DESC LIMIT 1",
        (editor, arquivo),
    )
    row = cur.fetchone()

    if row:
        cur.execute(
            "UPDATE edicoes SET fim_edicao = %s::timestamptz, "
            "duracao_segundos = EXTRACT(EPOCH FROM (%s::timestamptz - inicio_edicao))::INT "
            "WHERE id = %s",
            (ts, ts, row[0]),
        )
    else:
        cur.execute(
            "INSERT INTO edicoes (editor, arquivo, projeto, inicio_edicao) "
            "VALUES (%s, %s, %s, %s::timestamptz)",
            (editor, arquivo, projeto, ts),
        )


def atualizar_estado_redis(r, evento: dict, is_final: bool):
    """Atualiza o estado em tempo real do editor no Redis."""
    usuario = evento.get("usuario", "")
    if not usuario:
        return

    chave = f"editor:{usuario.lower().replace(' ', '_')}"
    status = "concluido" if is_final else "ocupado"

    r.hset(chave, mapping={
        "status":      status,
        "editor":      usuario,
        "projeto":     evento.get("projeto", ""),
        "arquivo":     evento.get("arquivo", ""),
        "ultimo_save": evento.get("timestamp", ""),
        "is_final":    str(is_final),
    })
    r.expire(chave, 3600)


# ── ETL ───────────────────────────────────────────────────────────────────────

def transformar(evento: dict) -> dict:
    if evento.get("usuario"):
        evento["usuario"] = evento["usuario"].strip().title()
    if evento.get("projeto"):
        evento["projeto"] = evento["projeto"].strip().title()
    return evento


def exporta_para_db(evento: dict, conn, r):
    evento   = transformar(evento)
    usuario  = evento.get("usuario", "").strip()
    projeto  = evento.get("projeto", "").strip()
    is_final = eh_evento_final(evento.get("caminho", ""))

    try:
        with conn.cursor() as cur:
            uid = upsert_usuario(cur, usuario) if usuario else None
            pid = upsert_projeto(cur, projeto, uid) if (uid and projeto) else None
            insert_evento(cur, evento, uid, pid, is_final)

            if uid:
                upsert_edicao(cur, evento)

            # ── Finalização ──────────────────────────────────────────────────
            if is_final and pid:
                mudou = concluir_projeto(cur, pid, evento["timestamp"])
                if mudou:
                    log.info(f"🏁 PROJETO CONCLUÍDO: {projeto} (usuario={usuario})")

        conn.commit()
        atualizar_estado_redis(r, evento, is_final)

        flag = " 🏁 FINAL" if is_final else ""
        log.info(
            f"✓ {evento['tipoEvento']:10} | {evento['arquivo']}"
            f" | usuario={usuario or '—'} | projeto={projeto or '—'}{flag}"
        )

    except Exception as e:
        conn.rollback()
        log.error(f"✗ Erro: {e}")
        raise


# ── LOOP ──────────────────────────────────────────────────────────────────────

if __name__ == "__main__":
    r    = conectar_redis()
    conn = conectar_postgres()
    criar_tabelas(conn)

    log.info(f"Worker aguardando eventos na fila '{REDIS_QUEUE}'...\n")

    while True:
        try:
            resultado = r.blpop(REDIS_QUEUE, timeout=5)
            if resultado is None:
                continue
            _, raw = resultado
            exporta_para_db(json.loads(raw), conn, r)

        except KeyboardInterrupt:
            log.info("Worker encerrado.")
            break
        except redis_lib.ConnectionError as e:
            log.error(f"Redis perdido: {e}. Reconectando...")
            r = conectar_redis()
        except psycopg2.OperationalError as e:
            log.error(f"Postgres perdido: {e}. Reconectando...")
            conn = conectar_postgres()
        except Exception as e:
            log.error(f"Erro inesperado: {e}")
            time.sleep(2)