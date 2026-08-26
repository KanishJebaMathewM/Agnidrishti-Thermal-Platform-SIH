# Deployment Guide

## Prerequisites

- Docker Engine with Compose v2.
- A built frontend in `dist/`.
- Backend and worker Dockerfiles supplied by the infrastructure contributor.
- A production `.env` file stored outside source control.

## Required environment

Set `POSTGRES_DB`, `POSTGRES_USER`, and `POSTGRES_PASSWORD`. Configure the application database URL, Redis URL, CORS origins, and any backend secrets in `.env`. Never place credentials in Compose files or frontend code.

## Production start

```bash
docker compose -f deployment/docker-compose.prod.yml config
docker compose -f deployment/docker-compose.prod.yml build
docker compose -f deployment/docker-compose.prod.yml up -d
```

PostgreSQL and Redis are only reachable on the internal Docker network. Nginx is the public entry point. It serves the SPA and proxies `/api/` to FastAPI.

## Verification

```bash
docker compose -f deployment/docker-compose.prod.yml ps
curl http://localhost/health
```

Review backend and worker logs before enabling operator workflows. A notification preview is safe to test; actual contact actions require an authorized human operator.

## Shutdown and rollback

```bash
docker compose -f deployment/docker-compose.prod.yml logs --tail=200 backend worker
docker compose -f deployment/docker-compose.prod.yml down
docker compose -f deployment/docker-compose.prod.yml up -d --no-build
```

Database volumes are persistent. Do not remove them during a routine rollback.
