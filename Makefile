.PHONY: help up down build backend frontend dev stop logs test lint format

help:
	@echo "AMI Makefile Commands:"
	@echo "  make up         - Start all services"
	@echo "  make down       - Stop all services"
	@echo "  make build      - Build images"
	@echo "  make backend    - Run backend locally"
	@echo "  make frontend   - Run frontend locally"
	@echo "  make dev        - Run both locally"
	@echo "  make stop       - Stop dev servers"
	@echo "  make logs       - View service logs"
	@echo "  make test       - Run tests"
	@echo "  make lint       - Lint code"
	@echo "  make format     - Format code"

up:
	docker-compose up -d

down:
	docker-compose down

build:
	docker-compose build

backend:
	cd backend && uv run uvicorn app.main:app --host 0.0.0.0 --port 11121 --reload

frontend:
	cd frontend && npm run dev

dev:
	(cd backend && uv run uvicorn app.main:app --host 0.0.0.0 --port 11121 --reload) & (cd frontend && npm run dev) & wait

stop:
	pkill -f "uvicorn|vite"

logs:
	docker-compose logs -f

test:
	uv run pytest tests/

lint:
	uv run ruff check backend/

format:
	uv run ruff format backend/
	@echo "  make db-seed            - Seed database with sample data"

