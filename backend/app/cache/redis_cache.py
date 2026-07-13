"""Distributed-cache contract used by the rate limiter, plus a mock implementation.

A real deployment backs `CacheClient` with a redis-py client; this
in-memory, thread-safe stand-in lets the rate limiter be exercised
without an external service, per the assignment's "mock" allowance.
"""
import threading
import time
from typing import Optional, Protocol


class CacheClient(Protocol):
    def get(self, key: str) -> Optional[int]: ...
    def set(self, key: str, value: int, ttl_seconds: int) -> None: ...
    def increment(self, key: str, ttl_seconds: int) -> int: ...


class InMemoryRedisCache:
    def __init__(self):
        self._store: dict[str, tuple[int, float]] = {}
        self._lock = threading.Lock()

    def get(self, key: str) -> Optional[int]:
        with self._lock:
            entry = self._store.get(key)
            if entry is None:
                return None
            value, expires_at = entry
            if expires_at < time.time():
                del self._store[key]
                return None
            return value

    def set(self, key: str, value: int, ttl_seconds: int) -> None:
        with self._lock:
            self._store[key] = (value, time.time() + ttl_seconds)

    def increment(self, key: str, ttl_seconds: int) -> int:
        with self._lock:
            current, expires_at = self._store.get(key, (0, time.time() + ttl_seconds))
            if expires_at < time.time():
                current = 0
                expires_at = time.time() + ttl_seconds
            new_value = current + 1
            self._store[key] = (new_value, expires_at)
            return new_value
