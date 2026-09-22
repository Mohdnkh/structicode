# Local Database and Authentication

## Local setup

Copy `.env.example` values into your local environment. Set a unique local `STRUCTICODE_AUTH_SECRET`; the repository does not provide a fallback secret.

```powershell
$env:STRUCTICODE_AUTH_SECRET = "replace-with-a-local-secret-at-least-32-bytes"
npm run db:migrate
```

The placeholder is intentionally at least 32 UTF-8 bytes; replace it with a unique local value before using authentication. Never commit a real secret.

Activate the repository virtual environment before running these commands. The root scripts intentionally use environment-resolved `python` and `python -m alembic`, so they work on Windows, macOS, and Linux without embedding `.venv` path syntax.

The default database is SQLite at `.structicode/structicode.db`, which is ignored by Git. Override it with `STRUCTICODE_DATABASE_URL` when testing another SQLAlchemy-supported database URL. PostgreSQL configuration support is not production qualification.

`STRUCTICODE_ACCESS_TOKEN_MINUTES` defaults to `30` and is bounded by the application. Local authentication endpoints are `POST /api/v1/auth/register`, `POST /api/v1/auth/login`, and `GET /api/v1/auth/me`.

Registration creates a local user, a default organization, and an `OWNER` membership in one transaction. Sign in returns a short-lived bearer access token. The frontend keeps that token only in `sessionStorage` and removes it after a 401 response.

Passwords use Passlib's `bcrypt_sha256` scheme, which hashes the complete UTF-8 password before bcrypt processing. The application still accepts 12–128 characters and never silently truncates long ASCII or Unicode passwords. Every `/api/v1/auth/*` operation checks `STRUCTICODE_AUTH_SECRET` before credential lookup or writes; an absent or blank secret returns `503 AUTH_NOT_CONFIGURED` without revealing account state.

The selected project is navigation state only and is stored in `sessionStorage`. Sign out, an invalid/expired token, and any authenticated HTTP 401 dispatch one `structicode-auth-cleared` event. The project context removes `structicode-active-project`, so a later user cannot inherit the previous user's project. If an accessible-project list no longer contains the stored selection, the UI selects the first accessible project or clears the selection. A project 404 clears the active selection while retaining the safe API error.

## Local reset

Stop the local backend, remove only the local `.structicode` database directory if you intentionally want to discard local users, organizations, projects, and persistent analysis records, then run `npm run db:migrate` again. Never use this as a production reset procedure.

## Limitations

This configuration has no production secret manager, SSO, MFA, password reset, email verification, invitations, cloud backup, durable PDF storage, production database hardening, deployment topology, or operational support. Do not use it as an institutional identity service.
