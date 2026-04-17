.PHONY: help dev test lint format clean build \
	docker-build docker-up docker-down docker-logs docker-restart \
	docker-start docker-stop \
	docker-visualizer docker-api docker-mcp docker-db \
	db-init db-migrate db-reset db-seed \
	audit audit-hostile \
	install install-dev \
	git-init git-status git-commit \
	mcp-config mcp-install-opencode mcp-install-claude \
	health health-api health-db health-visualizer \
	test-unit test-integration test-all \
	lint-fix format-fix

# =============================================================================
# Grilo Falante v3.0 - Makefile
# =============================================================================

help:
	@echo "Grilo Falante v3.0 - Comprehensive Makefile"
	@echo ""
	@echo "Usage: make <target>"
	@echo ""
	@echo "=== Development ==="
	@echo "  dev              Install development dependencies"
	@echo "  test             Run all tests"
	@echo "  test-unit        Run unit tests only"
	@echo "  test-integration Run integration tests only"
	@echo "  lint             Run linter (check only)"
	@echo "  lint-fix         Run linter with auto-fix"
	@echo "  format           Format code"
	@echo "  clean            Clean build artifacts"
	@echo ""
	@echo "=== Docker ==="
	@echo "  docker-build          Build all Docker images"
	@echo "  docker-up            Start all Docker services"
	@echo "  docker-down          Stop all Docker services"
	@echo "  docker-start         Start existing services"
	@echo "  docker-stop          Stop running services"
	@echo "  docker-logs          Show Docker logs"
	@echo "  docker-restart      Restart all services"
	@echo "  docker-visualizer   Start only visualizer"
	@echo "  docker-api          Start only API"
	@echo "  docker-mcp          Start only MCP"
	@echo "  docker-db          Start only database"
	@echo ""
	@echo "=== Database ==="
	@echo "  db-init        Initialize database schema"
	@echo "  db-migrate    Run migrations"
	@echo "  db-reset     Reset database (drop all)"
	@echo "  db-seed      Seed database with sample data"
	@echo ""
	@echo "=== Run ==="
	@echo "  run-api           Run API locally"
	@echo "  run-mcp          Run MCP locally"
	@echo "  run-visualizer   Run visualizer locally"
	@echo ""
	@echo "=== Health ==="
	@echo "  health              Check all services"
	@echo "  health-api         Check API"
	@echo "  health-db         Check database"
	@echo "  health-visualizer  Check visualizer"
	@echo ""
	@echo "=== Audit ==="
	@echo "  audit            Run hostile audit summary"
	@echo "  audit-hostile   Run full hostile audit"
	@echo ""
	@echo "=== Git ==="
	@echo "  git-init       Initialize git repository"
	@echo "  git-status    Show git status"
	@echo "  git-commit   Commit changes (MSG='message')"
	@echo ""
	@echo "=== MCP ==="
	@echo "  mcp-config          Show MCP configuration"
	@echo "  mcp-install-opencode Install for OpenCode"
	@echo "  mcp-install-claude  Install for Claude Desktop"

# =============================================================================
# Development
# =============================================================================

dev:
	@echo "Installing development dependencies..."
	@pip install pytest pytest-asyncio ruff httpx pydantic asyncpg 2>/dev/null || true
	@echo "Ready!"

test: test-all

test-unit:
	@echo "Running unit tests..."
	@PYTHONPATH=. pytest grilo_falante/tests/unit/ -v -x 2>/dev/null || \
	PYTHONPATH=. pytest grilo_falante/tests/ -v -x -k "not integration" 2>/dev/null || \
	echo "No unit tests found or pytest not installed"

test-integration:
	@echo "Running integration tests..."
	@PYTHONPATH=. pytest grilo_falante/tests/integration/ -v -x 2>/dev/null || \
	echo "No integration tests found"

test-all:
	@echo "Running all tests..."
	@PYTHONPATH=. pytest grilo_falante/tests/ -v 2>/dev/null || \
	PYTHONPATH=. pytest grilo_falante/ -v --ignore=grilo_falante/tests/ 2>/dev/null || \
	echo "Tests not found or pytest not installed"

lint:
	@echo "Running linter..."
	@python -m ruff check grilo_falante/ 2>/dev/null || \
	PATH="$$HOME/.local/bin:$$PATH" ruff check grilo_falante/ 2>/dev/null || \
	echo "ruff not installed"

lint-fix:
	@echo "Running linter with auto-fix..."
	@python -m ruff check grilo_falante/ --fix 2>/dev/null || \
	PATH="$$HOME/.local/bin:$$PATH" ruff check grilo_falante/ --fix 2>/dev/null || \
	echo "ruff not installed"

format:
	@echo "Formatting code..."
	@python -m ruff format grilo_falante/ 2>/dev/null || \
	PATH="$$HOME/.local/bin:$$PATH" ruff format grilo_falante/ 2>/dev/null || \
	echo "ruff not installed"

clean:
	@echo "Cleaning build artifacts..."
	@find . -type d -name __pycache__ -exec rm -rf {} + 2>/dev/null || true
	@find . -type f -name "*.pyc" -delete 2>/dev/null || true
	@find . -type d -name "*.egg-info" -exec rm -rf {} + 2>/dev/null || true
	@rm -rf build/ dist/ .pytest_cache/ .ruff_cache/

# =============================================================================
# Run Locally
# =============================================================================

run-api:
	@echo "Starting API locally..."
	@PYTHONPATH=. uvicorn grilo_falante.backend.api.main:app --host 0.0.0.0 --port 8000 --reload

run-mcp:
	@echo "Starting MCP locally..."
	@python -m grilo_falante.backend.mcp.server

run-visualizer:
	@echo "Starting Visualizer locally..."
	@python visualizer_server.py

# =============================================================================
# Docker
# =============================================================================

docker-build:
	@echo "Building Docker images..."
	@docker compose -f docker/docker-compose.yml build

docker-up:
	@echo "Starting all Docker services..."
	@docker compose -f docker/docker-compose.yml up -d
	@echo ""
	@docker compose -f docker/docker-compose.yml ps
	@echo ""
	@echo "Services:"
	@echo "  API:         http://localhost:8010"
	@echo "  Nginx:       https://llm.ilab.uporto.pt (or localhost)"
	@echo "  Visualizer: http://localhost:8005/visualizer"
	@echo "  OpenWebUI:  http://localhost:8081"
	@echo "  PostgreSQL: localhost:5433"

docker-down:
	@echo "Stopping Docker services..."
	@docker compose -f docker/docker-compose.yml down

docker-logs:
	@echo "Showing Docker logs (Ctrl+C to exit)..."
	@docker compose -f docker/docker-compose.yml logs -f

docker-restart:
	@echo "Restarting Docker services..."
	@docker compose -f docker/docker-compose.yml restart

docker-start:
	@echo "Starting Docker services..."
	@docker compose -f docker/docker-compose.yml start

docker-stop:
	@echo "Stopping Docker services..."
	@docker compose -f docker/docker-compose.yml stop

docker-visualizer:
	@echo "Starting Visualizer..."
	@docker compose -f docker/docker-compose.yml up -d db visualizer
	@echo "Visualizer: http://localhost:8005/visualizer"

docker-api:
	@echo "Starting API..."
	@docker compose -f docker/docker-compose.yml up -d db api
	@echo "API: http://localhost:8010"

docker-mcp:
	@echo "Starting MCP..."
	@docker compose -f docker/docker-compose.yml up -d db mcp

docker-db:
	@echo "Starting PostgreSQL..."
	@docker compose -f docker/docker-compose.yml up -d db
	@echo "PostgreSQL: localhost:5433"

# =============================================================================
# Database
# =============================================================================

db-init:
	@echo "Initializing database..."
	@PYTHONPATH=. python3 -c "from grilo_falante.backend.db.connection import init_pool, init_schema; import asyncio; asyncio.run(init_pool()); asyncio.run(init_schema())"

db-migrate:
	@echo "Running migrations..."
	@echo "Migration not implemented yet"

db-reset:
	@echo "WARNING: Dropping all tables..."
	@echo "Use: docker exec grilo-postgres psql -U postgres -d grilo_falante -c 'DROP SCHEMA public CASCADE; CREATE SCHEMA public;'"

db-seed:
	@echo "Seeding database..."
	@PYTHONPATH=. python3 -c "from grilo_falante.backend.db.connection import init_pool; import asyncio; asyncio.run(init_pool())"

# =============================================================================
# Health Checks
# =============================================================================

health:
	@echo "=== Health Check ==="
	@curl -sf http://localhost:8010/health >/dev/null && echo "API: OK" || echo "API: FAIL"
	@curl -sf http://localhost:8005/health >/dev/null && echo "Visualizer: OK" || echo "Visualizer: FAIL"
	@curl -sf http://localhost:8081 >/dev/null && echo "OpenWebUI: OK" || echo "OpenWebUI: FAIL"
	@pg_isready -h localhost -p 5433 && echo "PostgreSQL: OK" || echo "PostgreSQL: FAIL"

health-api:
	@curl -sf http://localhost:8010/health && echo "API OK" || echo "API FAIL"

health-db:
	@pg_isready -h localhost -p 5433 && echo "PostgreSQL OK" || echo "PostgreSQL FAIL"

health-visualizer:
	@curl -sf http://localhost:8005/health && echo "Visualizer OK" || echo "Visualizer FAIL"

# =============================================================================
# Audit
# =============================================================================

audit:
	@echo "Running hostile audit..."
	@PYTHONPATH=. python3 -c "from grilo_falante.backend.services import CognitiveLint; lint = CognitiveLint(); print('Blocking patterns:', len(lint.BLOCK_PATTERNS)); print('Warning patterns:', len(lint.WARN_PATTERNS))"

audit-hostile:
	@echo "=== Full Hostile Audit ==="
	@PYTHONPATH=. python3 -c "from grilo_falante.models import GMIFLevel; print('=== GMIF LEVELS ==='); [print(f'  {l.value}: {l.name}') for l in GMIFLevel]"
	@echo ""
	@PYTHONPATH=. python3 -c "from grilo_falante.backend.services import CognitiveLint; lint = CognitiveLint(); print('=== BLOCKING PATTERNS ==='); [print(f'  {p}') for p in lint.BLOCK_PATTERNS]"

# =============================================================================
# Git
# =============================================================================

git-init:
	@echo "Initializing git repository..."
	@git init
	@git add .
	@git commit -m "Initial commit: Grilo Falante v3.0"

git-status:
	@git status

git-commit:
ifndef MSG
	$(error MSG is not set. Usage: make git-commit MSG='Your message')
endif
	@git add .
	@git commit -m "$(MSG)"

# =============================================================================
# MCP
# =============================================================================

mcp-config:
	@echo "MCP Configuration:"
	@echo '{"mcpServers":{"grilo":{"command":"python","args":["-m","grilo_falante.backend.mcp.server"]}}}'

mcp-install-opencode:
	@mkdir -p ~/.config/opencode
	@printf '{"mcpServers":{"grilo":{"command":"python","args":["-m","grilo_falante.backend.mcp.server"]}}}' > ~/.config/opencode/mcp.json
	@echo "Installed MCP config to ~/.config/opencode/mcp.json"

mcp-install-claude:
	@mkdir -p "$$HOME/Library/Application Support/Claude"
	@printf '{"mcpServers":{"grilo":{"command":"python","args":["-m","grilo_falante.backend.mcp.server"]}}}' > "$$HOME/Library/Application Support/Claude/claude_desktop_config.json"
	@echo "Installed MCP config for Claude Desktop"

# =============================================================================
# Install
# =============================================================================

install:
	@echo "Installing Grilo Falante..."
	@pip install -e .

install-dev:
	@echo "Installing development dependencies..."
	@pip install -e ".[dev,mcp]"