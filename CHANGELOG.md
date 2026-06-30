# Changelog

All notable changes to this project are documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.1.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [Unreleased]

### Added
- Planning & architecture: full design, decisions, and roadmap (`docs/architecture.md`).
- Repository scaffolding: monorepo structure, OSS community health files, configuration.
- Docker/Dokploy infrastructure: `docker-compose.yml`, per-service Dockerfiles, optional Nginx profile.
- Backend (Django + DRF): split settings, custom email `User`, full data model + migrations, `/health`.
- Frontend (Next.js + Tailwind + shadcn-style UI): app shell, auth pages, dashboard.
- WhatsApp service (Node): `WhatsAppProvider` abstraction + whatsapp-web.js adapter, session manager.
- API communication: HMAC-signed Django ↔ Node channel (cross-language verified), event callback.
- Authentication: JWT (register/login/refresh/me) + scoped, hashed API keys with per-key rate limiting.
- QR login: device creation + SSE stream of QR/status.
- Device management: list/create/delete/logout + dashboard UI with live QR.
- Messaging API: send text/media (+ idempotency), inbound persistence, message logs.
- Webhooks: HMAC-signed delivery with exponential-backoff retries + delivery logs.
- Scheduler & auto-reply: scheduled sends (Celery `eta`) and a rules engine.
- Dashboard: all feature pages wired to the API.
- Testing: backend (pytest), wa-service (vitest), frontend (vitest + Testing Library); CI for all three.
- Documentation: API reference + cURL examples, OpenAPI export, and deployment guides.

[Unreleased]: https://github.com/Ridwan1711/waapi-unof/commits/main
