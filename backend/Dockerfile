FROM python:3.12-slim

WORKDIR /code

# Install system dependencies
RUN apt-get update && apt-get install -y \
    build-essential cmake g++ gcc \
    libmagic1 \
    && rm -rf /var/lib/apt/lists/*

# Copy only dependency file first (for layer caching)
COPY pyproject.toml ./

# Install dependencies with BuildKit cache mount (speeds up rebuilds)
RUN --mount=type=cache,target=/root/.cache/pip \
    pip install -U pip setuptools wheel && \
    pip install -e .

# Copy application code LAST (only rebuilds this layer when code changes)
COPY backend/ ./backend/

ENV PYTHONPATH=/code:$PYTHONPATH
WORKDIR /code/backend

# Healthcheck
HEALTHCHECK --interval=30s --timeout=10s --start-period=40s --retries=3 \
    CMD python -c "import httpx; httpx.get('http://localhost:11121/health')" || exit 1

CMD ["uvicorn", "main:app", "--host", "0.0.0.0", "--port", "11121"]
