---
ticket: T020
title: Create docs/TASKS/ with task templates
sprint: sprint-02
priority: medium
status: pending
created: 2026-06-21
tags: phase-b, templates
---

# T020 — Create docs/TASKS/ with Task Templates

## Context
O GF não tem `docs/TASKS/`, o que impede o uso do workflow two-agent
(`make task TASK=docs/TASKS/<name>.md`). Precisamos das templates AES
para feature, bugfix, refactor, performance, bootstrap.

## Acceptance Criteria
- [ ] `docs/TASKS/` directory criado
- [ ] Templates copiadas do AES: 00-feature-template.md, 00-bugfix-template.md, etc.
- [ ] `make task` funcional (testar com uma task simples)
