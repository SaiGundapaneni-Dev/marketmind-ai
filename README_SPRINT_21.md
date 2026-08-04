# MarketMind AI — Sprint 21

## Files to add

- `backend/app/schemas/investment_review_schema.py`
- `backend/app/services/investment_review_service.py`
- `backend/app/api/investment_review.py`
- `backend/tests/test_investment_review_service.py`
- `frontend/components/InvestmentReviewCard.tsx`

## Files to replace

- `backend/app/main.py`
- `backend/app/services/copilot_service.py`
- `frontend/components/HoldingsTable.tsx`

No database migration is required.

## Backend test

From `backend`:

```bash
pytest tests/test_investment_review_service.py -v
pytest -v
```

## Frontend checks

From `frontend`:

```bash
npm run lint
npm run build
```

## Swagger verification

1. Sign in and copy/use the bearer token.
2. Ensure a holding has an investment thesis.
3. Run:

```text
GET /portfolio/thesis/review/{holding_id}
```

Expected fields include:

```text
status
recommendation
current_price
target_price
target_progress_percent
news
position
signals
risks
```

## Copilot verification

Try:

```text
Review my Apple investment
Analyze my thesis for NVDA
Should I continue holding AAPL?
Give me an investment review for MSFT
```

## Git commit

```bash
git add .
git commit -m "Sprint 21 - Add AI investment review engine"
git push origin develop
```
