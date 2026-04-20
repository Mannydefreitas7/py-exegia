FROM denoland/deno:latest AS deno

FROM python:3.13-slim

# Copy uv binary from official image
COPY --from=ghcr.io/astral-sh/uv:latest /uv /uvx /bin/

# Copy dotenvx binary from official image
COPY --from=dotenv/dotenvx:latest /usr/local/bin/dotenvx /usr/local/bin/dotenvx

# Copy Deno binary from official image
COPY --from=deno /usr/local/bin/deno /usr/local/bin/deno

ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1 \
    UV_COMPILE_BYTECODE=1 \
    UV_LINK_MODE=copy \
    UV_PYTHON_DOWNLOADS=0 \
    DENO_DIR=/deno-dir/ \
    DENO_NO_UPDATE_CHECK=1

WORKDIR /app

# Install system dependencies needed by Python packages
RUN apt-get update && apt-get install -y --no-install-recommends \
    gcc \
    g++ \
    libpq-dev \
    curl \
    && rm -rf /var/lib/apt/lists/*

# Install dependencies in a separate layer for caching.
# Bind-mount the workspace root and all member pyproject.toml files so they
# don't need to be copied yet, while still resolving the full workspace graph.
RUN --mount=type=cache,target=/root/.cache/uv \
    --mount=type=bind,source=uv.lock,target=uv.lock \
    --mount=type=bind,source=pyproject.toml,target=pyproject.toml \
    --mount=type=bind,source=packages/corpus/pyproject.toml,target=packages/corpus/pyproject.toml \
    --mount=type=bind,source=packages/graphql/pyproject.toml,target=packages/graphql/pyproject.toml \
    --mount=type=bind,source=packages/models/pyproject.toml,target=packages/models/pyproject.toml \
    --mount=type=bind,source=packages/routers/pyproject.toml,target=packages/routers/pyproject.toml \
    --mount=type=bind,source=packages/schemas/pyproject.toml,target=packages/schemas/pyproject.toml \
    --mount=type=bind,source=packages/storage/pyproject.toml,target=packages/storage/pyproject.toml \
    uv sync --locked --no-install-project --no-dev

# Copy workspace metadata and all source code
COPY pyproject.toml uv.lock deno.json alembic.ini ./
COPY packages/ ./packages/
COPY src/ ./src/

# Install the workspace (all members + root project, without dev deps)
RUN --mount=type=cache,target=/root/.cache/uv \
    uv sync --locked --no-dev

# Create directory for datasets
RUN mkdir -p /app/datasets && chmod 755 /app/datasets

# Create non-root user
RUN useradd -m -u 1000 appuser && chown -R appuser:appuser /app
USER appuser

# Place the project venv on PATH
ENV PATH="/app/.venv/bin:$PATH"

EXPOSE 8000

HEALTHCHECK --interval=30s --timeout=10s --start-period=40s --retries=3 \
    CMD curl -f http://localhost:8000/health || exit 1

CMD ["uvicorn", "src.main:app", "--host", "0.0.0.0", "--port", "8000", "--workers", "4"]
