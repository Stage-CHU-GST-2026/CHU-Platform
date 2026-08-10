# Technical Debt & Refactoring Plan - CHU-Platform

Audit report identifying technical debt, hardcoded parameters, legacy packages, and missing architectural abstractions in CHU-Platform.

---

## 1. Summary of Identified Technical Debt

| Item | Severity | Location | Description | Refactoring Recommendation |
| :--- | :--- | :--- | :--- | :--- |
| **Missing Auth Middleware** | High | `apps/api/src/api/` | No user authentication or multi-tenant authorization controls on API endpoints. | Implement JWT middleware & `user_id` context scope. |
| **Legacy Frontend (`web-2`)** | Medium | `web-2/` | Outdated Svelte 4 codebase maintained alongside `apps/web`. | Deprecate `web-2/` and migrate residual components to `apps/web`. |
| **DuckDB File Cleanup** | Medium | `files/exports/` | No automated retention or garbage collection policy for generated export files. | Add daily cron cleanup task purging artifacts > 30 days old. |
| **Hardcoded CORS Policy** | Low | `apps/api/src/api/main.py` | Wildcard CORS (`allow_origins=["*"]`) enabled by default. | Parameterize via environment variables (`ALLOWED_ORIGINS`). |
| **Documentation Discrepancies**| Low | Root `ARCHITECTURE.md` | Legacy docs refer to older database models and missing package paths. | Replaced by updated unified docs in `docs/`. |

---

## 2. Priority Refactoring Roadmap

### Phase 1: Security & Auth Baseline (High Priority)
- Add User entity in PostgreSQL.
- Guard endpoints in `apps/api/src/api/routers/` with FastAPI authentication dependencies.

### Phase 2: Monorepo Consolidation (Medium Priority)
- Remove `web-2` directory.
- Consolidate common types into a shared TypeScript package `@chu/types`.
