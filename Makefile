# RAG System Makefile

.PHONY: help install run dev test clean docker-up docker-down docker-logs docker-restart test-db crawl-stats crawl-dry crawl ingest-data test-api

help:
	@echo "AMI RAG System - Available Commands:"
	@echo ""
	@echo "Development:"
	@echo "  make install       - Install dependencies with uv"
	@echo "  make run           - Run application (production)"
	@echo "  make dev           - Run application (development mode)"
	@echo ""
	@echo "Database:"
	@echo "  make docker-up     - Start all databases (PostgreSQL, Redis, ChromaDB)"
	@echo "  make docker-down   - Stop all database containers"
	@echo "  make docker-logs   - View database container logs"
	@echo "  make docker-restart- Restart all database containers"
	@echo "  make test-db       - Test all database connections"
	@echo ""
	@echo "Data Crawling:"
	@echo "  make crawl-stats   - Show crawl statistics from CSV"
	@echo "  make crawl-dry     - Dry run crawl (show what would be crawled)"
	@echo "  make crawl         - Crawl data from URLs (requires FireCrawl setup)"
	@echo ""
	@echo "Data Ingestion:"
	@echo "  make ingest-data   - Ingest markdown files into vector database"
	@echo ""
	@echo "Testing:"
	@echo "  make test-api      - Run API tests"
	@echo ""
	@echo "Utilities:"
	@echo "  make clean         - Clean temporary files"

install:
	uv sync

run:
	uv run uvicorn app.api.main:app --host 0.0.0.0 --port 6000

dev:
	uv run uvicorn app.api.main:app --reload --host 0.0.0.0 --port 6000

docker-up:
	@echo "🚀 Starting database services..."
	docker-compose up -d
	@echo "⏳ Waiting for services to be ready..."
	@sleep 10
	@echo "✅ Services are ready!"
	@echo ""
	@echo "Database connections:"
	@echo "  PostgreSQL: localhost:5432"
	@echo "  Redis:      localhost:6379"
	@echo "  ChromaDB:   localhost:8000"

docker-down:
	@echo "🛑 Stopping database services..."
	docker-compose down
	@echo "✅ Services stopped"

docker-logs:
	docker-compose logs -f

docker-restart:
	@echo "🔄 Restarting database services..."
	docker-compose restart
	@sleep 5
	@echo "✅ Services restarted"

test-db:
	@echo "🧪 Testing database connections..."
	uv run python scripts/test_db_connections.py

crawl-stats:
	@echo "Analyzing data sheet..."
	uv run python scripts/crawl_data.py --stats

crawl-dry:
	@echo "Dry run - showing what would be crawled..."
	uv run python scripts/crawl_data.py --dry-run --limit 10

crawl:
	@echo "Starting data crawl..."
	@echo "Note: This requires FireCrawl API setup"
	uv run python scripts/crawl_with_firecrawl.py --limit 5

ingest-data:
	@echo "Ingesting documents into vector database..."
	uv run python scripts/ingest_data.py

test-api:
	@echo "Testing API endpoints..."
	uv run pytest tests/ -v

clean:
	find . -type d -name "__pycache__" -exec rm -rf {} + 2>/dev/null || true
	find . -type f -name "*.pyc" -delete
	find . -type f -name "*.pyo" -delete
	find . -type d -name "*.egg-info" -exec rm -rf {} + 2>/dev/null || true
	rm -rf .pytest_cache
	rm -rf htmlcov
	rm -rf dist
	rm -rf build
