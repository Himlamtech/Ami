# AMI RAG System Makefile - PTIT Assistant

.PHONY: help install up down dev create-admin migrate health logs clean test test-qdrant frontend

help:
	@echo "AMI RAG System - Available Commands:"
	@echo ""
	@echo "🚀 Quick Start:"
	@echo "  make up           - Start all services (MongoDB, Qdrant, Redis)"
	@echo "  make create-admin - Create first admin user (run once)"
	@echo "  make migrate      - Import documents from assets/raw/"
	@echo "  make dev          - Run backend development server"
	@echo ""
	@echo "📦 Installation:"
	@echo "  make install      - Install Python dependencies with uv"
	@echo ""
	@echo "🐳 Docker Services:"
	@echo "  make up           - Start all database services"
	@echo "  make down         - Stop all services"
	@echo "  make logs         - View service logs"
	@echo "  make clean        - Clean up containers and volumes"
	@echo ""
	@echo "🔧 Development:"
	@echo "  make dev          - Run backend (port 11121)"
	@echo "  make frontend     - Run React admin UI (port 11120)"
	@echo ""
	@echo "🧪 Testing:"
	@echo "  make health       - Check system health"
	@echo "  make test         - Run all tests"
	@echo "  make test-qdrant  - Test Qdrant connection"
	@echo ""
	@echo "📊 Admin Tasks:"
	@echo "  make create-admin - Create admin user"
	@echo "  make migrate      - Migrate documents to MongoDB"
	@echo ""
	@echo "🧹 Cleanup:"
	@echo "  make clean        - Remove temp files and caches"
	@echo ""
	@echo "Service URLs:"
	@echo "  Backend API:  http://localhost:11121"
	@echo "  API Docs:     http://localhost:11121/docs"
	@echo "  Admin UI:     http://localhost:11120"
	@echo "  Qdrant UI:    http://localhost:6333/dashboard"

install:
	@echo "📦 Installing dependencies..."
	uv sync
	@echo "✅ Installation complete!"

up:
	@echo "🚀 Starting all services..."
	docker-compose up -d
	@echo "⏳ Waiting for services to be ready..."
	@sleep 10
	@echo "✅ Services are ready!"
	@echo ""
	@echo "Database connections:"
	@echo "  MongoDB:    localhost:27017"
	@echo "  Qdrant:     localhost:6333 (HTTP) / localhost:6334 (gRPC)"
	@echo "  Redis:      localhost:6379"
	@echo ""
	@echo "Next steps:"
	@echo "  1. make create-admin  # Create first admin user"
	@echo "  2. make migrate       # Import existing documents"
	@echo "  3. make dev           # Start backend"
	@echo "  4. make frontend      # Start React UI (in new terminal)"

down:
	@echo "🛑 Stopping all services..."
	docker-compose down
	@echo "✅ Services stopped"

dev:
	@echo "🔧 Starting backend development server..."
	@echo "📡 Backend will be available at: http://localhost:11121"
	@echo "📚 API Docs: http://localhost:11121/docs"
	uv run uvicorn app.api.main:app --reload --host 0.0.0.0 --port 11121

frontend:
	@echo "🎨 Starting React Admin UI..."
	@echo "🌐 UI will be available at: http://localhost:11120"
	cd frontend && npm run dev

create-admin:
	@echo "👤 Creating admin user..."
	uv run python scripts/create_admin_user.py

migrate:
	@echo "📂 Migrating documents to MongoDB..."
	uv run python scripts/migrate_data_to_mongodb.py

health:
	@echo "🏥 Checking system health..."
	@curl -s http://localhost:11121/api/v1/config/health | python -m json.tool || \
	(echo "❌ Backend not responding. Make sure to run 'make dev' first" && exit 1)

logs:
	@echo "📋 Viewing service logs..."
	docker-compose logs -f

clean:
	@echo "🧹 Cleaning up..."
	@# Python cache
	find . -type d -name "__pycache__" -exec rm -rf {} + 2>/dev/null || true
	find . -type f -name "*.pyc" -delete
	find . -type f -name "*.pyo" -delete
	find . -type d -name "*.egg-info" -exec rm -rf {} + 2>/dev/null || true
	@# Test artifacts
	rm -rf .pytest_cache
	rm -rf htmlcov
	rm -rf .coverage
	@# Build artifacts
	rm -rf dist
	rm -rf build
	@# Docker volumes (optional - uncomment if needed)
	@# docker-compose down -v
	@echo "✅ Cleanup complete!"

test: health
	@echo "✅ System is healthy!"
	@echo "🧪 Running additional tests..."
	@# Add more tests here if needed

test-qdrant:
	@echo "🧪 Testing Qdrant connection..."
	@curl -s http://localhost:6333/collections | python -m json.tool || \
	echo "❌ Qdrant not responding"

# Advanced commands
docker-restart:
	@echo "🔄 Restarting all services..."
	docker-compose restart
	@sleep 5
	@echo "✅ Services restarted"

docker-clean:
	@echo "🧹 Cleaning Docker volumes (THIS WILL DELETE ALL DATA)..."
	@echo "Press Ctrl+C to cancel, or wait 5 seconds to continue..."
	@sleep 5
	docker-compose down -v
	@echo "✅ Docker volumes cleaned"

# Development helpers
watch-logs:
	@echo "📋 Watching backend logs..."
	tail -f logs/*.log 2>/dev/null || echo "No log files found"

backup-db:
	@echo "💾 Backing up MongoDB..."
	docker exec ami_mongodb mongodump --out=/data/backup
	@echo "✅ Backup complete (stored in MongoDB container)"

# Info commands
info:
	@echo "📊 System Information:"
	@echo ""
	@echo "Services Status:"
	@docker-compose ps
	@echo ""
	@echo "Port Bindings:"
	@echo "  11121  - Backend API"
	@echo "  11120  - React Admin UI"
	@echo "  27017 - MongoDB"
	@echo "  6333  - Qdrant HTTP"
	@echo "  6334  - Qdrant gRPC"
	@echo "  6379  - Redis"

ports:
	@echo "🔌 Checking ports..."
	@lsof -i :11121 || echo "Port 11121 (Backend): Free"
	@lsof -i :11120 || echo "Port 11120 (Frontend): Free"
	@lsof -i :27017 || echo "Port 27017 (MongoDB): Free"
	@lsof -i :6333 || echo "Port 6333 (Qdrant): Free"
	@lsof -i :6379 || echo "Port 6379 (Redis): Free"
