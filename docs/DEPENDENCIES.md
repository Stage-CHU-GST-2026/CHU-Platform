# Package & Workspace Dependencies - CHU-Platform

This document details Python and Node.js dependency stacks across the monorepo workspace.

---

## 1. Python Monorepo Workspace (`pyproject.toml` & `uv.lock`)

Python package dependencies are managed via **`uv`**.

### Workspace Configuration (`/home/regisx001/CHU-Platform/pyproject.toml`)
```toml
[project]
name = "chu-platform"
version = "0.1.0"
description = "CHU Data Platform Monorepo"
requires-python = ">=3.11"
dependencies = [
    "fastapi>=0.110.0",
    "uvicorn[standard]>=0.28.0",
    "sqlalchemy[asyncio]>=2.0.28",
    "asyncpg>=0.29.0",
    "alembic>=1.13.1",
    "pydantic>=2.6.4",
    "pydantic-settings>=2.2.1",
    "duckdb>=0.10.1",
    "pandas>=2.2.1",
    "numpy>=1.26.4",
    "scipy>=1.12.0",
    "plotly>=5.20.0",
    "matplotlib>=3.8.3",
    "langchain>=0.1.13",
    "langchain-core>=0.1.33",
    "langchain-openai>=0.1.1",
    "langgraph>=0.0.30",
    "python-multipart>=0.0.9",
]

[tool.uv.workspace]
members = ["apps/api", "packages/*"]
```

---

## 2. Node.js / Bun Workspaces (`apps/web` & `apps/ui`)

Frontend package management is driven by Bun or npm.

### Primary SvelteKit Web App (`apps/web/package.json`)
```json
{
  "name": "@chu/web",
  "version": "0.1.0",
  "private": true,
  "type": "module",
  "scripts": {
    "dev": "vite dev",
    "build": "vite build",
    "preview": "vite preview",
    "check": "svelte-check --tsconfig ./tsconfig.json"
  },
  "dependencies": {
    "@sveltejs/kit": "^2.0.0",
    "svelte": "^5.0.0",
    "tailwindcss": "^3.4.1",
    "plotly.js-dist-min": "^2.29.1",
    "lucide-svelte": "^0.359.0"
  },
  "devDependencies": {
    "@sveltejs/adapter-auto": "^3.0.0",
    "@sveltejs/vite-plugin-svelte": "^3.0.0",
    "typescript": "^5.0.0",
    "vite": "^5.0.0"
  }
}
```
