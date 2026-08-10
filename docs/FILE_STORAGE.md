# File Storage Architecture - CHU-Platform

This document outlines storage strategy, file directory structures, dataset formats, cleanup policies, and export artifact persistence in CHU-Platform.

---

## 1. Storage Directory Layout

All physical file storage is centralized under `/home/regisx001/CHU-Platform/files/` (or `/app/files` inside Docker containers).

```
files/
├── datasets/             # Uploaded raw data files
│   ├── 4f8b2a1c-....csv  # Dataset saved using unique UUID prefix
│   └── c9d2e1f3-....parquet
├── exports/              # Generated output artifacts & charts
│   ├── chart_8a7b....json # Plotly json specification
│   ├── export_3f2e....csv # Cleaned CSV data export
│   └── chart_1d2e....png  # Rendered Matplotlib PNG artifact
└── static/               # Platform static assets & thumbnails
```

---

## 2. Dataset Format Handling

### 2.1 CSV File Ingestion
- **Delimiters**: Auto-detected by DuckDB (`read_csv_auto()`). Supports comma, semicolon, tab, and pipe delimiters.
- **Encoding**: UTF-8 auto-normalization.
- **Header Parsing**: Automatic header inference with column name fallback (`column_0`, `column_1`).

### 2.2 Parquet File Ingestion
- High-efficiency binary format supported natively by DuckDB.
- Preserves native column datatypes (`INT64`, `DOUBLE`, `TIMESTAMP`, `BOOLEAN`).

---

## 3. Artifact Storage Lifecycle

1. **Generation**: When a user or agent invokes visualization tools, chart JSON or exported data CSV files are written to `files/exports/`.
2. **Metadata Registration**: A row is inserted into PostgreSQL's `artifacts` table containing:
   - `id`: Unique artifact UUID
   - `conversation_id`: Associated thread UUID
   - `file_path`: Relative path to file (`files/exports/chart_...json`)
   - `artifact_type`: `chart` | `table` | `export` | `report`
3. **Retrieval**: Served over HTTP by FastAPI static router or `/api/artifacts/{id}` endpoint.
4. **Cleanup Policy**: Currently, files persist indefinitely. High-capacity deployments should schedule a periodic cron task to purge orphaned export files older than 30 days.
