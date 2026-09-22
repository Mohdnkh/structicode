"""Bounded process-local rate limiting for the local release candidate."""
from __future__ import annotations

from collections import OrderedDict, deque
from threading import Lock
import time

from .config import rate_window_seconds


class BoundedRateLimiter:
    def __init__(self, max_entries: int = 2048):
        self.max_entries = max_entries
        self._entries: OrderedDict[str, deque[float]] = OrderedDict()
        self._lock = Lock()

    def reset(self) -> None:
        with self._lock:
            self._entries.clear()

    def size(self) -> int:
        with self._lock:
            return len(self._entries)

    def allow(self, key: str, limit: int, now: float | None = None) -> bool:
        current = time.monotonic() if now is None else now
        cutoff = current - rate_window_seconds()
        with self._lock:
            timestamps = self._entries.get(key, deque())
            while timestamps and timestamps[0] <= cutoff:
                timestamps.popleft()
            if len(timestamps) >= limit:
                self._entries[key] = timestamps
                self._entries.move_to_end(key)
                return False
            timestamps.append(current)
            self._entries[key] = timestamps
            self._entries.move_to_end(key)
            while len(self._entries) > self.max_entries:
                self._entries.popitem(last=False)
            return True


RATE_LIMITER = BoundedRateLimiter()
