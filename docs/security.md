# Security Model

This document describes how `waapi-unof` protects users, data, and the platform.
For vulnerability reporting see [`../SECURITY.md`](../SECURITY.md).

## Authentication

Two distinct schemes for two distinct audiences:

| Scheme | Audience | Transport |
| --- | --- | --- |
| **JWT** (access + refresh) | Dashboard / browser users | `Authorization: Bearer <token>` |
| **API keys** | Programmatic REST clients | `Authorization: Api-Key <key>` |

### API keys

- Generated as `prefix.secret`; only the **hash** of the secret is stored.
- The **prefix** identifies the key for lookup and display (last-used, label).
- Keys carry **scopes** (e.g. `messages:send`, `devices:read`), a **per-key rate
  limit**, and a **revoked_at** timestamp for instant revocation.
- Raw keys are shown **once** at creation and never again.

## Authorization & multi-tenancy

- Every tenant-owned row carries a `workspace_id`.
- A base manager auto-scopes queries to the caller's workspace, preventing
  cross-tenant data access.
- Workspace **roles** (owner/admin/member) gate sensitive operations
  (team collaboration is future-ready).

## Internal service trust (Django ↔ Node)

- The Node WhatsApp service is **never publicly exposed**; it lives on the
  internal network only.
- Every Django ↔ Node request is **HMAC-signed** with `INTERNAL_API_SECRET`
  (timestamp + body), and verified on both sides to prevent forgery/replay.

## Webhooks

- Outgoing webhook deliveries include an HMAC **`X-Signature`** header so
  receivers can verify the payload came from the platform.
- Each webhook has its own secret; deliveries are retried with exponential
  backoff and recorded for auditing.

## Rate limiting & anti-ban

- DRF throttles + Redis token buckets protect the API from abuse.
- The Node service enforces **per-number send throttling** with human-like
  random delays (`WA_SEND_MIN_DELAY_MS`–`WA_SEND_MAX_DELAY_MS`) and a per-minute
  cap (`WA_SEND_RATE_PER_MIN`) to reduce the risk of WhatsApp bans.

## CSRF

- Django admin and any cookie-based flows keep CSRF protection enabled.
- The token/JWT REST API is **CSRF-exempt by design** because it is header-based
  (not cookie-based). This is intentional and documented to avoid confusion.

## Secrets management

- All secrets come from **environment variables**; `.env` is git-ignored and
  `.env.example` documents the contract.
- Secrets are **never logged**. Webhook/payload logs redact sensitive fields.
- On Dokploy, secrets are configured as service environment variables.

## Auditing

- Sensitive actions (key creation/revocation, device logout, webhook changes,
  membership changes) are written to an **audit log** with actor, action,
  target, IP, and timestamp.

## Transport security

- TLS terminates at Traefik (Dokploy) or Nginx.
- Strict CORS allow-lists the dashboard origin; Helmet sets secure headers on the
  Node service.
