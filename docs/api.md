# API

The REST API is served by Django/DRF under the `/v1` prefix. An interactive
**Swagger UI** is available at `/api/docs` (schema at `/api/schema/`), and a
generated snapshot is committed at [`openapi.yaml`](openapi.yaml).

> The OpenAPI snapshot is best-effort: the endpoints use plain DRF `APIView`s,
> so the schema lists every path but does not fully describe request/response
> bodies. This page is the practical reference; `/api/docs` is authoritative at
> runtime.

## Base URL & versioning

```
https://<API_DOMAIN>/v1/...
```

## Authentication

| Use case | Header |
| --- | --- |
| Dashboard (browser) | `Authorization: Bearer <jwt-access-token>` |
| Programmatic clients | `Authorization: Api-Key <prefix.secret>` |

```bash
# Register, then log in to obtain JWTs
curl -X POST https://api.example.com/v1/auth/register \
  -H 'Content-Type: application/json' \
  -d '{"email":"you@example.com","password":"a-strong-password","full_name":"You"}'

curl -X POST https://api.example.com/v1/auth/login \
  -H 'Content-Type: application/json' \
  -d '{"email":"you@example.com","password":"a-strong-password"}'
# => {"access":"<jwt>","refresh":"<jwt>"}
```

## Conventions

- **Content type**: `application/json` (media is sent base64-encoded in JSON).
- **IDs**: UUID strings. **Timestamps**: ISO-8601 UTC.
- **Pagination**: list endpoints that paginate return
  `{ "results": [...], "pagination": { count, page, pages, page_size, next, previous } }`.
- **Idempotency**: `POST /v1/messages` accepts an `idempotency_key` to prevent
  duplicate sends on retries.
- **Rate limits**: per API key (configurable per key); auth endpoints are
  throttled. Exceeding a limit returns **429**.

## Error format

```json
{ "error": { "code": "validation_error", "message": "…", "details": { } } }
```

Common statuses: `400`, `401`, `403`, `404`, `409`, `429`, `5xx`.

---

## Endpoints

### Auth — `/v1/auth/`

| Method | Path | Description |
| --- | --- | --- |
| POST | `/register` | Create a user (+ default workspace) |
| POST | `/login` | Obtain JWT access + refresh |
| POST | `/refresh` | Refresh an access token |
| GET | `/me` | Current user + workspaces (JWT) |
| GET | `/whoami` | Active workspace (JWT **or** API key) |

### API Keys — `/v1/api-keys/` (dashboard / JWT only)

| Method | Path | Description |
| --- | --- | --- |
| GET | `/` | List keys (secret never returned) |
| POST | `/` | Create a key — returns the raw `key` **once** |
| POST | `/{id}/revoke` | Revoke a key |

```bash
curl -X POST https://api.example.com/v1/api-keys/ \
  -H "Authorization: Bearer $JWT" -H 'Content-Type: application/json' \
  -d '{"name":"Production"}'
# => { ..., "prefix":"ab12cd34", "key":"ab12cd34.<secret>" }   # copy the key now
```

### Devices — `/v1/devices/`

| Method | Path | Description |
| --- | --- | --- |
| GET | `/` | List devices |
| POST | `/` | Create a device + start a session (QR) |
| GET | `/{id}` | Device status |
| POST | `/{id}/logout` | Log out the WhatsApp session |
| DELETE | `/{id}` | Delete the device |
| GET | `/{id}/events?token=<jwt>` | **SSE** stream of QR + status |

```bash
curl -X POST https://api.example.com/v1/devices/ \
  -H "Authorization: Bearer $JWT" -H 'Content-Type: application/json' \
  -d '{"name":"Support line"}'

# Stream QR + status (SSE). The access token is passed as a query param
# because EventSource cannot send an Authorization header.
curl -N "https://api.example.com/v1/devices/$DEVICE_ID/events?token=$JWT"
```

### Messages — `/v1/messages/`

| Method | Path | Description |
| --- | --- | --- |
| GET | `/?device=&direction=&status=` | Paginated logs (filterable) |
| POST | `/` | Send a message (text or media) |
| GET | `/{id}` | Message detail |

```bash
# Text (works for individuals and groups — `to` may be a group JID)
curl -X POST https://api.example.com/v1/messages/ \
  -H "Authorization: Api-Key $API_KEY" -H 'Content-Type: application/json' \
  -d '{"device":"<device-id>","to":"15551234567","text":"Hello!","idempotency_key":"order-42"}'

# Media (base64)
curl -X POST https://api.example.com/v1/messages/ \
  -H "Authorization: Api-Key $API_KEY" -H 'Content-Type: application/json' \
  -d '{"device":"<device-id>","to":"15551234567","type":"media",
       "media":{"mime_type":"image/png","data_base64":"<base64>","filename":"a.png","caption":"hi"}}'
```

### Webhooks — `/v1/webhooks/`

| Method | Path | Description |
| --- | --- | --- |
| GET / POST | `/` | List / create (create returns the signing `secret`) |
| GET / PATCH / DELETE | `/{id}` | Retrieve / update / delete |
| GET | `/{id}/deliveries` | Paginated delivery log |

Deliveries POST `{"event": "<type>", "data": {…}}` to your URL with headers
`X-Signature` (HMAC-SHA256 of `"{X-Timestamp}." + body` using the webhook
secret), `X-Timestamp`, and `X-Webhook-Event`. Event currently emitted:
`message.received`.

### Scheduled messages — `/v1/scheduled-messages/`

| Method | Path | Description |
| --- | --- | --- |
| GET / POST | `/` | List / schedule (`run_at` must be future) |
| GET | `/{id}` | Detail |
| POST | `/{id}/cancel` | Cancel |

### Auto-reply rules — `/v1/auto-reply-rules/`

| Method | Path | Description |
| --- | --- | --- |
| GET / POST | `/` | List / create |
| GET / PATCH / DELETE | `/{id}` | Retrieve / update / delete |

`match_type` is one of `exact`, `contains`, `starts_with`, `regex`; rules are
evaluated by descending `priority` on each inbound message.

---

## Health

| Path | Description |
| --- | --- |
| `/health/` | Liveness (used by the container healthcheck) |
| `/health/ready/` | Readiness (checks the database) |
