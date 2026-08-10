# Docker & Containerization - CHU-Platform

This document describes container orchestration, image build configs, volume mappings, and networking for CHU-Platform.

---

## 1. Docker Compose Services Overview (`docker-compose.yaml`)

```yaml
version: '3.8'

services:
  db:
    image: postgres:16-alpine
    container_name: chu-db
    environment:
      POSTGRES_USER: ${POSTGRES_USER:-postgres}
      POSTGRES_PASSWORD: ${POSTGRES_PASSWORD:-postgres}
      POSTGRES_DB: ${POSTGRES_DB:-chu_platform}
    ports:
      - "5432:5432"
    volumes:
      - postgres_data:/var/lib/postgresql/data
    healthcheck:
      test: ["CMD-SHELL", "pg_isready -U ${POSTGRES_USER:-postgres}"]
      interval: 5s
      timeout: 5s
      retries: 5

  api:
    build:
      context: .
      dockerfile: apps/api/Dockerfile
    container_name: chu-api
    ports:
      - "8000:8000"
    environment:
      - DATABASE_URL=postgresql+asyncpg://${POSTGRES_USER:-postgres}:${POSTGRES_PASSWORD:-postgres}@db:5432/${POSTGRES_DB:-chu_platform}
      - OPENAI_API_KEY=${OPENAI_API_KEY}
    volumes:
      - ./files:/app/files
    depends_on:
      db:
        condition: service_healthy

  web:
    build:
      context: apps/web
      dockerfile: Dockerfile
    container_name: chu-web
    ports:
      - "3000:3000"
    environment:
      - PUBLIC_API_URL=http://localhost:8000
    depends_on:
      - api

  nginx:
    image: nginx:alpine
    container_name: chu-nginx
    ports:
      - "80:80"
    volumes:
      - ./nginx/default.conf:/etc/nginx/conf.d/default.conf:ro
    depends_on:
      - web
      - api

volumes:
  postgres_data:
```

---

## 2. Dockerfile Breakdown

### 2.1 Backend API Dockerfile (`apps/api/Dockerfile`)
- Base image: `python:3.11-slim`
- Package manager: Uses `uv` for ultra-fast dependency resolution.
- Copy strategy: Copies root `pyproject.toml`, `uv.lock`, and `packages/` source tree to build the monorepo environment before starting Uvicorn.

### 2.2 Frontend Web Dockerfile (`apps/web/Dockerfile`)
- Base image: `node:20-alpine` (or `oven/bun:1`)
- Multi-stage build: First installs node dependencies and runs `vite build`, then launches Node server in production.

---

## 3. Container Management Commands

```bash
# Start all services in detached mode
docker-compose up -d --build

# View logs for API container
docker-compose logs -f api

# Stop and remove containers
docker-compose down

# Stop containers and erase postgres volume
docker-compose down -v
```
