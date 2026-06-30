# Folder Structure

`waapi-unof` is a **monorepo**: one clone, unified docs, atomic cross-service
changes, and an easy onboarding path for contributors. This document maps the
full intended structure and explains the purpose of each part. Directories are
created as their phase lands; the tree below is the target.

## Top level

```
waapi-unof/
├── README.md                  # Project overview
├── LICENSE                    # MIT
├── CONTRIBUTING.md            # How to contribute
├── CODE_OF_CONDUCT.md         # Community standards
├── SECURITY.md                # Vulnerability reporting
├── CHANGELOG.md               # Keep a Changelog format
├── .gitignore .gitattributes .editorconfig .nvmrc
├── .env.example               # Environment contract (copy to .env)
├── Makefile                   # Developer convenience commands
├── docker-compose.yml         # (Phase 4) Dokploy-native stack, Traefik labels
├── .github/                   # CI + issue/PR templates
├── frontend/                  # Next.js dashboard (UI only)
├── backend/                   # Django + DRF API + Celery
├── wa-service/                # Node WhatsApp engine (WA only)
├── nginx/                     # Optional reverse-proxy profile
├── docker/                    # Build helpers, entrypoints, healthchecks
├── scripts/                   # Setup / seed / maintenance scripts
└── docs/                      # All documentation
```

## `frontend/` — Next.js dashboard

UI only. Talks exclusively to the Django API (JWT + SSE). Server Components by
default; Client Components only where interactivity requires it.

```
frontend/
└── src/
    ├── app/                   # App Router
    │   ├── (auth)/            # login, register (route group)
    │   └── (dashboard)/       # devices, messages, webhooks, scheduler,
    │                          # automation, api-keys, analytics, settings
    ├── components/ui/         # shadcn/ui primitives
    ├── features/              # feature-scoped components + hooks
    ├── lib/                   # api (axios), auth, react-query, utils
    ├── hooks/                 # shared React hooks
    ├── types/                 # shared TypeScript types
    └── styles/                # global styles / Tailwind layers
```

## `backend/` — Django + DRF + Celery

Owns all business logic, persistence, and orchestration. Follows the HackSoft
Django Styleguide: thin **views**, logic in **services** (writes) and
**selectors** (reads).

```
backend/
├── config/                    # project: settings/{base,dev,prod}, urls, asgi/wsgi, celery
├── apps/
│   ├── core/                  # base models, pagination, exceptions, permissions,
│   │                          # middleware, storage abstraction
│   ├── accounts/              # users + JWT auth
│   ├── workspaces/            # workspace, membership, roles (team-ready)
│   ├── apikeys/               # scoped, hashed API keys
│   ├── devices/               # WhatsApp sessions (via wa_gateway)
│   ├── messaging/             # messages + media
│   ├── webhooks/              # endpoints + deliveries
│   ├── scheduler/             # scheduled messages (Celery Beat)
│   ├── automation/            # auto-reply rules
│   ├── analytics/             # usage stats / rollups
│   ├── audit/                 # audit logs
│   ├── billing/               # future, clean stub
│   └── integrations/
│       └── wa_gateway/        # typed HTTP client to the Node service
├── manage.py
├── pyproject.toml
└── requirements/{base,dev,prod}.txt
```

**Per-app convention** (each Django app uses this layout):

```
<app>/
├── models.py        # data only
├── selectors.py     # read/query logic
├── services.py      # write/business logic
├── serializers.py   # DRF (de)serialization
├── views.py         # thin DRF views/viewsets
├── urls.py          # routing
├── permissions.py   # access control
├── tasks.py         # Celery tasks (if any)
└── tests/           # unit + integration tests
```

## `wa-service/` — Node WhatsApp engine

Does **nothing but WhatsApp**. Hides the engine behind a `WhatsAppProvider`
interface (whatsapp-web.js today, Baileys-ready).

```
wa-service/
└── src/
    ├── providers/             # WhatsAppProvider interface + wwebjs adapter (+ future baileys)
    ├── session/               # ProviderManager, registry, heartbeat
    ├── auth-store/            # Local + Remote (DB/S3) session persistence
    ├── events/                # EventBridge → Redis + Django callback
    ├── http/                  # express routes /internal/*, middleware (HMAC, helmet)
    ├── ws/                    # websocket to Django (not to the frontend)
    ├── config/                # env loading & validation
    ├── utils/                 # logging, errors, helpers
    └── index.ts               # entrypoint
```

## `nginx/` — optional reverse-proxy profile

For non-Dokploy hosts (Dokploy uses Traefik instead). Holds `nginx.conf` and
`conf.d/` server blocks for routing the frontend and API.

## `docker/` — build helpers

Entrypoint scripts, healthcheck scripts, and any shared Docker build assets used
by the per-service Dockerfiles.

## `scripts/` — automation scripts

Cross-platform helper scripts: environment setup, database seeding, backups, and
maintenance tasks.

## `docs/` — documentation

Every guide lives here (see [`docs/README.md`](README.md) for the index):
`architecture`, `folder-structure`, `installation`, `development`, `api`,
`security`, `deployment`, `docker`, `dokploy`, `troubleshooting`.
