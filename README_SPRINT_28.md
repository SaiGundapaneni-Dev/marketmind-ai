# MarketMind AI — Sprint 28 Goal-Based Investing

## Add

- `backend/app/models/investment_goal.py`
- `backend/app/schemas/investment_goal_schema.py`
- `backend/app/repositories/investment_goal_repository.py`
- `backend/app/services/investment_goal_service.py`
- `backend/app/api/investment_goal.py`
- `backend/tests/test_investment_goal_service.py`
- `backend/alembic/versions/b8f1a2c3d4e5_add_investment_goals_table.py`
- `frontend/app/goals/page.tsx`
- `frontend/components/GoalCard.tsx`
- `frontend/components/GoalProgressChart.tsx`
- `frontend/components/GoalAllocationCard.tsx`

## Replace

- `backend/app/models/models.py`
- `backend/app/main.py`
- `backend/alembic/env.py`
- `frontend/components/Sidebar.tsx`

## Migration

```bash
cd /d/Projects/portfolio-ai/backend
alembic upgrade head
alembic current
```

Expected revision: `b8f1a2c3d4e5`.

## Backend

```bash
pytest tests/test_investment_goal_service.py -v
pytest -v
uvicorn app.main:app --reload
```

Swagger endpoints: `GET/POST /goals`, `GET/PUT/DELETE /goals/{goal_id}`.

## Frontend

```bash
cd /d/Projects/portfolio-ai/frontend
rm -rf .next
npm run dev
```

Open `http://localhost:3000/goals`, then run `npm run build`.

## Commit

```bash
cd /d/Projects/portfolio-ai
git add .
git commit -m "Sprint 28 - Add goal based investing"
git push origin develop
```
