# Security Architecture & Risk Analysis - CHU-Platform

This document provides a thorough audit of security controls, DuckDB execution safety, CORS policies, authentication status, and identified vulnerabilities within CHU-Platform.

---

## 1. SQL Execution Security in DuckDB

> [!WARNING]
> The AI Data Analyst Agent executes dynamic SQL statements constructed by LLM output against DuckDB (`packages/tools/duckdb_tools.py`).

### Controls Implemented
- **Read-Only / In-Memory Scope**: DuckDB operates in transient memory mode or opens data files in read-only mode (`read_only=True`), preventing destructive SQL operations (`DROP TABLE`, `DELETE`, `UPDATE`) on raw files.
- **Row Count Truncation**: Query results are bounded (`LIMIT 500`) to prevent memory exhaustion / Denial of Service (DoS).

### Vulnerability Risk: Arbitrary File Access via DuckDB Extensions
- **Risk**: DuckDB allows extensions (e.g. `httpfs`) and functions like `read_csv('/etc/passwd')` if unmanaged.
- **Recommendation**: Disable filesystem crawling functions in DuckDB connection configuration or restrict file paths strictly to `files/datasets/`.

---

## 2. Authentication & Authorization Status

> [!IMPORTANT]
> **Audit Finding**: Currently, `apps/api` **does not implement user authentication** (JWT, OAuth2, or session cookies). All API endpoints (`/api/datasets`, `/api/conversations`, `/api/chat/stream`) are publicly accessible without permissions checks.

### Recommendations
1. Implement JWT Authentication middleware in FastAPI.
2. Add `user_id` foreign key association to `datasets` and `conversations` tables in PostgreSQL to enforce multi-tenant authorization policies.

---

## 3. CORS & Network Security

- **CORS Configuration**: `apps/api/src/api/main.py` currently allows wildcard origins (`allow_origins=["*"]`).
- **Production Recommendation**: Restrict CORS origins in `main.py` to explicit domain names specified in environment variable `ALLOWED_ORIGINS`.
