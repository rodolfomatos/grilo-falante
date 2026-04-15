# 27. Cheatsheet

Referência rápida para comandos mais comuns.

---

## Quick Start

```bash
# 1. Instalar
docker-compose up -d

# 2. Chat governado
python3 -m app.skills.grilo_falante_skill chat

# 3. Iniciar ciclo
grilo_load()
grilo_acordar(temporal_anchor="2026-04-15", intention="...")

# 4. Trabalhar
> tua mensagem aqui

# 5. Terminar
:quit
```

---

## CLI Commands

```bash
# Chat interativo
/grilo chat
/grilo chat --session <id>

# Analisar ficheiro
/grilo analyse <path>

# Pesquisar memória
/grilo search "<query>"

# Estatísticas
/grilo stats
```

---

## MCP Tools - Regime

```python
# Iniciar ciclo
grilo_load()
grilo_acordar(temporal_anchor="2026-04-15", intention="...")
grilo_vai_dormir()      # Hibernar
grilo_resume()           # Retomar
grilo_status()           # Estado

#Chat
grilo_chat_start(intention="...")
grilo_chat_send(message="...", session_id="...")
grilo_chat_end(session_id="...")
grilo_export_session(session_id="...")
```

---

## MCP Tools - Claims

```python
# Criar
gepeto_create_claim(
    claim_text="...",
    gmif_level="M5",
    source_id=1
)

# Obter
gepeto_get_claim(claim_id=1)

# Validar
gepeto_validate_claim(
    claim_id=1,
    decision="approved"
)

# Classificar
grilo_classify_gmif(claim_text="...", source_count=1)
```

---

## MCP Tools - Query

```python
# Query com governance
gepeto_query(query="...", session_id="default")

# Pesquisa semântica (rápida)
grilo_semantic_search(query="...", limit=5)
```

---

## MCP Tools - Gaps

```python
# Listar
gepeto_list_gaps()

# Obter
gepeto_get_gap(gap_key="GAP-xxx")

# Resolver
gepeto_resolve_gap(gap_key="GAP-xxx", claim_key="CLM-xxx")

# School mode
gepeto_school_mode(gap_key="GAP-xxx")
```

---

## MCP Tools - PINA

```python
# Propor norma
grilo_pina_propose(
    source_document="...",
    faithful_statement="...",
    location="..."
)

# Decidir
grilo_pina_decide(nca_id="NCA-xxx", decision="A")

# Ver estado
grilo_pina_status()
grilo_pina_pending()
```

---

## GMIF Levels

| Level | Nome | Quando |
|-------|------|--------|
| M1 | Primary | Múltiplas fontes |
| M2 | Contextual | Com suposições |
| M3 | Partial | Estrutura incompleta |
| M4 | Doubtful | Contradições |
| M5 | Interpretation | Uma fonte |
| M6 | Derived | Inferência |
| M7 | Synthesis | Agregado |

---

## REST Endpoints

```bash
# Base
curl http://localhost:8001/health

# Claims
GET  /api/v1/claims/{id}
POST /api/v1/claims
POST /api/v1/claims/{id}/validate

# Gaps
GET  /api/v1/gaps
POST /api/v1/gaps/{key}/school-mode

# PINA
GET /api/v1/pina/pending
GET /api/v1/pina/status
GET /api/v1/pina/invariants

# Query
POST /api/v1/query

# Manual (RAG)
GET /api/v1/manual/
GET /api/v1/manual/{chapter}
GET /api/v1/manual/search?q=...
```

---

## Regime Lifecycle

```
INACTIVE
    │
    │ grilo_load()
    ▼
LOADED
    │
    │ grilo_acordar()
    ▼
GOVERNING ◄──────┐
    │             │
    │ grilo_vai_  │ grilo_
    │ dormir()    │ resume()
    ▼             │
HIBERNATED ──────┘
```

---

## Chat Commands

```
:quit, :exit    Sair
:save           Guardar sessão
:export         Exportar script resume
:status         Ver estado
```

---

## Environment Variables

```bash
# Base de dados
DATABASE_URL=postgresql://user:pass@host:5432/db

# MemPalace
MEMPALACE_PATH=/home/rodolfo/.mempalace

# LLM
OLLAMA_BASE_URL=http://localhost:11434
OPENWEBUI_BASE_URL=http://localhost:8080

# API
API_TOKEN=your_token_here
```

---

## Ports

| Serviço | Porta |
|---------|-------|
| MCP Server | 8001 |
| REST API | 8001 |
| PostgreSQL | 5432 |
| Ollama | 11434 |
| OpenWebUI | 8080 |

---

## Ficheiros Importantes

```
grilo_falante_v3.0/
├── grilo_falante/
│   ├── backend/
│   │   ├── mcp/server.py      # 40+ MCP tools
│   │   ├── api/main.py        # REST API
│   │   ├── memory/            # MemPalace, pgvector
│   │   └── services/          # Business logic
│   ├── regime/                # State machine
│   │   ├── state.py           # CycleState
│   │   ├── loader.py          # Loader
│   │   ├── acordar.py         # ACORDAR
│   │   └── pina.py            # PINA
│   └── models/                # Pydantic models
├── app/
│   ├── skills/
│   │   └── chat_shell.py      # Chat governado
│   └── integrations/
│       └── graphify_integration.py
├── docs/manual/                # Este manual
└── docker/
    └── docker-compose.yml
```

---

## Troubleshooting

```bash
# Ver estado dos serviços
docker-compose ps

# Logs
docker-compose logs -f app

# Reiniciar
docker-compose restart

# Tests
python3 -m pytest grilo_falante/tests/ -v
```

---

*Voltar ao [Índice](../00_INDICE.md)*
