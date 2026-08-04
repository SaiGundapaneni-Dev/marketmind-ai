# MarketMind AI — Sprint 24 Daily Intelligence Brief

## Add

- `backend/app/schemas/daily_brief_schema.py`
- `backend/app/services/daily_brief_service.py`
- `backend/tests/test_daily_brief_service.py`
- `frontend/app/daily-brief/page.tsx`

## Replace

- `backend/app/api/portfolio.py`
- `frontend/components/Sidebar.tsx`

No database migration is required.

## Backend tests

From Git Bash:

```bash
cd /d/Projects/portfolio-ai/backend
pytest tests/test_daily_brief_service.py -v
pytest -v
```

Start backend:

```bash
uvicorn app.main:app --reload
```

Swagger endpoint:

```text
GET /portfolio/daily-brief
```

## Frontend

```bash
cd /d/Projects/portfolio-ai/frontend
rm -rf .next
npm run dev
```

Open:

```text
http://localhost:3000/daily-brief
```

## Build

```bash
npm run build
```

## Commit

```bash
git add .
git commit -m "Sprint 24 - Add daily intelligence brief"
git push origin develop
```
