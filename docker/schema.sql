-- Grilo Falante v3.0 - Database Schema
-- PostgreSQL with pgvector extension

-- Extension for vector similarity
CREATE EXTENSION IF NOT EXISTS vector;

-- Curator table
CREATE TABLE IF NOT EXISTS curators (
    id SERIAL PRIMARY KEY,
    curator_key TEXT UNIQUE NOT NULL,
    name TEXT NOT NULL,
    curator_type TEXT NOT NULL DEFAULT 'human',
    model_name TEXT,
    specializations TEXT[] DEFAULT '{}',
    accountability_score REAL NOT NULL DEFAULT 0.5,
    is_active BOOLEAN NOT NULL DEFAULT TRUE,
    last_activity TIMESTAMPTZ,
    created_at TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    updated_at TIMESTAMPTZ
);

CREATE INDEX IF NOT EXISTS curators_key_idx ON curators(curator_key);
CREATE INDEX IF NOT EXISTS curators_type_idx ON curators(curator_type);

-- Governed sources table
CREATE TABLE IF NOT EXISTS governed_sources (
    id SERIAL PRIMARY KEY,
    source_key TEXT UNIQUE NOT NULL,
    title TEXT NOT NULL,
    authors TEXT[] DEFAULT '{}',
    year INTEGER,
    doi TEXT,
    url TEXT,
    source_type TEXT NOT NULL DEFAULT 'paper',
    source_origin TEXT NOT NULL DEFAULT 'unknown',
    tier TEXT NOT NULL DEFAULT 'tier_2',
    validation_status TEXT NOT NULL DEFAULT 'pending',
    ingestion_origin TEXT NOT NULL DEFAULT 'manual',
    raw_metadata JSONB DEFAULT '{}',
    created_at TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    updated_at TIMESTAMPTZ
);

CREATE INDEX IF NOT EXISTS sources_key_idx ON governed_sources(source_key);
CREATE INDEX IF NOT EXISTS sources_origin_idx ON governed_sources(source_origin);

-- Shadow documents table
CREATE TABLE IF NOT EXISTS shadow_documents (
    id SERIAL PRIMARY KEY,
    source_id INTEGER NOT NULL REFERENCES governed_sources(id) ON DELETE CASCADE,
    factual_summary TEXT DEFAULT '',
    projected_claims TEXT[] DEFAULT '{}',
    citations JSONB DEFAULT '[]',
    limits TEXT[] DEFAULT '{}',
    misuse_risks TEXT[] DEFAULT '{}',
    status TEXT NOT NULL DEFAULT 'pending',
    validation_notes TEXT,
    f1_count INTEGER DEFAULT 0,
    f2_count INTEGER DEFAULT 0,
    created_at TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    updated_at TIMESTAMPTZ
);

CREATE INDEX IF NOT EXISTS shadow_source_idx ON shadow_documents(source_id);

-- Governed claims table
CREATE TABLE IF NOT EXISTS governed_claims (
    id SERIAL PRIMARY KEY,
    claim_key TEXT UNIQUE NOT NULL,
    claim_text TEXT NOT NULL,
    claim_type TEXT NOT NULL DEFAULT 'core_claim',
    source_id INTEGER REFERENCES governed_sources(id) ON DELETE SET NULL,
    session_id TEXT NOT NULL DEFAULT 'global',
    gmif_level TEXT NOT NULL DEFAULT 'M4',
    gmif_confidence REAL NOT NULL DEFAULT 0.5,
    attribution TEXT NOT NULL DEFAULT 'source_explicit',
    epistemic_role TEXT NOT NULL DEFAULT 'descriptive',
    legitimacy_state TEXT NOT NULL DEFAULT 'unvalidated',
    validation_status TEXT NOT NULL DEFAULT 'pending',
    provenance JSONB DEFAULT '{}',
    usage_count INTEGER NOT NULL DEFAULT 0,
    last_used TIMESTAMPTZ,
    gfid TEXT,
    created_at TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    updated_at TIMESTAMPTZ
);

CREATE INDEX IF NOT EXISTS claims_key_idx ON governed_claims(claim_key);
CREATE INDEX IF NOT EXISTS claims_gmif_idx ON governed_claims(gmif_level);
CREATE INDEX IF NOT EXISTS claims_session_idx ON governed_claims(session_id);
CREATE INDEX IF NOT EXISTS claims_confidence_idx ON governed_claims(gmif_confidence);

-- Gaps table
CREATE TABLE IF NOT EXISTS gaps (
    id SERIAL PRIMARY KEY,
    gap_key TEXT UNIQUE NOT NULL,
    gap_type TEXT NOT NULL DEFAULT 'tipo_a_failure',
    query TEXT NOT NULL,
    claim_template JSONB DEFAULT '{}',
    reason TEXT NOT NULL,
    expected_claim TEXT,
    status TEXT NOT NULL DEFAULT 'identified',
    resolved_claim_id INTEGER REFERENCES governed_claims(id) ON DELETE SET NULL,
    resolved_by INTEGER REFERENCES curators(id) ON DELETE SET NULL,
    resolved_at TIMESTAMPTZ,
    related_claim_ids INTEGER[] DEFAULT '{}',
    created_at TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    updated_at TIMESTAMPTZ
);

CREATE INDEX IF NOT EXISTS gaps_key_idx ON gaps(gap_key);
CREATE INDEX IF NOT EXISTS gaps_status_idx ON gaps(status);

-- Study plans table
CREATE TABLE IF NOT EXISTS study_plans (
    id SERIAL PRIMARY KEY,
    plan_key TEXT UNIQUE NOT NULL,
    gap_key TEXT,
    topic TEXT NOT NULL,
    steps JSONB DEFAULT '[]',
    status TEXT NOT NULL DEFAULT 'identified',
    current_step INTEGER NOT NULL DEFAULT 0,
    completed_steps INTEGER NOT NULL DEFAULT 0,
    created_at TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    updated_at TIMESTAMPTZ
);

CREATE INDEX IF NOT EXISTS plans_key_idx ON study_plans(plan_key);
CREATE INDEX IF NOT EXISTS plans_gap_idx ON study_plans(gap_key);

-- Evaluations table
CREATE TABLE IF NOT EXISTS evaluations (
    id SERIAL PRIMARY KEY,
    claim_id INTEGER NOT NULL REFERENCES governed_claims(id) ON DELETE CASCADE,
    curator_id INTEGER NOT NULL REFERENCES curators(id) ON DELETE CASCADE,
    evaluation_type TEXT NOT NULL DEFAULT 'validation',
    decision TEXT NOT NULL,
    notes TEXT,
    evaluator_confidence REAL,
    created_at TIMESTAMPTZ NOT NULL DEFAULT NOW()
);

CREATE INDEX IF NOT EXISTS eval_claim_idx ON evaluations(claim_id);
CREATE INDEX IF NOT EXISTS eval_curator_idx ON evaluations(curator_id);

-- Session preferences table
CREATE TABLE IF NOT EXISTS session_preferences (
    session_id TEXT PRIMARY KEY,
    topics TEXT[] DEFAULT '{}',
    domains TEXT[] DEFAULT '{}',
    recency_weight REAL NOT NULL DEFAULT 0.3,
    preferred_categories TEXT[] DEFAULT '{M1,M2,M5,M7}',
    show_metadata BOOLEAN NOT NULL DEFAULT TRUE,
    auto_school_mode BOOLEAN NOT NULL DEFAULT TRUE,
    confidence_display TEXT NOT NULL DEFAULT 'full',
    updated_at TIMESTAMPTZ NOT NULL DEFAULT NOW()
);

-- Governance records table (immutable audit log)
CREATE TABLE IF NOT EXISTS governance_records (
    id SERIAL PRIMARY KEY,
    record_key TEXT UNIQUE NOT NULL,
    entity_type TEXT NOT NULL,
    entity_id INTEGER NOT NULL,
    entity_key TEXT NOT NULL,
    action TEXT NOT NULL,
    decision TEXT NOT NULL,
    reason TEXT,
    previous_state TEXT,
    new_state TEXT NOT NULL,
    curator_id INTEGER REFERENCES curators(id) ON DELETE SET NULL,
    curator_key TEXT,
    curator_confidence REAL,
    metadata JSONB DEFAULT '{}',
    created_at TIMESTAMPTZ NOT NULL DEFAULT NOW()
);

CREATE INDEX IF NOT EXISTS governance_entity_idx ON governance_records(entity_type, entity_id);
CREATE INDEX IF NOT EXISTS governance_curator_idx ON governance_records(curator_key);
CREATE INDEX IF NOT EXISTS governance_time_idx ON governance_records(created_at);

-- Curator score history for decay tracking
CREATE TABLE IF NOT EXISTS curator_score_history (
    id SERIAL PRIMARY KEY,
    curator_id INTEGER NOT NULL REFERENCES curators(id) ON DELETE CASCADE,
    old_score REAL NOT NULL,
    new_score REAL NOT NULL,
    reason TEXT NOT NULL,
    created_at TIMESTAMPTZ NOT NULL DEFAULT NOW()
);

CREATE INDEX IF NOT EXISTS curator_history_idx ON curator_score_history(curator_id);
