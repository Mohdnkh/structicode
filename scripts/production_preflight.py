"""Fail-closed validation for a public production environment.

The script validates configuration shape only. It never prints secret values and
does not contact a provider or a database.
"""

from __future__ import annotations

import os
import sys
from urllib.parse import urlparse


def validate_environment(environ: dict[str, str] | None = None) -> list[str]:
    values = os.environ if environ is None else environ
    errors: list[str] = []
    if values.get("STRUCTICODE_RUNTIME_MODE") != "production":
        errors.append("STRUCTICODE_RUNTIME_MODE must be production")

    database_url = values.get("STRUCTICODE_DATABASE_URL", "")
    if not database_url:
        errors.append("STRUCTICODE_DATABASE_URL is required")
    else:
        errors.extend(_database_url_errors(database_url))

    secret = values.get("STRUCTICODE_AUTH_SECRET", "")
    if len(secret.encode("utf-8")) < 32:
        errors.append("STRUCTICODE_AUTH_SECRET must be at least 32 UTF-8 bytes")

    origins = [item.strip() for item in values.get("STRUCTICODE_CORS_ORIGINS", "").split(",") if item.strip()]
    if not origins:
        errors.append("STRUCTICODE_CORS_ORIGINS must contain an HTTPS origin")
    for origin in origins:
        if not _is_browser_origin(origin):
            errors.append("STRUCTICODE_CORS_ORIGINS contains an invalid browser origin")

    for name, minimum, maximum in (
        ("STRUCTICODE_MAX_REQUEST_BYTES", 1024, 16 * 1024 * 1024),
        ("STRUCTICODE_RATE_LIMIT_WINDOW_SECONDS", 1, 3600),
        ("STRUCTICODE_RATE_LIMIT_AUTH", 1, 10000),
        ("STRUCTICODE_RATE_LIMIT_ANALYSIS", 1, 10000),
        ("PORT", 1, 65535),
    ):
        errors.extend(_integer_from(values, name, minimum=minimum, maximum=maximum))
    return errors


def _database_url_errors(value: str) -> list[str]:
    try:
        parsed = urlparse(value)
        hostname = parsed.hostname
        path = parsed.path.strip("/")
        # Accessing ``port`` validates malformed port syntax without exposing
        # the connection string in an error message.
        parsed.port
    except ValueError:
        return ["STRUCTICODE_DATABASE_URL has invalid PostgreSQL URL syntax"]
    if parsed.scheme not in {"postgresql", "postgresql+psycopg2"}:
        return ["production requires a PostgreSQL STRUCTICODE_DATABASE_URL"]
    if not hostname:
        return ["STRUCTICODE_DATABASE_URL must include a PostgreSQL hostname"]
    if not path:
        return ["STRUCTICODE_DATABASE_URL must include a PostgreSQL database name"]
    return []


def _is_browser_origin(value: str) -> bool:
    if value == "*":
        return False
    try:
        parsed = urlparse(value)
        parsed.port  # Validate malformed ports.
    except ValueError:
        return False
    return (
        parsed.scheme == "https"
        and bool(parsed.hostname)
        and parsed.username is None
        and parsed.password is None
        and parsed.path in {"", None}
        and not parsed.params
        and not parsed.query
        and not parsed.fragment
    )


def _integer_from(values: dict[str, str], name: str, *, minimum: int, maximum: int) -> list[str]:
    raw = values.get(name, "8000" if name == "PORT" else "")
    try:
        value = int(raw)
    except (TypeError, ValueError):
        return [f"{name} must be an integer"]
    if not minimum <= value <= maximum:
        return [f"{name} must be between {minimum} and {maximum}"]
    return []


def main() -> int:
    errors = validate_environment()
    if errors:
        for error in errors:
            print(f"ERROR: {error}", file=sys.stderr)
        return 1
    print("Production preflight passed")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
