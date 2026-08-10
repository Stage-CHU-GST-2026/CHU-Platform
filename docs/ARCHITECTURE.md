# System Architecture Documentation - CHU-Platform

## 1. Monorepo Organization & Architecture Strategy

CHU-Platform is structured as a **Python workspace monorepo** managed via [`uv`](https://github.com/astral-sh/uv) combined with multiple web clients.

```
/home/regisx001/CHU-Platform/
├── apps/
│   ├── api/             # FastAPI backend REST/SSE application
│   ├── ui/              # Svelte 5 component UI library / Storybook workspace
│   └── web/             # Primary SvelteKit 5 web application
├── packages/
│   ├── agents/          # LangGraph AI agent definitions & orchestrators
│   ├── analysis/        # Statistical computation & chart rendering engines
│   └── tools/           # DuckDB, data inspection, cleaning, & visualization tools
├── web-2/               # Legacy frontend application (Svelte 4 / Vite)
├── nginx/               # Nginx reverse proxy configuration
├── files/               # Storage directory for uploaded datasets and exports
└── docs/                # Comprehensive documentation suite
```

---

## 2. Component Subsystems

### 2.1 Backend API (`apps/api`)
- **FastAPI Application**: Configured in `src/api/main.py` using lifespan context managers for async database initialization.
- **Router Layer**: Modular endpoints under `src/api/routers/`:
  - `datasets.py`: Upload, profile, preview, update, list datasets.
  - `conversations.py`: Thread management, message history, agent invocations.
  - `chat.py`: SSE real-time chat execution pipeline.
  - `artifacts.py`: Retrieval and streaming of generated static chart files and data exports.
  - `semantic_categories.py`: Category hierarchy and tagging management.
- **Service Layer**: Business logic isolation in `src/api/services/` (`dataset_service.py`, `conversation_service.py`, `chat_service.py`).
- **Database & Models**: Async SQLAlchemy ORM definitions in `src/api/models/` using `asyncpg`.

### 2.2 AI Agent Subsystem (`packages/agents`)
- **Data Analyst Orchestrator**: `packages/agents/data_analyst/data_analyst_orchestrator.py` builds an execution state graph using `LangGraph`.
- **State Management**: Encapsulated in `packages/agents/data_analyst/state.py` keeping track of message history, execution steps, tool results, generated charts, and current plan.
- **Planner Node**: `data_analyst_planner.py` interprets complex user requests and decomposes them into executable tool calls.

### 2.3 Analytics & Tool Subsystems (`packages/analysis`, `packages/tools`)
- **DuckDB Engine**: Executes SQL queries directly against raw files using DuckDB connections managed in `packages/tools/duckdb_tools.py`.
- **Analysis Engine**: `packages/analysis/engine.py` provides high-performance data operations (aggregation, pivot tables, correlation matrices).
- **Visualization Engine**: `packages/analysis/charts.py` renders Plotly JSON configurations and static images for client-side display.

### 2.4 Frontend Subsystems (`apps/web` & `apps/ui`)
- **Primary Client (`apps/web`)**: Modern SvelteKit 5 web app using Runes (`$state`, `$derived`) and TailwindCSS. Handles real-time SSE stream processing, interactive chart rendering via Plotly, and dataset uploads.
- **Shared UI Library (`apps/ui`)**: Modular component library providing reusable primitives.

---

## 3. Communication Contracts

```
[SvelteKit Web Client] ---> (HTTP REST / SSE) ---> [Nginx :80] ---> [FastAPI :8000]
                                                                        |
                                                     +------------------+------------------+
                                                     |                                     |
                                        (Async SQLAlchemy ORM)                   (Python Function Invocations)
                                                     |                                     |
                                                     v                                     v
                                             [PostgreSQL :5432]                 [packages/agents & packages/tools]
                                                                                           |
                                                                                    (File I/O / In-Memory SQL)
                                                                                           |
                                                                                           v
                                                                                   [DuckDB Engine / files/]
```

---

## 4. Key Design Patterns
1. **Repository / Service Pattern**: Routers only handle HTTP concern; services handle database logic and agent calls.
2. **Event-Driven SSE Streaming**: Real-time feedback loop pushing JSON event frames (`step_start`, `tool_call`, `token`, `artifact`, `error`, `done`) over text/event-stream.
3. **In-Memory Query Offloading**: Relational metadata stored in PostgreSQL, while heavy analytical queries operate in-memory on raw file formats using DuckDB.
