# syntax=docker/dockerfile:1
# Data Analyst API — FastAPI backend.
#
# Build context = repository root (see docker-compose.yaml):
#   docker build -f apps/api/Dockerfile .

FROM ghcr.io/astral-sh/uv:python3.12-bookworm-slim

WORKDIR /app

# --- Python / uv runtime settings ---
ENV UV_COMPILE_BYTECODE=1 \
    UV_LINK_MODE=copy \
    PYTHONUNBUFFERED=1 \
    PYTHONDONTWRITEBYTECODE=1 \
    PIP_NO_CACHE_DIR=1 \
    # Expose the root packages/ tree + the api package to imports.
    # (The project itself is not installed — see uv sync --no-install-project below —
    # so packages/ must be importable directly from source.)
    PYTHONPATH=/app/apps/api/src:/app/packages:/app

# --- Copy dependency manifests first (better layer caching) ---
COPY pyproject.toml uv.lock README.md ./
COPY apps/api/pyproject.toml apps/api/pyproject.toml

# --- Install runtime dependencies (before source, so code changes don't
#     trigger a full reinstall) ---
RUN uv sync --frozen --no-install-project --no-dev \
    && uv pip install --python /app/.venv/bin/python \
    alembic \
    openpyxl

# --- Copy source ---
COPY packages ./packages
COPY apps/api/src ./apps/api/src
COPY apps/api/alembic.ini ./apps/api/alembic.ini
COPY apps/api/alembic ./apps/api/alembic
# StaticFiles mounts these directories at import time, so they must exist
COPY apps/api/static ./apps/api/static
# charts/ is excluded from the build context (.dockerignore) and populated at
# runtime, but the StaticFiles mount needs the directory to exist at import.
RUN mkdir -p /app/apps/api/static/charts /app/apps/api/static/datasets

EXPOSE 10000

# Health endpoint is served at /health (see api/main.py)
HEALTHCHECK --interval=10s --timeout=5s --start-period=20s --retries=5 \
    CMD /app/.venv/bin/python -c \
    "import urllib.request,sys; sys.exit(0 if urllib.request.urlopen('http://127.0.0.1:10000/health', timeout=3).status==200 else 1)"

CMD [".venv/bin/uvicorn", "api.main:app", "--host", "0.0.0.0", "--port", "10000", "--workers", "1"]
