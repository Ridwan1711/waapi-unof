# nginx

An **optional** reverse-proxy profile for hosts that don't use Dokploy. On
Dokploy, **Traefik** handles TLS and routing (via labels in
`docker-compose.yml`), so this directory is not used there.

> Config added in **Phase 4** (Docker infrastructure).

## When to use this

- Deploying to a plain VM/server without Dokploy/Traefik.
- Local production-like testing of the full stack behind one proxy.

## Intended layout

```
nginx/
├── nginx.conf      # top-level config
└── conf.d/         # server blocks: route / -> frontend, /v1 + /api -> api
```

## Responsibilities

- Terminate TLS.
- Route the dashboard (`frontend`) and API (`api`) by host/path.
- Pass through SSE correctly (disable buffering, long read timeouts).
- Never expose `wa-service`, `postgres`, or `redis`.
