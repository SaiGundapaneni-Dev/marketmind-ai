# Sprint 29 — Deployment Readiness

## Replace

- `backend/app/core/config.py`
- `backend/app/core/database.py`
- `backend/app/main.py`
- `backend/alembic/env.py`
- `backend/alembic.ini`

## Add

- `backend/requirements-prod.txt`
- `backend/Dockerfile`
- `backend/.dockerignore`
- `backend/.env.example`
- `backend/.python-version`
- `frontend/.env.example`
- `frontend/vercel.json`
- `render.yaml`
- `.gitignore.production-additions`
- `DEPLOYMENT_READINESS_AUDIT.md`

## Local verification

```bash
cd /d/Projects/portfolio-ai/backend
cp .env.example .env
pytest -v
alembic upgrade head
uvicorn app.main:app --reload
```

Check:

```text
http://127.0.0.1:8000/health
http://127.0.0.1:8000/health/database
```

Docker:

```bash
docker build -t marketmind-api .
docker run --rm -p 8000:8000 --env-file .env marketmind-api
```

Frontend:

```bash
cd /d/Projects/portfolio-ai/frontend
cp .env.example .env.local
npm run build
```

## Production environment variables

Backend:

```text
ENVIRONMENT=production
DATABASE_URL=<managed PostgreSQL URL with sslmode=require>
JWT_SECRET_KEY=<long random secret>
JWT_ALGORITHM=HS256
ACCESS_TOKEN_EXPIRE_MINUTES=60
CORS_ORIGINS=https://your-vercel-domain.vercel.app
LOG_LEVEL=INFO
```

Frontend:

```text
NEXT_PUBLIC_API_BASE_URL=https://your-render-service.onrender.com
```

## Deployment order

1. Rotate the exposed database password.
2. Create Neon PostgreSQL.
3. Deploy backend to Render using `render.yaml`.
4. Verify `/health` and `/health/database`.
5. Deploy frontend to Vercel with root directory `frontend`.
6. Add the Vercel URL to backend `CORS_ORIGINS`.
7. Redeploy the backend.
8. Verify registration, login, dashboard, goals, Coach, Scenarios, and Watchtower.
