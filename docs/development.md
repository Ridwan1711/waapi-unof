# Development

How to develop each service locally. The full stack normally runs in Docker, but
you can run any single service natively against shared dependencies (PostgreSQL +
Redis).

> **Dependencies for local dev.** The backend needs PostgreSQL and Redis. You can
> point to instances running on your server (set `DATABASE_URL` / `REDIS_URL` in
> `.env`) or install them natively. The WhatsApp service additionally needs the
> system libraries Chromium requires (for `whatsapp-web.js`).

## Repository conventions

- **Conventional Commits** (`feat:`, `fix:`, `docs:`, …)
- Formatting/linting enforced in CI (see [CONTRIBUTING](../CONTRIBUTING.md))
- Line endings are **LF** (enforced via `.gitattributes`) — important on Windows

## Backend (Django + DRF)

```bash
cd backend
python -m venv .venv
# Windows:  .venv\Scripts\activate
# Unix:     source .venv/bin/activate
pip install -r requirements/dev.txt
python manage.py migrate
python manage.py runserver 0.0.0.0:8000
```

Quality:

```bash
ruff check .      # lint
black .           # format
mypy .            # types
pytest            # tests
```

Architecture rule: **no business logic in views**. Put writes in `services.py`,
reads in `selectors.py`.

## Frontend (Next.js)

```bash
cd frontend
npm install
npm run dev        # http://localhost:3000
```

Quality:

```bash
npm run lint
npm run build      # also type-checks
```

Set `NEXT_PUBLIC_API_BASE_URL` to your running API (e.g. `http://localhost:8000`).

## WhatsApp service (Node)

```bash
cd wa-service
npm install
npm run dev        # starts Express on WA_SERVICE_PORT (default 8090)
```

Quality:

```bash
npm run lint
npm run build      # tsc
```

Keep this service **WhatsApp-only**. New engines are added as adapters under
`src/providers/` — do not leak engine specifics outside the provider interface.

## Running pieces together

For an end-to-end loop locally you generally need: PostgreSQL, Redis, the Django
API, and the WA service. The frontend then points at the API. If that is too much
to run natively, deploy the stack to your server/Dokploy and develop against it.
