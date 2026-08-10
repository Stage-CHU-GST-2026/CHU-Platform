# Troubleshooting Guide - CHU-Platform

Common operational issues, diagnosis steps, and resolution paths for CHU-Platform.

---

## 1. Database Connection Failures (`asyncpg.exceptions` / `ConnectionRefusedError`)

### Symptoms
- FastAPI output displays `ConnectionRefusedError: [Errno 111] Connect call failed ('127.0.0.1', 5432)`.

### Resolution
1. Verify PostgreSQL container is running: `docker-compose ps`
2. Check database credentials match `.env`:
   ```bash
   docker-compose exec db psql -U postgres -d chu_platform -c "\dt"
   ```
3. If running `apps/api` outside Docker, ensure `POSTGRES_HOST=localhost` in `.env`. Inside Docker, use `POSTGRES_HOST=db`.

---

## 2. Real-Time Chat SSE Stream Buffering Issues

### Symptoms
- Chat responses do not stream token-by-token; instead, the entire message appears at once after 10 seconds.

### Resolution
- Cause: Nginx or reverse proxy proxy buffering is enabled.
- Fix: Verify `nginx/default.conf` includes:
  ```nginx
  proxy_buffering off;
  proxy_cache off;
  chunked_transfer_encoding off;
  ```

---

## 3. DuckDB Memory Exhaustion (`OutOfMemoryException`)

### Symptoms
- FastAPI worker crashes when querying large CSV files (> 1GB).

### Resolution
1. DuckDB default memory limit can be configured in `packages/tools/duckdb_tools.py`:
   ```python
   conn.execute("SET max_memory='2GB'")
   ```
2. Convert large raw CSV files to compressed Parquet files before executing analytical queries.
