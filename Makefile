backend:
	cd backend && uv run uvicorn app.main:app --host 0.0.0.0 --port 11121 --reload

frontend:
	cd frontend && npm run dev

dev:
	(cd backend && uv run uvicorn app.main:app --host 0.0.0.0 --port 11121 --reload) & (cd frontend && npm run dev) & wait

stop:
	pkill -f "uvicorn|vite"

