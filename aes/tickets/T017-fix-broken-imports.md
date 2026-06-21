---
ticket: T017
title: Fix broken imports (ChatShell, CLI)
sprint: sprint-02
priority: critical
status: pending
created: 2026-06-21
tags: phase-a, critical, imports
---

# T017 — Fix Broken Imports

## Context
Dois imports quebrados impedem funcionalidade core:

1. `backend/mcp/server.py:73` faz `from app.skills.chat_shell import ChatShell`
   — `app.skills` não existe neste repositório
2. `cli.py` (o antigo, não o que criámos no Phase 1) usa `typer` com imports
   de `app.db`, `app.models` que apontam para código legado inexistente

## Acceptance Criteria
- [ ] ChatShell import corrigido ou removido com fallback
- [ ] CLI commands quebrados corrigidos ou marcados como deprecated
- [ ] Teste: `python3 -c "from grilo_falante.backend.mcp.server import mcp"` passa
