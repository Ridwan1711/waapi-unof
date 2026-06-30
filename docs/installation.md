# Installation

This guide gets the full stack running. The **canonical runtime is Docker**
(on a server or via [Dokploy](dokploy.md)). For working on a single service
without the full stack, see [Development](development.md).

## Prerequisites

- A host with **Docker** + **Docker Compose** (your server or Dokploy node)
- Git
- (Local service dev only) **Node 22** and **Python 3.11**

## 1. Clone & configure

```bash
git clone https://github.com/your-org/waapi-unof.git
cd waapi-unof
cp .env.example .env
```

Edit `.env` and set, at minimum:

- `DJANGO_SECRET_KEY` and `INTERNAL_API_SECRET` (long random strings)
- `POSTGRES_PASSWORD` (and keep `DATABASE_URL` in sync)
- `FRONTEND_DOMAIN` / `API_DOMAIN` (your hostnames)
- `NEXT_PUBLIC_API_BASE_URL` (the public API URL)

> Generate secrets:
> `python -c "import secrets; print(secrets.token_urlsafe(64))"`

## 2. Start the stack (Phase 4+)

Once the Docker phase has landed:

```bash
docker compose up -d --build
docker compose ps
```

Services: `frontend`, `api` (Django), `worker` (Celery), `beat`, `wa-service`,
`postgres`, `redis`, and the reverse proxy.

## 3. Initialize the database

```bash
docker compose exec api python manage.py migrate
docker compose exec api python manage.py createsuperuser
```

## 4. First steps

1. Open the dashboard at your `FRONTEND_DOMAIN`.
2. Register / log in, then create a **Workspace**.
3. Generate an **API key**.
4. Create a **Device** and scan the **QR** code.
5. Send your first message via the API — see [API](api.md).

## Deploying to production

Use [Dokploy](dokploy.md) (recommended for this project) or the general
[Deployment](deployment.md) guide.
