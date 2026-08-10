# Sprint 31 — Public Landing & Onboarding

## Purpose

Anonymous visitors should understand Vestora before being asked to create an account.

## Route structure

- `/` — public Vestora landing page
- `/login` — public sign in
- `/register` — public registration
- `/dashboard` — authenticated premium dashboard
- all other current product routes remain authenticated

## Add

- `frontend/app/dashboard/page.tsx`

## Replace

- `frontend/app/page.tsx`
- `frontend/components/AuthGuard.tsx`
- `frontend/components/Sidebar.tsx`
- `frontend/app/layout.tsx`

## Important routing behavior

The old AuthGuard allowed only `/login` and `/register`, so anonymous visitors to `/` were redirected to login.

The new AuthGuard:
- allows anonymous visitors to `/`
- protects `/dashboard` and all product pages
- redirects logged-in visitors from `/`, `/login`, and `/register` to `/dashboard`

This also means the existing login/register pages can continue redirecting to `/` after successful authentication; the guard will immediately route the authenticated user to `/dashboard`.

## Test

```bash
cd /d/Projects/portfolio-ai/frontend
rm -rf .next
npm run dev
```

### Logged out
- `/` shows landing page
- `/login` works
- `/register` works
- `/dashboard` redirects to `/login`
- `/intelligence` redirects to `/login`

### Logged in
- `/` redirects to `/dashboard`
- `/login` redirects to `/dashboard`
- `/register` redirects to `/dashboard`
- sidebar Home opens `/dashboard`
- Portfolio, Ask Vestora, Goals and Watchlist continue working

## Build

```bash
npm run build
```

## Commit / deploy

```bash
cd /d/Projects/portfolio-ai

git add .
git commit -m "Sprint 31 - Add public Vestora landing and onboarding"
git push origin develop

git fetch origin
git push origin develop:main --force-with-lease
```

Vercel should automatically deploy the updated main branch.
