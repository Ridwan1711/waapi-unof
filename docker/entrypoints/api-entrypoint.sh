#!/usr/bin/env sh
# -----------------------------------------------------------------------------
# Entrypoint for the Django `api` container.
# Waits for the database, applies migrations + collects static, then execs the
# given command (e.g. gunicorn). Used by the `api` service only; `worker`/`beat`
# override the entrypoint so they do NOT run migrations.
# -----------------------------------------------------------------------------
set -eu

echo "[api] Waiting for database to accept connections..."
python - <<'PY'
import os, socket, sys, time

host = os.environ.get("POSTGRES_HOST", "postgres")
port = int(os.environ.get("POSTGRES_PORT", "5432"))
for _ in range(60):
    try:
        with socket.create_connection((host, port), timeout=2):
            break
    except OSError:
        time.sleep(1)
else:
    print(f"[api] Database {host}:{port} not reachable after 60s", file=sys.stderr)
    sys.exit(1)
PY

echo "[api] Applying database migrations..."
python manage.py migrate --noinput

echo "[api] Collecting static files..."
python manage.py collectstatic --noinput

echo "[api] Starting process: $*"
exec "$@"
