"""Start the single-process production ASGI server."""

from __future__ import annotations

import os
import sys
from pathlib import Path

import uvicorn


def _port() -> int:
    raw = os.getenv("PORT", "8000")
    try:
        value = int(raw)
    except ValueError as exc:
        raise SystemExit("PORT must be an integer between 1 and 65535") from exc
    if not 1 <= value <= 65535:
        raise SystemExit("PORT must be an integer between 1 and 65535")
    return value


def main() -> None:
    # Executing this file by path places ``scripts`` on sys.path. Add the
    # application root so the backend namespace package is importable in the
    # production image as well as from a checkout.
    sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
    # P12 deliberately uses one worker because anonymous runs and rate limits are
    # process-local until a distributed state architecture is implemented.
    uvicorn.run(
        "backend.api.main:app",
        host="0.0.0.0",
        port=_port(),
        workers=1,
        reload=False,
    )


if __name__ == "__main__":
    main()
