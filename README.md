# Grilo Falante v3.0

**Regime de Governança Cognitiva Assistida para Produção de Conhecimento com LLMs**

Sistema unificado que consolida:
- **Grilo Falante v2.5.0**: Regime de governança cognitiva
- **GePeTo**: Infraestrutura operacional com PostgreSQL + MCP

---

## O Que É

O Grilo Falante é um regime de governação cognitiva que **não produz decisões, não valida verdades, não confere autoridade factual**. A sua única função é **impedir que decisões sejam tomadas sem método explícito e sem custo humano visível**.

> *"Este regime não impede erros. Impede que erros sejam cometidos sem que alguém tenha de olhar para eles de frente."*

---

## Arquitectura

```
grilo_falante/
├── regime/                    # Regime teórico e documentação
│   ├── regime.md             # Definição formal
│   ├── graphs/               # DOT epistemic graphs (G1-G15)
│   ├── capsules/             # Cápsulas conceptuais
│   └── contracts/             # Contratos normativos
├── backend/                   # Backend Python
│   ├── grilo_falante/        # Package principal
│   ├── api/                  # FastAPI REST
│   ├── mcp/                 # MCP Server
│   ├── services/             # Serviços de negócio
│   ├── db/                   # PostgreSQL + repositories
│   └── models/               # Pydantic models
├── frontend/                  # React + D3.js
├── docs/                     # Documentação técnica
├── docker/                   # Docker compose
└── ledger/                   # Registo persistente
```

---

## Quick Start

```bash
# Development
make dev

# Run tests
make test

# Run audit
make audit

# Build system.md
make build

# Start services
docker-compose up -d
```

---

## Ferramentas MCP

~25 tools para integração com OpenCode, Claude Desktop, Gemini:

```
 Regime: grilo_status, grilo_load, grilo_unload, grilo_acordar, grilo_vai_dormir
  Audit: grilo_audit, grilo_lint
   GFID: grilo_generate_gfid, grilo_classify_gmif
   PINA: grilo_pina_propose, grilo_pina_decide, grilo_pina_status
  Query: gepeto_query, gepeto_school_mode, gepeto_feynman_explain
 Claims: gepeto_get_claim, gepeto_create_claim, gepeto_validate_claim
   Gaps: gepeto_list_gaps, gepeto_get_gap, gepeto_resolve_gap
Curator: gepeto_create_curator, gepeto_get_curator, gepeto_list_sources
 Learning: gepeto_learning_path, gepeto_session_prefs
```

---

## GMIF Classification

| Level | Name | When to Use |
|-------|------|-------------|
| M1 | Primary Evidence | Multiple independent sources |
| M2 | Contextual | Valid under specific assumptions |
| M3 | Partial | Limited structure support |
| M4 | Doubtful | Contradictions detected |
| M5 | Interpretation | Single clear source |
| M6 | Derived | Logically inferred |
| M7 | Synthesis | Aggregated from multiple sources |
| M8 | Conclusion | Provisional conclusion |

---

## State Machine

```
INACTIVE → LOADED → ACTIVE → GOVERNING ↔ HIBERNATED
```

---

## License

MIT
