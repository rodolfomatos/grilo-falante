# 18. Schema da Base de Dados

## Visão Geral

```
┌─────────────────────────────────────────────────────────────┐
│                                                             │
│  PostgreSQL + pgvector                                     │
│                                                             │
│  ┌─────────────┐  ┌─────────────┐  ┌─────────────┐    │
│  │  governed_  │  │    gaps     │  │  curators   │    │
│  │   claims    │  │             │  │             │    │
│  └─────────────┘  └─────────────┘  └─────────────┘    │
│                                                             │
│  ┌─────────────┐  ┌─────────────┐  ┌─────────────┐    │
│  │ governed_   │  │  session_   │  │  governance_ │    │
│  │  sources    │  │ preferences │  │   records   │    │
│  └─────────────┘  └─────────────┘  └─────────────┘    │
│                                                             │
└─────────────────────────────────────────────────────────────┘
```

---

## Tabelas Principais

### governed_claims

```sql
CREATE TABLE governed_claims (
    id SERIAL PRIMARY KEY,
    claim_key TEXT UNIQUE NOT NULL,
    claim_text TEXT NOT NULL,
    gmif_level TEXT NOT NULL,
    gmif_confidence REAL,
    source_id INTEGER REFERENCES governed_sources(id),
    session_id TEXT DEFAULT 'global',
    validation_state TEXT DEFAULT 'pending',
    created_at TIMESTAMPTZ DEFAULT NOW()
);

CREATE INDEX idx_claims_session ON governed_claims(session_id);
CREATE INDEX idx_claims_gmif ON governed_claims(gmif_level);
```

---

### gaps

```sql
CREATE TABLE gaps (
    id SERIAL PRIMARY KEY,
    gap_key TEXT UNIQUE NOT NULL,
    gap_type TEXT NOT NULL,
    query TEXT NOT NULL,
    reason TEXT,
    session_id TEXT,
    status TEXT DEFAULT 'identified',
    created_at TIMESTAMPTZ DEFAULT NOW()
);
```

---

### governed_sources

```sql
CREATE TABLE governed_sources (
    id SERIAL PRIMARY KEY,
    source_key TEXT UNIQUE NOT NULL,
    title TEXT,
    authors TEXT[],
    year INTEGER,
    source_tier TEXT,
    created_at TIMESTAMPTZ DEFAULT NOW()
);
```

---

### curators

```sql
CREATE TABLE curators (
    id SERIAL PRIMARY KEY,
    curator_key TEXT UNIQUE NOT NULL,
    name TEXT,
    curator_type TEXT,
    accountability_score REAL DEFAULT 0.5,
    specializations TEXT[],
    created_at TIMESTAMPTZ DEFAULT NOW()
);
```

---

### session_preferences

```sql
CREATE TABLE session_preferences (
    session_id TEXT PRIMARY KEY,
    topics TEXT[] DEFAULT '{}',
    domains TEXT[] DEFAULT '{}',
    recency_weight REAL DEFAULT 0.3,
    preferred_categories TEXT[] DEFAULT '{M1,M2,M5,M7}',
    show_metadata BOOLEAN DEFAULT TRUE,
    auto_school_mode BOOLEAN DEFAULT TRUE,
    updated_at TIMESTAMPTZ DEFAULT NOW()
);
```

---

### governance_records

```sql
CREATE TABLE governance_records (
    id SERIAL PRIMARY KEY,
    entity_type TEXT NOT NULL,
    entity_id TEXT NOT NULL,
    action TEXT NOT NULL,
    details JSONB,
    created_at TIMESTAMPTZ DEFAULT NOW()
);
```

---

## pgvector

Extensão para pesquisa vetorial:

```sql
CREATE EXTENSION IF NOT EXISTS vector;

-- Tabela de embeddings
CREATE TABLE claim_embeddings (
    claim_id TEXT PRIMARY KEY REFERENCES governed_claims(claim_key),
    embedding vector(768),
    created_at TIMESTAMPTZ DEFAULT NOW()
);
```

---

## Comandos Úteis

```bash
# Aceder PostgreSQL
docker-compose exec postgres psql -U grilo -d grilo_falante

# Ver tabelas
\dt

# Ver estrutura
\d governed_claims

# Query exemplo
SELECT claim_key, gmif_level FROM governed_claims LIMIT 5;
```

---

*Voltar ao [Índice](../00_INDICE.md)*
