"""
Database Schema for Memory Islands - Ilhas e Pedras

Este módulo define o schema de base de dados para o sistema de memória insular.
"""

# SQL for creating island-related tables
SCHEMA_ILHAS = """
-- Ilhas table - agregado cognitivo consolidado
CREATE TABLE IF NOT EXISTS ilhas (
    id SERIAL PRIMARY KEY,
    ilha_key TEXT UNIQUE NOT NULL,

    -- Identificação
    nome TEXT NOT NULL DEFAULT '',
    descrição TEXT DEFAULT '',

    -- Estado
    estado TEXT NOT NULL DEFAULT 'EMBRIONARIA',

    -- Dinâmica
    grau_consolidação REAL NOT NULL DEFAULT 0.0,
    score_ativação REAL NOT NULL DEFAULT 0.0,

    -- Metadados epistémicos
    claims_validadas INTEGER NOT NULL DEFAULT 0,
    claims_pendentes INTEGER NOT NULL DEFAULT 0,
    lacunas_identificadas JSONB DEFAULT '[]',

    -- Timestamps
    data_criação TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    updated_at TIMESTAMPTZ
);

CREATE INDEX IF NOT EXISTS ilhas_key_idx ON ilhas(ilha_key);
CREATE INDEX IF NOT EXISTS ilhas_estado_idx ON ilhas(estado);
CREATE INDEX IF NOT EXISTS ilhas_score_idx ON ilhas(score_ativação);

-- Pedras table - interações relevantes que criam saliência
CREATE TABLE IF NOT EXISTS pedras (
    id SERIAL PRIMARY KEY,
    pedra_key TEXT UNIQUE NOT NULL,

    -- Tipo de interação
    tipo_interação TEXT NOT NULL DEFAULT 'MENSAGEM',

    -- Saliência
    saliência_valor REAL NOT NULL DEFAULT 0.0,
    saliência_frequência REAL NOT NULL DEFAULT 0.0,
    saliência_intensidade REAL NOT NULL DEFAULT 0.0,
    saliência_novidade REAL NOT NULL DEFAULT 0.0,
    saliência_relevância REAL NOT NULL DEFAULT 0.0,

    -- Impacto
    impacto_criou_ilha BOOLEAN NOT NULL DEFAULT FALSE,
    ilha_criada_key TEXT,

    -- Estado
    estado TEXT NOT NULL DEFAULT 'NOVA',

    -- Conteúdo (truncado para índice)
    conteúdo_original TEXT DEFAULT '',
    conteúdo_hash TEXT,

    -- Embedding (store as vector type if available, else as JSONB)
    embedding JSONB,

    -- Timestamps
    data_criação TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    última_reativação TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    contagem_reações INTEGER NOT NULL DEFAULT 0
);

CREATE INDEX IF NOT EXISTS pedras_key_idx ON pedras(pedra_key);
CREATE INDEX IF NOT EXISTS pedras_estado_idx ON pedras(estado);
CREATE INDEX IF NOT EXISTS pedras_saliência_idx ON pedras(saliência_valor);

-- Membros de Ilhas (relação N:M)
CREATE TABLE IF NOT EXISTS ilha_membros (
    id SERIAL PRIMARY KEY,
    ilha_key TEXT NOT NULL REFERENCES ilhas(ilha_key) ON DELETE CASCADE,

    -- Tipo de membro (claim, documento, nota, etc)
    member_id TEXT NOT NULL,
    member_type TEXT NOT NULL DEFAULT 'unknown',

    saliência REAL NOT NULL DEFAULT 0.0,
    data_inserção TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    inserido_por TEXT DEFAULT '',

    UNIQUE(ilha_key, member_id, member_type)
);

CREATE INDEX IF NOT EXISTS ilha_membros_ilha_idx ON ilha_membros(ilha_key);
CREATE INDEX IF NOT EXISTS ilha_membros_member_idx ON ilha_membros(member_id);

-- Histórico de reativações de Ilhas
CREATE TABLE IF NOT EXISTS ilha_reações (
    id SERIAL PRIMARY KEY,
    ilha_key TEXT NOT NULL REFERENCES ilhas(ilha_key) ON DELETE CASCADE,

    tipo TEXT NOT NULL DEFAULT 'reativação',
    session_id TEXT DEFAULT '',
    data TIMESTAMPTZ NOT NULL DEFAULT NOW()
);

CREATE INDEX IF NOT EXISTS ilha_reações_ilha_idx ON ilha_reações(ilha_key);

-- Relações entre Ilhas
CREATE TABLE IF NOT EXISTS ilha_relações (
    id SERIAL PRIMARY KEY,
    ilha_key TEXT NOT NULL REFERENCES ilhas(ilha_key) ON DELETE CASCADE,
    ilha_relacionada_key TEXT NOT NULL,

    tipo TEXT NOT NULL DEFAULT 'RELATED_TO',
    força REAL NOT NULL DEFAULT 0.5,

    UNIQUE(ilha_key, ilha_relacionada_key)
);

CREATE INDEX IF NOT EXISTS ilha_relações_ilha_idx ON ilha_relações(ilha_key);

-- Ledger cronológico - registo de sessões/interações por dia
CREATE TABLE IF NOT EXISTS ledger_cronológico (
    id SERIAL PRIMARY KEY,
    data DATE NOT NULL,
    session_id TEXT NOT NULL,

    -- Resumo do dia
    pedras_criadas INTEGER NOT NULL DEFAULT 0,
    ilhas_criadas INTEGER NOT NULL DEFAULT 0,
    ilhas_actualizadas INTEGER NOT NULL DEFAULT 0,

    -- Flags
    ciclo_dormir_executado BOOLEAN NOT NULL DEFAULT FALSE,
    relatório_sono TEXT DEFAULT '',

    created_at TIMESTAMPTZ NOT NULL DEFAULT NOW()
);

CREATE INDEX IF NOT EXISTS ledger_data_idx ON ledger_cronológico(data);
CREATE INDEX IF NOT EXISTS ledger_session_idx ON ledger_cronológico(session_id);
"""


async def init_schema_ilhas(conn) -> None:
    """Initialize island/pedra schema."""
    await conn.execute(SCHEMA_ILHAS)


async def drop_schema_ilhas(conn) -> None:
    """Drop island/pedra schema (for testing)."""
    await conn.execute("""
        DROP TABLE IF EXISTS ilha_relações CASCADE;
        DROP TABLE IF EXISTS ilha_reações CASCADE;
        DROP TABLE IF EXISTS ilha_membros CASCADE;
        DROP TABLE IF EXISTS pedras CASCADE;
        DROP TABLE IF EXISTS ilhas CASCADE;
        DROP TABLE IF EXISTS ledger_cronológico CASCADE;
    """)
