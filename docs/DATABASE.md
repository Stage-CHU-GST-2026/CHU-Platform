# Database Architecture & Schema Documentation - CHU-Platform

CHU-Platform relies on a dual-database design:
1. **PostgreSQL**: Stores relational domain data, user metadata, datasets catalog, conversations, messages, artifacts, and semantic category mappings.
2. **DuckDB**: Embedded, high-performance OLAP engine executing SQL queries directly on file-backed datasets (`.csv`, `.parquet`).

---

## 1. PostgreSQL ER Diagram

```mermaid
erDiagram
    SEMANTIC_CATEGORIES ||--o{ DATASETS : categorizes
    DATASETS ||--o{ DATASET_COLUMNS : contains
    DATASETS ||--o{ CONVERSATIONS : contextualizes
    CONVERSATIONS ||--o{ MESSAGES : stores
    CONVERSATIONS ||--o{ ARTIFACTS : produces
    MESSAGES ||--o{ ARTIFACTS : references

    SEMANTIC_CATEGORIES {
        uuid id PK
        string name
        string description
        uuid parent_id FK
        datetime created_at
    }

    DATASETS {
        uuid id PK
        string name
        string filename
        string file_path
        string file_type
        integer row_count
        integer column_count
        uuid category_id FK
        datetime created_at
        datetime updated_at
    }

    DATASET_COLUMNS {
        uuid id PK
        uuid dataset_id FK
        string column_name
        string data_type
        integer missing_count
        json summary_stats
    }

    CONVERSATIONS {
        uuid id PK
        string title
        uuid dataset_id FK
        datetime created_at
        datetime updated_at
    }

    MESSAGES {
        uuid id PK
        uuid conversation_id FK
        string sender_role
        text content
        json tool_calls
        datetime created_at
    }

    ARTIFACTS {
        uuid id PK
        uuid conversation_id FK
        uuid message_id FK
        string title
        string artifact_type
        string file_path
        json content_json
        datetime created_at
    }
```

---

## 2. SQLAlchemy ORM Model Definitions (`apps/api/src/api/models/`)

- **`Dataset`**: Maps file paths on host volume (`files/datasets/`), store row/column counts, and dataset metadata.
- **`DatasetColumn`**: Stores inferenced data types (e.g. `INTEGER`, `VARCHAR`, `TIMESTAMP`), nullability, and pre-computed profiling stats (min, max, mean, stddev, quantiles).
- **`Conversation`**: Context window boundary for AI chats. Tied to a specific `dataset_id`.
- **`Message`**: Chat turn history (User vs Assistant) storing raw prompts, AI responses, and JSON tool execution traces.
- **`Artifact`**: Generated output artifacts (Interactive charts, exported CSV clean tables, statistical summary reports).
- **`SemanticCategory`**: Hierarchical category tree allowing classification of datasets.

---

## 3. Database Migrations (Alembic)

Database schema versioning is managed via **Alembic** located in `apps/api/alembic/`.
- Configuration: `apps/api/alembic.ini`
- Migration track: `apps/api/alembic/versions/`

### Running Migrations Manually
```bash
cd apps/api
# Run all pending migrations
uv run alembic upgrade head

# Generate a new migration revision
uv run alembic revision --autogenerate -m "Add new column"
```
