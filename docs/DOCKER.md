# Grilo Falante v3.0 — Docker Deployment

## Quick Start

```bash
# Build and run
docker-compose up -d

# Check health
curl http://localhost:8001/health

# View logs
docker-compose logs -f grilo-falante

# Stop
docker-compose down
```

## Environment Variables

Create a `.env` file (copy from `.env.example`):

```bash
cp .env.example .env
# Edit .env with your values
```

| Variable | Description | Default |
|----------|-------------|---------|
| `GRILO_JWT_SECRET` | JWT signing secret | `changeme` |
| `DB_PASSWORD` | PostgreSQL password | `grilo123` |
| `GRILO_STORAGE_PATH` | Path to JSON storage | `/app/data/ilhas.json` |

## Services

### Grilo Falante API

- **Port:** 8001
- **Health endpoint:** http://localhost:8001/health
- **API docs:** http://localhost:8001/docs

### PostgreSQL (optional)

Enable with: `docker-compose --profile with-postgres up -d`

- **Port:** 5432
- **Database:** grilo_falante
- **User:** grilo

## Data Persistence

Data is stored in:
- `./data/ilhas.json` (mapped to container)
- `./data/` (gitignored)

## Production Deployment

For production:

1. Change `GRILO_JWT_SECRET` to a secure random string
2. Enable PostgreSQL for scalability
3. Set up reverse proxy (nginx, traefik)
4. Configure CORS for your domain
5. Use Docker secrets for sensitive values

## Troubleshooting

### Container won't start

```bash
# Check logs
docker-compose logs grilo-falante

# Rebuild
docker-compose build --no-cache
```

### Health check fails

```bash
# Check if port is available
lsof -i :8001

# Check container networking
docker-compose exec grilo-falante curl http://localhost:8001/health
```

### Permission issues

```bash
# Fix data directory permissions
chmod -R 755 data/
```

## Development

For local development with Docker:

```bash
# Build
docker-compose build

# Run with file watching (requires nodemon or similar)
docker-compose -f docker-compose.yml -f docker-compose.dev.yml up
```
