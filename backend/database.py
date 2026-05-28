import os
import psycopg2
import redis

# ── Redis ──────────────────────────────────────────────────────────────────────
# Conexão leve — Redis aceita conexão instantânea
redis_client = redis.Redis(
    host=os.getenv("REDIS_HOST", "redis"),
    port=int(os.getenv("REDIS_PORT", 6379)),
    decode_responses=True
)

# ── PostgreSQL ─────────────────────────────────────────────────────────────────
# Conexão LAZY: não conecta no import, conecta só quando chamado.
# Isso evita crash se o Postgres ainda estiver iniciando.

_postgres_conn = None

def get_postgres_conn():
    """
    Retorna a conexão com o PostgreSQL, criando-a se necessário.
    Se a conexão estiver fechada ou quebrada, reconecta automaticamente.
    """
    global _postgres_conn

    try:
        if _postgres_conn is None or _postgres_conn.closed:
            raise psycopg2.OperationalError("sem conexão")
        # testa se ainda está viva
        _postgres_conn.cursor().execute("SELECT 1")
    except Exception:
        _postgres_conn = psycopg2.connect(
            host=os.getenv("DB_HOST", "postgres"),
            port=int(os.getenv("DB_PORT", 5432)),
            database=os.getenv("DB_NAME", "globo2_db"),
            user=os.getenv("DB_USER", "globo_user"),
            password=os.getenv("DB_PASSWORD", "123456")
        )

    return _postgres_conn

# Atalho mantendo compatibilidade com quem importava `postgres_conn` direto
# Agora é uma função — troque postgres_conn.cursor() por get_postgres_conn().cursor()
postgres_conn = get_postgres_conn