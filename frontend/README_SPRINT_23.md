# MarketMind AI — Sprint 23 Dashboard 2.0

## Replace

- `frontend/app/page.tsx`

## Add

- `frontend/components/TodayIntelligence.tsx`
- `frontend/components/ActionMemo.tsx`

No backend changes or database migrations are required.

## Existing endpoints used

- `GET /portfolio/`
- `GET /portfolio/score`
- `GET /portfolio/intelligence`

## Run with Git Bash

```bash
cd /d/Projects/portfolio-ai/frontend
rm -rf .next
npm run dev
```

Open `http://localhost:3000/`.

## Verify

- Portfolio Score Hero loads
- Today's Intelligence appears
- Action Memo shows Hold, Monitor, or Review
- Snapshot cards show value, return, largest position, and risk
- Allocation, performance, and timeline load
- Add Holding and Holdings still work
- Thesis and AI Review still open from Holdings
- Embedded stock-news search is removed from the dashboard

## Build

```bash
npm run build
```

## Commit

```bash
git add .
git commit -m "Sprint 23 - Redesign dashboard around daily intelligence"
git push origin develop
```
