---
ticket: T019
title: Add AES-standard Makefile targets
sprint: sprint-02
priority: high
status: pending
created: 2026-06-21
tags: phase-b, makefile
---

# T019 — Add AES-Standard Makefile Targets

## Context
O Makefile do GF está desactualizado em relação ao AES v4.3. Faltam targets
essenciais para quality gates e operação.

## Missing Targets
- `validate` — Fast pre-commit check
- `docs-check` — Validate required docs
- `check-epistemic` — Epistemic quality gate via grilo CLI
- `premise-check` — Premise graph integrity
- `metrics` — Health dashboard
- `roadmap` — Show task status
- `install-hooks` — Sync hooks/ → .aes/hooks/

## Acceptance Criteria
- [ ] Todos os targets acima adicionados ao Makefile
- [ ] `make check` alargado para incluir `docs-check`, `premise-check`, `check-epistemic`
- [ ] `make check` passa no estado actual do GF
