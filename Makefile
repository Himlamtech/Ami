# AMI System - Simple Makefile

.PHONY: help backend frontend stop

help:
	@echo "AMI System - Available Commands:"
	@echo ""
	@echo "  make backend   - Run FastAPI backend (port 11121)"
	@echo "  make frontend  - Run React frontend (port 11120)"
	@echo "  make stop      - Stop backend and frontend"
	@echo ""

backend:
	@echo "🚀 Starting FastAPI backend on port 11121..."
	@cd /home/iec/LamNH/Ami/AmiVer2 && .venv/bin/uvicorn app.main:app --host 0.0.0.0 --port 11121 --reload

frontend:
	@echo "🎨 Starting React frontend on port 11120..."
	@cd frontend && npm run dev

stop:
	@echo "🛑 Stopping backend and frontend..."
	@pkill -f "uvicorn app.main:app" || echo "Backend not running"
	@pkill -f "vite" || echo "Frontend not running"
	@echo "✅ Stopped"
