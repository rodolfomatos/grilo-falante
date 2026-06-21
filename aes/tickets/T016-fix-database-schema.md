---
ticket: T016
title: Fix database schema gaps (claim_embeddings, ILHAS, init_db startup)
sprint: sprint-02
priority: critical
status: pending
created: 2026-06-21
tags: phase-a, critical, db
---

# T016 — Fix Database Schema Gaps

## Context
Três bugs críticos na camada de base de dados que causam runtime errors:

1. `claim_embeddings` é referenciada em `repositories.py` (JOIN, INSERT, SELECT)
   mas NUNCA criada no schema em `connection.py`
2. Schema ILHAS (`schema_ilhas.py`) define 6 tabelas mas `init_schema_ilhas()` 
   nunca é chamado em `init_db()`
3. `init_db()` é definida em `connection.py` mas NUNCA é chamada no startup
   do FastAPI (`main.py`)

## Acceptance Criteria
- [ ] `claim_embeddings` table é criada no schema init
- [ ] `init_schema_ilhas()` é chamada em `init_db()`
- [ ] FastAPI startup chama `init_db()` via `@app.on_event("startup")`
- [ ] Teste manual: import e init_db() não lança excepções
