# Grilo Falante v3.0 — Changelog

## v3.0.0 (2026-04-15)

### Breaking Changes
- Consolidated Grilo Falante v2.5.0 and GePeTo into single project
- Unified models: `GovernedClaim`, `Gap`, `Curator`, `Source`
- PostgreSQL as primary database (replaced JSON ledger)

### New Features
- ~25 MCP tools for full integration
- REST API with FastAPI
- Feynman Explanation Protocol (FEP-1/2/3)
- Gap Detection with TIPO A/B/C
- Curator Scoring with decay
- School Mode 8-step workflow
- Trusted Source Registry (Tier 1/2/3)

### Infrastructure
- Docker Compose for local development
- PostgreSQL with pgvector support
- MCP server (stdio-based)
- REST API with OpenAPI docs

### Migration from v2.5.0
- Install: `pip install grilo-falante`
- MCP config: `python -m grilo_falante.backend.mcp.server`
- API: `uvicorn grilo_falante.backend.api.main:app`
