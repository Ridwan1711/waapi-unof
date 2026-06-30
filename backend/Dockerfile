# syntax=docker/dockerfile:1
# =============================================================================
# Backend image (Django + DRF + Celery). Build context = repository root.
# Multi-stage: deps are built in a venv, copied into a slim non-root runtime.
# =============================================================================

FROM python:3.11-slim AS base
ENV PYTHONUNBUFFERED=1 \
    PYTHONDONTWRITEBYTECODE=1 \
    PIP_NO_CACHE_DIR=1 \
    PIP_DISABLE_PIP_VERSION_CHECK=1 \
    PATH="/opt/venv/bin:$PATH"
WORKDIR /app

# ---- builder: compile/install Python dependencies into /opt/venv -----------
FROM base AS builder
RUN apt-get update && apt-get install -y --no-install-recommends \
        build-essential libpq-dev \
    && rm -rf /var/lib/apt/lists/*
RUN python -m venv /opt/venv
COPY backend/requirements ./requirements
RUN pip install --upgrade pip && pip install -r requirements/prod.txt

# ---- final: slim runtime ----------------------------------------------------
FROM base AS final
RUN apt-get update && apt-get install -y --no-install-recommends \
        libpq5 curl \
    && rm -rf /var/lib/apt/lists/* \
    && groupadd --system app \
    && useradd --system --gid app --home-dir /app --shell /usr/sbin/nologin app
COPY --from=builder /opt/venv /opt/venv
COPY backend/ ./
COPY docker/entrypoints/api-entrypoint.sh /usr/local/bin/api-entrypoint.sh
RUN chmod +x /usr/local/bin/api-entrypoint.sh \
    && mkdir -p /data/media \
    && chown -R app:app /app /data
USER app
EXPOSE 8000
HEALTHCHECK --interval=30s --timeout=5s --start-period=40s --retries=3 \
    CMD curl -fsS http://localhost:8000/health/ || exit 1
ENTRYPOINT ["api-entrypoint.sh"]
CMD ["gunicorn", "config.asgi:application", \
     "-k", "uvicorn.workers.UvicornWorker", \
     "-b", "0.0.0.0:8000", "--workers", "3", "--timeout", "120"]
