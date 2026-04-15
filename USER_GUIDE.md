# Análise Exaustiva: Formas de Utilização do Grilo Falante

## 1. Interfaces Disponíveis

O Grilo Falante v3.0 oferece **4 interfaces** para o utilizador:

| Interface | Descrição | Tools/Endpoints |
|-----------|-----------|----------------|
| **MCP Server** | Modelo de Plugin para LLMs | 36 tools |
| **REST API** | FastAPI HTTP | 29 endpoints |
| **Skill OpenCode** | `/grilo` command | 7 subcommands |
| **CLI** | grilo_pipeline.py | Argumentos de linha |

---

## 2. MCP Server (Ferramenta Principal)

### 2.1 Estado do Regime

| Tool | Descrição | Input |
|------|-----------|-------|
| `grilo_load` | Carregar regime para novo ciclo | - |
| `grilo_unload` | Terminar ciclo atual | - |
| `grilo_acordar` | Ritual de acordar | `temporal_anchor`, `intention`, `mode` |
| `grilo_vai_dormir` | Hibernar regime | - |
| `grilo_resume` | Retomar de hibernação | - |
| `grilo_status` | Estado atual | - |
| `grilo_health` | Verificação saúde | - |

**Fluxo correto:**
```
1. grilo_load()
2. grilo_acordar(temporal_anchor="2026-04-15", intention="Analisar X")
3. [trabalho]
4. grilo_vai_dormir()
```

### 2.2 Claims e GF-ID

| Tool | Descrição |
|------|-----------|
| `grilo_generate_gfid` | Gerar identificador |
| `grilo_classify_gmif` | Classificar por força epistémica |

### 2.3 Query e Análise

| Tool | Descrição |
|------|-----------|
| `gepeto_query` | Executar query com governança |
| `gepeto_get_claim` | Obter claim por ID |
| `gepeto_create_claim` | Criar claim |
| `gepeto_validate_claim` | Validar claim |

### 2.4 Gaps e School Mode

| Tool | Descrição |
|------|-----------|
| `gepeto_list_gaps` | Listar gaps |
| `gepeto_get_gap` | Obter gap |
| `gepeto_resolve_gap` | Resolver gap |
| `gepeto_school_mode` | Executar school mode |

### 2.5 Auditoria e Workflows

| Tool | Descrição |
|------|-----------|
| `grilo_audit` | Auditoria hostil |
| `grilo_lint` | Linting cognitivo |
| `grilo_run_auditoria_hostil` | Workflow auditoria (5 eixos) |
| `grilo_run_autopsia_literatura` | Workflow autopsia literatura |
| `grilo_run_triagem` | Workflow triagem |

### 2.6 PINA Protocol

| Tool | Descrição |
|------|-----------|
| `grilo_pina_propose` | Propor normativa |
| `grilo_pina_decide` | Decidir [A/B/C] |
| `grilo_pina_status` | Estado do PINA |

### 2.7 Grafos e Transitions

| Tool | Descrição |
|------|-----------|
| `grilo_validate_transition` | Validar transição |
| `grilo_list_graphs` | Listar grafos |
| `grilo_stamp_capsule` | Assinar cápsula |

---

## 3. REST API Endpoints

### 3.1 Core
- `GET /health` - Verificação saúde
- `POST /api/v1/query` - Query com governança
- `POST /api/v1/claims` - Criar claim
- `GET /api/v1/claims/{id}` - Obter claim
- `POST /api/v1/claims/{id}/validate` - Validar

### 3.2 Sources
- `POST /api/v1/sources` - Criar source
- `GET /api/v1/sources` - Listar sources

### 3.3 Gaps
- `GET /api/v1/gaps` - Listar gaps
- `POST /api/v1/gaps` - Criar gap
- `POST /api/v1/gaps/{key}/school-mode` - School mode

### 3.4 Cognitive
- `GET /api/v1/kanban` - Estado kanban
- `POST /api/v1/kanban/movements` - Criar movimento
- `POST /api/v1/audit` - Executar auditoria
- `POST /api/v1/prompts/triagem` - Workflow triagem
- `POST /api/v1/prompts/radiografia` - Workflow radiografia

### 3.5 Ingestion
- `POST /api/v1/ingest/pdf` - Upload PDF
- `GET /api/v1/shadow/{source_id}` - Shadow document

---

## 4. SKILL OpenCode (`/grilo`)

### 4.1 Comandos

| Comando | Descrição |
|---------|-----------|
| `/grilo analyse <path>` | Analisar ficheiro/diretório |
| `/grilo analyze <text>` | Analisar texto |
| `/grilo chat` | Iniciar sessão governada |
| `/grilo status` | Estado atual |
| `/grilo memory search "<query>"` | Buscar no MemPalace |
| `/grilo memory list` | Listar wings |
| `/grilo export GF-XXXXXX` | Exportar claim |
| `/grilo graph <gf-id>` | Mostrar grafo |

### 4.2 Instalação Automática
- Wing `wing_grilo_falante` (regime)
- Wing `wing_conversas` (conversas)
- Wing `wing_artigos` (artigos)

---

## 5. CLI (grilo_pipeline.py)

```bash
python3 grilo_pipeline.py <path> [opções]

Opções:
  --no-store         Skip storage
  --cache            Use cache
  --export-html      Export HTML
  --verify-m4        Human verification of M4
  --llm PROVIDER     LLM provider (iaedu, openai, ollama)
  --graph NAME       Use state machine graph
  --intention TEXT   Set intention
  --temporal DATE    Set temporal anchor
  --log FILE         Log to file
  --dashboard        Open dashboard
  --timeout N        Timeout (default: 60)
  --retry N          Retries (default: 3)
```

---

## 6. Análise Hostil: Problemas Identificados

### 6.1 PROBLEMAS CRÍTICOS

#### P1: SKILL.md Desatualizado
**Problema:** SKILL.md menciona:
- `MemPalace` (ChromaDB) - **NÃO EXISTE em v3.0**
- `analyse <path>` - **NÃO EXISTE como tool**
- `chat` command - **NÃO EXISTE**
- `memory search/list` - **NÃO EXISTE**

**Realidade v3.0:**
- Usa **PostgreSQL + pgvector** em vez de MemPalace
- Não tem comando `analyse` - tem `gepeto_query`
- Não tem `chat` - MCP tools são chamadas pelo cliente MCP

#### P2: README Inconsistente
**Problema:** README diz "21 MCP tools" mas existem **36 tools**.

#### P3: Regime Lifecycle Desconectado
**Problema:** ACORDAR, VAI_DORMIR sãodocumentados mas:
- Não há indicação clara de quando usar
- O utilizador não é guiado para o fluxo correto
- Não há proteção contra uso sem ACORDAR

**Fluxo correto:**
```
grilo_load() → grilo_acordar() → trabalho → grilo_vai_dormir()
```

### 6.2 PROBLEMAS MÉDIOS

#### P4: Sem Guia de Início para MCP
- Quick Start do README assume Docker
- Não explica como usar MCP tools manualmente
- Não há exemplos concretos de调用

#### P5: Documentação ACORDAR Não Integrada
- ACORDAR.md existe mas não está linked do README
- Utilizador não sabe que existe ritual de arranque
- Passos 1-5 do ACORDAR não estão automatizados

#### P6: SKILL.md Contradiz Regime
- SKILL.md: "O skill NUNCA produz decisão"
- Mas não há mecanismo real de forçar isso
- O que acontece se um LLM decidir sem permissão?

#### P7: PINA Protocol Sem UI
- PINA tem 3 tools (propose, decide, status)
- Mas não há explicação de quando propor
- Não há interface para rever NCAs pendentes

### 6.3 PROBLEMAS MENORES

#### P8: CLI Não Documentada
- grilo_pipeline.py tem muitas opções
- README não menciona CLI
- grilo_pipeline.py está no root (não em grilo_falante/)

#### P9: Kanban Sem Fluxo
- API tem `/kanban` endpoints
- Mas não há documentação de fluxo de trabalho
- Quando usar kanban vs claims?

#### P10: Auditoria e Workflows Separados
- `grilo_audit` vs `grilo_run_auditoria_hostil` - qual usar?
- Diferença não explicada

---

## 7. Matriz de Decisão: Qual Interface Usar?

| Objetivo | Interface Recomendada |
|----------|-------------------|
| Usar com LLM (OpenCode, Claude, etc) | MCP Server |
| Integrar noutra aplicação | REST API |
| Análise rápida de texto | Skill `/grilo` |
| Processar ficheiros em batch | CLI |
| Desenvolver novo frontend | REST API |

---

## 8. Propostas de Correção

### P1: Atualizar SKILL.md
```
MUDAR DE:
- MemPalace (ChromaDB local)

PARA:
- PostgreSQL + pgvector (backend de memória epistémica)
```

### P2: Adicionar Quick Start MCP
```markdown
## Quick Start MCP

1. Conectar ao MCP server
2. Iniciar ciclo:
   grilo_load()
   grilo_acordar(temporal_anchor="2026-04-15", intention="...")
3. Fazer query:
   gepeto_query(query="...")
4. Terminar ciclo:
   grilo_vai_dormir()
```

### P3: Criar指引 de Regime
```markdown
## Regime Lifecycle

O Grilo Falante exige ritual explícito:

1. LOAD - Carregar regime
2. ACORDAR - Declarar tempo e intenção
3. [Trabalho Governado]
4. VAI_DORMIR - Hibernar

Sem este ritual, o sistema está em estado INACTIVE.
```

### P4: Unificar Auditoria
- `grilo_audit` → usar `AuditoriaHostil` internamente
- `grilo_run_auditoria_hostil` → remover ou renomear
- Documentar como "low-level" vs "high-level"

### P5: Adicionar PINA UI
- Criar endpoint `GET /api/v1/pina/pending`
- Listar NCAs pendentes de decisão

---

## 9. Checklist de Usabilidade

| Item | Status | Notas |
|------|--------|-------|
| Utilizador sabe que tem de fazer grilo_load primeiro | ❌ | Não há indicação |
| Utilizador sabe o que é temporal_anchor | ❌ | Requer ler documentação |
| Utilizador sabe quando usar PINA | ❌ | Não há guidance |
| Utilizador consegue fazer query simples | ✅ | gepeto_query existe |
| Utilizador consegue ver estado do sistema | ✅ | grilo_status existe |
| Utilizador sabe quando hibernar | ❌ | Não há notificação |

---

## 10. Conclusão

O Grilo Falante tem **múltiplas interfaces** mas:

1. **Documentação Fragmentada** - SKILL.md, README.md, regime.md, ACORDAR.md não estão linked
2. **SKILL.md Desatualizado** - Menciona tecnologia que não existe (MemPalace)
3. **Regime Lifecycle Não Forçado** - Utilizador pode usar sem ACORDAR
4. **Sem Fluxo Guiado** - Não há orientação de próximos passos
5. **Tool Explosion** - 36 tools sem hierarquia clara

### Prioridade de Correções

1. **ALTA**: Atualizar SKILL.md (corrigir MemPalace → PostgreSQL)
2. **ALTA**: Criar "Getting Started" para MCP
3. **MÉDIA**: Documentar fluxo ACORDAR → VAI_DORMIR
4. **MÉDIA**: Criar PINA dashboard
5. **BAIXA**: Unificar auditoria tools