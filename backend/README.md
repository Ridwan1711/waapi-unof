# backend

The Django + DRF API and Celery workers. This service owns **all business logic,
persistence, and orchestration**. It is the only service the frontend talks to,
and the only service that commands the Node WhatsApp service.

> Implemented starting in **Phase 5**. This README documents the intended layout.

## Stack

- Django + Django REST Framework
- JWT authentication + API keys
- PostgreSQL, Redis
- Celery + Celery Beat (async jobs, scheduling)

## Architecture rules

Follows the [HackSoft Django Styleguide](https://github.com/HackSoftware/Django-Styleguide):

- **Thin views.** No business logic in views/viewsets.
- **Services** hold write/business logic (`services.py`).
- **Selectors** hold read/query logic (`selectors.py`).
- **Models** hold data + invariants only.
- Validation in serializers; access control in `permissions.py`.

## Structure

```
config/                 # settings/{base,dev,prod}, urls, asgi/wsgi, celery
apps/
├── core/               # base models, pagination, exceptions, permissions,
│                       # middleware, storage abstraction
├── accounts/           # users + JWT auth
├── workspaces/         # workspace, membership, roles
├── apikeys/            # scoped, hashed API keys
├── devices/            # WhatsApp sessions (via integrations/wa_gateway)
├── messaging/          # messages + media
├── webhooks/           # endpoints + deliveries
├── scheduler/          # scheduled messages (Celery Beat)
├── automation/         # auto-reply rules
├── analytics/          # usage stats
├── audit/              # audit logs
├── billing/            # future, stub
└── integrations/
    └── wa_gateway/     # typed HTTP client to the Node service (HMAC-signed)
requirements/{base,dev,prod}.txt
```

## Develop

```bash
python -m venv .venv && source .venv/bin/activate   # or .venv\Scripts\activate on Windows
pip install -r requirements/dev.txt
python manage.py migrate
python manage.py runserver 0.0.0.0:8000
```

Quality: `ruff check .`, `black .`, `mypy .`, `pytest`. See
[`../docs/development.md`](../docs/development.md).
