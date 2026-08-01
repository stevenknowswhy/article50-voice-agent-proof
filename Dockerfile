# syntax=docker/dockerfile:1
ARG PYTHON_VERSION=3.14
FROM ghcr.io/astral-sh/uv:python${PYTHON_VERSION}-bookworm-slim AS base

ENV PYTHONUNBUFFERED=1
ENV UV_COMPILE_BYTECODE=1
WORKDIR /app

FROM base AS build
COPY pyproject.toml ./
RUN mkdir -p src && uv sync
RUN uv run --module livekit.agents download-files
COPY . .

FROM base
ARG UID=10001
RUN adduser --disabled-password --gecos "" --home /app --shell /sbin/nologin --uid "${UID}" appuser
COPY --from=build --chown=appuser:appuser /app /app
USER appuser
CMD ["uv", "run", "src/agent.py", "start"]
