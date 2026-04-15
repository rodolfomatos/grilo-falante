# 21. State Machine

## Ciclo de Estados

```
INACTIVE ──load()──> LOADED ──acordar()──> GOVERNING
                                           ▲       │
                                           │       │
                                           │   dormir()
                                           │       │
                                           └───────┘
```

---

## CycleState

```python
class CycleState(Enum):
    INACTIVE = "inactive"
    LOADED = "loaded"
    ACTIVE = "active"
    GOVERNING = "governing"
    HIBERNATED = "hibernated"
```

---

## Transições

| De | Para | Método |
|----|------|--------|
| INACTIVE | LOADED | load() |
| LOADED | GOVERNING | acordar() |
| GOVERNING | HIBERNATED | vai_dormir() |
| HIBERNATED | GOVERNING | resume() |
| * | INACTIVE | unload() |

---

## CycleContext

```python
@dataclass
class CycleContext:
    cycle_id: str           # "CYCLE-260415-abc123"
    state: CycleState
    started_at: datetime
    claims_count: int
    nca_pending: int
    is_exploratory: bool
    legitimacy_declared: bool
    temporal_anchor: str
    intention: str
```

---

## Loader

```python
from grilo_falante.regime import Loader, Ledger

ledger = Ledger()
loader = Loader(ledger=ledger)

result = loader.load()
# result.success, result.cycle_id, result.message
```

---

## Acordar

```python
from grilo_falante.regime import Acordar

acordar = Acordar(
    state_machine=loader.state_machine,
    ledger=ledger
)

result = acordar.execute(
    temporal_anchor="2026-04-15",
    intention="Analisar relatório",
    mode="exploratory"
)
```

---

## Ledger

Registo imutável de eventos:

```python
ledger.add_entry(
    entry_type=LedgerEntryType.CLAIM_CREATED,
    content="Texto da claim",
    gf_id="GF-260415-M5-abc123",
    metadata={"gmif_level": "M5"},
    cycle_id=cycle_id
)
```

---

## Diagrama Completo

```
┌─────────────────────────────────────────────────────────────┐
│                                                             │
│  ┌──────────┐                                              │
│  │ INACTIVE │ ◄─── unload() ──────────────────────────┐   │
│  └────┬─────┘                                            │   │
│       │ load()                                           │   │
│       ▼                                                  │   │
│  ┌──────────┐     dormir()      ┌─────────────┐        │   │
│  │  LOADED  │ ───────────────► │  GOVERNING  │        │   │
│  └────┬─────┘                  └──────┬──────┘        │   │
│       │                                ▲       │        │   │
│       │ acordar()                      │ resume()│        │   │
│       ▼                                │       │        │   │
│  ┌──────────┐                        └───────┴────────┘   │
│  │  ACTIVE  │                                              │
│  └────┬─────┘                                              │
│       │                                                    │
│       └────────────────────────────────────►HIbernated     │
│              dormir()                                     │
│                                                             │
└─────────────────────────────────────────────────────────────┘
```

---

*Voltar ao [Índice](../00_INDICE.md)*
