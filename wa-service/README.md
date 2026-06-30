# wa-service

The Node.js WhatsApp engine. This service does **nothing but WhatsApp**: it owns
sessions, QR generation, sending, receiving, and emitting events. It is internal
only — never exposed publicly — and is commanded by the Django API over an
HMAC-signed internal REST contract.

> Implemented in **Phase 7**. This README documents the intended layout.

## Stack

- Node.js 22 + TypeScript
- Express (internal REST) + `ws` (WebSocket to Django)
- `whatsapp-web.js` (default engine) — **Baileys-ready** via the provider interface
- Helmet, structured logging

## Provider abstraction (important)

The engine is hidden behind a `WhatsAppProvider` interface so it can be swapped
without touching Django or the frontend. `whatsapp-web.js` runs a headless
browser (heavy, ~300–600 MB/session); [Baileys](https://github.com/WhiskeySockets/Baileys)
is a future, much lighter WebSocket-based alternative. **Never leak engine
specifics outside `src/providers/`.**

## Structure

```
src/
├── providers/      # WhatsAppProvider interface + wwebjs adapter (+ future baileys)
├── session/        # ProviderManager, device→worker registry, heartbeats
├── auth-store/     # session persistence: Local (disk) | Remote (DB/S3)
├── events/         # EventBridge → Redis pub/sub + signed Django callback
├── http/           # express routes (/internal/*), middleware (HMAC, helmet)
├── ws/             # websocket channel to Django (not to the frontend)
├── config/         # env loading & validation
├── utils/          # logging, errors, helpers
└── index.ts        # entrypoint
```

## Internal contract (commanded by Django)

```
POST /internal/sessions            # init a device session
GET  /internal/devices/:id/status  # current status
POST /internal/devices/:id/send    # send text/media
POST /internal/devices/:id/logout  # log out / destroy session
```

Events posted back to Django (`/internal/events`): `qr`, `ready`,
`disconnected`, `message`.

## Develop

```bash
npm install
npm run dev     # Express on WA_SERVICE_PORT (default 8090)
npm run lint
npm run build   # tsc
```

Requires the system libraries Chromium needs when using `whatsapp-web.js`.
