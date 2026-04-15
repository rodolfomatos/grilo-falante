# Grilo Falante Regime — v3.0

## Overview

O Grilo Falante é um **regime de governação cognitiva** que não produz decisões, não valida verdades, não confere autoridade factual. A sua única função é **impedir que decisões sejam tomadas sem método explícito e sem custo humano visível**.

## Estado Machine

```
INACTIVE → LOADED → ACTIVE → GOVERNING ↔ HIBERNATED
```

## GMIF Classification

| Level | Name | Confidence |
|-------|------|------------|
| M1 | Primary Evidence | 0.8-1.0 |
| M2 | Contextual | 0.6-0.9 |
| M3 | Partial | 0.4-0.7 |
| M4 | Doubtful | 0.1-0.5 |
| M5 | Interpretation | 0.5-0.8 |
| M6 | Derived | 0.4-0.7 |
| M7 | Synthesis | 0.5-0.8 |
| M8 | Conclusion | 0.3-0.7 |

## Pipeline Phases

| Phase | Name | Function |
|-------|------|----------|
| -1 | Lock Ontológico | Define Digital Object |
| 0 | Framing | Contextualize |
| 1 | Snapshot | Materialize state |
| 2 | Indexing | Organize |
| 3 | Working Set | Select subset |
| 4 | Exploration | Generate hypotheses |
| 5 | Audit | Critical testing |
| 6 | Decision | Selection |
| 7 | Promotion Gate | Revalidate |
| 8 | Cycle Closure | Record |

## PINA Protocol

Detection of normative occurrences does NOT trigger PINA. Only Normative Candidates (NCA) trigger decision gate.

Decision options:
- [A] Incorporate
- [B] Do not incorporate
- [C] Defer
