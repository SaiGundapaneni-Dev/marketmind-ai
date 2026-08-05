# MarketMind AI — Portfolio Visualization Upgrade

## Replace

- `frontend/components/PortfolioTimeline.tsx`
- `frontend/app/page.tsx`

No backend changes or database migration are required.

The existing snapshot API already returns:

- total value
- total cost
- total profit
- total return
- health score
- created date

## Run

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

- Portfolio Performance appears directly below the four snapshot cards
- Portfolio Value and Invested Cost both appear on the chart
- 1W, 1M, 3M, 6M, 1Y, and ALL filters work
- Tooltip shows value, cost, profit, return, and health
- Chart has no permanent dots
- Current value and selected-period return are shown above the chart
- Performance summary appears
- Contributors and snapshot comparison still work
- Save Today's Snapshot still works

## Build and commit

```bash
npm run build

cd /d/Projects/portfolio-ai
git add .
git commit -m "Enhance dashboard portfolio performance visualization"
git push origin develop
```
