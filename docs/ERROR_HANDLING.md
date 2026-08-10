# Error Handling & Logging Specification - CHU-Platform

This document outlines exception handling patterns, HTTP error response formats, agent tool failure recoveries, and logging practices across CHU-Platform.

---

## 1. Standard HTTP Error Response Format

FastAPI endpoints return consistent JSON error objects when exceptions occur:

```json
{
  "detail": "Dataset with ID 4f8b2a1c-1234-5678-90ab-cdef12345678 not found."
}
```

Common status codes returned:
- `400 Bad Request`: Invalid file format, malformed JSON body, or corrupted CSV header.
- `404 Not Found`: Dataset, Conversation, or Artifact ID does not exist in PostgreSQL.
- `422 Unprocessable Entity`: Pydantic schema validation failures.
- `500 Internal Server Error`: Unhandled backend exception or database driver disconnection.

---

## 2. Real-Time Chat & SSE Error Handling

During SSE execution (`POST /api/chat/stream`), errors do not interrupt the HTTP connection with a 500 status code. Instead, an `error` SSE event is emitted:

```json
{
  "event": "error",
  "data": {
    "message": "DuckDB SQL Execution Error: Table 'dataset' has no column named 'unknown_col'",
    "code": "SQL_EXECUTION_ERROR"
  }
}
```

The frontend Svelte client listens for `error` events and presents inline warning toasts or retry prompts without breaking the chat thread state.

---

## 3. Agent Tool Fault Tolerance

When an LLM tool call fails (e.g. invalid DuckDB SQL query), the exception is caught by `packages/agents/data_analyst/nodes.py`.
The error trace is formatted into a tool output message and appended back into the agent conversation scratchpad. This allows the Planner node to inspect the error message and correct its SQL query on the subsequent iteration.
