# Deploying with Dokploy

[Dokploy](https://dokploy.com) is a self-hostable PaaS built on Docker Swarm +
Traefik. This is the recommended deployment path for `waapi-unof`.

## Overview

We deploy the repo as a **Compose** application. Traefik (managed by Dokploy)
terminates TLS and routes traffic to the `frontend` and `api` services using the
labels in `docker-compose.yml`. All other services stay internal.

## Prerequisites

- A server with Dokploy installed
- DNS records for your domains (e.g. `app.example.com`, `api.example.com`)
  pointing at the server

## Steps

1. **Create a project** in Dokploy.
2. **Add a Compose service** and connect this Git repository (choose the branch
   and the `docker-compose.yml` at the repo root).
3. **Set environment variables** from [`.env.example`](../.env.example). At a
   minimum: secrets (`DJANGO_SECRET_KEY`, `INTERNAL_API_SECRET`,
   `POSTGRES_PASSWORD`), domains, and `NEXT_PUBLIC_API_BASE_URL`.
4. **Configure domains** for the `frontend` and `api` services so Dokploy/Traefik
   issues TLS certificates and routes them.
5. **Declare persistent volumes** so data survives redeploys:
   - `pgdata` → PostgreSQL
   - `wa-sessions` → WhatsApp session data (**critical** — losing this forces a
     re-scan of every device)
   - `media` → uploaded/received media (until you migrate to S3)
6. **Deploy.** Watch the build and container logs in Dokploy.
7. **Initialize the database** from the Dokploy terminal for the `api` service:

   ```bash
   python manage.py migrate
   python manage.py createsuperuser
   ```

## Scaling on Dokploy

- `api`, `worker`, `frontend` are stateless — increase replicas freely.
- `wa-service` is **stateful**: keep its session volume, and scale the pool
  deliberately (sessions are pinned per worker via the Redis registry). For
  larger scale, switch to **RemoteAuth** so sessions can move between workers.

## Updating

Push to the deployed branch (or trigger a redeploy in Dokploy). For zero-downtime
on stateless services, Dokploy performs rolling updates; coordinate `wa-service`
restarts since active sessions will reconnect.

## Tips

- Keep secrets in Dokploy's env settings — never commit `.env`.
- Back up the `pgdata` and `wa-sessions` volumes regularly.
- See [Troubleshooting](troubleshooting.md) for common deploy issues.
