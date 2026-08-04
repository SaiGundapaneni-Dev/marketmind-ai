# MarketMind AI — Sprint 25 AI Portfolio Coach

## Add

- `backend/app/schemas/ai_coach_schema.py`
- `backend/app/services/ai_coach_service.py`
- `backend/app/api/ai_coach.py`
- `backend/tests/test_ai_coach_service.py`
- `frontend/components/AIPortfolioCoach.tsx`

## Replace

- `backend/app/main.py`
- `frontend/app/page.tsx`

No database migration is required.

## Backend

```bash
cd /d/Projects/portfolio-ai/backend
pytest tests/test_ai_coach_service.py -v
pytest -v
uvicorn app.main:app --reload
```

Swagger:

```text
GET /portfolio/coach
```

## Frontend

```bash
cd /d/Projects/portfolio-ai/frontend
rm -rf .next
npm run dev
```

Open:

```text
http://localhost:3000/
```

## Verify

- AI Portfolio Coach appears above Portfolio Score
- Priorities include concentration, losses, missing theses, and overdue reviews
- Positive highlights appear when available
- Estimated review time is 2, 5, or 8 minutes
- Existing dashboard, Daily Brief, Thesis, and AI Review continue working

## Build

```bash
npm run build
```

## Commit

```bash
cd /d/Projects/portfolio-ai
git add .
git commit -m "Sprint 25 - Add proactive AI Portfolio Coach"
git push origin develop
```
