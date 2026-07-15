# CHU Platform — API Documentation

Base URL: `http://localhost:10000/api/v1`

- [Configuration](#configuration)
- [Database models](#database-models)
- [Conversations CRUD](#conversations-crud)
- [Chat (SSE streaming)](#chat-sse-streaming)
- [Health](#health)
- [Full workflow example](#full-workflow-example)
- [Legacy endpoints (deprecated)](#legacy-endpoints-deprecated)

---

## Configuration

All settings are read from the root `.env` file via `pydantic-settings`.

| Variable | Default | Description |
|---|---|---|
| `HOST` | `0.0.0.0` | Server bind address |
| `PORT` | `10000` | Server port |
| `RELOAD` | `true` | Auto-reload on code changes |
| `DATABASE_URL` | `postgresql+asyncpg://postgres:postgres@localhost:5432/app` | PostgreSQL connection string |
| `CHARTS_DIR` | `static/charts` | Directory for generated charts (project-relative) |
| `OPENAI_BASE_URL` | `http://localhost:6060/v1` | LLM endpoint |
| `OPENAI_API_KEY` | `""` | LLM API key |
| `AGENT_MODEL` | `gpt-4o-mini` | Model name |
| `AGENT_TEMPERATURE` | `0.0` | LLM temperature |
| `AGENT_MAX_ITERATIONS` | `15` | Max agent reasoning steps |

---

## Database models

### `conversations`

| Column | Type | Notes |
|---|---|---|
| `id` | `UUID` (PK) | Auto-generated |
| `title` | `VARCHAR(255)` | Nullable; auto-titled from first message |
| `created_at` | `TIMESTAMPTZ` | Server default `now()` |
| `updated_at` | `TIMESTAMPTZ` | Auto-updated on change |

### `messages`

| Column | Type | Notes |
|---|---|---|
| `id` | `INTEGER` (PK) | Auto-increment |
| `conversation_id` | `UUID` (FK → conversations) | Indexed, cascading delete |
| `role` | `VARCHAR(16)` | `"user"` or `"assistant"` |
| `content` | `TEXT` | Message body |
| `created_at` | `TIMESTAMPTZ` | Server default `now()` |

---

## Conversations CRUD

### `GET /conversations` — List conversations

Returns all conversations, most recently updated first.

**Query parameters:**

| Param | Default | Description |
|---|---|---|
| `limit` | `50` | Max results |
| `offset` | `0` | Pagination offset |

**Response `200`:**

```json
[
  {
    "id": "c6cb9ca8-3e9d-48e9-bd5d-e9f20c117a36",
    "title": "Show me sales by category…",
    "created_at": "2026-07-15T12:00:00Z",
    "updated_at": "2026-07-15T12:05:00Z",
    "message_count": 4
  }
]
```

---

### `POST /conversations` — Create a conversation

**Request body:**

```json
{ "title": "Sales Q3 Analysis" }
```

`title` is optional — if omitted the conversation will be auto-titled after the first message.

**Response `201`:**

```json
{
  "id": "c6cb9ca8-3e9d-48e9-bd5d-e9f20c117a36",
  "title": "Sales Q3 Analysis",
  "created_at": "2026-07-15T12:00:00Z",
  "updated_at": "2026-07-15T12:00:00Z",
  "messages": []
}
```

---

### `GET /conversations/{id}` — Get a conversation

Returns the conversation with all its messages.

**Response `200`:**

```json
{
  "id": "c6cb9ca8-3e9d-48e9-bd5d-e9f20c117a36",
  "title": "Show me sales by category…",
  "created_at": "2026-07-15T12:00:00Z",
  "updated_at": "2026-07-15T12:05:00Z",
  "messages": [
    {
      "id": 1,
      "role": "user",
      "content": "Show me sales by category",
      "created_at": "2026-07-15T12:00:00Z"
    },
    {
      "id": 2,
      "role": "assistant",
      "content": "Here's a breakdown of sales by category...",
      "created_at": "2026-07-15T12:05:00Z"
    }
  ]
}
```

**Response `404`:**

```json
{ "detail": "Conversation not found" }
```

---

### `PATCH /conversations/{id}` — Update conversation title

**Request body:**

```json
{ "title": "Updated: Q3 Review" }
```

**Response `200`:** Same shape as `GET /conversations/{id}`.

---

### `DELETE /conversations/{id}` — Delete a conversation

Deletes the conversation **and all its messages** (cascading).

**Response `204`:** No content.

---

## Chat (SSE streaming)

### `POST /conversations/{id}/chat` — Send a message

Sends a message inside an existing conversation. The conversation's UUID is used as the agent's `thread_id`, so LangGraph state is preserved across messages.

**Both the user message and the complete assistant response are automatically saved to the `messages` table.**

If the conversation has no title, it's auto-generated from the first message (truncated to 80 chars).

**Request body:**

```json
{
  "message": "Show me sales by category",
  "dataset_path": "data/sales.csv"
}
```

`dataset_path` is optional — if provided it's prepended to the prompt as context.

**Response:** Server-Sent Events (SSE) stream.

```
event: thread_id
data: c6cb9ca8-3e9d-48e9-bd5d-e9f20c117a36

event: token
data: Here

event: token
data: 's a breakdown

event: token
data:  of sales by category...

event: image
data: /api/v1/charts/sales_by_category.png

event: done
data:
```

| Event | Data | Description |
|---|---|---|
| `thread_id` | UUID string | Emitted once at the start |
| `token` | Text string | A single token of the assistant response |
| `image` | URL path | A chart URL emitted when the agent generates a visualization |
| `done` | Empty | Signals the stream is complete |

**Errors:** Returns `404` if the conversation doesn't exist.

---

## Health

### `GET /health`

```json
{ "status": "ok" }
```

---

## Full workflow example

```bash
# 1. Start PostgreSQL
docker compose up -d postgres

# 2. Apply migrations
cd apps/api && uv run alembic upgrade head

# 3. Start the API
uv run --directory apps/api run.py

# 4. Create a conversation
CONV_ID=$(curl -s -X POST http://localhost:10000/api/v1/conversations \
  -H "Content-Type: application/json" \
  -d '{}' | jq -r '.id')

echo "Conversation ID: $CONV_ID"

# 5. Chat inside it (SSE stream)
curl -s -N -X POST "http://localhost:10000/api/v1/conversations/$CONV_ID/chat" \
  -H "Content-Type: application/json" \
  -d '{"message": "Show me sales by category"}'

# 6. List conversations
curl -s http://localhost:10000/api/v1/conversations | jq

# 7. View saved messages
curl -s "http://localhost:10000/api/v1/conversations/$CONV_ID" | jq '.messages'
```

---

## Legacy endpoints (deprecated)

These endpoints use in-memory session storage (no persistence). Prefer the conversation-based endpoints above.

| Method | Path | Description |
|---|---|---|
| `POST` | `/chat/new` | Create a new ephemeral session |
| `POST` | `/chat` | Send a message (in-memory, no DB persistence) |
| `GET` | `/chat/{thread_id}/history` | Get LangGraph state history |
| `DELETE` | `/chat/{thread_id}` | Delete an in-memory session |
