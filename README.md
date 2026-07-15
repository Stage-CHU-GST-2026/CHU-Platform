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

## Project structure

```
apps/
  api/           # FastAPI backend (routers, models, schemas)
  web/           # Svelte frontend
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
