# Developer Guide & Local Setup - CHU-Platform

Instructions for setting up a local development environment, running services, and code formatting.

---

## 1. Prerequisites
- **Python**: 3.11+
- **`uv`**: Installed (`curl -LsSf https://astral.sh/uv/install.sh | sh`)
- **Node.js**: 20+ (or **Bun**)
- **Docker & Docker Compose** (optional for local DB)

---

## 2. Local Backend Setup

1. **Install Python Dependencies**:
   ```bash
   cd /home/regisx001/CHU-Platform
   uv sync
   ```

2. **Start Local PostgreSQL Database**:
   ```bash
   docker-compose up -d db
   ```

3. **Run Migrations & Start FastAPI App**:
   ```bash
   cd apps/api
   uv run alembic upgrade head
   uv run python run.py
   ```
   FastAPI server runs at `http://localhost:8000`.

---

## 3. Local Frontend Setup

1. **Install Node Dependencies & Start Dev Server**:
   ```bash
   cd apps/web
   bun install # or npm install
   bun run dev
   ```
   SvelteKit app runs at `http://localhost:5173` (or `http://localhost:3000`).

---

## 4. Code Formatting & Linting

- **Python**: Formatted using `ruff` / `black`.
  ```bash
  uv run ruff check .
  uv run ruff format .
  ```
- **Svelte / TypeScript**: Formatted using Prettier & ESLint.
  ```bash
  cd apps/web
  bun run check
  bun npx prettier --write .
  ```
