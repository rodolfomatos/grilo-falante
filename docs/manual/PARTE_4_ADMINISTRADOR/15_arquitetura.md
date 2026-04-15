# 15. Arquitetura Técnica

## Visão Geral

```
┌─────────────────────────────────────────────────────────────┐
│                                                             │
│                    GRILO FALANTE v3.0                      │
│                                                             │
├─────────────────────────────────────────────────────────────┤
│                                                             │
│  ┌─────────────────────────────────────────────────────┐  │
│  │                   INTERFACES                        │  │
│  │  MCP Server (8001)  │  REST API (8001)            │  │
│  │  OpenWebUI (8080)   │  CLI                        │  │
│  └─────────────────────────────────────────────────────┘  │
│                           │                               │
│                           ▼                               │
│  ┌─────────────────────────────────────────────────────┐  │
│  │              CAMADA DE APLICAÇÃO                   │  │
│  │  ChatShell │ Pipeline │ Auditoria │ PINA           │  │
│  └─────────────────────────────────────────────────────┘  │
│                           │                               │
│                           ▼                               │
│  ┌─────────────────────────────────────────────────────┐  │
│  │              CAMADA DE DADOS                        │  │
│  │  Regime │ Memory │ Governance │ Cognitive           │  │
│  └─────────────────────────────────────────────────────┘  │
│                           │                               │
│                           ▼                               │
│  ┌──────────────┐ ┌──────────────┐ ┌──────────────┐  │
│  │  PostgreSQL  │ │   MemPalace  │ │    Ollama    │  │
│  │  + pgvector │ │   (ChromaDB) │ │  (Embeddings)│  │
│  └──────────────┘ └──────────────┘ └──────────────┘  │
│                                                             │
└─────────────────────────────────────────────────────────────┘
```

---

## Estrutura de Diretórios

```
grilo_falante_v3.0/
├── grilo_falante/           # Package principal
│   ├── backend/
│   │   ├── api/            # REST API (FastAPI)
│   │   ├── mcp/            # MCP Server
│   │   ├── db/             # PostgreSQL repositórios
│   │   ├── memory/         # MemPalace, Vector, KG
│   │   └── services/       # Lógica de negócio
│   ├── regime/             # State machine, lifecycle
│   │   ├── state.py        # CycleState, StateMachine
│   │   ├── loader.py       # LOADER
│   │   ├── acordar.py      # ACORDAR
│   │   ├── pina.py         # PINA protocol
│   │   └── ledger.py      # Audit trail
│   ├── cognitive/          # Kanban, Auditoria
│   └── models/            # Pydantic models
├── app/                   # Serviços de alto nível
│   ├── skills/            # ChatShell, GriloSkill
│   └── integrations/       # Graphify integration
├── docs/                  # Documentação
│   └── manual/            # Este manual
└── docker/               # Docker Compose
```

---

## Componentes

### MCP Server
- Protocolo para LLMs
- 40+ tools
- Porta 8001

### REST API
- FastAPI
- 29+ endpoints
- Porta 8001

### PostgreSQL + pgvector
- Store autoritativo
- Pesquisa vetorial
- Schema: `governed_claims`, `gaps`, `curators`, etc.

### MemPalace
- Cache semântico (ChromaDB)
- Pesquisa rápida (~10ms)
- Wing `wing_conversas` para chat

### Ollama
- Embeddings locais
- Modelo: `nomic-embed-text`

---

## Fluxo de Dados

```
USER INPUT
    │
    ▼
┌─────────────┐
│ MCP/REST   │  ← Interfaces
└──────┬──────┘
       │
       ▼
┌─────────────┐
│ ChatShell   │  ← Aplicação
│ Pipeline    │
└──────┬──────┘
       │
       ├──────────────────────┐
       ▼                      ▼
┌─────────────┐        ┌─────────────┐
│ MemPalace   │        │ PostgreSQL  │
│ (cache)     │        │ (authoritative)│
└─────────────┘        └─────────────┘
```

---

## Modelo de Dados

### Claims
```python
GovernedClaim:
  - claim_key: str      # GF-YYMMDD-TYPE-HASH
  - claim_text: str
  - gmif_level: GMIFLevel  # M1-M7
  - gmif_confidence: float
  - source_id: int
  - session_id: str
```

### Gaps
```python
Gap:
  - gap_key: str         # GAP-YYMMDD-HASH
  - gap_type: GapType     # factual, conceptual, etc.
  - query: str
  - reason: str
  - status: GapStatus    # identified, resolved, etc.
```

---

## Segurança

- Autenticação via API token
- Rate limiting opcional
- Ledger imutável para audit

---

## Performance

| Operação | Latência |
|----------|----------|
| MemPalace search | ~10ms |
| PostgreSQL query | ~50ms |
| Embedding generation | ~200ms |

---

*Voltar ao [Índice](../00_INDICE.md)*
