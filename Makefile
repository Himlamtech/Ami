.PHONY: backend frontend dev stop

backend:
	cd backend && uv run uvicorn main:app --host 0.0.0.0 --port 11121 --reload

frontend:
	cd frontend && npm run dev

dev:
	(cd backend && uv run uvicorn main:app --host 0.0.0.0 --port 11121 --reload) & (cd frontend && npm run dev) & wait

stop:
	pkill -f "uvicorn|vite"

