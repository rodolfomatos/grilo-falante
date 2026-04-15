# Grilo Falante v3.0

**Regime de Governança Cognitiva Assistida para Produção de Conhecimento com LLMs**

## Quick Start

```bash
# Development
make dev

# Production with Docker
docker-compose -f docker/docker-compose.yml up -d

# Run tests
make test

# Run audit
make audit
```

## Services

| Service | Port | Description |
|---------|------|-------------|
| API | 8000 | FastAPI REST |
| MCP | stdio | MCP Server |
| PostgreSQL | 5432 | Database |

## Environment Variables

```bash
DATABASE_URL=postgresql://postgres:postgres@localhost:5432/grilo_falante
LOG_LEVEL=info
POSTGRES_PASSWORD=postgres
```

## API Documentation

- Swagger UI: http://localhost:8000/docs
- ReDoc: http://localhost:8000/redoc
