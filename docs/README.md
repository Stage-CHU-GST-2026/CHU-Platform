# CHU-Platform Documentation Suite

Welcome to the technical documentation for **CHU-Platform**, an AI-powered conversational data analysis, visualization, and semantic category management platform built for healthcare dataset exploration.

> [!NOTE]
> All documentation files in this directory are derived from an in-depth codebase audit of [/home/regisx001/CHU-Platform](file:///home/regisx001/CHU-Platform).

---

## 📚 Documentation Index

| Documentation File | Description |
| :--- | :--- |
| [PROJECT_OVERVIEW.md](file:///home/regisx001/CHU-Platform/docs/PROJECT_OVERVIEW.md) | High-level system overview, business context, key capabilities, and user workflows. |
| [ARCHITECTURE.md](file:///home/regisx001/CHU-Platform/docs/ARCHITECTURE.md) | Modular multi-package architecture, request lifecycles, and design patterns. |
| [DIRECTORY_STRUCTURE.md](file:///home/regisx001/CHU-Platform/docs/DIRECTORY_STRUCTURE.md) | Exhaustive directory tree detailing all applications, packages, scripts, and configurations. |
| [DATA_FLOW.md](file:///home/regisx001/CHU-Platform/docs/DATA_FLOW.md) | Data ingestion, DuckDB processing, streaming SSE chat, state mutation, and export flows. |
| [API.md](file:///home/regisx001/CHU-Platform/docs/API.md) | OpenAPI specification breakdown, endpoints, payload validation schemas, and error responses. |
| [DATABASE.md](file:///home/regisx001/CHU-Platform/docs/DATABASE.md) | Relational database schema, ER diagrams, SQLAlchemy ORM models, and Alembic migration tracks. |
| [AI_SYSTEM.md](file:///home/regisx001/CHU-Platform/docs/AI_SYSTEM.md) | LangGraph Data Analyst agent, tool registries, execution nodes, and prompt strategies. |
| [FRONTEND.md](file:///home/regisx001/CHU-Platform/docs/FRONTEND.md) | SvelteKit 5 web app, UI component architecture, state management, SSE handling, and legacy apps. |
| [BACKEND.md](file:///home/regisx001/CHU-Platform/docs/BACKEND.md) | FastAPI core architecture, application setup, router mounting, services, and middlewares. |
| [DOCKER.md](file:///home/regisx001/CHU-Platform/docs/DOCKER.md) | Containerization topology, multi-stage Dockerfiles, Docker Compose configuration, and networking. |
| [CONFIGURATION.md](file:///home/regisx001/CHU-Platform/docs/CONFIGURATION.md) | Environment variables reference, default values, configuration models, and secret management. |
| [FILE_STORAGE.md](file:///home/regisx001/CHU-Platform/docs/FILE_STORAGE.md) | File directory structures, dataset storage formats (CSV/Parquet), temporary files, and exports. |
| [DEPENDENCIES.md](file:///home/regisx001/CHU-Platform/docs/DEPENDENCIES.md) | Package dependencies for Python (uv workspace) and Node.js/Bun workspaces. |
| [SECURITY.md](file:///home/regisx001/CHU-Platform/docs/SECURITY.md) | Security controls, SQL execution safety in DuckDB, CORS policies, authentication, and vulnerability risks. |
| [ERROR_HANDLING.md](file:///home/regisx001/CHU-Platform/docs/ERROR_HANDLING.md) | Exception handling patterns, HTTP error codes, agent tool fallback, and logging practices. |
| [TESTING.md](file:///home/regisx001/CHU-Platform/docs/TESTING.md) | Test suites, pytest setup, tool node tests, boundary tests, and instructions for running tests. |
| [DEPLOYMENT.md](file:///home/regisx001/CHU-Platform/docs/DEPLOYMENT.md) | Production deployment instructions, Nginx reverse proxy setup, environment configuration, and SSL. |
| [DEVELOPMENT.md](file:///home/regisx001/CHU-Platform/docs/DEVELOPMENT.md) | Local dev environment setup, `uv` workspace commands, running web clients, and formatting. |
| [TROUBLESHOOTING.md](file:///home/regisx001/CHU-Platform/docs/TROUBLESHOOTING.md) | Common failure modes, database lock issues, memory consumption during DuckDB queries, and fix steps. |
| [TECHNICAL_DEBT.md](file:///home/regisx001/CHU-Platform/docs/TECHNICAL_DEBT.md) | Identified technical debt, hardcoded values, missing auth, legacy code in `web-2`, and refactoring plan. |
| [AUDIT_REPORT.md](file:///home/regisx001/CHU-Platform/docs/AUDIT_REPORT.md) | Complete repository audit findings, security analysis, code quality assessment, and recommendations. |

---

## 📊 Visual Diagrams

Architecture and flow diagrams are located in [docs/diagrams/](file:///home/regisx001/CHU-Platform/docs/diagrams/):

- [System Architecture Diagram](file:///home/regisx001/CHU-Platform/docs/diagrams/architecture.mmd)
- [Data Flow Sequence Diagram](file:///home/regisx001/CHU-Platform/docs/diagrams/data-flow.mmd)
- [HTTP Request Flow Diagram](file:///home/regisx001/CHU-Platform/docs/diagrams/request-flow.mmd)
- [AI Execution Flow Diagram](file:///home/regisx001/CHU-Platform/docs/diagrams/ai-flow.mmd)
- [Container Deployment Topology](file:///home/regisx001/CHU-Platform/docs/diagrams/deployment.mmd)
