# Production Environment Template

Placeholder names only. Store values in the selected provider's secret and environment facility. Never commit real credentials.

```text
STRUCTICODE_RUNTIME_MODE=production
STRUCTICODE_DATABASE_URL=
STRUCTICODE_AUTH_SECRET=
STRUCTICODE_ACCESS_TOKEN_MINUTES=
STRUCTICODE_CORS_ORIGINS=
STRUCTICODE_MAX_REQUEST_BYTES=
STRUCTICODE_RATE_LIMIT_WINDOW_SECONDS=
STRUCTICODE_RATE_LIMIT_AUTH=
STRUCTICODE_RATE_LIMIT_ANALYSIS=
PORT=
```

Production CORS must contain the exact public HTTPS origin. The database URL must use PostgreSQL. `scripts/production_preflight.py` validates these rules without printing secret values.
