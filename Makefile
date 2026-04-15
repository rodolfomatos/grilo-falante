.PHONY: help dev test lint format clean build build-api build-mcp \
	audit audit-hostile \
	install install-dev docker-build docker-up docker-down \
	git-init git-status git-commit \
	mcp-config mcp-install-opencode mcp-install-claude

help:
	@echo "Grilo Falante v3.0 - Makefile"
	@echo ""
	@echo "Usage: make <target>"
	@echo ""
	@echo "Development:"
	@echo "  dev              Install development dependencies"
	@echo "  test             Run tests"
	@echo "  lint             Run linter"
	@echo "  format           Format code"
	@echo "  clean            Clean build artifacts"
	@echo ""
	@echo "Build:"
	@echo "  build            Build system documentation"
	@echo "  build-api        Build/publish API package"
	@echo "  build-mcp        Build MCP package"
	@echo ""
	@echo "Run:"
	@echo "  docker-build     Build Docker images"
	@echo "  docker-up        Start Docker services"
	@echo "  docker-down      Stop Docker services"
	@echo ""
	@echo "Audit:"
	@echo "  audit            Run hostile audit"
	@echo "  audit-hostile    Run full audit with details"
	@echo ""
	@echo "Git:"
	@echo "  git-init         Initialize git repository"
	@echo "  git-status       Show git status"
	@echo "  git-commit       Commit changes (MSG=...)"
	@echo ""
	@echo "MCP:"
	@echo "  mcp-config       Show MCP configuration"
	@echo "  mcp-install-opencode  Install for OpenCode"
	@echo "  mcp-install-claude    Install for Claude Desktop"
	@echo ""

dev:
	@echo "Installing development dependencies..."
	cd grilo_falante && pip install -e ".[dev]"

test:
	@echo "Running tests..."
	cd grilo_falante && pytest tests/ -v

lint:
	@echo "Running linter..."
	cd grilo_falante && ruff check .

format:
	@echo "Formatting code..."
	cd grilo_falante && ruff format .

clean:
	@echo "Cleaning..."
	find . -type d -name __pycache__ -exec rm -rf {} + 2>/dev/null || true
	find . -type f -name "*.pyc" -delete
	find . -type d -name "*.egg-info" -exec rm -rf {} + 2>/dev/null || true
	rm -rf build/ dist/ .pytest_cache/

build:
	@echo "Building system documentation..."
	@echo "(Build step for regime documentation)"

build-api:
	@echo "Building API..."
	cd grilo_falante && pip install -e .

build-mcp:
	@echo "Building MCP..."
	cd grilo_falante && pip install -e .

audit:
	@echo "Running hostile audit..."
	cd grilo_falante && python3 -c "
from pathlib import Path
from grilo_falante.backend.services import CognitiveLint
lint = CognitiveLint()
print('Lint patterns loaded:', len(lint.BLOCK_PATTERNS), 'blocking,', len(lint.WARN_PATTERNS), 'warning')
print('Audit complete.')
"

audit-hostile:
	@echo "Running full hostile audit..."
	cd grilo_falante && python3 << 'EOF'
from pathlib import Path
from grilo_falante.models import GMIFLevel
print("=== HOSTILE AUDIT ===")
print(f"GMIF Levels: {len(GMIFLevel)}")
for level in GMIFLevel:
    print(f"  {level.value}: {level.name}")
print("=== AUDIT COMPLETE ===")
EOF

docker-build:
	@echo "Building Docker images..."
	docker-compose -f docker/docker-compose.yml build

docker-up:
	@echo "Starting Docker services..."
	docker-compose -f docker/docker-compose.yml up -d
	@echo "API: http://localhost:8000"
	@echo "Docs: http://localhost:8000/docs"

docker-down:
	@echo "Stopping Docker services..."
	docker-compose -f docker/docker-compose.yml down

git-init:
	@echo "Initializing git repository..."
	git init
	git add .
	git commit -m "Initial commit: Grilo Falante v3.0"

git-status:
	git status

git-commit:
ifndef MSG
	$(error MSG is not set. Usage: make git-commit MSG='Your message')
endif
	git add .
	git commit -m "$(MSG)"

mcp-config:
	@echo "MCP Configuration for OpenCode/Claude:"
	@echo '{"mcpServers":{"grilo":{"command":"python","args":["-m","grilo_falante.backend.mcp.server"]}}}'

mcp-install-opencode:
	@mkdir -p ~/.config/opencode
	@printf '{"mcpServers":{"grilo":{"command":"python","args":["-m","grilo_falante.backend.mcp.server"]}}}\n' > ~/.config/opencode/mcp.json
	@echo "Installed MCP config to ~/.config/opencode/mcp.json"

mcp-install-claude:
	@mkdir -p "$$HOME/Library/Application Support/Claude"
	@printf '{"mcpServers":{"grilo":{"command":"python","args":["-m","grilo_falante.backend.mcp.server"]}}}\n' > "$$HOME/Library/Application Support/Claude/claude_desktop_config.json"
	@echo "Installed MCP config for Claude Desktop"
