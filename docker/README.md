# docker

Shared Docker build assets used by the per-service Dockerfiles. The build
context for every image is the **repository root**, so these scripts can be
`COPY`'d into any image.

> The per-service Dockerfiles live inside each service (`backend/Dockerfile`,
> `frontend/Dockerfile`, `wa-service/Dockerfile`); this folder holds the
> cross-cutting build-time pieces.

## Contents

```
docker/
└── entrypoints/
    └── api-entrypoint.sh   # waits for DB, runs migrate + collectstatic, then execs CMD
```

The `worker`/`beat` Celery containers reuse the backend image but override the
entrypoint (so they skip migrations). `wa-service` and `frontend` start directly
via their image `CMD`.

## Conventions

- Scripts are POSIX `sh`, LF line endings (enforced by `.gitattributes`).
- Containers run as **non-root** users.
- Container **healthchecks are defined inline** in `docker-compose.yml` and the
  Dockerfiles (no separate scripts needed).
- Entrypoints fail fast (`set -eu`) and wait for dependencies before starting.
