FROM python:3.10-slim AS base

COPY --from=ghcr.io/astral-sh/uv:latest /uv /uvx /bin/

WORKDIR /app

COPY pyproject.toml uv.lock .python-version ./

RUN uv sync --frozen --no-install-project --no-dev

COPY config.py main.py ./

COPY pipeline ./pipeline

RUN uv sync --frozen --no-dev


ENTRYPOINT ["uv", "run", "python", "main.py"]