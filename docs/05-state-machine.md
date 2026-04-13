# State Machine — Documentação Técnica

## Visão Geral

O grilo-falante-skill agora executa como uma **state machine** governed por grafos Graphviz (.dot).

---

## Arquitetura

```
┌─────────────────────────────────────────────────────────────┐
│                    state_machine.py                          │
├─────────────────────────────────────────────────────────────┤
│                                                             │
│  .dot file ──► DotParser ──► States + Transitions          │
│                                         │                   │
│                                         ▼                   │
│                                    StateMachine              │
│                                         │                   │
│                                         ▼                   │
│                               Handlers por fase              │
│                               (F0, F1, F2, ...)            │
│                                                             │
└─────────────────────────────────────────────────────────────┘
```

---

## Componentes

### DotParser

```python
from state_machine import DotParser

parser = DotParser("g7_grilo_falante_cognitive_model_v7.dot")
states, transitions = parser.parse()

print(f"States: {len(states)}")
print(f"Transitions: {len(transitions)}")
```

### StateMachine

```python
from state_machine import StateMachine

sm = StateMachine(states, transitions)
sm.start()  # Auto-detecta estado inicial

# Registrar handler
sm.set_handler("F1", my_handler)

# Executar
result = sm.step(input_data, context)
```

---

## Grafos Disponíveis

| Graph | Estados | Descrição |
|-------|---------|-----------|
| g7 | 17 | Modelo cognitivo v7 |
| g8 | 33 | Modelo unificado (completo) |
| g9 | 27 | Arquitetura unificada |

Localização: `graphs/` ou `/home/rodolfo/src/ambrosio_v2.5.0/graphs/`

---

## Estados do Modelo g8

### Pipeline Cognitivo

```
F_M1 → F0 → F1 → F15 → F2 → EXPLORATION_CONTROL → F3 → F4
                                              ↓
                                    VALIDATION_QUEUE → VALIDATION_TIERS → F6
                                              ↓
                                    EVIDENCE → VERIFY → CONFIDENCE → F7 → F8
```

### Decisões (Lint)

- **F4 (Cognitive LINT)**: ACCEPT → F6, REJECT → F_M1, REEXECUTE → F5
- **F7 (Promotion Gate)**: PROMOTE → F8, BLOCK → F_M1

### Epistemic System

- LEDGER → PARADIGM_MAP → ANOMALY_BUFFER → FOUNDATION_AUDIT → DRIFT_AUDIT → LINEAGE → GATES

---

## Handlers

Cada estado tem um handler que retorna:

```python
{
    "phase": "F1",           # Nome do estado
    "status": "continue",    # continuing ou terminal
    "output": {...}          # Dados opcionais
}
```

Estados terminais:
- `ACCEPT` → passar para F6
- `REJECT` → retornar a F_M1
- `REEXECUTE` → retornar a F2
- `PROMOTE` → passar para F8
- `BLOCK` → retornar a F_M1

---

## Uso no Pipeline

```bash
python3 grilo_pipeline.py ./app --graph g8_grilo_falante_unified_cognitive_model
```

**Flags novos:**
- `--graph NAME` — selecionar grafo
- `--no-store` —skip MemPalace
- `--export-html` —gerar HTML
- `--verify-m4` —verificação humana

---

## Extensibilidade

Para adicionar novo grafo:

1. Colocar .dot em `graphs/`
2. Executar com `--graph nome_do_grafo`
3. Handler registration é automática para estados conhecidos

---

## Transição Types

```python
class TransitionType(Enum):
    NORMAL = "normal"      # Transição normal
    ACCEPT = "accept"     # Passou LINT
    REJECT = "reject"     # Falhou LINT
    REEXECUTE = "reexecute"  # Re-executar
    PROMOTE = "promote"   # Promover
    BLOCK = "block"        # Bloquear
```

---

## Limitações

1. Parsing de .dot é básico (não suporta subgraphs complexos)
2. Handlers são minimal — lógica de negócio precisa de expansão
3. Estados sem handler são ignorados (pass-through)

---

## Funcionalidades Implementadas (v1.0)

### ACORDAR Ritual
- Temporal anchoring (data/hora)
- Declaração de intenção
- Flags: `--intention "texto"`, `--temporal "2026-04-12"`

### LEGITIMACY States
- `LEGITIMACY_SUSPENDED` (default) → `LEGITIMACY_ASSERTED` (após validação humana)
- Tracking automático no output JSON

### F7 Promotion Gate
- BLOCK se: M4 não verificado, sem M1, sem LEGITIMACY_ASSERTED
- PROMOTE se: todos os critérios cumplidos

### BLOCK Estruturado
- ciclos bloqueados agora geram payload persistido em `graphify-out/gmif_output.json`
- categorias atuais:
  - `invalid_load_act`
  - `missing_required_artefact`
  - `unverified_m4_claims`
  - `no_m1_claims`
  - `no_legitimacy_asserted`
- o output inclui:
  - `status: blocked`
  - `block.reason`
  - `block.message`
  - `block.details`
  - `loader_kernel`
  - `system_use_records`

### F8 Persistence
- Output JSON com metadata completa
- Metadata inclui: legitimacy_suspended, legitimacy_asserted, total

### LOADER/KERNEL Minimo
- Ativacao explicita do regime via `LOAD GriloFalante FROM system.md`
- Resolucao de autoridade minima a partir de `KERNEL.md`
- Materializacao de `SystemUseRecord` para uso do loader, kernel e grafo
- Inclusao de `loader_kernel` e `system_use_records` no output JSON

### Cognitive Modes
- MEX (Free Exploration)
- MEX-S (Structured Exploration)
- AUDIT (Hostile Audit)
- MULTI (Multi-Agent)
- MTS (Simulated Terminal)

---

## Uso

```bash
# Completo com state machine g8
python3 grilo_pipeline.py ./app \
  --graph g8_grilo_falante_unified_cognitive_model \
  --intention "Verificar claims" \
  --verify-m4 \
  --export-html

# Modelo mais simples (g7)
python3 grilo_pipeline.py ./app --graph g7_grilo_falante_cognitive_model_v7

# Sem state machine (original)
python3 grilo_pipeline.py ./app
```

---

## Exemplo de Output

```json
{
  "nodes": [
    {"gf_id": "GF-260412-M1-abc123", "gmif_type": "M1", "legitimacy": "LEGITIMACY_ASSERTED"},
    {"gf_id": "GF-260412-M3-def456", "gmif_type": "M3", "legitimacy": "LEGITIMACY_SUSPENDED"}
  ],
  "metadata": {
    "legitimacy_asserted": 86,
    "legitimacy_suspended": 110,
    "total": 196
  }
}
```

### Exemplo de Output Bloqueado

```json
{
  "status": "blocked",
  "block": {
    "reason": "no_legitimacy_asserted",
    "message": "Promotion blocked because no claim has explicit asserted legitimacy."
  },
  "loader_kernel": {...},
  "system_use_records": [...]
}
```
