"""Sliding-window-counter rate limiter, implemented from scratch.

Blends the previous window's count (weighted by remaining overlap with
"now") with the current window's count. This avoids the burst-at-boundary
flaw of a fixed window while needing only two cache reads per check, so
it scales cleanly to a real distributed cache.
"""
import time

from app.cache.redis_cache import CacheClient


class SlidingWindowRateLimiter:
    def __init__(self, cache: CacheClient, max_requests: int, window_seconds: float):
        self._cache = cache
        self._max_requests = max_requests
        self._window_seconds = window_seconds

    def is_allowed(self, identity_key: str) -> bool:
        now = time.time()
        current_window = int(now // self._window_seconds)
        elapsed_fraction = (now % self._window_seconds) / self._window_seconds

        current_key = f"{identity_key}:{current_window}"
        previous_key = f"{identity_key}:{current_window - 1}"

        previous_count = self._cache.get(previous_key) or 0
        current_count = self._cache.get(current_key) or 0
        weighted_count = current_count + previous_count * (1 - elapsed_fraction)

        if weighted_count >= self._max_requests:
            return False

        self._cache.increment(current_key, ttl_seconds=int(self._window_seconds * 2) + 1)
        return True
