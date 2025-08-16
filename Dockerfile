# 🚀 AmiAgent FastAPI Application - Multi-stage build
FROM python:3.12-slim as base

# Set environment variables for Python optimization
ENV PYTHONUNBUFFERED=1 \
    PYTHONDONTWRITEBYTECODE=1 \
    PIP_NO_CACHE_DIR=1 \
    PIP_DISABLE_PIP_VERSION_CHECK=1 \
    UV_CACHE_DIR=/tmp/uv-cache

# ========================================
# PRODUCTION STAGE
# ========================================
FROM base as production

WORKDIR /app

# Install system dependencies (minimal for production)
RUN apt-get update && apt-get install -y --no-install-recommends \
    curl \
    && rm -rf /var/lib/apt/lists/* \
    && apt-get clean

# Install uv for fast Python package management
RUN pip install --no-cache-dir uv==0.4.30

# Copy dependency files first (for better layer caching)
COPY pyproject.toml uv.lock ./

# Install Python dependencies using uv (production only)
RUN uv sync --frozen --no-dev && \
    rm -rf /tmp/uv-cache

# Create non-root user early
RUN useradd --create-home --shell /bin/bash --uid 1000 app

# Create necessary directories with proper permissions
RUN mkdir -p logs storage/messages && \
    chown -R app:app /app

# Copy application code
COPY --chown=app:app . .

# Switch to non-root user
USER app

# ========================================
# DEVELOPMENT STAGE (optional)
# ========================================
FROM base as development

WORKDIR /app

# Install system dependencies (including dev tools)
RUN apt-get update && apt-get install -y --no-install-recommends \
    curl \
    build-essential \
    git \
    && rm -rf /var/lib/apt/lists/* \
    && apt-get clean

# Install uv for fast Python package management
RUN pip install --no-cache-dir uv==0.4.30

# Copy dependency files
COPY pyproject.toml uv.lock ./

# Install ALL dependencies (including dev)
RUN uv sync --frozen && \
    rm -rf /tmp/uv-cache

# Create non-root user
RUN useradd --create-home --shell /bin/bash --uid 1000 app

# Create necessary directories with proper permissions
RUN mkdir -p logs storage/messages && \
    chown -R app:app /app

# Copy application code
COPY --chown=app:app . .

# Switch to non-root user
USER app

# Expose port
EXPOSE 1912

# Development command (overridden in docker-compose)
CMD ["uv", "run", "uvicorn", "app.api.main:app", "--host", "0.0.0.0", "--port", "1912", "--reload"]

# ========================================
# FINAL PRODUCTION STAGE
# ========================================
FROM production as final

# Expose port
EXPOSE 1912

# Health check - optimized
HEALTHCHECK --interval=30s --timeout=10s --start-period=40s --retries=3 \
    CMD curl -f http://localhost:1912/health || exit 1

# Run the application
CMD ["uv", "run", "uvicorn", "app.api.main:app", "--host", "0.0.0.0", "--port", "1912", "--workers", "1"]
