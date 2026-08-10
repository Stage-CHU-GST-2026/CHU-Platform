# Configuration Reference - CHU-Platform

This document details configuration parameters, environment variables, default values, and secrets management across the CHU-Platform repository.

---

## 1. Environment Variable Reference (`.env` & `apps/api/src/api/config.py`)

| Variable Name | Required | Default Value | Description |
| :--- | :--- | :--- | :--- |
| `POSTGRES_USER` | No | `postgres` | PostgreSQL administrative username. |
| `POSTGRES_PASSWORD` | No | `postgres` | PostgreSQL password. |
| `POSTGRES_HOST` | No | `localhost` / `db` | Database host address. |
| `POSTGRES_PORT` | No | `5432` | Database port number. |
| `POSTGRES_DB` | No | `chu_platform` | Database name. |
| `DATABASE_URL` | No | `postgresql+asyncpg://...` | Full SQLAlchemy async database connection URI. |
| `OPENAI_API_KEY` | **Yes** | `""` | API Key for OpenAI provider model calls in LangGraph agents. |
| `OPENAI_MODEL` | No | `gpt-4o` | Model identifier used by agent planner and synthesizer. |
| `FILES_DIR` | No | `./files` | Host path for raw datasets and generated exports storage. |
| `DATASETS_DIR` | No | `./files/datasets` | Path storing uploaded raw `.csv` and `.parquet` files. |
| `EXPORTS_DIR` | No | `./files/exports` | Path storing generated artifacts and chart files. |
| `PUBLIC_API_URL` | No | `http://localhost:8000` | Public API endpoint accessed by web browser client. |
| `LOG_LEVEL` | No | `INFO` | Logging level (`DEBUG`, `INFO`, `WARNING`, `ERROR`). |

---

## 2. Configuration Management via Pydantic

Configuration is defined using Pydantic's `BaseSettings` model in `apps/api/src/api/config.py`:

```python
class Settings(BaseSettings):
    postgres_user: str = Field(default="postgres", alias="POSTGRES_USER")
    postgres_password: str = Field(default="postgres", alias="POSTGRES_PASSWORD")
    postgres_host: str = Field(default="localhost", alias="POSTGRES_HOST")
    postgres_port: int = Field(default=5432, alias="POSTGRES_PORT")
    postgres_db: str = Field(default="chu_platform", alias="POSTGRES_DB")
    
    openai_api_key: str = Field(default="", alias="OPENAI_API_KEY")
    openai_model: str = Field(default="gpt-4o", alias="OPENAI_MODEL")
    
    files_dir: str = Field(default="./files", alias="FILES_DIR")
    
    class Config:
        env_file = ".env"
        extra = "ignore"

settings = Settings()
```

---

## 3. Secret Management Security Practices
- **Do not commit secrets**: `.env` is listed in `.gitignore`. Use `.env.example` as a template for team deployment.
- **Production Secrets**: Use Docker Secrets or cloud environment variables (e.g. AWS Secrets Manager / GCP Secret Manager) in production deployments.
