# 16. Docker Setup

## docker-compose.yml

```yaml
version: '3.8'

services:
  postgres:
    image: postgres:15
    environment:
      POSTGRES_USER: grilo
      POSTGRES_PASSWORD: grilo123
      POSTGRES_DB: grilo_falante
    volumes:
      - postgres_data:/var/lib/postgresql/data
    ports:
      - "5432:5432"

  app:
    build: .
    depends_on:
      - postgres
    environment:
      DATABASE_URL: postgresql://grilo:grilo123@postgres:5432/grilo_falante
      MEMPALACE_PATH: /home/rodolfo/.mempalace
    volumes:
      - .:/app
    ports:
      - "8001:8001"

  ollama:
    image: ollama/ollama:latest
    ports:
      - "11434:11434"

  openwebui:
    image: ghcr.io/open-webui/open-webui:latest
    ports:
      - "8080:8080"
    environment:
      OLLAMA_BASE_URL: http://ollama:11434

volumes:
  postgres_data:
```

---

## Comandos Docker

```bash
# Construir e iniciar
docker-compose up -d

# Ver estado
docker-compose ps

# Logs
docker-compose logs -f app

# Parar
docker-compose down

# Rebuild
docker-compose up -d --build

# Limpar volumes (PERDE DADOS!)
docker-compose down -v
```

---

## Verificar Funcionamento

```bash
# Health check
curl http://localhost:8001/health

# PostgreSQL
docker-compose exec postgres psql -U grilo -d grilo_falante -c "SELECT 1"

# Ollama
curl http://localhost:11434
```

---

## Desenvolvimento Local

```bash
# Sem Docker
source venv/bin/activate
python3 -m grilo_falante.backend.mcp.server
```

---

*Voltar ao [Índice](../00_INDICE.md)*
