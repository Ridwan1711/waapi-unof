# Docker

How the containerized stack is composed. The `docker-compose.yml` is added in
**Phase 4** and is **Dokploy-native** (Traefik labels on public services).

> The author develops on Windows and does **not** run Docker locally; the
> compose stack runs on the deployment server / Dokploy. Locally we only
> validate compose/config syntax.

## Services

| Service | Image source | Public? | Notes |
| --- | --- | --- | --- |
| `frontend` | `frontend/Dockerfile` | Yes (Traefik) | Next.js production build |
| `api` | `backend/Dockerfile` | Yes (Traefik) | Django + Gunicorn/Uvicorn |
| `worker` | `backend/Dockerfile` | No | Celery worker |
| `beat` | `backend/Dockerfile` | No | Celery Beat scheduler |
| `wa-service` | `wa-service/Dockerfile` | No | Node + Chromium; **stateful** |
| `postgres` | official `postgres` | No | Persistent volume |
| `redis` | official `redis` | No | Broker / cache / pub-sub |

## Volumes

| Volume | Used by | Purpose |
| --- | --- | --- |
| `pgdata` | `postgres` | Database files |
| `wa-sessions` | `wa-service` | WhatsApp session/auth data |
| `media` | `api`, `worker` | Uploaded/received media (local backend) |

## Networks

- `public` — proxy ↔ `frontend`, `api`
- `internal` — `api`/`worker`/`beat` ↔ `postgres`, `redis`, `wa-service`

The `wa-service` is attached to the internal network only and is never exposed
publicly.

## Configuration

All configuration is via environment variables (see [`.env.example`](../.env.example)).
On Dokploy, set them as the service's environment variables rather than shipping
a `.env` file.

## Common commands

```bash
docker compose up -d --build      # build & start
docker compose ps                 # status
docker compose logs -f api        # tail a service
docker compose exec api python manage.py migrate
docker compose down               # stop
```

## Image principles

- Multi-stage builds; small final images.
- Non-root runtime users.
- Healthchecks per service.
- Pinned base image versions for reproducibility.
