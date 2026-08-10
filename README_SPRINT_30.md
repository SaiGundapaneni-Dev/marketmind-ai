# Sprint 30 — Premium 30-Second Portfolio Experience

## Replace these files

- frontend/app/page.tsx
- frontend/components/Sidebar.tsx
- frontend/app/intelligence/page.tsx

## What changed

### Home
The dashboard is now a decision layer:
- portfolio value and total return
- plain-English portfolio health
- portfolio performance timeline
- one important message
- one thing to watch
- holdings
- Ask Vestora and Goals shortcuts

Removed from the primary dashboard:
- numeric Portfolio Score
- score breakdown cards
- AI Portfolio Coach block
- separate Action Memo block
- Allocation card
- Leaders/Laggards cards
- duplicated analytics

All backend analytics remain available.

### Portfolio
The `/intelligence` route stays unchanged technically, but the user-facing page is now simply called Portfolio.

Primary view:
- Portfolio health
- What matters most
- One thing to watch
- Ask Vestora

Advanced analytics are behind:
- View deeper analysis

### Sidebar
Primary navigation:
- Home
- Portfolio
- Ask Vestora
- Goals
- Watchlist

Secondary navigation is under More:
- Daily Brief
- Scenario Simulator
- Stock Search
- News
- IPO Analyzer
- Watchtower

## Brand direction
- Deep navy: #020817 / #0F172A
- Electric blue: #3B82F6
- Emerald: #10B981
- Gold: #F59E0B
- White: #FFFFFF

## Run locally

```bash
cd /d/Projects/portfolio-ai/frontend
rm -rf .next
npm run dev
```

Verify:
- Home loads
- chart loads
- holdings load
- Portfolio opens
- Ask Vestora opens
- Goals opens
- Watchlist opens
- More expands
- deeper analysis expands
- logout works

## Production build

```bash
npm run build
```

## Commit

```bash
cd /d/Projects/portfolio-ai

git add .
git commit -m "Sprint 30 - Premium 30 second portfolio experience"
git push origin develop
git fetch origin
git push origin develop:main --force-with-lease
```

Vercel should automatically redeploy the updated `main` branch.
