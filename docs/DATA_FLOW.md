# Data Flow Documentation - CHU-Platform

This document details the lifecycle of data within CHU-Platform across ingestion, query execution, streaming responses, chart rendering, state mutations, and export workflows.

---

## 1. Dataset Ingestion & Profiling Flow

```mermaid
sequenceDiagram
    autonumber
    actor User
    participant UI as SvelteKit Web App
    participant Router as datasets.py Router
    participant Service as dataset_service.py
    participant Storage as files/datasets/
    participant Profiler as packages/analysis/profiler.py
    participant DB as PostgreSQL DB

    User->>UI: Select & Upload File (CSV/Parquet)
    UI->>Router: POST /api/datasets/upload
    Router->>Service: process_upload(file)
    Service->>Storage: Write raw file to disk (UUID-based name)
    Service->>Profiler: Profile columns (data types, missing counts, statistics)
    Profiler-->>Service: Return column profiling metadata JSON
    Service->>DB: INSERT into datasets table
    Service->>DB: INSERT into dataset_columns table
    DB-->>Service: Confirm transaction commit
    Service-->>Router: Dataset DB object
    Router-->>UI: 201 Created (Dataset Response Schema)
```

---

## 2. Conversational Agent & SSE Execution Flow

```mermaid
sequenceDiagram
    autonumber
    actor User
    participant UI as SvelteKit Web App
    participant ChatRouter as chat.py Router
    participant Orchestrator as DataAnalystOrchestrator
    participant LLM as OpenAI Provider API
    participant DuckDB as DuckDB Query Engine
    participant DB as PostgreSQL DB

    User->>UI: Submit Natural Language Data Question
    UI->>ChatRouter: POST /api/chat/stream (SSE)
    ChatRouter->>DB: Create User Message record
    ChatRouter->>Orchestrator: run_stream(conversation_id, prompt)

    loop Event Generation Stream
        Orchestrator->>LLM: Send Prompt & Dataset Schema
        LLM-->>Orchestrator: Tool Execution Plan (e.g. execute_sql)
        Orchestrator->>UI: Stream Event `step_start` / `tool_call`
        Orchestrator->>DuckDB: Execute SQL on raw dataset file
        DuckDB-->>Orchestrator: DataFrame Result
        Orchestrator->>UI: Stream Event `tool_result`
        Orchestrator->>LLM: Send SQL Results for Interpretation
        LLM-->>Orchestrator: Text Answer & Chart Generation Spec
        Orchestrator->>UI: Stream Event `token` (Text chunk)
    end

    Orchestrator->>DB: Save Assistant Message & Created Artifacts
    Orchestrator->>UI: Stream Event `done`
```

---

## 3. Dynamic Chart Rendering & Artifact Storage

1. **Tool Invocations**: When the agent calls `packages/tools/visualization.py` or `packages/analysis/charts.py`, it constructs a chart spec (Plotly JSON format or Matplotlib figure).
2. **File Persistence**: Plotly specs are saved as JSON artifacts in `files/exports/` and logged in PostgreSQL's `artifacts` table with `artifact_type="chart"`.
3. **Client-Side Hydration**: The SSE stream yields an `artifact` event containing the artifact UUID. The web frontend fetches the artifact payload via `GET /api/artifacts/{id}` and hydrates interactive Plotly components directly in the chat panel.

---

## 4. State Mutations & Memory Persistence

- **Session Context**: Active dataset UUID and category context are bound to each `Conversation` record in PostgreSQL.
- **Agent Memory**: `packages/agents/data_analyst/memory.py` pulls past message history from the PostgreSQL `messages` table and feeds sliding-window context to the LLM during turn iterations.
