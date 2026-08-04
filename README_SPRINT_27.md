# MarketMind AI — Sprint 27 AI Watchtower

## Add

- `backend/app/schemas/watchtower_schema.py`
- `backend/app/services/watchtower_service.py`
- `backend/app/api/watchtower.py`
- `backend/tests/test_watchtower_service.py`
- `frontend/app/watchtower/page.tsx`

## Replace

- `backend/app/main.py`
- `frontend/components/Sidebar.tsx`

No database migration is required.

## Backend

```bash
cd /d/Projects/portfolio-ai/backend
pytest tests/test_watchtower_service.py -v
pytest -v
uvicorn app.main:app --reload
```

Swagger:

```text
GET /watchtower
GET /watchtower?include_noise=true
```

## Frontend

```bash
cd /d/Projects/portfolio-ai/frontend
rm -rf .next
npm run dev
```

Open:

```text
http://localhost:3000/watchtower
```

## Verify

- Portfolio and watchlist symbols are monitored
- Critical, important, informational, and noise classifications appear
- Silence Filter hides noise by default
- Thesis impact shows supports, contradicts, neutral, or unknown
- Portfolio allocation appears for owned holdings
- Severity and source filters work
- Source links open correctly
- Existing Dashboard, Daily Brief, Coach, Scenarios, Watchlist, Thesis, and Copilot remain functional

## Build and commit

```bash
npm run build

cd /d/Projects/portfolio-ai
git add .
git commit -m "Sprint 27 - Add AI Watchtower material event intelligence"
git push origin develop
```
