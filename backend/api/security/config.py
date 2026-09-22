"""Environment-backed runtime security settings with safe bounded defaults."""
from __future__ import annotations

from os import getenv

DEFAULT_CORS_ORIGINS = ("http://127.0.0.1:5173", "http://localhost:5173")
DEFAULT_MAX_REQUEST_BYTES = 1024 * 1024


def approved_cors_origins() -> list[str]:
    raw = getenv("STRUCTICODE_CORS_ORIGINS", "")
    values = [item.strip() for item in raw.split(",") if item.strip() and item.strip() != "*"]
    return values or list(DEFAULT_CORS_ORIGINS)


def max_request_bytes() -> int:
    try:
        value = int(getenv("STRUCTICODE_MAX_REQUEST_BYTES", str(DEFAULT_MAX_REQUEST_BYTES)))
    except ValueError:
        return DEFAULT_MAX_REQUEST_BYTES
    return min(max(value, 1024), 16 * 1024 * 1024)


def rate_window_seconds() -> int:
    try:
        value = int(getenv("STRUCTICODE_RATE_LIMIT_WINDOW_SECONDS", "60"))
    except ValueError:
        return 60
    return min(max(value, 1), 3600)


def rate_limit_for(path: str) -> int | None:
    variable = "STRUCTICODE_RATE_LIMIT_AUTH" if path.startswith("/api/v1/auth/") else "STRUCTICODE_RATE_LIMIT_ANALYSIS"
    if not (path.startswith("/api/v1/auth/") or path in {"/api/v1/analysis/element", "/api/v1/analysis/structure"}):
        return None
    try:
        # Keep the default high enough for ordinary local batch/design workflows;
        # deployments can set a materially lower limit through the environment.
        value = int(getenv(variable, "60" if variable.endswith("AUTH") else "1000"))
    except ValueError:
        return 60
    return min(max(value, 1), 10000)
