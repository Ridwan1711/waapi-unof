# API

The public REST API is served by Django/DRF under a versioned prefix. This page
covers conventions; the **interactive reference (OpenAPI/Swagger)** is generated
from the code and served at `/api/docs` once the backend lands (Phase 5+).

## Base URL & versioning

```
https://<API_DOMAIN>/v1/...
```

All public endpoints live under `/v1`. Breaking changes ship under a new version.

## Authentication

| Use case | Header |
| --- | --- |
| Dashboard (browser) | `Authorization: Bearer <jwt-access-token>` |
| Programmatic clients | `Authorization: Api-Key <prefix.secret>` |

- Obtain JWTs via the auth endpoints (login/refresh).
- Create API keys in the dashboard; the raw key is shown **once**. Keys are
  scoped (e.g. `messages:send`) and revocable.

## Conventions

- **Content type**: `application/json` (media uploads use `multipart/form-data`).
- **IDs**: opaque string identifiers.
- **Timestamps**: ISO-8601 UTC.
- **Pagination**: cursor/limit style, returning `results` + paging metadata.
- **Idempotency**: send-message endpoints accept an idempotency key to avoid
  duplicate sends on retries.

## Rate limiting

Requests are throttled per API key. When exceeded you receive **429** with a
`Retry-After` header. The WhatsApp layer additionally throttles per-number sends
to reduce ban risk.

## Error format

Errors use a consistent envelope:

```json
{
  "error": {
    "code": "validation_error",
    "message": "Human-readable summary.",
    "details": { "field": ["what went wrong"] }
  }
}
```

Common statuses: `400` validation, `401` unauthenticated, `403` forbidden,
`404` not found, `409` conflict, `429` rate-limited, `5xx` server.

## Resource overview (built across Phases 9–14)

| Area | Examples |
| --- | --- |
| Auth | register, login, refresh |
| Workspaces | create/list, members (future) |
| API keys | create, list, revoke |
| Devices | create, list, status, logout, QR (via SSE) |
| Messages | send text/media/location, list/logs |
| Webhooks | create, list, deliveries |
| Scheduler | schedule message, list, cancel |
| Automation | auto-reply rules CRUD |
| Analytics | usage & delivery stats |

Each resource's exact request/response shapes appear in the OpenAPI docs at
`/api/docs` as endpoints are implemented.
