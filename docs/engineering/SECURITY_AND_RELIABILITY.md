# Security and Reliability Boundaries

P10 establishes a QA and security gate for the current local release candidate. It is not a production-security certification.

- Authentication is a local JWT foundation only; SSO, MFA, password reset, and email verification are not implemented.
- Rate limiting is bounded and process-local. A distributed gateway limiter is required for multi-instance deployment.
- SQLite is local-development persistence. Production backups, HTTPS topology, and a production secret manager are not configured.
- There is no multi-instance cache or session coordination and no production observability deployment.
- No production deployment has been completed.
- CORS defaults to the documented local frontend origins and can be explicitly configured for a controlled local environment.
- Request-size and model-complexity limits reduce local abuse risk but are not a substitute for an internet-facing gateway.
- Dependency audit results are recorded in the P10 audit; advisories require normal dependency maintenance and risk review.
