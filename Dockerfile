ARG PYTHON_VERSION=3.12

FROM python:${PYTHON_VERSION}-slim-bookworm AS builder

COPY --from=ghcr.io/astral-sh/uv:0.7.17 /uv /uvx /bin/

ENV UV_COMPILE_BYTECODE=1 \
    UV_LINK_MODE=copy

WORKDIR /app

# psycopg2 is compiled against libpq during dependency installation.
RUN apt-get update \
    && apt-get install --yes --no-install-recommends build-essential libpq-dev \
    && rm -rf /var/lib/apt/lists/*

COPY pyproject.toml uv.lock ./
RUN uv sync --frozen --no-dev --no-install-project


FROM python:${PYTHON_VERSION}-slim-bookworm AS runtime

ENV PATH="/app/.venv/bin:$PATH" \
    PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1

WORKDIR /app

# libpq is required by psycopg2 at runtime; ca-certificates is needed for the
# Google and SerpApi HTTPS requests.
RUN apt-get update \
    && apt-get install --yes --no-install-recommends ca-certificates libpq5 \
    && rm -rf /var/lib/apt/lists/* \
    && useradd --create-home --uid 10001 appuser \
    && mkdir -p /app/runtime-outputs \
    && chown appuser:appuser /app/runtime-outputs

COPY --from=builder /app/.venv /app/.venv
COPY --chown=appuser:appuser src ./src

USER appuser

# The pipeline is a one-shot job. Scheduling should be handled by systemd or
# cron on the VM with: docker compose run --rm app
CMD ["python", "src/main.py"]
