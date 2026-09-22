"""ASGI security middleware for request limits, rate limits, and safe headers."""
from __future__ import annotations

import json
import logging
from starlette.types import ASGIApp, Message, Receive, Scope, Send

from .config import max_request_bytes, rate_limit_for
from .rate_limit import RATE_LIMITER

logger = logging.getLogger(__name__)


def _json_response(status: int, payload: dict, headers: list[tuple[bytes, bytes]] | None = None):
    body = json.dumps(payload).encode("utf-8")
    base = [(b"content-type", b"application/json"), (b"content-length", str(len(body)).encode())]
    return [
        {"type": "http.response.start", "status": status, "headers": base + (headers or [])},
        {"type": "http.response.body", "body": body},
    ]


class SecurityHeadersMiddleware:
    def __init__(self, app: ASGIApp): self.app = app

    async def __call__(self, scope: Scope, receive: Receive, send: Send):
        async def secure_send(message: Message):
            if message["type"] == "http.response.start":
                headers = list(message.get("headers", []))
                names = {name.lower() for name, _ in headers}
                if b"x-content-type-options" not in names: headers.append((b"x-content-type-options", b"nosniff"))
                if b"referrer-policy" not in names: headers.append((b"referrer-policy", b"no-referrer"))
                message = {**message, "headers": headers}
            await send(message)
        await self.app(scope, receive, secure_send)


class RequestSizeLimitMiddleware:
    def __init__(self, app: ASGIApp): self.app = app

    async def __call__(self, scope: Scope, receive: Receive, send: Send):
        if scope["type"] != "http" or not (scope["path"].startswith("/api/v1/") or scope["path"] in {"/analyze", "/generate-pdf"}):
            await self.app(scope, receive, send)
            return
        limit = max_request_bytes()
        chunks: list[bytes] = []
        total = 0
        while True:
            message = await receive()
            if message["type"] != "http.request":
                chunks.append(b"")
                break
            chunk = message.get("body", b"")
            total += len(chunk)
            if total > limit:
                payload = {"request_status": "error", "verification_status": "NOT_EVALUATED", "error": {"code": "REQUEST_TOO_LARGE", "message": "Request body exceeds the configured limit"}}
                for response in _json_response(413, payload): await send(response)
                return
            chunks.append(chunk)
            if not message.get("more_body", False): break
        # Replay with a proper message sequence, retaining an empty final chunk.
        replay_messages = iter(({"type": "http.request", "body": chunk, "more_body": index < len(chunks) - 1} for index, chunk in enumerate(chunks)))
        async def receive_buffered():
            try: return next(replay_messages)
            except StopIteration: return {"type": "http.disconnect"}
        await self.app(scope, receive_buffered, send)


class RateLimitMiddleware:
    def __init__(self, app: ASGIApp): self.app = app

    async def __call__(self, scope: Scope, receive: Receive, send: Send):
        if scope["type"] == "http" and scope.get("method") in {"POST", "PATCH"}:
            limit = rate_limit_for(scope["path"])
            if limit is not None:
                host = (scope.get("client") or ("unknown", 0))[0]
                if not RATE_LIMITER.allow(f"{host}:{scope['path']}", limit):
                    payload = {"request_status": "error", "verification_status": "NOT_EVALUATED", "error": {"code": "RATE_LIMITED", "message": "Request rate limit exceeded"}}
                    for response in _json_response(429, payload, [(b"retry-after", b"60")]): await send(response)
                    return
        await self.app(scope, receive, send)
