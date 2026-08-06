# Deployment Readiness Audit

## Critical security action

The previously uploaded `backend/alembic.ini` contained a plaintext PostgreSQL password.

Before public deployment:

1. Rotate that PostgreSQL user's password.
2. Confirm the previous password no longer works.
3. Remove the credential from Git history if it was ever committed.
4. Keep database URLs only in environment variables.

## Included improvements

- Environment-driven production CORS
- `/health` service health check
- `/health/database` database readiness check
- SQLAlchemy `pool_pre_ping`
- Alembic reads `DATABASE_URL`
- Docker backend
- Render Blueprint
- Minimal Linux-compatible dependencies
- Strong JWT secret validation
- Production Swagger disabled
- Vercel environment template
