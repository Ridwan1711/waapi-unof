# waapi-unof Documentation

Welcome to the documentation. Start here and follow the guide that matches what
you want to do.

## Guides

| Guide | Read this when you want to… |
| --- | --- |
| [Architecture](architecture.md) | Understand the system design and key decisions |
| [Folder structure](folder-structure.md) | Know where every file/dir lives and why |
| [Installation](installation.md) | Get the stack running for the first time |
| [Development](development.md) | Develop a single service locally |
| [API](api.md) | Use the REST API (auth, conventions, OpenAPI) |
| [Security](security.md) | Understand the security model |
| [Deployment](deployment.md) | Deploy to production |
| [Docker](docker.md) | Understand the compose services & volumes |
| [Dokploy](dokploy.md) | Deploy specifically with Dokploy |
| [Troubleshooting](troubleshooting.md) | Fix common problems |

## The 30-second mental model

```
Frontend (Next.js)  ──JWT/SSE──►  Django API (DRF)  ──signed REST──►  Node WA service  ──►  WhatsApp
                                        │                                   │
                                        ├── PostgreSQL (system of record)   └── Redis (events, registry)
                                        └── Celery (webhooks, schedules)
```

- The **frontend** only talks to **Django**.
- **Django** owns all business logic, data, and orchestration.
- The **Node service** does **nothing but WhatsApp**.
- Events (QR, inbound messages, status) flow back via **Redis → Django → SSE**.
