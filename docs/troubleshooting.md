# Troubleshooting

Common problems and how to resolve them.

## QR code does not appear

- Confirm the `wa-service` container is running and reachable by `api`
  (`WA_SERVICE_INTERNAL_URL`).
- Check `wa-service` logs for Chromium/Puppeteer launch errors — missing system
  libraries are the usual cause.
- Verify the SSE connection from the dashboard to `api` is open (browser dev
  tools → Network → the events stream should stay pending/open).

## Device shows "disconnected" or session lost

- WhatsApp may have invalidated the session (logged out on the phone, or banned).
- Ensure the `wa-sessions` volume is persistent — losing it forces a re-scan.
- For multi-worker setups, confirm the device is registered to a live worker in
  the Redis registry.

## Number got banned

- Automated/bulk sending violates WhatsApp ToS. Reduce volume and rely on the
  built-in throttling (`WA_SEND_*` env vars). Warm up new numbers slowly. There
  is no guaranteed way to avoid bans.

## Webhook not received

- Check the **delivery log** for the webhook — it records attempts, response
  codes, and retry schedule.
- Ensure your endpoint returns **2xx** quickly; slow endpoints trigger retries.
- Verify the HMAC **`X-Signature`** using your webhook secret on your side.

## 401 / 403 from the API

- Dashboard calls need a valid **JWT** (`Authorization: Bearer …`).
- Programmatic calls need a valid **API key** (`Authorization: Api-Key …`) with
  the right scope, and the key must not be revoked.
- Confirm you are operating within the correct **workspace**.

## CORS / CSRF errors in the browser

- Add your dashboard origin to `DJANGO_CORS_ALLOWED_ORIGINS` and
  `DJANGO_CSRF_TRUSTED_ORIGINS`.
- Remember the token API is header-based; ensure the frontend sends the
  `Authorization` header, not cookies.

## Database connection errors

- Verify `DATABASE_URL` matches the `POSTGRES_*` values and that `postgres` is
  healthy (`docker compose ps`).
- Apply migrations: `docker compose exec api python manage.py migrate`.

## Build fails in CI

- CI auto-skips services that aren't scaffolded yet. If a service exists, ensure
  its lint/type/build scripts are defined and pass locally first.

## Still stuck?

Open a [bug report](https://github.com/your-org/waapi-unof/issues/new/choose)
with logs (secrets redacted) and your environment details.
