# Contributing to waapi-unof

First off — thank you! This project aims to be friendly to first-time
contributors. This guide explains how to set up, make changes, and submit them.

By participating, you agree to abide by our [Code of Conduct](CODE_OF_CONDUCT.md).

## Table of contents

- [Ways to contribute](#ways-to-contribute)
- [Project structure](#project-structure)
- [Development setup](#development-setup)
- [Branching & commits](#branching--commits)
- [Code style](#code-style)
- [Tests](#tests)
- [Pull requests](#pull-requests)

## Ways to contribute

- Report bugs (use the bug report issue template)
- Propose features (use the feature request template)
- Improve documentation under `docs/`
- Submit code via pull requests

## Project structure

This is a **monorepo** with three independently deployable services:

- `frontend/` — Next.js dashboard (UI only)
- `backend/` — Django + DRF API and Celery workers (business logic)
- `wa-service/` — Node WhatsApp engine (WhatsApp only)

See [`docs/folder-structure.md`](docs/folder-structure.md) for the full map and
[`docs/development.md`](docs/development.md) for the local workflow.

## Development setup

```bash
git clone https://github.com/your-org/waapi-unof.git
cd waapi-unof
cp .env.example .env
```

Each service has its own README with run instructions:

- [`backend/README.md`](backend/README.md) — Python 3.11, Django
- [`frontend/README.md`](frontend/README.md) — Node 22, Next.js
- [`wa-service/README.md`](wa-service/README.md) — Node 22, Express

## Branching & commits

- Branch from `main` using a descriptive name:
  `feat/device-status`, `fix/webhook-retry`, `docs/architecture`.
- We use [**Conventional Commits**](https://www.conventionalcommits.org/):

```
feat(devices): add QR refresh endpoint
fix(webhooks): correct HMAC signature header
docs(readme): clarify Dokploy steps
chore(deps): bump next to latest
```

Common types: `feat`, `fix`, `docs`, `refactor`, `test`, `chore`, `ci`, `perf`.

## Code style

Formatting and linting are enforced in CI. Run them before pushing:

| Service | Tools |
| --- | --- |
| backend | `ruff` (lint + format) |
| frontend | `eslint`, `prettier`, `tsc --noEmit` |
| wa-service | `eslint`, `prettier`, `tsc --noEmit` |

Guiding principles (see also [`docs/architecture.md`](docs/architecture.md)):

- **No business logic in views/controllers.** Use services + selectors.
- Keep the Node service **WhatsApp-only**.
- Type everything. Handle errors explicitly. Validate all input.
- Comments explain **why**, not **what**.

## Tests

- backend: `pytest`
- frontend: React Testing Library
- wa-service: vitest/jest + contract tests against the Django API

Please add or update tests for any behavior change.

## Pull requests

1. Ensure lint, type-check, and tests pass locally.
2. Fill in the PR template (what/why/how-tested).
3. Keep PRs focused and reasonably small.
4. Link related issues (e.g., `Closes #123`).

A maintainer will review and may request changes. Thanks for contributing!
