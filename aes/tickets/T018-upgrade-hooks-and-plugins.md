---
ticket: T018
title: Upgrade hooks system + add plugins
sprint: sprint-02
priority: high
status: pending
created: 2026-06-21
tags: phase-b, hooks, plugins
---

# T018 — Upgrade Hooks System + Add Plugins

## Context
Os hooks actuais do GF são versões antigas (AES v4.0). Precisam de ser
actualizados para o AES v4.3 e falta o directório `hooks/` source.

## Acceptance Criteria
- [ ] Criar `hooks/` source directory com hooks actuais: pre-build, pre-verify, pre-review, pre-merge, pre-build-gf
- [ ] Actualizar `.aes/hooks/` com versões que verificam `status: done` nos phase files
- [ ] `pre-verify.sh` adicionado (build→verify guard)
- [ ] `pre-build-gf.sh` adicionado (premise propagation gate)
- [ ] Criar `.aes/plugins/10-premise-integrity.sh` adaptado do AES
- [ ] `make install-hooks` funcional
