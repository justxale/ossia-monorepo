FROM jrottenberg/ffmpeg:7.1-alpine AS ffmpeg
FROM python:3.12.2-slim AS base

LABEL authors="justxale"

FROM base AS builder

COPY --from=ghcr.io/astral-sh/uv:0.7.19 /uv /bin/uv
ENV UV_COMPILE_BYTECODE=1

WORKDIR /app

COPY uv.lock pyproject.toml /app/
RUN uv sync --frozen --no-dev --no-cache --group prod

COPY main.py zipper.py /app/
COPY ./pulsola /app/pulsola

FROM base
COPY --from=ffmpeg /bin/ffmpeg /usr/local/bin/
COPY --from=ffmpeg /bin/ffprobe /usr/local/bin/
COPY --from=ffmpeg /lib /lib
COPY --from=ffmpeg /share /share

COPY --from=builder /app /app
ENV PYTHONUNBUFFERED=1 PYTHONDONTWRITEBYTECODE=1 PATH="/app/.venv/bin:$PATH"
ENTRYPOINT ["python", "/app/main.py"]