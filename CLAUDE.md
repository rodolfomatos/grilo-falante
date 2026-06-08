# Grilo Falante v3.0 - Operational Contract

## Intent
This document establishes the operational contract for the Grilo Falante v3.0 project, defining critical files, non-goals, and evidence required for contributions.

## Non-Goals
- Grilo Falante does not produce decisions or validate truths
- It does not confer authority factual on claims
- It is not a general-purpose knowledge graph tool without epistemic governance
- It does not aim to replace human judgment, only to make the cost of judgment visible

## Critical Files
- `docs/VISION.md` - Core vision and concepts
- `docs/REQUIREMENTS.md` - Functional and non-functional requirements
- `docs/ROADMAP.md` - Implementation plan and priorities
- `docs/HOSTILE_INSIGHTS.md` - Accumulated lessons from hostile analysis
- `grilo_falante/backend/mcp/server.py` - MCP server implementation
- `grilo_falante/models/` - Pydantic models for core concepts (ILHA, PEDRA, ShadowDocument)
- `grilo_falante/backend/services/` - Cognitive services (audit, lint, governance)
- `app/services/pipeline.py` - Main analysis pipeline
- `app/data/memory/graph/gmif.py` - GMIF classification logic

## Never-Do List
- Never commit code without corresponding tests
- Never bypass the Shadow First methodology (research before assuming)
- Never implement features without updating documentation
- Never ignore failing tests or lint errors
- Never make architectural decisions without hostile analysis
- Never combine multiple unrelated changes in a single commit
- Never deploy to production without running all quality gates

## Evidence Required
For any change claiming to implement a feature from the roadmap:
1. Reference the specific requirement ID from REQUIREMENTS.md
2. Show hostile analysis (assumptions, alternatives, risks considered)
3. Provide test evidence (unit/integration tests that validate the change)
4. Document any impact on existing functionality
5. Update relevant documentation (VISION, REQUIREMENTS, ROADMAP as needed)

## AES Project Structure
This project uses AES (Aggressive Engineering System) for project management:
- `aes/kanban.md` - Global project state
- `aes/sprints/` - Sprint planning and retrospectives
- `aes/tickets/` - Individual tickets with plan/build/verify/review/learn phases
- `aes/handoffs/` - Session continuity files
- `aes/verification/` - Archived test output and logs

## Quality Gates
Before declaring work complete, verify:
- [ ] Tests pass (unit and integration)
- [ ] Lint passes (ruff check)
- [ ] Format correct (ruff format)
- [ ] No console.log/debug in src
- [ ] No TODO in src
- [ ] Docs updated if behaviour changed
- [ ] Diffstory written (what changed, why, what was untouched, remaining risks)
- [ ] Reviewed for simplicity and correctness

## Environment
- Language: Python 3.9+
- Framework: FastAPI for API, MCP for tool exposure
- Testing: pytest
- Linting: ruff
- Formatting: ruff
- Docker: Available for containerization