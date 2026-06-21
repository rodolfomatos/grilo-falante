---
project: Grilo Falante v3.0
created: 2026-06-08
current_sprint: sprint-03
current_ticket: T016
last_updated: 2026-06-21
---

# Grilo Falante v3.0 Project Kanban

## Project Overview
Grilo Falante v3.0 is an epistemic governance regime implementation.
Template original: protocolos formais agnósticos a agente.
v3.0: implementação Python/AI dos protocolos ACORDAR, VAI_DORMIR, PINA,
Cognitive Lint, com MCP, API REST, PostgreSQL + pgvector.

## Current State
- **Current Sprint:** sprint-04
- **Current Ticket:** T023 — ACORDAR light + VAI_DORMIR real + PINA mínimo

## Swimlanes
- **Backlog** → Items awaiting prioritization
- **In Progress** → Items actively being worked on
- **Review** → Items completed but awaiting review
- **Done** → Items completed and reviewed

## Backlog
| ID | Title | Priority | Tags |
|----|-------|----------|------|
| T010 | Fix Pydantic V2 deprecation warnings | medium | tech-debt |
| T011 | Fix lint debt across codebase | medium | tech-debt, cleanup |
| T012 | Fix docs/references/ duplication | low | docs |
| T013 | Add code coverage tracking | low | infra |
| T014 | Implement graph-based governance (RF-10) | high | regime, critical |

## Sprint-04 — Protocol Implementation (post-hostile-audit)

| ID | Title | Priority | Status |
|----|-------|----------|--------|
| T023 | ACORDAR light: external time + git + island restore | critical | in-progress |
| T024 | VAI_DORMIR real: handoff + cycle summary | critical | in-progress |
| T025 | PINA mínimo: detect + configure + gate | critical | in-progress |
| T026 | I1-I6 as ADR document | medium | in-progress |
| T027 | Cognitive Lint pre-commit hook | medium | in-progress |

## Sprint-03 — AES Re-alignment + Critical Fixes
| ID | Title | Priority | Status |
|----|-------|----------|--------|
| T016 | Fix database schema gaps (claim_embeddings, ILHAS, init_db) | critical | done |
| T017 | Fix broken imports (ChatShell, CLI) | critical | done |
| T018 | Upgrade hooks system + add plugins | high | done |
| T019 | Add AES-standard Makefile targets | high | done |
| T020 | Create docs/TASKS/ task templates | medium | done |
| T021 | Update CLAUDE.md + SKILL.md + kanban.md | medium | done |
| T022 | Create premise graphs + .aes/config.mk | medium | done |

## Sprints
| Sprint | Tickets | Status |
|--------|---------|--------|
| sprint-01 | T001-T007 | done |
| sprint-02 | T008-T015 | parked (moved to sprint-04) |
| sprint-03 | T016-T022 | done |
| sprint-04 | T023-T027 | active |

## Learning History

### sprint-01 (AES Alignment)
- AES re-alignment revealed that sprint-01 produced no phase evidence files.
- Lesson: evidence files are not optional.

### sprint-02 (Core Features) — Parked
- Tickets T008-T015 deferred after hostile audit identified over-engineering.
- Decided to implement lightweight versions: ACORDAR light, VAI_DORMIR real, PINA mínimo.

### sprint-03 (AES Re-alignment + Critical Fixes)
- T016: Added claim_embeddings table, init_schema_ilhas() call, fixed startup event
- T017: Added ChatShell import fallback with stub in MCP server
- T018: Added pre-verify hook, pre-build-gf.sh propagator, premise-integrity plugin
- T019: Added validate/docs-check/check-epistemic/premise-check/metrics/roadmap/install-hooks targets
- T020: Created docs/TASKS/ with feature/bugfix/refactor templates
- T022: Premise graphs + .aes/config.mk

### sprint-04 (Protocol Implementation)
- Hostile audit identified over-engineering in original spec.
- Decided: implement what adds value, skip what is theatre.
- ACORDAR: external time source instead of human-supplied anchor
- VAI_DORMIR: handoff files in aes/handoffs/ for session continuity
- PINA: configurable mode (auto/confirm/disabled) + normative occurrence detection
- I1-I6: documented as ADR-001 with verification pseudocode
- Pre-commit hook: cognitive lint patterns on staged .md files

## Workflow
1. Plan phase (/aes-plan) → creates aes/tickets/TXXX-plan.md
2. Build phase (/aes-build) → creates aes/tickets/TXXX-build.md with diffstory
3. Verify phase (/aes-verify) → runs quality gates, creates aes/tickets/TXXX-verify.md
4. Review phase (/aes-review) → code review, creates aes/tickets/TXXX-review.md
5. Learn phase (/aes-learn) → documents lessons, creates aes/tickets/TXXX-learn.md

## How to Use
- To start work on a ticket: `/aes-plan` followed by `/aes-build`, `/aes-verify`, `/aes-review`, `/aes-learn`
- To run full cycle: `/aes run TXXX` (with confirmation between phases)
- To work on all tickets in sprint: `/aes sprint`
- For automatic execution: `/aes auto` (stops on failures)

## Notes
- This file is the single source of truth for project state
- Update current_sprint and current_ticket as work progresses
- All tickets should follow the AES execution loop
- Hostile analysis is required before implementation
- Anti-drift hooks installed at .aes/hooks/ — they block phase transitions if evidence is missing
