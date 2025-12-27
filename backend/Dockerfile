FROM python:3.12-slim

WORKDIR /code

RUN apt-get update && apt-get install -y \
    build-essential cmake g++ gcc \
    && rm -rf /var/lib/apt/lists/*

COPY pyproject.toml ./

RUN --mount=type=cache,target=/root/.cache/pip \
    pip install -U pip setuptools wheel \
    && pip install -e .

COPY backend/ ./backend/

ENV PYTHONPATH=/code:$PYTHONPATH
WORKDIR /code/backend

CMD ["uvicorn", "main:app", "--host", "0.0.0.0", "--port", "11121"]
