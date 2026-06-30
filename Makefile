# =============================================================================
# waapi-unof — developer convenience commands
# -----------------------------------------------------------------------------
# These targets are intended to run on a host with Docker (your server / Dokploy
# shell) or for local per-service development. Run `make help` to list commands.
#
# NOTE: Docker is NOT run in the local dev environment of this repo's author;
# the compose-based targets are for the deployment server.
# =============================================================================

.DEFAULT_GOAL := help
COMPOSE := docker compose

# ---- Meta -------------------------------------------------------------------
.PHONY: help
help: ## Show this help
	@grep -hE '^[a-zA-Z_-]+:.*?## .*$$' $(MAKEFILE_LIST) \
		| sort \
		| awk 'BEGIN {FS = ":.*?## "}; {printf "  \033[36m%-22s\033[0m %s\n", $$1, $$2}'

.PHONY: env
env: ## Create .env from .env.example if missing
	@test -f .env || (cp .env.example .env && echo "Created .env — edit it before deploying")

# ---- Compose lifecycle (server / Dokploy shell) -----------------------------
.PHONY: build up down restart logs ps
build: ## Build all images
	$(COMPOSE) build

up: ## Start the full stack (detached)
	$(COMPOSE) up -d

down: ## Stop the stack
	$(COMPOSE) down

restart: ## Restart the stack
	$(COMPOSE) down && $(COMPOSE) up -d

logs: ## Tail logs for all services
	$(COMPOSE) logs -f --tail=200

ps: ## Show running services
	$(COMPOSE) ps

# ---- Backend (Django) -------------------------------------------------------
.PHONY: migrate makemigrations superuser shell-backend
migrate: ## Apply database migrations
	$(COMPOSE) exec api python manage.py migrate

makemigrations: ## Create new migrations
	$(COMPOSE) exec api python manage.py makemigrations

superuser: ## Create a Django superuser
	$(COMPOSE) exec api python manage.py createsuperuser

shell-backend: ## Open a shell in the api container
	$(COMPOSE) exec api bash

# ---- Quality ----------------------------------------------------------------
.PHONY: fmt lint test
fmt: ## Format all code (backend + frontend + wa-service)
	-cd backend && ruff format .
	-cd frontend && npm run format
	-cd wa-service && npm run format

lint: ## Lint all code
	-cd backend && ruff check .
	-cd frontend && npm run lint
	-cd wa-service && npm run lint

test: ## Run all test suites
	-cd backend && pytest
	-cd frontend && npm test
	-cd wa-service && npm test
