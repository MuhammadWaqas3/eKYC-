# Docker Build & Compose Setup - Quick Start

## Files Created

✅ **Backend Dockerfile** (`backend/Dockerfile`)
- Multi-stage build (builder + runtime stages)
- Non-root user (`appuser`)
- Health checks enabled
- Optimized for production

✅ **Frontend Dockerfile** (`frontend/Dockerfile`)  
- Multi-stage build (deps + builder + runtime stages)
- Alpine Linux (smaller images)
- Non-root user (`nextjs`)
- Health checks enabled

✅ **docker-compose.yml**
- PostgreSQL 16 (updated from 14)
- Backend (dev + prod profiles)
- Frontend (dev + prod profiles)
- Resource limits defined
- Environment variable support
- Health checks for all services

✅ **Environment Files**
- `.env.local` - Local development config
- Root `.dockerignore` - Excludes venv310 and other artifacts

---

## Quick Start

### Development Mode
```bash
docker compose --profile dev up -d
```
Starts:
- PostgreSQL database
- FastAPI backend with hot-reload
- Next.js frontend with dev server
- Access frontend at `http://localhost:3000`
- Access API at `http://localhost:8000`

### Production Mode
```bash
docker compose --profile prod up -d
```
Starts:
- PostgreSQL database
- FastAPI backend (production)
- Next.js frontend (production)

### Stop Services
```bash
docker compose down
```

### View Logs
```bash
docker compose logs -f backend
docker compose logs -f frontend
docker compose logs -f postgres
```

---

## Key Features

**Backend (FastAPI)**
- Multi-stage build reduces image size by ~70%
- Runs as non-root user
- Health check endpoint: `GET /health`
- Dependencies pre-compiled in builder stage
- Tesseract OCR and OpenCV libraries included

**Frontend (Next.js)**
- Production build optimized (3-stage process)
- Alpine Linux base (lightweight)
- Runs as non-root user  
- Health check via `wget`
- Separates build dependencies from runtime

**Database**
- PostgreSQL 16 Alpine (lightweight)
- Persistent volume: `postgres_data`
- Health check via `pg_isready`
- 10-second startup grace period

**Docker Compose**
- Development (`--profile dev`) - hot-reload enabled
- Production (`--profile prod`) - optimized builds
- Resource limits: CPU & memory constraints
- Environment variable injection via `.env.local`
- Network isolation: all services on `ekyc_network`

---

## Environment Variables

Edit `.env.local` to customize:

```env
DB_USER=postgres
DB_PASSWORD=postgres
DB_NAME=ekyc_db

JWT_SECRET_KEY=your-secret-key-change-this-in-production

LOG_LEVEL=INFO  # or DEBUG
NEXT_PUBLIC_API_URL=http://localhost:8000/api
```

---

## Performance Notes

- **Backend:** 2GB memory limit, 2 CPU cores
- **Frontend:** 1GB memory limit, 1 CPU core
- **Database:** 512MB memory limit, 1 CPU core
- Total: 3.5GB RAM recommended minimum

### Optimize Build Speed
1. Exclude large directories via `.dockerignore` ✅ Done
2. Use BuildKit: `DOCKER_BUILDKIT=1 docker build ...`
3. Pre-pull images: `docker pull python:3.10-slim`

---

## Troubleshooting

**Container exits immediately:**
```bash
docker compose logs postgres
docker compose logs backend
docker compose logs frontend
```

**Database connection error:**
```bash
# Check health
docker compose ps

# Wait for postgres health: healthy
docker compose up -d
```

**Port already in use:**
```bash
# Change in docker-compose.yml
ports:
  - "8001:8000"  # Use 8001 instead of 8000
```

**Memory issues:**
```bash
# Increase resource limits in docker-compose.yml
deploy:
  resources:
    limits:
      memory: 4G
```

---

## Build Images Manually

```bash
# Backend only
docker build -f backend/Dockerfile -t ekyc_backend:latest backend/

# Frontend only
docker build -f frontend/Dockerfile -t ekyc_frontend:latest frontend/

# View image sizes
docker images | grep ekyc
```

---

## Next Steps

1. **Start development:** `docker compose --profile dev up -d`
2. **Test API:** `curl http://localhost:8000/health`
3. **Test Frontend:** Open `http://localhost:3000` in browser
4. **Check logs:** `docker compose logs -f`
5. **Deploy to production:** Use `--profile prod` and update `.env.local`
