"""
Database Schema for Chat - Conversations and Messages

Este módulo define o schema de base de dados para o sistema de chat.
"""

SCHEMA_CHAT = """
-- Conversations (threads)
CREATE TABLE IF NOT EXISTS conversations (
    id SERIAL PRIMARY KEY,
    conversation_key TEXT UNIQUE NOT NULL,

    -- Identification
    title TEXT NOT NULL DEFAULT 'New Conversation',
    user_id TEXT NOT NULL DEFAULT 'anonymous',

    -- LLM Configuration
    model_used TEXT,
    system_prompt TEXT,

    -- Stats
    message_count INTEGER NOT NULL DEFAULT 0,
    claims_count INTEGER NOT NULL DEFAULT 0,
    gaps_count INTEGER NOT NULL DEFAULT 0,

    -- Status
    is_archived BOOLEAN NOT NULL DEFAULT FALSE,

    -- Timestamps
    created_at TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    updated_at TIMESTAMPTZ,
    last_message_at TIMESTAMPTZ
);

CREATE INDEX IF NOT EXISTS conversations_key_idx ON conversations(conversation_key);
CREATE INDEX IF NOT EXISTS conversations_user_idx ON conversations(user_id);
CREATE INDEX IF NOT EXISTS conversations_updated_idx ON conversations(updated_at DESC);

-- Messages
CREATE TABLE IF NOT EXISTS messages (
    id SERIAL PRIMARY KEY,
    message_key TEXT UNIQUE NOT NULL,
    conversation_id INTEGER NOT NULL REFERENCES conversations(id) ON DELETE CASCADE,

    -- Content
    role TEXT NOT NULL CHECK (role IN ('user', 'assistant')),
    content TEXT NOT NULL,

    -- LLM Metadata
    model TEXT,
    tokens_used INTEGER,
    inference_time_ms INTEGER,

    -- Epistemic state
    claims_detected INTEGER[] DEFAULT '{}',
    gaps_identified INTEGER[] DEFAULT '{}',
    gmif_level TEXT,

    -- Timestamps
    created_at TIMESTAMPTZ NOT NULL DEFAULT NOW()
);

CREATE INDEX IF NOT EXISTS messages_conversation_idx ON messages(conversation_id);
CREATE INDEX IF NOT EXISTS messages_created_idx ON messages(created_at DESC);

-- Message-Claim links (N:M)
CREATE TABLE IF NOT EXISTS message_claims (
    id SERIAL PRIMARY KEY,
    message_id INTEGER NOT NULL REFERENCES messages(id) ON DELETE CASCADE,
    claim_id INTEGER NOT NULL REFERENCES governed_claims(id) ON DELETE CASCADE,
    relationship TEXT NOT NULL DEFAULT 'mentions',
    salience REAL NOT NULL DEFAULT 0.5,
    UNIQUE(message_id, claim_id)
);

CREATE INDEX IF NOT EXISTS message_claims_message_idx ON message_claims(message_id);
CREATE INDEX IF NOT EXISTS message_claims_claim_idx ON message_claims(claim_id);

-- Message-Gap links (N:M)
CREATE TABLE IF NOT EXISTS message_gaps (
    id SERIAL PRIMARY KEY,
    message_id INTEGER NOT NULL REFERENCES messages(id) ON DELETE CASCADE,
    gap_id INTEGER NOT NULL REFERENCES gaps(id) ON DELETE CASCADE,
    relationship TEXT NOT NULL DEFAULT 'identifies',
    UNIQUE(message_id, gap_id)
);

CREATE INDEX IF NOT EXISTS message_gaps_message_idx ON message_gaps(message_id);
CREATE INDEX IF NOT EXISTS message_gaps_gap_idx ON message_gaps(gap_id);
"""


async def init_schema_chat(conn) -> None:
    """Initialize chat schema."""
    await conn.execute(SCHEMA_CHAT)


async def drop_schema_chat(conn) -> None:
    """Drop chat schema (for testing)."""
    await conn.execute("""
        DROP TABLE IF EXISTS message_gaps CASCADE;
        DROP TABLE IF EXISTS message_claims CASCADE;
        DROP TABLE IF EXISTS messages CASCADE;
        DROP TABLE IF EXISTS conversations CASCADE;
    """)