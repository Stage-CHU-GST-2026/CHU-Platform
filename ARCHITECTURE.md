# CHU Platform — Architecture Document

> **CHU Platform** is an AI-powered data analyst platform where users converse with datasets in natural language, generate statistical analyses and visualizations, and persist conversations. It follows a **modular monorepo** architecture with clearly separated concerns across backend, frontend, agent, analysis, and infrastructure layers.

---

## Table of Contents

1. [High-Level Architecture Overview](#1-high-level-architecture-overview)
2. [Project Structure](#2-project-structure)
3. [Backend — FastAPI (`apps/api/`)](#3-backend--fastapi-appsapi)
4. [Frontend — SvelteKit (`apps/web/`)](#4-frontend--sveltekit-appsweb)
5. [AI Agent System (`packages/`)](#5-ai-agent-system-packages)
6. [Analysis Engine (`packages/analysis/`)](#6-analysis-engine-packagesanalysis)
7. [Tool System (`packages/tools/`)](#7-tool-system-packagestools)
8. [Infrastructure](#8-infrastructure)
9. [Data Flow](#9-data-flow)
10. [Key Design Decisions](#10-key-design-decisions)

---

## 1. High-Level Architecture Overview

```
┌─────────────────────────────────────────────────────────┐
│                      Browser (User)                       │
│  ┌──────────────────────────────────────────────────┐   │
│  │          SvelteKit Frontend (apps/web/)           │   │
│  │  + Svelte 5 runes state management               │   │
│  │  + Tailwind CSS 4 / GitHub-dark design system     │   │
│  │  + SSE streaming for real-time chat               │   │
│  └──────────────┬───────────────────────────────────┘   │
└─────────────────┼───────────────────────────────────────┘
                  │ HTTP / SSE
                  ▼
┌─────────────────────────────────────────────────────────┐
│              FastAPI Backend (apps/api/)                  │
│  ┌──────────┐  ┌──────────┐  ┌──────────────────────┐   │
│  │ Chat API  │  │Conversa- │  │ Artifacts API        │   │
│  │ (SSE)     │  │tions API │  │ (files, charts)      │   │
│  └─────┬─────┘  └──────────┘  └──────────┬───────────┘   │
│        │                                  │               │
│  ┌─────┴──────────────────────────────────┴───────────┐  │
│  │           SessionManager + AgentService             │  │
│  │   (in-memory session registry, 1h TTL eviction)    │  │
│  └─────┬──────────────────────────────────────────────┘  │
│        │                                                  │
│  ┌─────┴──────┐  ┌──────────────┐  ┌──────────────────┐ │
│  │ PostgreSQL  │  │ AsyncSQLAlch.│  │ Static File      │ │
│  │ (via asyncpg)│  │ ORM models   │  │ Serving (charts) │ │
│  └─────────────┘  └──────────────┘  └──────────────────┘ │
└─────────────────────────────────────────────────────────┘
                        │
                        ▼
┌─────────────────────────────────────────────────────────┐
│                 AI Agent Layer (packages/)                │
│                                                          │
│  ┌──────────────────────────────────────────────────┐   │
│  │           LangGraph Orchestrator Workflow         │   │
│  │  ┌──────────┐   ┌──────────┐   ┌──────────────┐ │   │
│  │  │ Planner   │──▶│ Executor  │──▶│ Synthesizer  │ │   │
│  │  │ (generate │   │ (loop:   │   │ (final       │ │   │
│  │  │  plan)    │   │  steps)  │   │  report)     │ │   │
│  │  └──────────┘   └──────────┘   └──────────────┘ │   │
│  └──────────────────────────────────────────────────┘   │
│                                                          │
│  ┌────────────────────┐  ┌──────────────────────────┐  │
│  │ Generic AI Agent   │  │ Tool Registry (22 tools) │  │
│  │ (LangGraph-based)  │──│ inspection, stats, viz,  │  │
│  │                    │  │ cleaning, aggregation,    │  │
│  │                    │  │ relationships, planning  │  │
│  └────────────────────┘  └──────────────────────────┘  │
│                                                          │
│  ┌────────────────────┐  ┌──────────────────────────┐  │
│  │ AnalysisEngine     │  │ Chart Engine             │  │
│  │ (pandas, pure      │  │ (matplotlib/seaborn,     │  │
│  │  Python, no AI)    │  │  18 chart types)         │  │
│  └────────────────────┘  └──────────────────────────┘  │
└─────────────────────────────────────────────────────────┘
```

---

## 2. Project Structure

```
CHU-Platform/
├── apps/
│   ├── api/          # FastAPI backend server
│   ├── ui/           # Design system HTML + TypeScript chat client
│   └── web/          # SvelteKit frontend application
├── packages/
│   ├── agents/       # Data Analyst agent definition & orchestrator
│   ├── ai/           # Generic AI framework (LangGraph/LangChain)
│   ├── analysis/     # Pure-Python analysis engine (pandas, no AI deps)
│   └── tools/        # LangChain tool implementations (22 tools)
├── data/             # Sample datasets (CSV, Parquet, etc.)
├── docs/             # Documentation & evidence
├── static/charts/    # Generated chart PNG files
├── examples/         # Usage example scripts
├── notebooks/        # Jupyter notebooks
├── docker-compose.yaml   # PostgreSQL + pgAdmin
├── pyproject.toml    # Root workspace config (uv workspace)
└── README.md         # Project documentation
```

The project uses **uv** (Astral's package manager) for workspace management. Root `pyproject.toml` defines the workspace with `apps/api` as a member. All packages (`packages/ai`, `packages/analysis`, `packages/tools`, `packages/agents`) are importable from the root package `chu-platform`.

---

## 3. Backend — FastAPI (`apps/api/`)

### 3.1 Application Factory

The backend is a **FastAPI** application created via a factory pattern in `src/api/main.py`. The `create_app()` function assembles the application and registers routers.

**Lifespan events** (async context manager):

| Phase | Action |
|-------|--------|
| **Startup** | Creates charts directory, patches visualization tool's `CHARTS_DIR`, creates DB tables via SQLAlchemy `Base.metadata.create_all()`, initialises Postgres-based LangGraph checkpointer, injects it into the shared `SessionManager` |
| **Shutdown** | Closes Postgres checkpointer connection, disposes SQLAlchemy engine |

### 3.2 Configuration (`config.py`)

Uses `pydantic-settings.BaseSettings` with `.env` file support. Key settings:

| Setting | Default | Purpose |
|---------|---------|---------|
| `host` | `0.0.0.0` | Bind address |
| `port` | `10000` | Server port |
| `database_url` | `postgresql+asyncpg://postgres:postgres@localhost:5432/app` | PostgreSQL connection |
| `charts_dir` | `static/charts` | Chart output directory |
| `openai_base_url` | `http://localhost:6060/v1` | LLM endpoint (OpenAI-compatible) |
| `agent_model` | `gpt-4o-mini` | LLM model name |
| `agent_max_iterations` | `15` | Max agent tool-call iterations |

### 3.3 Database Layer (`database.py`)

- **Engine**: Async SQLAlchemy engine with `asyncpg` driver, connection pooling (pool size 5, max overflow 10).
- **Session**: `async_sessionmaker` producing `AsyncSession` instances with `expire_on_commit=False`.
- **Dependency**: `get_db()` — FastAPI dependency for per-request session management (commit on success, rollback on exception).

### 3.4 Data Models (`models/`)

| Model | Table | Key Fields | Relationships |
|-------|-------|------------|---------------|
| `Conversation` | `conversations` | `id` (UUID PK), `title`, `created_at`, `updated_at` | `messages` (cascade), `artifacts` (cascade) |
| `Message` | `messages` | `id` (auto-inc PK), `conversation_id` (UUID FK), `role`, `content`, `created_at` | Belongs to `Conversation` |
| `Artifact` | `artifacts` | `id` (UUID PK), `conversation_id` (UUID FK), `filename`, `filepath`, `mime_type`, `file_size`, `created_at` | Belongs to `Conversation` |

### 3.5 API Routers

All routers are mounted under the `/api/v1` prefix.

#### Conversations Router (`/api/v1/conversations`)

| Method | Path | Description |
|--------|------|-------------|
| `GET` | `/` | List conversations (paginated, with message/artifact counts) |
| `GET` | `/{id}` | Get conversation details (messages, optionally artifacts) |
| `POST` | `/` | Create new conversation |
| `PATCH` | `/{id}` | Update conversation title |
| `DELETE` | `/{id}` | Delete conversation |

#### Chat Router (`/api/v1/chat`)

| Method | Path | Description |
|--------|------|-------------|
| `POST` | `/new` | Create new chat session, returns `thread_id` |
| `POST` | `/` | Send message, returns **SSE stream** with events |
| `GET` | `/{thread_id}/history` | Get message history from LangGraph state |
| `DELETE` | `/{thread_id}` | Delete session |

#### Artifacts Router (`/api/v1/artifacts`)

| Method | Path | Description |
|--------|------|-------------|
| `GET` | `/` | List artifacts for a conversation |
| `GET` | `/{id}` | Get single artifact metadata |
| `GET` | `/{id}/file` | Serve the actual artifact file |

### 3.6 Services Layer

#### `AgentService` (`services/agent_service.py`)

Wraps the Data Analyst agent creation and the Orchestrator. Provides `stream()` which:
- Detects simple conversational queries (greetings, pleasantries, help) and uses a **fast path** (direct LLM streaming)
- Routes complex analytical queries through the **Orchestrator** (plan → execute → synthesize)
- Yields structured SSE events: `plan`, `step_started`, `step_update`, `step_finished`, `token`, `image`, `artifact`, `done`

#### `SessionManager` (`services/session.py`)

- In-memory dictionary mapping `thread_id` → `AgentService` instance
- **1-hour TTL eviction** of stale sessions
- Pluggable checkpointer backend (InMemory ↔ Postgres) injected during app lifespan
- Singleton `session_manager` shared across all routers

### 3.7 Alembic Migrations

- `0001_initial_models.py`: Creates `conversations` and `messages` tables
- `0002_add_artifacts_table.py`: Creates `artifacts` table

---

## 4. Frontend — SvelteKit (`apps/web/`)

### 4.1 Stack

| Technology | Purpose |
|------------|---------|
| **SvelteKit 5** | Full-stack framework with file-based routing |
| **Svelte 5** | Reactive UI with runes (`$state`, `$derived`, `$effect`) |
| **TypeScript 6.0** | Type-safe code |
| **Tailwind CSS 4.3** | Utility-first CSS with custom design tokens |
| **PaneForge** | Resizable panel layouts |
| **marked + DOMPurify** | Markdown rendering |
| **@tabler/icons-svelte** | Icon library |
| **Vite** | Build tool with API proxy (`/api` → `localhost:10000`) |

### 4.2 Routing Structure

```
src/routes/
├── +layout.svelte           # Root layout (imports CSS, renders children)
├── +page.svelte             # Root page → redirects to /dashboard
├── dashboard/
│   ├── +layout.svelte       # Dashboard layout (wraps in AppShell)
│   ├── +page.svelte         # Landing page with hero & chat composer
│   ├── new-chat/
│   │   └── +page.svelte     # "New Chat" page with suggestion buttons
│   └── conversation/
│       └── +page.svelte     # Main conversation view with SSE streaming
```

### 4.3 App Shell (`AppShell.svelte`)

The UI is structured around a three-panel layout using `PaneForge`:

```
┌──────────┬──────────────────────────────────┬────────────┐
│ Sidebar  │                                  │ Artifact   │
│ (260px)  │   TopBar                         │ Panel      │
│          │                                  │ (optional) │
│  - New   │   Main Content Area               │            │
│  Chat    │   (Chat messages / composer)      │ Charts &   │
│  - Conv1 │                                  │ files      │
│  - Conv2 │                                  │            │
│  ...     │                                  │            │
└──────────┴──────────────────────────────────┴────────────┘
```

The artifact panel only appears during active conversations when artifacts are present. Layout auto-saves state via `autoSaveId="app-layout"`.

### 4.4 State Management

Uses **Svelte 5 runes** (`$state`, `$derived`) for reactive state across the application:

| Store | Purpose |
|-------|---------|
| `app.svelte.ts` | Global app state (sidebar collapse, artifact panel visibility) |
| `conversations.svelte.ts` | Conversation list, active conversation, streaming state |
| `agents.svelte.ts` | Agent configuration state |
| `datasets.svelte.ts` | Available datasets state |
| `notifications.svelte.ts` | Toast/notification state |
| `settings.svelte.ts` | User settings state |

### 4.5 API Client (`lib/api/chat.ts`)

Full-featured API client handling:
- **CRUD operations** for conversations (list, create, get, update, delete)
- **SSE streaming** for chat messages — parses events: `token`, `artifact`, `plan`, `step_started`, `step_update`, `step_finished`, `done`
- **Artifact management** — list, fetch, serve files
- **Plan reconstruction** — fetches plan artifacts and reconstructs step progress

### 4.6 Design System

Custom design tokens defined in `src/lib/css/tokens.css` via Tailwind's `@theme` directive:

- **Colors**: GitHub-dark-inspired palette (`--color-bg: #0d1117`, `--color-canvas: #161b22`, `--color-sidebar: #010409`, `--color-accent: #2f81f7`)
- **Spacing**: 8-pt rhythm (0–96px)
- **Type scale**: 10px–18px with Inter (sans) and JetBrains Mono (mono) fonts
- **Theme support**: Dark mode by default, with light mode support via `@media (prefers-color-scheme: light)` and `.light`/`.dark` class overrides

---

## 5. AI Agent System (`packages/`)

### 5.1 Generic AI Framework (`packages/ai/`)

A **generic, reusable AI agent framework** based on LangGraph. It knows nothing about datasets, CSV files, or analysis — it only knows how to call an LLM, execute tools, and maintain state.

```
┌──────────────────────────────────────────────────┐
│                 LangGraph Workflow                │
│                                                   │
│  START ──▶ agent (LLM) ──▶ tools (ToolNode)      │
│               │                   │               │
│               │         ┌─────────┘               │
│               ▼         ▼                         │
│           summarize (memory) ──▶ END               │
└──────────────────────────────────────────────────┘
```

**Key Components:**

| Component | File | Responsibility |
|-----------|------|----------------|
| `Agent` | `agent.py` | High-level API: `run()`, `astream()`, `get_memory()`, `get_full_state()` |
| `build_graph()` | `graph.py` | Constructs LangGraph with agent → tools → summarize nodes |
| `AgentConfig` | `models/config.py` | Model settings (model name, base URL, temperature, max iterations) |
| `AgentState` | `state.py` | TypedDict with `messages`, `summary`, and orchestrator fields |
| `make_llm_node()` | `nodes/llm.py` | LLM node creation with tool binding and error handling |
| `make_tools_node()` | `nodes/tools.py` | ToolNode with error-safe wrappers |
| `make_summary_node()` | `nodes/memory.py` | Conversation summarization after each agent loop |
| `create_checkpointer()` | `memory/factory.py` | Factory for InMemory or Postgres checkpointers |
| `ToolProtocol` | `tool_protocol.py` | Runtime-checkable protocol for tool compliance |

### 5.2 Data Analyst Agent (`packages/agents/data_analyst/`)

Configured via `agent.yaml`:

```yaml
name: Data Analyst
model: meta-llama/llama-4-scout-17b-16e-instruct
temperature: 0
max_iterations: 15
```

The agent is created by `create_data_analyst()` which wires together the generic `Agent` framework with the Data Analyst-specific prompt (`prompt.md`) and the 22 registered tools.

#### The Orchestrator (`data_analyst_orchestrator.py`)

The **core architectural innovation** — a 3-phase LangGraph that coordinates the entire analytical workflow:

```
              ┌──────────┐
              │  START   │
              └────┬─────┘
                   │
                   ▼
              ┌──────────┐
              │ PLANNER   │  Phase 1: Generate execution plan
              │ Node      │  - Calls LLM with planner_prompt.md
              └────┬─────┘  - Parses JSON plan (PlanStep[])
              │     - Emits "plan" event
              │     - Creates run_id
              ▼
              ┌──────────┐
         ┌───▶│ EXECUTOR  │  Phase 2: Execute steps sequentially
         │    │ Node      │  - For each PlanStep:
         │    └────┬─────┘    - Builds step-specific instruction
         │         │          - Creates isolated LangGraph sub-thread
         │         │          - Streams tokens via "step_token" events
         │         │          - Detects ChartArtifacts in ToolMessages
         │         │          - Accumulates evidence + chart artifacts
         │         │
         │    ┌────▼─────┐
         │    │ More      │
         └────│ steps?    │
              │           │
              └────┬──────┘
                   │ No
                   ▼
              ┌──────────┐
              │SYNTHESIZER│  Phase 3: Generate final report
              │ Node      │  - Feeds all accumulated evidence
              └────┬─────┘  - Uses synthesis_prompt.md
                   │        - Research-paper style with evidence manifest
                   ▼
              ┌──────────┐
              │   END    │
              └──────────┘
```

**Key Design Points:**

- **Sub-thread isolation**: Each step runs in its own LangGraph thread (`{thread_id}_run_{run_id}_step_{step.id}`) to prevent tool-call contamination between steps.
- **SSE Events**: Custom LangGraph events (`adispatch_custom_event`) for real-time frontend updates: `plan`, `step_started`, `step_update`, `step_finished`, `step_token`, `image`, `chart_artifact`, `artifact`, `token`.
- **Fast path**: Simple conversational queries bypass the orchestrator entirely and go straight to the LLM.
- **Fallback plan**: If plan generation fails (JSON parse error, LLM timeout), a default 3-step plan is used.

### 5.3 Prompt Architecture

| Prompt | File | Purpose |
|--------|------|---------|
| System prompt | `prompt.md` | Core agent behavior — analysis workflow, tool usage guidelines, chart lifecycle |
| Planner prompt | `prompts/planner_prompt.md` | Generates structured execution plans with JSON output |
| Step prompt | `prompts/step_prompt.md` | Per-step execution with chart lifecycle directives |
| Synthesis prompt | `prompts/synthesis_prompt.md` | Final report generation — research-paper style |

---

## 6. Analysis Engine (`packages/analysis/`)

A **pure Python analysis library** with zero dependencies on LangChain, LangGraph, or any AI framework. Uses pandas, numpy, and matplotlib/seaborn.

```
┌─────────────────────────────────────────────────────────┐
│                    AnalysisEngine                         │
│                                                          │
│  ┌──────────────┐  ┌──────────────┐  ┌──────────────┐  │
│  │   I/O Layer   │  │  Profiling   │  │  Statistics  │  │
│  │               │  │              │  │              │  │
│  │ • Auto-detect │  │ • Profile()  │  │ • describe() │  │
│  │   encoding    │  │ • ColumnPro- │  │ • quantiles()│  │
│  │ • Auto-detect │  │   file[]     │  │ • correlation│  │
│  │   delimiter   │  │ • Memory     │  │   matrix()   │  │
│  │ • Multi-format│  │   estimation │  │              │  │
│  │   (CSV, TSV,  │  └──────────────┘  └──────────────┘  │
│  │    XLSX, ...)  │                                      │
│  └──────────────┘  ┌──────────────┐  ┌──────────────┐  │
│                    │   Charts     │  │  Aggregation  │  │
│                    │              │  │              │  │
│                    │ • 18 chart   │  │ • aggregate()│  │
│                    │   types      │  │ • filter()   │  │
│                    │ • ChartSpec  │  │ • sort()     │  │
│                    │ • ChartArtif-│  │              │  │
│                    │   act        │  └──────────────┘  │
│                    └──────────────┘                    │
└─────────────────────────────────────────────────────────┘
```

**Supported file formats**: CSV, TSV, XLSX, XLS, Parquet, JSON, Feather

**Auto-detection**: Encoding (UTF-8 → latin-1, cp1252, iso-8859-15), delimiters (`,` → `;` → `\t` → `|`)

---

## 7. Tool System (`packages/tools/`)

### 7.1 Tool Registry (`registry.py`)

A central registry pattern using the `@register_tool` decorator:

```python
@register_tool
class DescribeDatasetTool(BaseTool):
    ...
```

All 22 tools are auto-registered at import time via `packages/tools/__init__.py`.

### 7.2 Tool Categories

| Category | Tools | Description |
|----------|-------|-------------|
| **Inspection** | `ListDatasetsTool`, `DescribeDatasetTool`, `DatasetSummaryTool`, `DatasetHeadTool`, `DatasetShapeTool`, `ListColumnsTool`, `ColumnInfoTool` | Dataset discovery, schema inspection, profiling |
| **Statistics** | `MeanTool`, `MedianTool`, `MinTool`, `MaxTool`, `StdTool`, `QuantilesTool` | Per-column descriptive statistics |
| **Cleaning** | `MissingValuesTool`, `DuplicatesTool`, `DropColumnsTool` | Data quality assessment |
| **Aggregation** | `AggregateTool`, `FilterTool`, `SortTool` | Group-by, filtering, sorting operations |
| **Relationships** | `CorrelationTool`, `OutlierDetectionTool` | Pearson correlation, IQR outlier detection |
| **Visualization** | `GenerateChartTool`, `CorrelationHeatmapTool` | Chart generation with `ChartArtifact` output |
| **Planning** | `CreateBlueprintTool` | Markdown plan document generation |

All tools are `langchain.tools.BaseTool` subclasses with Pydantic `args_schema` for type validation.

---

## 8. Infrastructure

### 8.1 Docker Compose

```yaml
services:
  postgres:  # PostgreSQL 16, port 5432, health checks, named volume
  pgadmin:   # pgAdmin 4, port 5050, depends on healthy postgres

volumes:
  postgres_data:
  pgadmin_data:

networks:
  chu-network:  # bridge driver
```

### 8.2 LLM Backend

The platform expects an **OpenAI-compatible API endpoint** (default `http://localhost:6060/v1`). This can be:
- OpenAI API
- Azure OpenAI
- Local LLM servers (Ollama, vLLM, LM Studio, etc.)
- Any OpenAI-compatible proxy

### 8.3 Agent Memory Persistence

Two backends for conversation memory:

| Backend | Implementation | Use Case |
|---------|---------------|----------|
| **InMemory** | `InMemorySaver` | Development, testing |
| **Postgres** | `AsyncPostgresSaver` | Production — persists across server restarts |

---

## 9. Data Flow

### 9.1 Chat Flow (Complex Query)

```
User: "Analyze sales trends"
       │
       ▼
  SvelteKit UI ──POST /api/v1/chat──▶ FastAPI Router
       │                                    │
       │                              SessionManager.get_or_create()
       │                              AgentService.stream(message)
       │                                    │
       │                              Orchestrator.stream()
       │                                    │
       │                         ┌──────────┴──────────┐
       │                         │   Planner Node       │
       │                         │   "plan" event ──────┤
       │                         └──────────┬──────────┘
       │                                    │
       │                         ┌──────────┴──────────┐
       │                         │  Executor Node       │
       │                         │  For each step:      │
       │   ◄──── SSE events ─────┤  - "step_started"    │
       │                         │  - "step_token"      │
       │                         │  - "image"/"artifact"│
       │                         │  - "step_finished"   │
       │                         └──────────┬──────────┘
       │                                    │
       │                         ┌──────────┴──────────┐
       │                         │ Synthesizer Node     │
       │   ◄──── SSE events ─────┤  - "token" (report)  │
       │                         │  - "done"            │
       │                         └─────────────────────┘
       │
  SvelteKit renders:
  - Step progress cards
  - Chart images inline
  - Final report with Markdown
```

### 9.2 SSE Event Types

| Event | When | Data |
|-------|------|------|
| `thread_id` | Start of stream | Thread UUID string |
| `plan` | After planning | JSON execution plan with steps |
| `step_started` | Each step begins | JSON `{id, title, description, tool_hint}` |
| `step_update` | Within a step | Progress text string |
| `step_token` | Within a step | Text token (LLM output) |
| `step_finished` | Each step ends | JSON `{id}` |
| `image` | Chart generated | Chart URL string |
| `chart_artifact` | Chart generated | Full `ChartArtifact` dict |
| `artifact` | Plan artifact created | Artifact metadata JSON |
| `token` | During synthesis | Text token (final report) |
| `done` | Stream complete | Empty string |

---

## 10. Key Design Decisions

### 10.1 Separation of Concerns

The architecture enforces a clean separation between **AI orchestration** and **pure computation**:

- **`packages/analysis/`** — Zero AI dependencies. Pure pandas/numpy/matplotlib. Can be used standalone without any LLM infrastructure.
- **`packages/tools/`** — LangChain wrappers around the AnalysisEngine. Each tool is a thin adapter that calls `AnalysisEngine` methods and formats the output.
- **`packages/ai/`** — Generic, reusable AI agent framework. Knows nothing about data analysis. Could be reused for any tool-based agent.
- **`packages/agents/`** — Domain-specific agent that wires the generic framework to the specific tools and prompts.

### 10.2 Modular Monorepo with UV Workspaces

- Single `pyproject.toml` at root defines the project and workspace members.
- All `packages/*` are importable as `chu-platform` submodules.
- `apps/api` is a workspace member with its own `pyproject.toml` and dependencies.
- Unified version management.

### 10.3 Streaming-First Architecture

- All LLM interactions are streamed token-by-token via SSE.
- The Orchestrator streams structured events (plan, steps, charts) rather than waiting for complete results.
- The frontend renders progressively — step cards update in real-time, charts appear as generated.
- `X-Accel-Buffering: no` header ensures nginx doesn't buffer SSE responses.

### 10.4 Pluggable Memory Backend

- The `SessionManager` accepts any `BaseCheckpointSaver` implementation.
- Development uses `InMemorySaver` (no infrastructure required).
- Production uses `AsyncPostgresSaver` for durable conversation persistence.
- The checkpointer is injected during app lifespan, keeping the rest of the code agnostic.

### 10.5 LangGraph as the Orchestration Engine

- **Generic agent graph** (`packages/ai/graph.py`): agent → tools → summarize loop.
- **Orchestrator graph** (`packages/agents/data_analyst/data_analyst_orchestrator.py`): planner → executor (loop) → synthesizer.
- The executor reuses the generic agent graph internally, creating isolated sub-threads for each step.
- Custom events (`adispatch_custom_event`) bridge LangGraph internals to HTTP SSE responses.

### 10.6 Svelte 5 Runes for State

- Frontend state management uses Svelte 5's reactive runes (`$state`, `$derived`) instead of external state libraries.
- Each domain (conversations, app, agents, datasets, notifications, settings) has a dedicated rune-based store.
- SSE streaming is handled directly in the conversation page with event-by-event processing.

### 10.7 Custom Design Tokens over Frameworks

- Instead of a UI framework (Material, Shadcn), the project defines custom CSS design tokens.
- GitHub-dark-inspired color palette with full light/dark mode support.
- Tailwind CSS 4 `@theme` directive for type-safe token usage in markup.
