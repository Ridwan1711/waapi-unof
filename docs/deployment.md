# Deployment

Production overview. For the recommended step-by-step path on this project, see
[Dokploy](dokploy.md). For compose internals, see [Docker](docker.md).

## Topology

```
Internet ──► Reverse proxy (Traefik on Dokploy / Nginx) ──► frontend + api
                                                            │
                          api ──► postgres, redis, wa-service (internal only)
                          worker + beat ──► redis, postgres, customer webhooks
```

- **Public** services: `frontend`, `api`. Everything else is internal-only.
- **Stateful** service: `wa-service` (WhatsApp sessions) — needs a persistent
  volume and careful placement (not freely replicated).
- **Stateless** services: `api`, `worker`, `beat`, `frontend` — scale by adding
  replicas.

## Pre-deploy checklist

- [ ] Strong `DJANGO_SECRET_KEY`, `INTERNAL_API_SECRET`, `POSTGRES_PASSWORD`
- [ ] `DJANGO_DEBUG=false`
- [ ] `DJANGO_ALLOWED_HOSTS`, `DJANGO_CSRF_TRUSTED_ORIGINS`, CORS origins set
- [ ] Domains point to the host; TLS configured at the proxy
- [ ] Persistent volumes for `postgres`, `redis` (if persisted), and
      `wa-service` session data
- [ ] Database migrations applied; superuser created
- [ ] Backups configured for PostgreSQL and session data

## Scaling notes

- Scale `api` / `worker` horizontally behind the proxy.
- Scale `wa-service` as a **worker pool**; sessions are pinned to a worker via the
  Redis registry. Use **RemoteAuth** (DB/S3) so sessions survive worker moves.
- At large scale, migrate storage to **S3** and consider the **Baileys** provider
  to cut per-session cost. See [architecture](architecture.md#scaling-roadmap).

## Backups & recovery

- **PostgreSQL**: scheduled `pg_dump` / managed snapshots.
- **Sessions**: back up the `wa-service` data volume (or the RemoteAuth store).
- **Media**: back up the media volume (or rely on S3 versioning once migrated).
