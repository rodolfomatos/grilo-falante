---
title: "Full Stack Installation — AES + Grilo Falante + llm-iaedu"
target: "Ubuntu 22.04 LTS (jammy)"
harness: "OpenCode"
created: 2026-06-21
verified_by: "grilo_falante.regime.Acordar + PINA"
---

# Full Stack Installation Guide

## Como se fosse uma criança

Imagina que tens um robô que te ajuda a programar. Mas esse robô precisa de
três coisas:

1. **AES** — a sala de controlo que diz ao robô *como* trabalhar: primeiro
   planear, depois construir, verificar, rever, aprender. Sempre pela mesma
   ordem, para não se esquecer de nada.

2. **Grilo Falante (GF)** — o detector de mentiras do robô. Sempre que ele diz
   "isto é obviamente verdade", o GF obriga-o a provar. Se não provar, não
   passa.

3. **llm-iaedu** — o telefone do robô. É como ele liga a uma central (iaedu.pt)
   para pedir ajuda a modelos de IA mais potentes.

Este documento explica como montar as três peças num computador Ubuntu novo em
folha. Cada passo pode ser verificado — ou detectado como falso — pelo GF.

## Como se fosse um especialista

This document covers a **bare-metal installation** of three interdependent
systems on Ubuntu 22.04 LTS:

| System | Function | Language | Port |
|--------|----------|----------|------|
| AES (Aggressive Engineering System) | Engineering methodology with kanban, phases, quality gates | Bash, Python | CLI |
| Grilo Falante v3.0 | Epistemic governance regime — ACORDAR/VAI_DORMIR/PINA, MCP tools, cognitive lint | Python 3.10+ | 8001 (API), stdio (MCP) |
| llm-iaedu | LLM plugin for Simon Willison's `llm` CLI — connects to iaedu.pt API | Python 3.8+ | CLI |

**Prerequisite chain:**
```
apt → python3 → pip → pipx / venv → git clone → pip install → make check
```

---

## 1. System Prerequisites

### 1.1. Base packages

```bash
sudo apt update && sudo apt upgrade -y

sudo apt install -y \
    git \
    make \
    curl \
    wget \
    python3 \
    python3-pip \
    python3-venv \
    python3-dev \
    shellcheck \
    graphviz \
    ca-certificates
```

**Verification (run each):**

```bash
git --version          # ≥ 2.34
make --version         # ≥ 4.3
python3 --version      # ≥ 3.10
pip3 --version         # ≥ 22.0
shellcheck --version   # ≥ 0.8.0
dot -V                 # graphviz ≥ 2.42
```

### 1.2. Python user-base (pip install --user)

Ensure `~/.local/bin` is in PATH:

```bash
# Add to ~/.bashrc or ~/.zshrc:
export PATH="$HOME/.local/bin:$PATH"

# Activate now:
source ~/.bashrc
```

### 1.3. linters and formatters (extra, needed by AES `make check`)

```bash
pip3 install --user ruff shfmt-py
```

Verification:

```bash
ruff --version        # ≥ 0.1.0
```

Note: `shfmt` (shell formatter) is installed separately if needed. AES does not
block on its absence — `make check` falls back gracefully. To install the native
binary:

```bash
sudo snap install shfmt
```

### 1.4. PyYAML (required by AES scripts)

```bash
pip3 install --user pyyaml
python3 -c "import yaml; print('PyYAML:', yaml.__version__)"
```

---

## 2. AES Installation

### 2.1. Clone

```bash
cd /opt
sudo mkdir -p aes && sudo chown "$USER:$USER" aes
git clone https://github.com/rodolfomatos/aes.git aes
cd aes
```

### 2.2. Setup

```bash
make setup
```

This runs:
1. `scripts/detect-language.sh` — detects Bash
2. `scripts/detect-harness.sh` — detects OpenCode or Claude Code
3. `scripts/detect-domain.sh` — detects domain metadata
4. `scripts/install-deps.sh` — verifies PyYAML and Graphviz

### 2.3. Verify

```bash
make check
```

**Expected output (last line):**
```
✅ CHECK PASSED in Ns
ALL QUALITY GATES PASSED
```

### 2.4. Install skills (for agent harness)

For **OpenCode**:

```bash
make install-opencode
```

This copies:

| Skill | Destination |
|-------|-------------|
| `aes` (orchestrator) | `~/.config/opencode/skills/aes/` |
| `aes-plan` | `~/.config/opencode/skills/aes-plan/` |
| `aes-build` | `~/.config/opencode/skills/aes-build/` |
| `aes-verify` | `~/.config/opencode/skills/aes-verify/` |
| `aes-review` | `~/.config/opencode/skills/aes-review/` |
| `aes-learn` | `~/.config/opencode/skills/aes-learn/` |

For **Claude Code**:

```bash
make install-claude
```

For **both**:

```bash
make install-all
```

### 2.5. Install CLI (optional, requires sudo)

```bash
sudo make install-cli
# → /usr/local/bin/aes
```

### 2.6. Install session hooks

```bash
make install-session-hooks
```

This installs the Debate Partner Protocol loader, which loads
`prompts/debate-partner.md` at the start of every agent session.

### 2.7. Verify skills installed

```bash
ls ~/.config/opencode/skills/aes/SKILL.md
ls ~/.config/opencode/skills/aes-plan/SKILL.md
ls ~/.config/opencode/skills/aes-build/SKILL.md
```

---

## 3. Grilo Falante Installation

### 3.1. Clone

```bash
cd /opt
git clone git@github.com:rodolfomatos/grilo-falante.git grilo_falante_v3.0
# or via HTTPS:
git clone https://github.com/rodolfomatos/grilo-falante.git grilo_falante_v3.0
cd grilo_falante_v3.0
```

### 3.2. Python environment

```bash
python3 -m venv .venv
source .venv/bin/activate
```

### 3.3. Install dependencies

```bash
# Core
pip install -e .

# Development (linting, testing)
pip install -e ".[dev]"

# MCP support (for agent integration)
pip install -e ".[mcp]"

# Or everything:
pip install -e ".[all]"
```

This installs:
- `fastapi`, `uvicorn` — API server
- `pydantic`, `pydantic-settings` — configuration
- `httpx` — HTTP client
- `structlog`, `jinja2` — logging, templates
- `ruff`, `pytest`, `pytest-asyncio`, `pytest-cov` — dev tooling
- `mcp[cli]` — MCP protocol server

### 3.4. Install git hooks

```bash
make install-hooks
# or manually:
cp hooks/pre-commit-gf.sh .git/hooks/pre-commit
chmod +x .git/hooks/pre-commit
```

This installs the **cognitive lint** pre-commit hook that BLOCKs epistemic
patterns ("obviously", "clearly", "Trust me") in governance files
(`aes/adr/*.md`, `docs/TASKS/*.md`, etc.) and WARNs on hedging language
("maybe", "I think", "it seems") in any `.md` file.

### 3.5. Verify

```bash
# Within the virtual environment:
make check

# Test GF protocol imports:
python3 -c "
from grilo_falante.regime import Acordar, PINAProtocol, StateMachine
print('Regime imports: OK')
"

# Test MCP tool imports:
python3 -c "
from grilo_falante.backend.mcp.server import mcp
print('MCP server: OK')
"
```

### 3.6. Optional: Configure MCP for agent harness

The GF MCP server provides tools via stdio transport (used by OpenCode/Claude
Code) or HTTP (port 8001).

For **OpenCode**, add to `~/.config/opencode/config.json`:

```json
{
  "mcpServers": {
    "grilo-falante": {
      "command": "/opt/grilo_falante_v3.0/.venv/bin/python",
      "args": ["-m", "grilo_falante.backend.mcp.server"],
      "env": {
        "GRILO_JWT_SECRET": "your-secret-here"
      }
    }
  }
}
```

For **Claude Code**, add to `.claude/mcp.json` in the project root:

```json
{
  "mcpServers": {
    "grilo-falante": {
      "command": "/opt/grilo_falante_v3.0/.venv/bin/python",
      "args": ["-m", "grilo_falante.backend.mcp.server"]
    }
  }
}
```

Verify MCP tools are registered:

```bash
# List available tools (requires MCP Inspector or agent session):
/opt/grilo_falante_v3.0/.venv/bin/python -c "
from grilo_falante.backend.mcp.server import mcp
print('Tools available:', [t.name for t in mcp._tools])
"
```

### 3.7. Optional: Docker deployment

```bash
# All services:
docker compose up -d

# API only:
make docker-api

# Verify health:
curl http://localhost:8001/health
```

---

## 4. llm-iaedu Installation

### 4.1. Install base `llm` CLI

```bash
pipx install llm
```

`pipx` ensures the `llm` command runs in an isolated environment but is
accessible globally. If `pipx` is not installed:

```bash
sudo apt install pipx
pipx ensurepath
source ~/.bashrc
```

### 4.2. Verify base `llm`

```bash
llm --version
# Expected: llm, version 0.31 or later
```

### 4.3. Clone and install plugin

```bash
cd /opt
git clone https://github.com/rodolfomatos/llm-iaedu.git llm-iaedu
cd llm-iaedu

# Install as editable (allows future git pull + no reinstall):
pipx install --editable .
```

Alternatively, if `pipx` conflicts:

```bash
pip install --user -e .
# Then verify:
llm plugins
# Should show: llm-iaedu v0.2
```

### 4.4. Configure API keys

```bash
# Method 1 — interactive:
llm keys set iaedu
# Paste your IAEDU_API_KEY when prompted.

# Method 2 — .env file:
cat > ~/.config/iaedu/env << 'EOF'
IAEDU_API_KEY=sk-xxxxxxxxxxxx
IAEDU_CHANNEL_ID=your-channel-id
IAEDU_AGENT_ID=your-agent-id
# Alternatively, use a custom endpoint:
# IAEDU_ENDPOINT=https://your-proxy.example.com/stream
EOF
chmod 600 ~/.config/iaedu/env
```

### 4.5. Verify

```bash
# List available models — must include "iaedu":
llm models | grep iaedu

# Quick test (requires API key):
echo "Hello, what is 2+2?" | llm -m iaedu
```

---

## 5. AES Project Initialisation for GF

The GF repository uses AES for its own engineering management. If cloning
fresh, initialise the project:

```bash
cd /opt/grilo_falante_v3.0

# Initialise AES kanban structure (if not present):
make aes-init

# Verify:
ls aes/kanban.md aes/sprints/ aes/tickets/
```

This creates:
- `aes/kanban.md` — project state source of truth
- `aes/sprints/` — sprint files
- `aes/tickets/` — ticket definitions
- `aes/handoffs/` — session continuity
- `aes/verification/` — archived test output
- `aes/learning/` — learning records
- `aes/templates/` — plan.yml template
- `aes/adr/` — architecture decision records (GF extension)
- `aes/ticket-map.json` — ticket mapping

The GF project extends AES with `aes/adr/` (see `.aes/config.mk`:
`AES_EXTRA_DIRS=adr`).

---

## 6. OpenCode Configuration

### 6.1. Base config

Create `~/.config/opencode/config.json`:

```json
{
  "mcpServers": {
    "filesystem": {
      "command": "npx",
      "args": ["-y", "@modelcontextprotocol/server-filesystem", "/opt/aes,/opt/grilo_falante_v3.0"]
    },
    "grilo-falante": {
      "command": "/opt/grilo_falante_v3.0/.venv/bin/python",
      "args": ["-m", "grilo_falante.backend.mcp.server"]
    }
  }
}
```

### 6.2. Environment variables

Add to `~/.bashrc` or equivalent:

```bash
export AES_PATH=/opt/aes
export AES_ECC_PATH=/opt/ECC
export AES_MODEL=claude-sonnet-4-6
export PATH="$HOME/.local/bin:$PATH"
```

### 6.3. Verify OpenCode detects skills

```bash
ls ~/.config/opencode/skills/aes/SKILL.md 2>/dev/null && \
  echo "AES skills: OK" || \
  echo "AES skills: missing (run make install-opencode in /opt/aes)"
```

---

## 7. Verification Matrix

| Component | Command | Expected |
|-----------|---------|----------|
| System | `python3 --version` | 3.10+ |
| System | `shellcheck --version` | `version: 0.8.0` |
| System | `ruff --version` | `ruff 0.1.0+` |
| System | `git --version` | `git 2.34+` |
| AES repo | `make check` | `ALL QUALITY GATES PASSED` |
| AES skills | `ls ~/.config/opencode/skills/aes-plan/SKILL.md` | file exists |
| GF repo | `.venv/bin/python -c "from grilo_falante.regime import Acordar"` | no error |
| GF regime | `.venv/bin/python -c "from grilo_falante.regime.acordar import _get_system_time"` | no error |
| GF MCP | `.venv/bin/python -c "from grilo_falante.backend.mcp.server import mcp"` | no error |
| GF lint | `ruff check grilo_falante/regime/acordar.py` | 0 errors |
| GF pre-commit | `bash hooks/pre-commit-gf.sh` (with no .md staged) | `No staged .md files` |
| llm | `llm --version` | `llm, version 0.31` |
| llm-iaedu | `llm plugins` | `llm-iaedu v0.2` |
| llm-iaedu model | `llm models \| grep iaedu` | `iaedu` listed |
| OpenCode | `opencode --version` | ≥ current |
| OpenCode config | `ls ~/.config/opencode/config.json` | file exists |

---

## 8. PINA Configuration (Normative Gates)

Grilo Falante uses PINA (Pergunta, Identificação, Norma, Aplicação) to gate
normative decisions. Three modes:

| Mode | Behaviour | Use case |
|------|-----------|----------|
| `auto` | Agent auto-incorporates norms | Trusted agent, routine work |
| `confirm` | Agent proposes, human decides A/B/C | **Default.** Normal operation |
| `disabled` | No PINA gating | Debugging, prototyping |

Configure per session via the MCP tool `grilo_pina_configure`:

```python
grilo_pina_configure(mode="confirm")
```

Or set the default in code:

```python
from grilo_falante.regime import PINAProtocol
pina = PINAProtocol(...)
pina.mode = "confirm"  # auto | confirm | disabled
```

---

## 9. Epistemic Self-Check (GF verification)

This document itself must pass GF's cognitive standards. Run:

```bash
cd /opt/grilo_falante_v3.0

# 1. Cognitive lint — no unwarranted confidence:
bash hooks/pre-commit-gf.sh -- staged
# (Stage this file first: git add docs/INSTALL.md)

# 2. Logical consistency — ACORDAR verification:
python3 -c "
from grilo_falante.regime import Acordar
a = Acordar(...)
print('ACORDAR protocol: loadable')
"

# 3. PINA check — are any claims in this doc normative?
python3 -c "
from grilo_falante.regime.pina import scan_for_normative_occurrences
with open('docs/INSTALL.md') as f:
    norms = scan_for_normative_occurrences(f.read())
print(f'Normative occurrences detected: {len(norms)}')
for n in norms:
    print(f'  [{n.severity}] {n.text}')
"
```

---

## 10. Troubleshooting

| Symptom | Likely cause | Fix |
|---------|-------------|-----|
| `make check` fails on lint | ruff not installed | `pip3 install --user ruff` |
| `llm` command not found | `~/.local/bin` not in PATH | Add to `~/.bashrc`, source |
| `llm-iaedu` not in plugins | `pipx install` used wrong python | `pipx reinstall --editable /opt/llm-iaedu` |
| GF MCP connection refused | venv not activated or wrong path | Check `command` in opencode config |
| GF `from grilo_falante...` fails | Not in venv or `-e .` not run | `source .venv/bin/activate && pip install -e .` |
| AES `make check` fails on shfmt | Not critical — check shellcheck passes | `snap install shfmt` if desired |
| Pre-commit hook blocks false positive | File is not governance context | Add `--no-verify` or refine `DECISION_PATHS` in hook |

---

## References

- AES: <https://github.com/rodolfomatos/aes>
- Grilo Falante: <https://github.com/rodolfomatos/grilo-falante>
- llm-iaedu: <https://github.com/rodolfomatos/llm-iaedu>
- Simon Willison's `llm`: <https://github.com/simonw/llm>
