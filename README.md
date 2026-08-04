# CHU Platform

AI-powered data analyst — chat with your datasets, generate charts, and persist conversations.

---

## Prerequisites

- Python 3.10+
- [uv](https://docs.astral.sh/uv/)
- Docker (for PostgreSQL)

## Quick start

```bash
# 1. Clone & enter
git clone <repo> && cd CHU-Platform

# 2. Environment
cp .env.example .env
# Edit .env — set OPENAI_API_KEY and DATABASE_URL if needed

# 3. Start PostgreSQL
docker compose up -d postgres

# 4. Install dependencies
uv sync
uv sync --directory apps/api

# 5. Apply database migrations
cd apps/api && uv run alembic upgrade head && cd ../..

# 6. Start the API
uv run --directory apps/api run.py
```

API runs at `http://localhost:10000`.

---

## Full stack with Docker (Nginx load balancer)

Run the entire platform — Postgres, PgAdmin, API, and web app — behind a single Nginx load balancer:

>  Full details in **[DOCKERISATION.md](DOCKERISATION.md)** — architecture,
> Dockerfiles, environment variables, scaling, persistence, and gotchas.

```bash
# 1. Edit .env — set OPENAI_API_KEY (and POSTGRES_* for different credentials)

# 2. Build & start everything
 docker compose up -d --build

# 3. Apply database migrations (once)
docker compose exec api alembic upgrade head
```

Everything is served from one origin:

| Service | URL |
|---|---|
| Web app | http://localhost (or `http://localhost:${NGINX_PORT}`) |
| API | http://localhost/api/v1 (load-balanced across `API_REPLICAS` instances) |
| PgAdmin | http://localhost/pgadmin (user: `${PGADMIN_EMAIL}`, pass: `${PGADMIN_PASSWORD}`) |

Uploaded datasets and generated charts live in `apps/api/static/datasets` and
`apps/api/static/charts`, which are bind-mounted into the API container so data
persists and is shared across scaled replicas.

### Scaling the API

Nginx round-robins across every instance in the `api` upstream. Scale out with:

```bash
docker compose up -d --scale api=3
```

The default is `API_REPLICAS=1` in `.env`. Conversation/checkpoint state lives in Postgres, so any instance can serve any request.

---

## Project structure

```
apps/
  api/           # FastAPI backend (routers, models, schemas)
  web/           # Svelte frontend
nginx/           # Nginx load balancer / reverse proxy config
packages/
  agents/        # Data analyst agent definition
  ai/            # LangGraph agent framework
  analysis/      # Chart rendering (matplotlib)
  tools/         # LangChain tools (inspection, stats, viz)
```

## API endpoints

See `apps/api/API.md` for full docs.

| Method | Path | Description |
|---|---|---|
| `GET` | `/health` | Health check |
| `POST` | `/api/v1/conversations` | Create conversation |
| `GET` | `/api/v1/conversations` | List conversations |
| `GET` | `/api/v1/conversations/{id}` | Get conversation + messages |
| `PATCH` | `/api/v1/conversations/{id}` | Update title |
| `DELETE` | `/api/v1/conversations/{id}` | Delete conversation |
| `POST` | `/api/v1/conversations/{id}/chat` | Send message (SSE stream) |
| `GET` | `/api/v1/charts/{filename}` | Served chart PNG |

## Chat example

```bash
# Create a conversation
CID=$(curl -s -X POST http://localhost:10000/api/v1/conversations \
  -H "Content-Type: application/json" -d '{}' | jq -r '.id')

# Send a message (SSE stream)
curl -s -N -X POST "http://localhost:10000/api/v1/conversations/$CID/chat" \
  -H "Content-Type: application/json" \
  -d '{"message": "Show me sales by category", "dataset_path": "data/sales.csv"}'

# View saved messages
curl -s "http://localhost:10000/api/v1/conversations/$CID" | jq '.messages'
```

## Environment variables

See `.env.example` for all options. Key ones:

| Variable | Default | Description |
|---|---|---|
| `DATABASE_URL` | `postgresql+asyncpg://postgres:postgres@localhost:5432/app` | PostgreSQL |
| `OPENAI_BASE_URL` | `http://localhost:6060/v1` | LLM endpoint |
| `OPENAI_API_KEY` | — | LLM API key |
| `CHARTS_DIR` | `static/charts` | Chart output directory |
| `PORT` | `10000` | API port |

## Migrations

```bash
cd apps/api
uv run alembic upgrade head      # Apply
uv run alembic revision --autogenerate -m "desc"  # Create new
uv run alembic downgrade -1      # Rollback
```
