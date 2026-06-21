---
ticket: T022
title: Create premise graphs + .aes/config.mk
sprint: sprint-02
priority: medium
status: pending
created: 2026-06-21
tags: phase-b, premises, config
---

# T022 — Create Premise Graphs + .aes/config.mk

## Context
O GF só tem um premise graph (T001-gf-premises.dot). Falta:
- `aes/premises/project-graph.dot` — project-level premise graph
- `aes/premises/project-graph.json` — JSON version
- `.aes/config.mk` — language/harness config
- `.aes/harness.env` — harness detection

## Acceptance Criteria
- [ ] project-graph.dot criado com premissas do GF
- [ ] project-graph.json criado
- [ ] .aes/config.mk com AES_LANGUAGE=python
- [ ] .aes/harness.env gerado
