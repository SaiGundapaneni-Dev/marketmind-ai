# Sprint 32 — Production Polish & Account Recovery

## Backend replace
- backend/app/core/config.py
- backend/app/core/security.py
- backend/app/api/auth.py
- backend/app/schemas/auth_schema.py
- backend/app/services/auth_service.py
- backend/app/repositories/user_repository.py
- backend/.env.example

## Backend add
- backend/app/services/email_service.py
- backend/tests/test_auth_recovery.py

No database migration is required.

## Frontend replace
- frontend/app/login/page.tsx
- frontend/app/register/page.tsx
- frontend/components/AuthGuard.tsx
- frontend/components/Sidebar.tsx
- frontend/app/layout.tsx

## Frontend add
- frontend/app/forgot-password/page.tsx
- frontend/app/reset-password/page.tsx
- frontend/app/settings/page.tsx
- frontend/app/privacy/page.tsx
- frontend/app/terms/page.tsx
- frontend/app/not-found.tsx
- frontend/app/icon.svg

## New auth endpoints
POST /auth/forgot-password
POST /auth/reset-password
PUT  /auth/me
POST /auth/change-password

## Password reset behavior

Development:
- Without SMTP, forgot-password returns `dev_reset_url`.
- The frontend shows a development reset link.
- You can fully test password reset locally without email.

Production:
- Reset tokens are never returned to the browser.
- Configure SMTP in Render to deliver reset emails.

## Render variables for production reset email

FRONTEND_URL=https://YOUR-VESTORA-VERCEL-DOMAIN
PASSWORD_RESET_EXPIRE_MINUTES=30
SMTP_HOST=<provider host>
SMTP_PORT=587
SMTP_USERNAME=<username>
SMTP_PASSWORD=<password>
SMTP_FROM_EMAIL=<verified sender>
SMTP_FROM_NAME=Vestora AI
SMTP_USE_TLS=true

Do not commit SMTP credentials.

## Test backend

```bash
cd /d/Projects/portfolio-ai/backend
pytest tests/test_auth_recovery.py -v
pytest -v
uvicorn app.main:app --reload
```

## Test frontend

```bash
cd /d/Projects/portfolio-ai/frontend
rm -rf .next
npm run dev
```

Verify:
- Login has Forgot password
- Register has password visibility + Terms/Privacy
- Forgot password works
- Development reset link works
- New password works at login
- Settings updates profile
- Settings changes password
- Mobile menu works
- Privacy and Terms are public
- Favicon shows Vestora V

Then:

```bash
npm run build
```

## Commit and deploy

```bash
cd /d/Projects/portfolio-ai
git add .
git commit -m "Sprint 32 - Add account recovery and production polish"
git push origin develop
git fetch origin
git push origin develop:main --force-with-lease
```

## Legal note
The included Privacy Policy and Terms are product drafts, not legal advice.
Have qualified counsel review them before broad commercial launch.
