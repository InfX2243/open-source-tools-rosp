# Multi-stage container build for DataGuard
FROM python:3.11-slim as base

ENV PYTHONUNBUFFERED=1 \
    PYTHONDONTWRITEBYTECODE=1 \
    PIP_NO_CACHE_DIR=1

WORKDIR /app

# Install system build dependencies
RUN apt-get update && apt-get install -y --no-install-recommends \
    build-essential \
    curl \
    && rm -rf /var/lib/apt/lists/*

# Install Python requirements
COPY pyproject.toml .
RUN pip install --upgrade pip && \
    pip install ".[all]"

# Copy source code and dashboard
COPY dataguard ./dataguard
COPY api ./api
COPY dashboard ./dashboard
COPY examples ./examples
COPY README.md .

# Install package in editable mode
RUN pip install -e .

EXPOSE 8000

# Default entrypoint starts API and Web Dashboard
CMD ["uvicorn", "api.app:app", "--host", "0.0.0.0", "--port", "8000"]
