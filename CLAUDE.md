# Grilo Falante v3.0 — Operational Contract

## Essential Commands

```bash
make dev                  # Install development dependencies (run first)
make check                # Run ALL quality gates — lint + format-check + tests
make validate             # Fast syntax check (bash scripts)
make docs-check           # Verify documentation files + cognitive lint
make check-epistemic      # Epistemic integrity gate (premise graphs)
make premise-check        # Premise graph DOT/JSON validation
make metrics              # Health dashboard
make roadmap              # Show task status
make install-hooks        # Sync hooks from hooks/ to .aes/hooks/
make check-premises       # Validate premise graphs via grilo CLI
make doctor               # System diagnostics
make lint                 # Lint check with ruff (auto-fix)
make format               # Format with ruff
make test                 # Run all tests
make coverage             # Tests with coverage report
make run-api              # Start FastAPI locally
make run-mcp              # Start MCP server locally
make install-git-hooks    # Install hooks/pre-commit-gf.sh into .git/hooks/
```

## Project Structure

```
grilo_falante/              # Main package (new architecture)
  backend/
    api/                    # FastAPI REST endpoints
    db/                     # Database (asyncpg, schema, repositories)
    mcp/                    # MCP server (52+ tools)
    memory/                 # Island memory system
    services/               # Cognitive services (GMIF, lint, pipeline)
  regime/                    # State machine (LOADED → ACORDAR → DORMIR)
  models.py                 # Pydantic models
  cli.py                    # grilo CLI bridge
app/                        # Legacy package
  skills/                   # ChatShell, skill definitions
  ontology/                 # ILHA, PEDRA, estado definitions
  ilhas/                    # Island management
  regime/                   # Sleep/wake cycle
  services/                 # Analysis pipeline, school mode
  data/                     # Memory graphs, semantic search
aes/                        # AES project management
  kanban.md                 # Source of truth for project state
  sprints/                  # Sprint files
  tickets/                  # Ticket + phase output files
  premises/                 # Premise graphs (DOT/JSON)
docs/                       # Documentation
  TASKS/                    # Task templates for two-agent mode
  VISION.md
  REQUIREMENTS.md
  ROADMAP.md
.aes/                       # AES configuration
  config.mk                 # Language/harness config
  hooks/                    # Anti-drift hooks
  plugins/                  # Pre/post check plugins
```

## Epistemic Protocols — MCP Tools

Every cycle must start with ACORDAR and end with VAI_DORMIR.

### ACORDAR (início de ciclo)
```
grilo_acordar intention=<string> [temporal_anchor] [mode=exploratory|committed]
```
- temporal_anchor vem do relógio do sistema (fonte externa), não do modelo
- Se fornecido, o anchor humano é cruzado com o relógio; discrepâncias são sinalizadas
- Devolve: estado, âncora verificada, contexto git (branch, commit, dirty), ilhas ativas, warnings

### VAI_DORMIR (fecho de ciclo)
```
grilo_vai_dormir [session_id] [handoff_dir=aes/handoffs]
```
- Coleta estado do ciclo, escreve handoff em `aes/handoffs/`, processa ilhas, hiberna
- `grilo_resume` lê o handoff mais recente e restaura contexto

### PINA (gate normativo)
```
grilo_pina_propose   # Propor candidato normativo (NCA)
grilo_pina_decide    # A=Incorporar, B=Não incorporar, C=Diferir
grilo_pina_detect    # Scannear texto por ocorrências normativas
grilo_pina_configure # Modo: auto | confirm | disabled
```
- Modo `confirm` (default): toda NCA precisa de decisão A/B/C humana
- Modo `auto`: incorpora normas triviais automaticamente
- Modo `disabled`: PINA não é executado

### Pre-commit Hook
`hooks/pre-commit-gf.sh` corre Cognitive Lint (BLOCK/WARN patterns) em `.md` staged.
Instalar com: `make install-git-hooks` (copia para .git/hooks/pre-commit)

## I/O Contracts

For any change claiming to implement a feature:
1. **Plan first**: Create aes/tickets/TXXX-plan.md before implementation
2. **Build with diffstory**: aes/tickets/TXXX-build.md explaining what changed, why, what was untouched, remaining risks
3. **Verify**: Run quality gates (lint + format + tests + premise-check)
4. **Review**: Code review across correctness, simplicity, maintainability, security, performance
5. **Learn**: Document lessons in aes/tickets/TXXX-learn.md

## Behaviour Guidelines

- Never produce decisions or validate truths — only make the cost of judgment visible
- Never bypass the Shadow First methodology (research before assuming)
- Never commit without phase evidence files and passing quality gates
- Pre-surgical changes: smallest possible diff, no scope creep
- Challenge assumptions openly — hostile analysis is required before implementation

## Non-Goals
- Grilo Falante does not produce decisions or validate truths
- It does not confer authority factual on claims
- It is not a general-purpose knowledge graph tool without epistemic governance
- It does not aim to replace human judgment, only to make the cost of judgment visible

## Critical Files
- `docs/VISION.md` - Core vision and concepts
- `docs/REQUIREMENTS.md` - Functional and non-functional requirements
- `docs/ROADMAP.md` - Implementation plan and priorities
- `docs/HOSTILE_INSIGHTS.md` - Accumulated lessons from hostile analysis
- `grilo_falante/backend/mcp/server.py` - MCP server implementation
- `grilo_falante/models/` - Pydantic models for core concepts (ILHA, PEDRA, ShadowDocument)
- `grilo_falante/backend/services/` - Cognitive services (audit, lint, governance)
- `app/services/pipeline.py` - Main analysis pipeline
- `app/data/memory/graph/gmif.py` - GMIF classification logic

## Never-Do List
- Never commit code without corresponding tests
- Never bypass the Shadow First methodology (research before assuming)
- Never implement features without updating documentation
- Never ignore failing tests or lint errors
- Never make architectural decisions without hostile analysis
- Never combine multiple unrelated changes in a single commit
- Never deploy to production without running all quality gates

## Evidence Required
For any change claiming to implement a feature from the roadmap:
1. Reference the specific requirement ID from REQUIREMENTS.md
2. Show hostile analysis (assumptions, alternatives, risks considered)
3. Provide test evidence (unit/integration tests that validate the change)
4. Document any impact on existing functionality
5. Update relevant documentation (VISION, REQUIREMENTS, ROADMAP as needed)

## AES Project Structure
This project uses AES (Aggressive Engineering System) for project management:
- `aes/kanban.md` - Global project state
- `aes/sprints/` - Sprint planning and retrospectives
- `aes/tickets/` - Individual tickets with plan/build/verify/review/learn phases
- `aes/handoffs/` - Session continuity files
- `aes/verification/` - Archived test output and logs
- `.aes/hooks/` - Anti-drift hooks (pre-build, pre-review, pre-merge)

## AES Evidence Rules
- Every ticket MUST have phase output files before it can be marked "done"
- No sprint ticket can be closed without corresponding files in aes/tickets/
- pre-merge hook verifies all 5 phase files exist before allowing completion

## Quality Gates
Before declaring work complete, verify:
- [ ] Tests pass (unit and integration)
- [ ] Lint passes (ruff check)
- [ ] Format correct (ruff format)
- [ ] No console.log/debug in src
- [ ] No TODO in src
- [ ] Docs updated if behaviour changed
- [ ] Diffstory written (what changed, why, what was untouched, remaining risks)
- [ ] Reviewed for simplicity and correctness

## Environment
- Language: Python 3.9+
- Framework: FastAPI for API, MCP for tool exposure
- Testing: pytest
- Linting: ruff
- Formatting: ruff
- Docker: Available for containerization