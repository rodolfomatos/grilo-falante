# AES + Grilo Falante — Guia de Integração Prática

## Visão Geral

GF e AES operam em níveis diferentes e complementares:

| Dimensão | GF | AES |
|----------|----|-----|
| O que governa | Estado epistémico do agente | Processo de engenharia |
| Como | Protocolos formais (ACORDAR, PINA, Lint) | Fases (plan→build→verify→review→learn) |
| Artefacto | Claims, gaps, grafos de premissas | Kanban, tickets, hooks |
| Quando usar | Síntese de pesquisa, análise conceptual, decisão multi-sessão | Desenvolvimento de software |

A integração é **leve**: AES chama GF via CLI (`grilo check-epistemic`) sempre que disponível, com fallback gracioso para validadores Bash/Python autónomos.

---

## Pré-requisitos

```bash
# Skills instalados (faz parte do make install-all)
ls ~/.config/opencode/skills/grilo_falante/SKILL.md
ls ~/.config/opencode/skills/gf-premise-propagator/SKILL.md

# CLI grilo acessível
grilo --help  # ou python3 -m grilo_falante.cli --help

# Hooks instalados no projecto
ls .aes/hooks/pre-build-gf.sh
ls .aes/plugins/10-premise-integrity.sh
```

Se faltar algum:
```bash
make install-all        # instala todos os skills
make install-extra      # instala gf-premise-propagator
make aes-init           # cria estrutura aes/ se não existir
```

---

## Fluxo Diário

### 1. `make check` — o centro de tudo

```bash
make check
```

Corre, por ordem:
1. **docs-check** — valida documentos
2. **code-check** — linta código
3. **test-check** — corre testes
4. **lint-check** — formatação
5. **premise-check** — corre `pre-build-gf.sh` (verificador de premissas)
6. **check-epistemic** — chama `grilo check-epistemic --dir aes/premises/`
7. **Plugins** (`.aes/plugins/*.sh`) — validação epistémica por grafo

Se o `grilo` CLI não estiver disponível, o passo 6 salta com aviso e o passo 7 cai para fallback (validação DOT + JSON + staleness check).

### 2. `make premise-check` — verificador de premissas

```bash
make premise-check
```

Lê os grafos de premissas em `aes/premises/*.dot`, verifica cada premissa contra a realidade (ficheiros, comandos CLI, variáveis de ambiente) e faz cascata BFS de falhas através das arestas DEPENDS_ON/SUPPORTS.

Bloqueia o build (exit 1) se premissas críticas (FOUNDATIONAL, ASSUMPTION) forem falsificadas.

Nível de porta configurável em `.aes/config.mk`:
```makefile
AES_PREMISE_GATE=critical    # critical | all | strict | custom
```

### 3. Hooks de Fase

| Hook | Disparo | O que verifica |
|------|---------|---------------|
| `pre-build-gf.sh` | Antes de build | Premissas contra realidade (cascata BFS) |
| `pre-build.sh` | Antes de build | Plano feito + ficheiros críticos não alterados |
| `pre-verify.sh` | Antes de verify | Build completo |
| `pre-review.sh` | Antes de review | Verify `verdict: pass` + diffstory presente |
| `pre-merge.sh` | Antes de merge | Tamanho do diff + ficheiros proibidos |

O `pre-review.sh` **não chama ainda** o `can_promote()` do GF (loop closure). Está documentado no skill `gf-premise-propagator` como integração futura.

### 4. Plugin de Premise Integrity

`make check` corre automaticamente `.aes/plugins/10-premise-integrity.sh`. Este plugin:

1. Tenta `grilo check-epistemic --graph <file>.dot` para cada grafo
2. Se GF não disponível: verifica se `lib/gf-premise-propagator/propagator.py` está sincronizado (<30 dias)
3. Valida sintaxe DOT com `dot -Tsvg`
4. Valida estrutura JSON com Python

---

## MCP Tools do GF em Sessões AES

Os 58 MCP tools do GF estão disponíveis em sessões AES se registados na configuração do harness:

### OpenCode

Em `~/.config/opencode/settings.json`:
```json
{
  "mcpServers": {
    "grilo-falante": {
      "command": "python3",
      "args": ["-m", "grilo_falante.backend.mcp.server"]
    }
  }
}
```

### Claude Code

Em `CLAUDE.md`:
```markdown
## MCP Servers
- grilo-falante: python3 -m grilo_falante.backend.mcp.server
```

Ou via `.mcp.json` do projecto.

### Carregar o skill

```markdown
/skill grilo_falante
```

Os 4 tools portados do GePeTo (grilo_graph_lint, grilo_learning_path, grilo_trusted_sources, grilo_source_propose) funcionam sem PostgreSQL — só precisam do MCP server.

---

## Artefactos Partilhados

| Directoria | Quem escreve | Quem lê | Conteúdo |
|-----------|-------------|---------|----------|
| `aes/premises/` | `generate-premises.sh` | `pre-build-gf.sh`, `check-epistemic` | Grafos DOT/JSON de premissas |
| `aes/handoffs/` | VAI_DORMIR | Próxima sessão AES | Contexto de ciclo |
| `aes/knowledge/` | GF | AES (futuro) | Claims, gaps, loops |
| `aes/verification/` | Testes | pre-review.sh | Output de verificação arquivado |

---

## Bateria de Testes

O repositório GF inclui uma bateria multi-camada em `grilo_falante/tests/`:

```
tests/
├── conftest.py                    # Fixtures partilhadas (sample_claims, sample_gaps, sample_study_plan)
├── test_services.py               # L1-L8 completos + source_registry + learning_path
├── test_mcp.py                    # Registo MCP, schemas, dispatch (8 testes)
├── test_models.py                 # Modelos (pré-existente)
└── e2e/
    ├── test_scenario_climatologia.py      # 5 critérios: L1, L2, L5, L6, L7
    ├── test_scenario_curadoria.py         # 4 passos: propose, vote, approve, reject
    └── test_scenario_learning_path.py     # 4 critérios: generate, order, study_plan, markdown
```

```bash
python3 -m pytest grilo_falante/tests/ -v
# 40 passed, 0 failed
```

Os testes MCP usam o SDK interno (`app.request_handlers[ListToolsRequest/CallToolRequest]`) e não precisam de PostgreSQL. Tools que dependem de DB (grilo_status) devolvem estado in-memory sem DB.

---

## Diagrama de Integração

```
┌─────────────────────────────────────────────────┐
│                 AES (make check)                 │
│                                                  │
│  ┌──────────┐  ┌──────────┐  ┌───────────────┐  │
│  │ premise- │  │ check-   │  │ .aes/plugins/ │  │
│  │ check    │  │ epistemic│  │ *.sh          │  │
│  └────┬─────┘  └────┬─────┘  └───────┬───────┘  │
│       │             │                │          │
│       ▼             ▼                ▼          │
│  pre-build-gf.sh    grilo CLI    grilo CLI      │
│  (Bash+Python)      check-        --graph       │
│                     epistemic                   │
│                                                  │
└──────────────────────┬──────────────────────────┘
                       │
                       ▼
┌─────────────────────────────────────────────────┐
│          Grilo Falante v3.0                      │
│                                                  │
│  ┌──────────┐  ┌────────────┐  ┌────────────┐  │
│  │ MCP      │  │ CLI        │  │ Bateria de │  │
│  │ Server   │  │ check-     │  │ Testes     │  │
│  │ (58 tools)│  │ epistemic  │  │ (40 testes)│  │
│  └──────────┘  └────────────┘  └────────────┘  │
│                                                  │
└─────────────────────────────────────────────────┘
```

---

## Resolução de Problemas

| Problema | Causa | Solução |
|----------|-------|---------|
| `make check` diz "epistemic gate skipped" | `grilo` CLI não está no PATH | `make install-all` ou alias manual |
| `grilo_lint` falha com erro DB | Servidor MCP corre `init_pool()` antes de cada tool | Usar versão >= 21955e7 (init_pool wrapped em try/except) |
| `pre-build-gf.sh` bloqueia sem razão | Premissa crítica falsificada | Corrigir premissa ou mudar `AES_PREMISE_GATE` |
| Testes MCP falham com coroutine | Testes chamam handler sem await | Usar `@pytest.mark.asyncio` + `await` |
| MCP tools não aparecem no agente | Servidor não registado no harness | Adicionar ao `settings.json` ou `CLAUDE.md` |

---

## Referências

- Paper: `docs/paper/paper.md` (Secção 6: Relationship with AES)
- Instalação: `docs/INSTALL.md`
- Skill GF: `~/.config/opencode/skills/grilo_falante/SKILL.md`
- Skill bridge: `~/.config/opencode/skills/gf-premise-propagator/SKILL.md`
- Makefile AES: `Makefile` (targets premise-check, check-epistemic)
- Hooks: `hooks/pre-build-gf.sh`, `hooks/pre-review.sh`
- Plugins: `.aes/plugins/10-premise-integrity.sh`
- Testes: `grilo_falante/tests/`
