---
name: grilo_falante
description: Grilo Falante v3.0 - Epistemic Governance Regime via MCP
trigger: /grilo
---

# /grilo

Grilo Falante v3.0 — **Shell Conversacional Governada** para análise epistemológica.

## Arquitectura

```
┌─────────────────────────────────────────────────────────────┐
│                    GRILO FALANTE v3.0                       │
├─────────────────────────────────────────────────────────────┤
│  MCP Server (port 8000)                                     │
│  ├── 40+ tools for LLM interaction                         │
│  └── Regime lifecycle management                            │
│                                                              │
│  ChatShell (/grilo chat)                                   │
│  ├── Claims extraction                                      │
│  ├── GMIF classification (M1-M7)                           │
│  └── Automatic storage in MemPalace + PostgreSQL            │
└─────────────────────────────────────────────────────────────┘
```

## Quick Start

```bash
# 1. Chat interactivo
/grilo chat

# 2. Iniciar regime
grilo_load()
grilo_acordar(temporal_anchor="2026-04-15", intention="Analisar relatório")

# 3. Trabalhar
> A temperatura global aumentou 1.1°C desde 1880.

# 4. Terminar
:quit
```

---

## Comandos CLI

| Comando | Descrição |
|---------|-----------|
| `/grilo chat` | Iniciar chat governado |
| `/grilo chat --session <id>` | Retomar sessão |
| `/grilo analyse <path>` | Analisar ficheiro |
| `/grilo search "<query>"` | Pesquisar em MemPalace |
| `/grilo stats` | Estatísticas |

---

## Regime Lifecycle

```
INACTIVE ──grilo_load()──> LOADED ──grilo_acordar()──> ACTIVE ──govern()──> GOVERNING
                                                              │
                              grilo_vai_dormir()               │ (trabalho)
                                     │                        │
                                     ▼                        │
                               HIBERNATED <────────────────────┘
```

**Estados:**
- `INACTIVE`: Sistema parado
- `LOADED`: Regime carregado mas não ativo
- `ACTIVE`: Regime ativo em modo exploração
- `GOVERNING`: Regime em modo governado (chat activo)
- `HIBERNATED`: Regime adormecido

### Comandos de Regime

| Tool | Descrição |
|------|-----------|
| `grilo_load` | Carregar regime |
| `grilo_unload` | Terminar ciclo |
| `grilo_acordar` | Wake-up ritual (temporal_anchor, intention) |
| `grilo_vai_dormir` | Hibernar (sync - apenas transição) |
| `grilo_vai_dormir_async` | Hibernar com ciclo dormir completo |
| `grilo_resume` | Retomar de hibernação |
| `grilo_status` | Estado actual |
| `grilo_health` | Verificação saúde |

### Comandos Chat (no shell interactivo)

| Comando | Descrição |
|---------|-----------|
| `:quit` | Sair (executa dormir antes) |
| `:save` | Guardar sessão |
| `:export` | Exportar script de resume |
| `:status` | Ver estado |
| `:ilhas` | Listar ilhas activas |
| `:dormir` | Forçar ciclo dormir |
| `:acordar` | Restaurar contexto das ilhas |

---

## Chat Governado

O `/grilo chat` cria uma shell interativa onde cada mensagem é:

1. **Extraída** para claims
2. **Classificada** com GMIF (M1-M7)
3. **Verificada** pelo governance gate
4. **Guardada** em MemPalace + PostgreSQL

### Chat MCP Tools

| Tool | Descrição |
|------|-----------|
| `grilo_chat_start` | Iniciar sessão de chat |
| `grilo_chat_send` | Enviar mensagem |
| `grilo_chat_end` | Terminar sessão |
| `grilo_export_session` | Exportar para resume |
| `grilo_import_session` | Importar sessão (bash ou JSON) |

---

## School Mode (Ir à Escola)

O School Mode é um **modo temporário** para resolver lacunas de conhecimento.

### Fluxo Completo

```
GOVERNING ──gepeto_school_mode()──> EM_ESCOLA
                                    │
                         [processamento_batch]
                                    │
                         gepeto_sair_da_escola()
                                    │
                                    ▼
                              GOVERNING
```

**IMPORTANTE:** School mode TEM saída. Use `gepeto_sair_da_escola()` para voltar.

### Comandos

| Tool | Descrição |
|------|-----------|
| `gepeto_school_mode` | Entrar em modo escola |
| `gepeto_sair_da_escola` | Sair e voltar a GOVERNING |

---

## GMIF Classification

| Level | Nome | Quando Usar |
|-------|------|-------------|
| M1 | Primary | Múltiplas fontes independentes |
| M2 | Contextual | Válido com suposições |
| M3 | Partial | Estrutura incompleta |
| M4 | Doubtful | Contradições detetadas |
| M5 | Interpretation | Uma fonte clara |
| M6 | Derived | Inferência lógica |
| M7 | Synthesis | Agregado final |

---

## Tools Hierarchy

### Regime (obrigatório)
```
grilo_load, grilo_unload, grilo_acordar, grilo_vai_dormir, grilo_resume
```

### Chat 🆕
```
grilo_chat_start, grilo_chat_send, grilo_chat_end, grilo_export_session, grilo_import_session
```

### Query
```
gepeto_query, grilo_semantic_search, grilo_generate_gfid
```

### Claims
```
gepeto_create_claim, gepeto_get_claim, gepeto_validate_claim, grilo_classify_gmif
```

### Gaps
```
gepeto_list_gaps, gepeto_get_gap, gepeto_resolve_gap, gepeto_school_mode
```

### PINA
```
grilo_pina_propose, grilo_pina_decide, grilo_pina_status, grilo_pina_pending
```

### Governance
```
grilo_audit, grilo_lint, grilo_run_auditoria_hostil
```

---

## Exemplos

### Chat Completo

```python
# Iniciar sessão
grilo_chat_start(
    intention="Analisar relatório de vendas",
    temporal_anchor="2026-04-15"
)
# → {"success": true, "session_id": "mcp_260415_xxx", "state": "GOVERNING"}

# Enviar mensagem
grilo_chat_send(
    message="As vendas aumentaram 20% no Q1.",
    session_id="mcp_260415_xxx"
)
# → {"claims_extracted": 2, "gmif_summary": {"fact": 1, "claim": 1}, "governance_passed": true}

# Terminar
grilo_chat_end(session_id="mcp_260415_xxx")
```

### Query com RAG

```python
# Pesquisa semântica (~10ms)
grilo_semantic_search(query="mudanças climáticas", limit=5)

# Query completa com governance
gepeto_query(query="Quais são as conclusões?", session_id="default")
```

### PINA Protocol

```python
# Propor norma
grilo_pina_propose(
    source_document="relatorio.pdf",
    faithful_statement="Todas as fontes devem ser renováveis",
    location="page 5"
)

# Decidir (A=incorporar, B=rejeitar, C=adiar)
grilo_pina_decide(nca_id="NCA-xxx", decision="A")
```

---

## Arquitectura de Memória

```
Query → MemPalace (cache ~10ms) → PostgreSQL (autoritativo)
              ↓
       Se cache miss → Full retrieval
```

- **MemPalace** (ChromaDB): Cache semântico rápido
- **PostgreSQL + pgvector**: Store autoritativo com embeddings

---

## Manual API (RAG)

O manual está disponível via REST para integração RAG:

```bash
# Índice
GET /api/v1/manual/

# Capítulo
GET /api/v1/manual/{chapter}

# Pesquisa
GET /api/v1/manual/search?q=GMIF
```

---

## Notas

- Regime lifecycle é **obrigatório** — sem `grilo_load()` + `grilo_acordar()`, sistema está INACTIVE
- Claims com "obviamente", "claramente" são **bloqueadas** até verificação
- PINA requer **decisão humana** — LLM só propõe
- 40+ tools disponíveis via MCP
