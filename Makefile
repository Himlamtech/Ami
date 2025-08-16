# Install development dependencies once
install-dev:
	uv add --dev mypy black ruff

# Main clean target that uses pre-installed dependencies
clean:
	uv run ruff check . --fix
	uv run ruff format .
	uv run black . --check
	uv run mypy . --install-types --non-interactive

# Complete setup and clean in one command
setup-and-clean: install-dev clean

# === DOCKER COMMANDS ===

# Build and start all services
docker-up:
	docker compose up --build -d

# Start with development tools (pgAdmin, Redis Commander)
docker-up-tools:
	docker compose --profile tools up --build -d

# Start in development mode with hot reload
docker-dev:
	docker compose -f docker compose.yml -f docker compose.dev.yml up --build -d

# Stop all services
docker-down:
	docker compose down

# View application logs
docker-logs:
	docker compose logs -f amiagent

# Check service status and health
docker-status:
	@echo "=== Service Status ==="
	docker compose ps
	@echo "\n=== Health Check ==="
	@curl -s http://localhost:1912/health 2>/dev/null || echo "❌ API not healthy"
	@echo "\n=== Database Status ==="
	@docker compose exec -T postgres pg_isready -U rag -d ragdb 2>/dev/null || echo "❌ Database not ready"

# Restart services
docker-restart: docker-down docker-up

# Clean up containers and volumes (DESTRUCTIVE!)
docker-clean:
	docker compose down -v --remove-orphans
	docker system prune -f

# Initialize environment for Docker
docker-init:
	@if [ ! -f .env ]; then \
		echo "Creating .env from .env.example..."; \
		cp .env.example .env; \
		echo "⚠️  Please update .env with your configuration"; \
	fi
	@mkdir -p storage/messages logs
	@echo "✅ Docker environment initialized"

# Complete Docker setup
docker-setup: docker-init docker-up docker-status

# === TESTING WITH DOCKER ===

# Test API endpoints
docker-test-api:
	@echo "Testing health endpoint..."
	@curl -s http://localhost:1912/health | jq '.'
	@echo "\nTesting chat endpoint..."
	@curl -s -X POST "http://localhost:1912/api/v1/chat/" \
		-H "Content-Type: application/json" \
		-d '{"message": "Hello Docker!", "model": "gpt-5-nano"}' | jq '.'

# Run tests inside container
docker-test:
	docker compose exec amiagent uv run pytest tests/ -v

# === HELP ===

help:
	@echo "Available targets:"
	@echo "  Development:"
	@echo "    install-dev    - Install development dependencies"
	@echo "    clean          - Run linting and formatting"
	@echo "    setup-and-clean - Complete development setup"
	@echo ""
	@echo "  Docker - Core:"
	@echo "    docker-setup   - Complete Docker setup (init + up + status)"
	@echo "    docker-up      - Build and start services"
	@echo "    docker-down    - Stop services"
	@echo "    docker-restart - Restart services"
	@echo "    docker-status  - Check service status"
	@echo "    docker-logs    - View application logs"
	@echo ""
	@echo "  Docker - Development:"
	@echo "    docker-dev     - Start in development mode"
	@echo "    docker-up-tools - Start with development tools"
	@echo "    docker-test-api - Test API endpoints"
	@echo "    docker-test    - Run tests in container"
	@echo ""
	@echo "  Docker - Maintenance:"
	@echo "    docker-init    - Initialize environment"
	@echo "    docker-clean   - Clean up (DESTRUCTIVE!)"

.PHONY: install-dev clean setup-and-clean docker-up docker-up-tools docker-dev docker-down docker-logs docker-status docker-restart docker-clean docker-init docker-setup docker-test-api docker-test help
