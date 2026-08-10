# Deployment & Production Setup - CHU-Platform

This guide describes production deployment procedures, Nginx reverse proxy configuration, environment variable setup, and SSL termination.

---

## 1. Nginx Reverse Proxy Configuration (`nginx/default.conf`)

```nginx
server {
    listen 80;
    server_name _;

    # Frontend SvelteKit Web App
    location / {
        proxy_pass http://web:3000;
        proxy_http_version 1.1;
        proxy_set_header Upgrade $http_upgrade;
        proxy_set_header Connection 'upgrade';
        proxy_set_header Host $host;
        proxy_cache_bypass $http_upgrade;
    }

    # FastAPI REST & SSE Backend
    location /api/ {
        proxy_pass http://api:8000/api/;
        proxy_http_version 1.1;
        proxy_set_header Connection '';
        proxy_set_header Host $host;
        
        # Disable buffering for Server-Sent Events (SSE)
        proxy_buffering off;
        proxy_cache off;
        chunked_transfer_encoding off;
    }

    # Static File Uploads & Artifact Exports
    location /files/ {
        alias /app/files/;
        autoindex off;
    }
}
```

---

## 2. Production Deployment Steps

1. **Clone Repository & Set Environment Variables**:
   ```bash
   git clone https://github.com/organization/CHU-Platform.git
   cd CHU-Platform
   cp .env.example .env
   # Edit .env and supply OPENAI_API_KEY and production POSTGRES passwords
   ```

2. **Launch Docker Stack**:
   ```bash
   docker-compose up -d --build
   ```

3. **Run Database Migrations**:
   ```bash
   docker-compose exec api uv run alembic upgrade head
   ```

4. **Verify Health Status**:
   - Web App: `http://<server-ip>/`
   - API Docs: `http://<server-ip>/api/docs`
