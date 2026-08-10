# REST & SSE API Documentation - CHU-Platform

Complete specification of all FastAPI REST endpoints and Server-Sent Event (SSE) channels defined in `apps/api/src/api/routers/`.

---

## 1. Overview & Base URL
- **Base URL**: `/api` (or `http://localhost:8000/api` when accessed directly)
- **Content-Type**: `application/json` (unless multipart upload or SSE stream)
- **OpenAPI / Swagger UI**: `http://localhost:8000/docs`

---

## 2. Router Endpoint Matrix

### 2.1 Datasets Endpoints (`src/api/routers/datasets.py`)

| Method | Endpoint | Description | Request Body | Response |
| :--- | :--- | :--- | :--- | :--- |
| `POST` | `/api/datasets/upload` | Upload a new raw dataset (.csv / .parquet) | `multipart/form-data` (file) | `DatasetResponse` |
| `GET` | `/api/datasets/` | List all datasets with column metadata | None | `List[DatasetResponse]` |
| `GET` | `/api/datasets/{id}` | Get detailed dataset schema & column profile | None | `DatasetResponse` |
| `GET` | `/api/datasets/{id}/preview` | Preview head rows of dataset | `limit: int = 50` (query param) | `DatasetPreviewResponse` |
| `PATCH` | `/api/datasets/{id}` | Update dataset name, description, or category | `DatasetUpdateSchema` | `DatasetResponse` |
| `DELETE` | `/api/datasets/{id}` | Delete dataset file & relational records | None | `{"message": "Dataset deleted"}` |

### 2.2 Conversations Endpoints (`src/api/routers/conversations.py`)

| Method | Endpoint | Description | Request Body | Response |
| :--- | :--- | :--- | :--- | :--- |
| `POST` | `/api/conversations/` | Create a new conversation thread | `ConversationCreateSchema` | `ConversationResponse` |
| `GET` | `/api/conversations/` | List all conversations | None | `List[ConversationResponse]` |
| `GET` | `/api/conversations/{id}` | Get conversation metadata & messages | None | `ConversationDetailResponse` |
| `DELETE` | `/api/conversations/{id}` | Delete a conversation and message history | None | `{"message": "Conversation deleted"}` |

### 2.3 Real-Time Chat & SSE Endpoint (`src/api/routers/chat.py`)

| Method | Endpoint | Description | Payload Format |
| :--- | :--- | :--- | :--- |
| `POST` | `/api/chat/stream` | Stream AI execution steps, SQL tool output, and response tokens | `ChatStreamRequest` (`conversation_id`, `prompt`) |
| **Response Format** | `text/event-stream` | Real-time Server-Sent Events stream yielding JSON payloads. |

#### SSE Event Payload Schema
```json
{
  "event": "token | step_start | tool_call | tool_result | artifact | error | done",
  "data": {
    "content": "Text token string",
    "step_name": "data_analyst_planner",
    "tool_name": "execute_duckdb_sql",
    "tool_input": {"sql": "SELECT age, COUNT(*) FROM dataset GROUP BY 1"},
    "artifact_id": "uuid-string-of-generated-chart"
  }
}
```

### 2.4 Artifacts Endpoints (`src/api/routers/artifacts.py`)

| Method | Endpoint | Description | Response |
| :--- | :--- | :--- | :--- |
| `GET` | `/api/artifacts/{id}` | Download/view an artifact payload (chart JSON or raw export) | `ArtifactDetailResponse` / File Download |
| `GET` | `/api/artifacts/conversation/{conversation_id}` | List all artifacts generated within a conversation thread | `List[ArtifactResponse]` |

### 2.5 Semantic Categories Endpoints (`src/api/routers/semantic_categories.py`)

| Method | Endpoint | Description | Request Body | Response |
| :--- | :--- | :--- | :--- | :--- |
| `GET` | `/api/semantic-categories/` | List semantic category tree | None | `List[CategoryResponse]` |
| `POST` | `/api/semantic-categories/` | Create a new category | `CategoryCreateSchema` | `CategoryResponse` |
| `PATCH` | `/api/semantic-categories/{id}` | Update category metadata | `CategoryUpdateSchema` | `CategoryResponse` |
| `DELETE` | `/api/semantic-categories/{id}` | Delete category tag | None | `204 No Content` |
