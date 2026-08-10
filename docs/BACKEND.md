# Backend Subsystem Documentation - CHU-Platform

The backend subsystem is a modern Python application housed under `apps/api`.

---

## 1. Application Architecture (`apps/api/src/api/`)

```
src/api/
├── main.py              # FastAPI app creation, middleware registration, router mounts
├── config.py            # Environment settings management via Pydantic Settings
├── database.py          # SQLAlchemy Async Engine & SessionMaker setup
├── models/              # Declarative SQLAlchemy ORM models
│   ├── dataset.py
│   ├── conversation.py
│   ├── message.py
│   ├── artifact.py
│   └── semantic_category.py
├── schemas/             # Pydantic schemas for request/response validation
├── routers/             # API Router definitions
│   ├── datasets.py
│   ├── conversations.py
│   ├── chat.py
│   ├── artifacts.py
│   └── semantic_categories.py
└── services/            # Business logic encapsulation
    ├── dataset_service.py
    ├── conversation_service.py
    └── chat_service.py
```

---

## 2. Main Entrypoint & Middleware (`main.py`)

`src/api/main.py` initializes the FastAPI application instance using a lifespan context manager:

```python
@asynccontextmanager
async def lifespan(app: FastAPI):
    # Initialize DB pools and verify static/file directories
    await init_db()
    yield

app = FastAPI(
    title="CHU-Platform API",
    version="1.0.0",
    lifespan=lifespan
)

# CORSMiddleware configuration
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)
```

---

## 3. Asynchronous Database Connection (`database.py`)

SQLAlchemy 2.0 with `asyncpg` driver provides non-blocking relational operations:
- Engine string: `postgresql+asyncpg://${POSTGRES_USER}:${POSTGRES_PASSWORD}@${POSTGRES_HOST}:${POSTGRES_PORT}/${POSTGRES_DB}`
- Session Dependency: `get_db()` yields an `AsyncSession` per HTTP request.

---

## 4. Service Layer Responsibilities

- **`DatasetService`**: Handles multipart dataset file validation, writing raw files to `files/datasets/`, calling `packages/analysis/profiler.py`, and persisting column schemas.
- **`ConversationService`**: Controls thread life cycle, message indexing, and metadata updates.
- **`ChatService`**: Intermediary between HTTP chat request and `DataAnalystOrchestrator` execution. Converts agent outputs into text/event-stream chunks.
