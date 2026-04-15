# Grilo Falante v3.0

**Regime de Governança Cognitiva Assistida para Produção de Conhecimento com LLMs**

Sistema unificado que consolida:
- **Grilo Falante**: Regime de governança cognitiva
- **GePeTo**: Infraestrutura operacional
- **epistemic-memory-architecture**: Governance layer e hybrid retrieval

---

## O Que É

O Grilo Falante é um regime de governação cognitiva que **não produz decisões, não valida verdades, não confere autoridade factual**. A sua única função é **impedir que decisões sejam tomadas sem método explícito e sem custo humano visível**.

> *"Este regime não impede erros. Impede que erros sejam cometidos sem que alguém tenha de olhar para eles de frente."*

---

## Arquitectura

```
grilo_falante/
├── config.py                     # Configuração centralizada
├── cognitive/                    # Artefactos cognitivos
│   ├── kanban.py                # Kanban Epistemico
│   ├── auditoria.py             # Auditoria Hostil (5 eixos)
│   └── prompt_workflows.py       # TRIAGEM + RADIOGRAFIA
├── models/
│   ├── shadow.py                # ShadowDocument, ConceptualCapsule
│   └── *.py                    # Pydantic models
└── backend/
    ├── api/main.py             # FastAPI REST API (30+ endpoints)
    ├── auth.py                 # Bearer token auth + rate limiting
    ├── cognitive/              # Cognitive services
    ├── ingestion/
    │   ├── pdf_ingestion.py    # OpenDataLoader PDF parsing
    │   └── shadow_document_generator.py
    ├── memory/
    │   ├── vector_index.py     # pgvector similarity
    │   ├── knowledge_graph.py  # Knowledge graph store
    │   └── hybrid_retrieval.py # 65% semantic + 35% epistemic
    ├── reasoning/
    │   └── graph_linter.py     # Graph Lint (L1-L8)
    ├── services/
    │   ├── governance/         # GovernanceLayer, TransitionValidator
    │   ├── llm/               # Ollama, IAEDU, OpenWebUI
    │   └── *.py               # Services
    └── mcp/server.py           # MCP Server (21 tools)
```

---

## Quick Start

```bash
# 1. Clone
git clone https://github.com/.../grilo_falante_v3.0.git
cd grilo_falante_v3.0

# 2. Configure
cp .env.example .env
# Edit .env with your settings

# 3. Start with Docker
docker-compose up -d

# Or development
make dev

# Run tests
make test
```

---

## API Endpoints

### Core
| Method | Endpoint | Description |
|--------|----------|-------------|
| GET | `/health` | Health check |
| POST | `/api/v1/query` | Execute epistemic query |
| POST | `/api/v1/claims` | Create claim |
| GET | `/api/v1/claims/{id}` | Get claim |
| GET | `/api/v1/claims/{id}/card` | Get claim card |
| POST | `/api/v1/claims/{id}/validate` | Validate claim |

### Sources
| Method | Endpoint | Description |
|--------|----------|-------------|
| POST | `/api/v1/sources` | Create source |
| GET | `/api/v1/sources` | List sources |
| GET | `/api/v1/registry/sources` | Trusted registry |
| POST | `/api/v1/registry/proposals` | Propose change |

### Gaps & Learning
| Method | Endpoint | Description |
|--------|----------|-------------|
| GET | `/api/v1/gaps` | List gaps |
| POST | `/api/v1/gaps` | Create gap |
| POST | `/api/v1/gaps/{key}/school-mode` | Execute school mode |
| POST | `/api/v1/learning-path` | Generate learning path |

### Ingestion
| Method | Endpoint | Description |
|--------|----------|-------------|
| POST | `/api/v1/ingest/pdf` | Upload PDF |
| GET | `/api/v1/shadow/{source_id}` | Get shadow document |

### Cognitive
| Method | Endpoint | Description |
|--------|----------|-------------|
| GET | `/api/v1/kanban` | Kanban state |
| POST | `/api/v1/kanban/movements` | Create movement |
| POST | `/api/v1/audit` | Run hostile audit |
| POST | `/api/v1/prompts/triagem` | TRIAGEM workflow |
| POST | `/api/v1/prompts/radiografia` | RADIOGRAFIA workflow |

### Graph
| Method | Endpoint | Description |
|--------|----------|-------------|
| GET | `/api/v1/graph/dot` | Get DOT graph |

---

## MCP Tools (36)

### Regime Lifecycle
| Tool | Description |
|------|-------------|
| `grilo_load` | Load regime for new cycle |
| `grilo_unload` | End current cycle |
| `grilo_acordar` | Wake-up ritual with temporal anchoring |
| `grilo_vai_dormir` | Hibernate regime |
| `grilo_resume` | Resume from hibernation |
| `grilo_status` | Current regime status |
| `grilo_health` | System health check |

### PINA Protocol
| Tool | Description |
|------|-------------|
| `grilo_pina_propose` | Propose normative candidate |
| `grilo_pina_decide` | Record decision [A/B/C] |
| `grilo_pina_status` | PINA status |
| `grilo_get_ledger_stats` | Ledger statistics |

### Claims & Query
| Tool | Description |
|------|-------------|
| `gepeto_query` | Execute epistemic query |
| `gepeto_get_claim` | Get claim by ID |
| `gepeto_create_claim` | Create claim |
| `gepeto_validate_claim` | Validate claim |
| `grilo_generate_gfid` | Generate GF-ID |
| `grilo_classify_gmif` | Classify by GMIF |

### Gaps & Learning
| Tool | Description |
|------|-------------|
| `gepeto_list_gaps` | List gaps |
| `gepeto_get_gap` | Get gap |
| `gepeto_resolve_gap` | Resolve gap |
| `gepeto_school_mode` | Execute school mode |

### Sources & Curators
| Tool | Description |
|------|-------------|
| `gepeto_list_sources` | List sources |
| `gepeto_get_source` | Get source |
| `gepeto_create_source` | Create source |
| `gepeto_create_curator` | Create curator |
| `gepeto_get_curator` | Get curator |
| `gepeto_session_prefs` | Session preferences |

### Cognitive Workflows
| Tool | Description |
|------|-------------|
| `grilo_run_auditoria_hostil` | Execute 5-axis hostile audit |
| `grilo_run_autopsia_literatura` | Execute literature autopsy |
| `grilo_run_triagem` | Execute triage workflow |
| `grilo_audit` | Basic hostile audit |
| `grilo_lint` | Cognitive lint |
| `grilo_stamp_capsule` | Add GF-ID header to capsule |
| `grilo_validate_transition` | Validate graph transition |
| `grilo_list_graphs` | List epistemic graphs |
| `gepeto_feynman_explain` | Feynman explanation |

---

## GMIF Classification

| Level | Name | Trigger |
|-------|------|---------|
| M1 | Primary Evidence | Multiple independent sources |
| M2 | Contextual | Valid under specific assumptions |
| M3 | Partial | Limited structure support |
| M4 | Doubtful | Contradictions detected |
| M5 | Interpretation | Single clear source |
| M6 | Derived | Logically inferred |
| M7 | Synthesis | Aggregated from multiple sources |

---

## Claim State Machine

```
derived → audited → stabilized → promoted
            ↘ contested ↗
            deprecated/archived
```

---

## Graph Lint (L1-L8)

| Code | Check |
|------|-------|
| L1 | Orphan nodes (no edges) |
| L2 | Self-referential edges |
| L3 | Contradictory edges |
| L4 | Circular dependencies |
| L5 | Unsupported conclusions (M4→M1) |
| L6 | Missing M1 prerequisites |
| L7 | Confidence mismatches |
| L8 | Temporal inconsistencies |

---

## LLM Providers

Supports multiple LLM backends:
- **Ollama** (local)
- **IAEDU** (University of Porto academic API)
- **OpenWebUI** bridge
- **OpenAI** (GPT-4o)
- **Anthropic** (Claude)

---

## Docker Services

```yaml
services:
  db:         PostgreSQL + pgvector
  ollama:     Local LLM
  openwebui:  Web UI
  api:        FastAPI
  mcp:        MCP Server
  lake:       File browser
```

---

## License

MIT
