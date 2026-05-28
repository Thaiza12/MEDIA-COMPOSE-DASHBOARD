-- ============================================================
-- Media Compose Dashboard - Schema PostgreSQL
-- ============================================================

-- Tabela de ilhas de edição (estações)
CREATE TABLE IF NOT EXISTS ilhas (
    id          SERIAL PRIMARY KEY,
    nome        VARCHAR(100) NOT NULL UNIQUE,
    hostname    VARCHAR(255),
    ip          VARCHAR(45),
    criado_em   TIMESTAMP DEFAULT NOW()
);

-- Tabela de editores
CREATE TABLE IF NOT EXISTS editores (
    id          SERIAL PRIMARY KEY,
    nome        VARCHAR(100) NOT NULL,
    login       VARCHAR(100) UNIQUE,
    ativo       BOOLEAN DEFAULT TRUE,
    criado_em   TIMESTAMP DEFAULT NOW()
);

-- Tabela principal de sessões de edição
CREATE TABLE IF NOT EXISTS edicoes (
    id                  SERIAL PRIMARY KEY,
    ilha_id             INTEGER REFERENCES ilhas(id),
    editor_id           INTEGER REFERENCES editores(id),
    editor_nome         VARCHAR(100),
    arquivo             VARCHAR(512) NOT NULL,
    software            VARCHAR(100) DEFAULT 'Avid Media Composer',
    tamanho_arquivo_mb  NUMERIC(10, 2),
    inicio_edicao       TIMESTAMP NOT NULL DEFAULT NOW(),
    fim_edicao          TIMESTAMP,
    ultimo_save         TIMESTAMP,
    duracao_segundos    INTEGER,
    status              VARCHAR(20) DEFAULT 'ativo' CHECK (status IN ('ativo', 'encerrado', 'ocioso')),
    previsao_etc        TIMESTAMP,
    minutos_restantes   INTEGER,
    criado_em           TIMESTAMP DEFAULT NOW()
);

-- Tabela de eventos de save (log detalhado)
CREATE TABLE IF NOT EXISTS eventos_save (
    id              SERIAL PRIMARY KEY,
    edicao_id       INTEGER REFERENCES edicoes(id) ON DELETE CASCADE,
    tamanho_mb      NUMERIC(10, 2),
    timestamp_save  TIMESTAMP DEFAULT NOW(),
    delta_mb        NUMERIC(10, 2)
);

-- Tabela de predições geradas pela IA
CREATE TABLE IF NOT EXISTS predicoes (
    id              SERIAL PRIMARY KEY,
    edicao_id       INTEGER REFERENCES edicoes(id) ON DELETE CASCADE,
    editor_id       INTEGER REFERENCES editores(id),
    tamanho_mb      NUMERIC(10, 2),
    duracao_prevista_min INTEGER,
    duracao_real_min     INTEGER,
    erro_percentual      NUMERIC(6, 2),
    criado_em       TIMESTAMP DEFAULT NOW()
);

-- Índices para performance
CREATE INDEX IF NOT EXISTS idx_edicoes_status       ON edicoes(status);
CREATE INDEX IF NOT EXISTS idx_edicoes_editor       ON edicoes(editor_id);
CREATE INDEX IF NOT EXISTS idx_edicoes_inicio       ON edicoes(inicio_edicao);
CREATE INDEX IF NOT EXISTS idx_eventos_edicao       ON eventos_save(edicao_id);
CREATE INDEX IF NOT EXISTS idx_eventos_timestamp    ON eventos_save(timestamp_save);

-- Dados iniciais para teste
INSERT INTO ilhas (nome, hostname, ip) VALUES
    ('Ilha-01', 'edit-ws-01.local', '192.168.1.101'),
    ('Ilha-02', 'edit-ws-02.local', '192.168.1.102'),
    ('Ilha-03', 'edit-ws-03.local', '192.168.1.103')
ON CONFLICT (nome) DO NOTHING;

INSERT INTO editores (nome, login) VALUES
    ('João Silva', 'joao.silva'),
    ('Maria Santos', 'maria.santos'),
    ('Pedro Costa', 'pedro.costa')
ON CONFLICT (login) DO NOTHING;