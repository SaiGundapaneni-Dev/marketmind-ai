# MarketMind AI — Sprint 26 Scenario Simulator

## Add

- `backend/app/schemas/scenario_simulator_schema.py`
- `backend/app/services/scenario_simulator_service.py`
- `backend/app/api/scenario_simulator.py`
- `backend/tests/test_scenario_simulator_service.py`
- `frontend/app/scenario-simulator/page.tsx`

## Replace

- `backend/app/main.py`
- `frontend/components/Sidebar.tsx`

No database migration is required.

## Backend

```bash
cd /d/Projects/portfolio-ai/backend
pytest tests/test_scenario_simulator_service.py -v
pytest -v
uvicorn app.main:app --reload
```

Swagger:

```text
GET  /portfolio/scenarios/presets
POST /portfolio/scenarios/simulate
```

## Frontend

```bash
cd /d/Projects/portfolio-ai/frontend
rm -rf .next
npm run dev
```

Open:

```text
http://localhost:3000/scenario-simulator
```

## Verify

- Presets load from current portfolio symbols
- Custom symbol changes can be added
- Before/after portfolio value appears
- Impact amount and percentage are correct
- Risk and resilience are shown
- Holding-level impacts are sorted by magnitude
- Unknown symbols generate warnings
- Existing Dashboard, Daily Brief, Coach, Watchlist, Thesis, and Copilot work

## Build and commit

```bash
npm run build

cd /d/Projects/portfolio-ai
git add .
git commit -m "Sprint 26 - Add portfolio scenario simulator"
git push origin develop
```
