.PHONY: help dev test lint format clean build \
	check doctor coverage \
	docker-build docker-up docker-down docker-logs docker-restart \
	docker-start docker-stop \
	docker-visualizer docker-api docker-mcp docker-db \
	docker-rebuild docker-rebuild-api docker-rebuild-visualizer docker-rebuild-nginx \
	db-init db-migrate db-reset db-seed \
	audit audit-hostile \
	install install-dev \
	git-init git-status git-commit \
	mcp-config mcp-install-opencode mcp-install-claude \
	health health-api health-db health-visualizer \
	test-unit test-integration test-all \
	lint-fix format-fix \
	check-premises \
	validate docs-check check-epistemic premise-check metrics roadmap install-hooks

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
	@echo "  format-check     Check formatting without modifying"
	@echo "  check            Run lint + format-check + tests (CI gate)"
	@echo "  doctor           Diagnose environment and project health"
	@echo "  coverage         Run tests with coverage report"
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
	@echo "  docker-rebuild     Rebuild and restart all services"
	@echo "  docker-rebuild-api Rebuild API only"
	@echo "  docker-rebuild-visualizer Rebuild visualizer only"
	@echo "  docker-rebuild-nginx Rebuild nginx only"
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
	@command -v pytest >/dev/null 2>&1 || { echo "ERROR: pytest not found. Run 'make install-dev'"; exit 1; }
	@PYTHONPATH=. pytest grilo_falante/tests/ -v -x -k "not integration"

test-integration:
	@echo "Running integration tests..."
	@command -v pytest >/dev/null 2>&1 || { echo "ERROR: pytest not found. Run 'make install-dev'"; exit 1; }
	@if [ -d "grilo_falante/tests/integration/" ]; then PYTHONPATH=. pytest grilo_falante/tests/integration/ -v -x; else echo "No integration test directory found"; fi

test-all:
	@echo "Running all tests..."
	@command -v pytest >/dev/null 2>&1 || { echo "ERROR: pytest not found. Run 'make install-dev'"; exit 1; }
	@PYTHONPATH=. pytest grilo_falante/tests/ app/tests/ -v

lint:
	@echo "Running linter..."
	@command -v ruff >/dev/null 2>&1 || { echo "ERROR: ruff not found. Run 'make install-dev'"; exit 1; }
	@ruff check grilo_falante/ app/

lint-fix:
	@echo "Running linter with auto-fix..."
	@command -v ruff >/dev/null 2>&1 || { echo "ERROR: ruff not found. Run 'make install-dev'"; exit 1; }
	@ruff check grilo_falante/ app/ --fix

format:
	@echo "Formatting code..."
	@command -v ruff >/dev/null 2>&1 || { echo "ERROR: ruff not found. Run 'make install-dev'"; exit 1; }
	@ruff format grilo_falante/ app/

check: lint format-check test-all
	@echo "=== All checks passed ==="

doctor:
	@echo "=== Environment Doctor ==="
	@echo -n "Python: "; python3 --version 2>&1 || echo "NOT FOUND"
	@echo -n "pytest: "; python3 -m pytest --version 2>&1 || echo "NOT FOUND"
	@echo -n "ruff: "; ruff --version 2>&1 || echo "NOT FOUND"
	@echo -n "Docker: "; docker --version 2>&1 || echo "NOT FOUND"
	@echo -n "PostgreSQL: "; pg_isready --version 2>&1 || echo "NOT FOUND"
	@echo ""
	@echo "=== Dependencies ==="
	@python3 -m pip list 2>/dev/null | grep -iE "fastapi|uvicorn|asyncpg|pydantic|httpx|structlog" || echo "Some deps missing"
	@echo ""
	@echo "=== Project Structure ==="
	@for d in aes/tickets aes/sprints aes/handoffs aes/verification docs/HOSTILE_INSIGHTS.md; do \
		if [ -e "$$d" ]; then echo "  [OK] $$d"; else echo "  [MISSING] $$d"; fi; \
	done
	@echo ""
	@echo "=== AES Hooks ==="
	@for h in .aes/hooks/pre-build.sh .aes/hooks/pre-review.sh .aes/hooks/pre-merge.sh; do \
		if [ -x "$$h" ]; then echo "  [OK] $$h"; else echo "  [MISSING/NOT EXEC] $$h"; fi; \
	done

coverage:
	@echo "Running tests with coverage..."
	@command -v pytest >/dev/null 2>&1 || { echo "ERROR: pytest not found. Run 'make install-dev'"; exit 1; }
	@PYTHONPATH=. pytest grilo_falante/tests/ app/tests/ -v --cov=grilo_falante --cov=app --cov-report=term --cov-report=html

format-check:
	@echo "Checking formatting..."
	@command -v ruff >/dev/null 2>&1 || { echo "ERROR: ruff not found. Run 'make install-dev'"; exit 1; }
	@ruff format grilo_falante/ app/ --check

clean:
	@echo "Cleaning build artifacts..."
	@find . -type d -name __pycache__ -exec rm -rf {} + 2>/dev/null || true
	@find . -type f -name "*.pyc" -delete 2>/dev/null || true
	@find . -type d -name "*.egg-info" -exec rm -rf {} + 2>/dev/null || true
	@rm -rf build/ dist/ .pytest_cache/ .ruff_cache/ coverage_html/

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

docker-rebuild:
	@echo "Rebuilding and restarting all Docker services..."
	@docker compose -f docker/docker-compose.yml up --build -d
	@echo ""
	@docker compose -f docker/docker-compose.yml ps

docker-rebuild-api:
	@echo "Rebuilding API..."
	@docker compose -f docker/docker-compose.yml up --build -d api

docker-rebuild-visualizer:
	@echo "Rebuilding Visualizer..."
	@docker compose -f docker/docker-compose.yml up --build -d visualizer

docker-rebuild-nginx:
	@echo "Rebuilding Nginx..."
	@docker compose -f docker/docker-compose.yml up --build -d nginx

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

check-premises:
	@echo "=== Premise Graph Validation ==="
	@command -v grilo >/dev/null 2>&1 || { echo "ERROR: grilo CLI not found. Run 'make install' first"; exit 1; }
	@if [ -d "aes/premises" ]; then \
		count=0; failed=0; \
		for f in aes/premises/*.dot; do \
			[ -f "$$f" ] || continue; \
			count=$$((count+1)); \
			if grilo validate-dot --graph "$$f" --json >/dev/null 2>&1; then \
				name=$$(basename "$$f"); \
				echo "  PASS  $$name"; \
			else \
				failed=$$((failed+1)); \
				grilo validate-dot --graph "$$f" 2>&1; \
			fi; \
		done; \
		if [ "$$count" -eq 0 ]; then \
			echo "  No .dot files found in aes/premises/"; \
		else \
			total=$$((count)); \
			passed=$$((count - failed)); \
			echo ""; \
			echo "  ──────────────────────────────────"; \
			echo "  $$passed passed, $$failed failed ($$total total)"; \
		fi; \
	else \
		echo "  Directory aes/premises/ not found"; \
	fi

validate:
	@echo "=== Quick Validation ==="
	@bash -n hooks/*.sh .aes/hooks/*.sh .aes/plugins/*.sh 2>&1 || { echo "Syntax error in scripts"; exit 1; }
	@command -v shellcheck >/dev/null 2>&1 && shellcheck hooks/*.sh .aes/hooks/*.sh .aes/plugins/*.sh 2>/dev/null || \
		echo "shellcheck not installed, skipping"
	@echo "Validate passed"

docs-check:
	@echo "=== Documentation Check ==="
	@for f in docs/VISION.md docs/REQUIREMENTS.md docs/ROADMAP.md; do \
		if [ -f "$$f" ]; then echo "  [OK] $$f"; else echo "  [MISSING] $$f"; fi; \
	done
	@if command -v grilo >/dev/null 2>&1; then \
		for f in docs/*.md; do \
			[ -f "$$f" ] || continue; \
			name=$$(basename "$$f"); \
			if grilo lint-text --file "$$f" --json >/dev/null 2>&1; then \
				echo "  PASS  $$name"; \
			else \
				echo "  FAIL  $$name (cognitive lint)"; \
				grilo lint-text --file "$$f" 2>&1; \
			fi; \
		done; \
	else \
		echo "  grilo CLI not available — cognitive linting skipped"; \
	fi

check-epistemic:
	@echo "=== Epistemic Quality Gate ==="
	@if command -v grilo &>/dev/null; then \
		if [ -d "aes/premises" ] && ls aes/premises/*.dot >/dev/null 2>&1; then \
			grilo check-epistemic --dir aes/premises/ || exit 1; \
		else \
			echo "  No premise graphs found — skipping"; \
		fi \
	elif python3 -m grilo_falante.cli check-epistemic --help >/dev/null 2>&1; then \
		if [ -d "aes/premises" ] && ls aes/premises/*.dot >/dev/null 2>&1; then \
			python3 -m grilo_falante.cli check-epistemic --dir aes/premises/ || exit 1; \
		else \
			echo "  No premise graphs found — skipping"; \
		fi \
	else \
		echo "  WARN  grilo CLI not available — epistemic gate skipped"; \
	fi

premise-check:
	@echo "=== Premise Graph Validation ==="
	@if command -v grilo >/dev/null 2>&1; then \
		if [ -d "aes/premises" ] && ls aes/premises/*.dot >/dev/null 2>&1; then \
			for f in aes/premises/*.dot; do \
				[ -f "$$f" ] || continue; \
				name=$$(basename "$$f"); \
				if grilo validate-dot --graph "$$f" --json >/dev/null 2>&1; then \
					echo "  PASS  $$name"; \
				else \
					echo "  FAIL  $$name"; \
					grilo validate-dot --graph "$$f" 2>&1; \
				fi; \
			done; \
		else \
			echo "  No .dot files found in aes/premises/"; \
		fi \
	else \
		if [ -d "aes/premises" ] && ls aes/premises/*.dot >/dev/null 2>&1; then \
			for f in aes/premises/*.dot; do \
				[ -f "$$f" ] || continue; \
				name=$$(basename "$$f"); \
				if command -v dot &>/dev/null; then \
					dot -Tsvg "$$f" -o /dev/null 2>/dev/null && echo "  PASS  $$name" || echo "  FAIL  $$name"; \
				else \
					grep -q '^digraph ' "$$f" 2>/dev/null && echo "  PASS  $$name" || echo "  FAIL  $$name (no digraph)"; \
				fi; \
			done; \
		else \
			echo "  No premise graphs found — skipping"; \
		fi; \
	fi

metrics:
	@echo "=== Project Metrics ==="
	@echo -n "Python files: "; find grilo_falante/ app/ -name "*.py" 2>/dev/null | wc -l
	@echo -n "Shell scripts: "; find hooks/ .aes/hooks/ scripts/ -name "*.sh" 2>/dev/null | wc -l
	@echo -n "Markdown files: "; find docs/ aes/ -name "*.md" 2>/dev/null | wc -l
	@echo -n "DOT graphs: "; find aes/premises/ -name "*.dot" 2>/dev/null | wc -l
	@echo -n "Total LOC Python: "
	@find grilo_falante/ app/ -name "*.py" -exec cat {} + 2>/dev/null | wc -l || echo "0"
	@echo ""
	@echo "=== Ticket Status ==="
	@if [ -f aes/kanban.md ]; then \
		grep "^|" aes/kanban.md | grep "T[0-9]" || echo "  No tickets found in kanban"; \
	else \
		echo "  No kanban file found"; \
	fi
	@echo ""
	@if [ -d aes/tickets ]; then \
		total=0; done=0; \
		for f in aes/tickets/*.md; do \
			[ -f "$$f" ] || continue; \
			total=$$((total+1)); \
			grep -q "status: done" "$$f" && done=$$((done+1)) || true; \
		done; \
		echo "Tickets: $$done/$$total done"; \
	fi

roadmap:
	@echo "=== Roadmap ==="
	@if [ -f docs/ROADMAP.md ]; then \
		grep -E "^## |^- \[[ x]\]" docs/ROADMAP.md || echo "  No roadmap items found"; \
	else \
		echo "  No ROADMAP.md found"; \
	fi
	@echo ""
	@if [ -f aes/kanban.md ]; then \
		echo "=== Sprint Status ==="; \
		grep -E "^|.*sprint" aes/kanban.md | grep -v "^-" | head -20; \
	fi

install-hooks:
	@echo "Installing AES hooks..."
	@mkdir -p .aes/hooks .aes/plugins
	@if [ -d hooks ]; then \
		for hook in hooks/*.sh; do \
			[ -f "$$hook" ] || continue; \
			name=$$(basename "$$hook"); \
			cp "$$hook" ".aes/hooks/$$name"; \
			chmod +x ".aes/hooks/$$name"; \
			echo "  AES hook: $$name"; \
		done; \
	fi
	@if [ -d .aes/plugins ]; then \
		for plugin in .aes/plugins/*.sh; do \
			[ -f "$$plugin" ] || continue; \
			chmod +x "$$plugin"; \
			echo "  Plugin: $$(basename $$plugin)"; \
		done; \
	fi
	@echo "AES hooks installed."

install-git-hooks:
	@echo "Installing git pre-commit hook..."
	@mkdir -p .git/hooks
	@if [ -f hooks/pre-commit-gf.sh ]; then \
		cp hooks/pre-commit-gf.sh .git/hooks/pre-commit; \
		chmod +x .git/hooks/pre-commit; \
		echo "  Installed: .git/hooks/pre-commit"; \
		echo "  Cognitive Lint will now run on staged .md files."; \
	else \
		echo "  hooks/pre-commit-gf.sh not found. Skipping."; \
	fi

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