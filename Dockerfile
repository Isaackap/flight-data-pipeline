ARG PYTHON_VERSION=3.12.9
FROM python:${PYTHON_VERSION}-slim-bookworm

COPY --from=ghcr.io/astral-sh/uv:0.7.17 /uv /uvx /bin/

WORKDIR /app

# Copy dependency files first for better Docker caching
COPY pyproject.toml uv.lock* ./

# Install Python dependencies
RUN uv sync --frozen || uv sync

# Copy project files
COPY . .


EXPOSE 8000

CMD ["uv", "run", "src/main.py"]
