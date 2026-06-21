---
ticket: T008
title: Implement ACORDAR ritual (RF-07)
sprint: sprint-02
priority: high
status: pending
created: 2026-06-20
---

# T008 — Implement ACORDAR Ritual

## Context
RF-07 (ACORDAR Ritual) is the entry point for the epistemic governance regime. Currently, the system runs without verifying temporal anchoring or intention declaration. This makes it impossible to distinguish legitimate sessions from unauthorized ones.

## Acceptance Criteria
- [ ] ACORDAR endpoint accepts `data` + `intencao` parameters
- [ ] Without ACORDAR, regime remains in LEGITIMACY_SUSPENDED
- [ ] ACORDAR validates timestamp anchoring (ntp_sync)
- [ ] Output is regime active + session_id ou BLOCK
- [ ] Tests for valid/invalid ACORDAR calls
- [ ] Documentation updated (VISION, REQUIREMENTS)

## Scope
**In scope:** Implementation of the ACORDAR ritual as defined in RF-07, including endpoint, validation, and state transition.
**Out of scope:** DORMIR cycle, full legitimacy state machine (T009), graph-based governance (RF-10).

## Dependencies
T009 (legitimacy states)

## Rollback
Revert ACORDAR endpoint and state machine changes. Regime continues without ACORDAR requirement.

## Known Risks
- ACORDAR without persistence will not survive restart
- Integration with existing MCP tools may require interface changes

## Notes
See docs/VISION.md §3.3 and docs/REQUIREMENTS.md RF-07.
