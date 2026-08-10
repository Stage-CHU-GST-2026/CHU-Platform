# Directory Structure Documentation - CHU-Platform

An exhaustive breakdown of the workspace layout and key files in `/home/regisx001/CHU-Platform`.

```
/home/regisx001/CHU-Platform/
├── .dockerignore                     # Docker build exclusion rules
├── .env                              # Environment configuration file (local active)
├── .env.example                      # Template for environment variables
├── .gitignore                        # Git exclusion rules
├── ARCHITECTURE.md                   # Legacy root architecture documentation
├── DOCKERISATION.md                  # Containerization & deployment notes
├── NEXT.md                           # Development roadmap and outstanding tasks
├── README.md                         # Repository landing page
├── docker-compose.yaml               # Docker Compose service orchestration
├── pyproject.toml                    # Root uv workspace configuration & dependencies
├── uv.lock                           # Lockfile for Python workspace dependencies
│
├── apps/
│   ├── api/                          # FastAPI Backend Application
│   │   ├── Dockerfile                # API container image definition
│   │   ├── pyproject.toml            # API package metadata & dependencies
│   │   ├── run.py                    # Dev entrypoint script
│   │   ├── alembic.ini               # Alembic database migration config
│   │   ├── alembic/                  # Database migration scripts
│   │   └── src/
│   │       └── api/
│   │           ├── main.py           # FastAPI application factory & router setup
│   │           ├── config.py         # Pydantic Settings configuration loader
│   │           ├── database.py       # Async SQLAlchemy session initialization
│   │           ├── models/           # SQLAlchemy DB ORM schemas (Dataset, Conversation, Message, Artifact)
│   │           ├── schemas/          # Pydantic data validation schemas
│   │           ├── routers/          # API Route handlers (chat, datasets, conversations, artifacts, semantic_categories)
│   │           └── services/         # Core business logic services
│   │
│   ├── ui/                           # Svelte Component Library workspace
│   │   ├── package.json              # UI library package config
│   │   └── src/                      # Reusable UI component source code
│   │
│   └── web/                          # Primary SvelteKit 5 Web Application
│       ├── Dockerfile                # Web app container image definition
│       ├── package.json              # Web app dependencies & scripts
│       ├── vite.config.ts            # Vite build setup
│       ├── svelte.config.js          # SvelteKit configuration
│       └── src/
│           ├── app.html              # Core HTML template
│           ├── lib/                  # Svelte UI components, stores, API clients
│           └── routes/               # SvelteKit page routes (+page.svelte, +layout.svelte)
│
├── packages/
│   ├── agents/                       # LangGraph AI Agent Library
│   │   └── data_analyst/
│   │       ├── agent.py              # Main Agent wrapper class
│   │       ├── agent.yaml            # Agent metadata & prompt bindings
│   │       ├── data_analyst_orchestrator.py # LangGraph graph builder & SSE executor
│   │       ├── data_analyst_planner.py      # Strategic planning LLM node
│   │       ├── graph.py              # StateGraph state machine graph
│   │       ├── memory.py             # Chat memory management
│   │       ├── nodes.py              # Execution node handlers
│   │       ├── state.py              # Agent state definitions
│   │       └── tools.py              # Tool bindings for agent
│   │
│   ├── analysis/                     # Statistical & Visualization Package
│   │   ├── charts.py                 # Plotly & Matplotlib chart generation routines
│   │   ├── engine.py                 # Core pandas/numpy aggregation engine
│   │   ├── profiler.py               # Data profiling & column summaries
│   │   └── statistics.py             # Statistical hypothesis & distribution tests
│   │
│   └── tools/                        # DuckDB & Data Execution Tools
│       ├── analytics.py              # Analytics tool wrappers
│       ├── cleaning.py               # Outlier cleaning & null handling tools
│       ├── duckdb_tools.py           # DuckDB connection & SQL execution functions
│       ├── inspection.py             # Schema inspection & head viewer tools
│       ├── planning.py               # Plan parsing utilities
│       ├── registry.py               # Dynamic tool registry
│       └── visualization.py          # Visualization tool bindings
│
├── web-2/                            # Legacy Svelte 4 / Vite Web Frontend
│   ├── Dockerfile
│   ├── package.json
│   └── src/
│
├── nginx/                            # Nginx Proxy Configuration
│   └── default.conf                  # Routing config for API and Web services
│
├── files/                            # Shared File Storage
│   ├── datasets/                     # Raw uploaded CSV / Parquet files
│   └── exports/                      # Exported reports, CSVs, and PNG charts
│
└── docs/                             # Full Exhaustive Documentation Suite
    ├── README.md                     # Documentation index
    ├── diagrams/                     # Mermaid diagram source files (.mmd)
    └── [21 Markdown Docs]            # Comprehensive system specification files
```
