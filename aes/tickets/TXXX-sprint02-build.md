---
ticket: Sprint-02-initialisation
phase: build
status: done
---

# Diffstory — Sprint-02 Initialisation + AES Compliance Audit

## What Changed

### 1. Created `docs/HOSTILE_INSIGHTS.md` (NEW)
Critical file listed in CLAUDE.md but missing. Contains 7 entries documenting lessons from hostile analysis:
- Sprint-01 ticket evidence gap
- HOSTILE_INSIGHTS.md itself missing
- Makefile anti-pattern (2>/dev/null)
- Documentation duplication (reference vs references)
- Pydantic deprecation warnings
- Lint debt (~100+ issues)
- AES protocol gap (no artifact verification between phases)

### 2. Fixed `Makefile` (MODIFIED)
**Removed silent error swallowing:** All `2>/dev/null` patterns replaced with explicit dependency checks.
- `test-unit`: Now checks pytest exists before running. Removed broken fallback chain.
- `test-all`: Now runs `grilo_falante/tests/` AND `app/tests/` explicitly. Previously only ran one.
- `lint`: Now checks ruff exists. Removed broken PATH fallback.
- `format`: Now checks ruff exists. Removed broken PATH fallback.

**Added new targets:**
- `check` — runs lint + format-check + test-all (CI gate)
- `doctor` — diagnoses Python version, test framework, ruff, Docker, PostgreSQL, project structure, hooks
- `coverage` — runs tests with `--cov=grilo_falante --cov=app --cov-report=html`
- `format-check` — runs `ruff format --check` (non-destructive formatting check)

### 3. Created `.aes/hooks/` (NEW)
Three anti-drift hooks:
- `pre-build.sh` — blocks if no plan file exists, checks critical files exist
- `pre-review.sh` — blocks if no verify or build output exists
- `pre-merge.sh` — blocks if any phase file missing, warns on large diffs, detects debug/TODO in src

### 4. Created `sprint-02` with backlog (NEW)
- `aes/sprints/sprint-02.md` — Core Features and Technical Debt
- `aes/tickets/T008-acordar-ritual.md` — ACORDAR ritual ticket
- 6 more tickets in kanban backlog (T009 to T015)

### 5. Updated `aes/kanban.md` (MODIFIED)
- Moved to sprint-02
- Added rich backlog with 8 tickets
- Added note about anti-drift hooks
- Updated last_updated

### 6. Updated `CLAUDE.md` (MODIFIED)
- Added AES Evidence Rules section
- Added .aes/hooks/ to project structure

### 7. Fixed `docs/references/` duplication (MODIFIED)
- Added README.md redirecting to `docs/reference/`
- Documented all known duplicates

## What Was Intentionally NOT Touched
- **Pre-existing lint issues** (~100+ findings) — scope creep. Added to sprint-02 as T011.
- **Pydantic V2 deprecation warnings** — scope creep. Added as T010.
- **TODOs in source code** (acordar.py, gap_detector.py) — pre-existing, not introduced here.
- **File named `erosão.py`** — N999 lint error, but renaming has unknown consequences. Added to T011.

## Remaining Risks
- Pre-merge hook currently blocks because no phase files exist yet — this is correct behaviour, it will unblock once sprint-02 work starts properly
- Pydantic V2 warnings will become errors in Pydantic V3 — medium-term risk
- `erosão.py` with special character may cause import issues on some filesystems — low risk but should be addressed
