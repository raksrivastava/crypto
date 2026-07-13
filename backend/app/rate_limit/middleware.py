"""Custom ASGI interceptor that rejects over-limit requests before decryption runs.

Scoped to the one CPU-expensive endpoint so unrelated routes (health
checks, public key retrieval) are never throttled.
"""
import json

from starlette.middleware.base import BaseHTTPMiddleware
from starlette.requests import Request
from starlette.responses import JSONResponse

from app.rate_limit.sliding_window import SlidingWindowRateLimiter

RATE_LIMITED_PATH = "/api/v1/sandbox/secure-payload"


class PartnerRateLimitMiddleware(BaseHTTPMiddleware):
    def __init__(self, app, limiter: SlidingWindowRateLimiter):
        super().__init__(app)
        self._limiter = limiter

    async def dispatch(self, request: Request, call_next):
        if request.method != "POST" or request.url.path != RATE_LIMITED_PATH:
            return await call_next(request)

        partner_id = await self._extract_partner_id(request)
        if partner_id and not self._limiter.is_allowed(partner_id):
            return JSONResponse(
                status_code=429,
                content={"data": None, "message": "Rate limit exceeded: max requests/second per partner_id"},
            )
        return await call_next(request)

    @staticmethod
    async def _extract_partner_id(request: Request) -> str | None:
        body_bytes = await request.body()
        try:
            body = json.loads(body_bytes)
        except json.JSONDecodeError:
            return None
        return body.get("partner_id") if isinstance(body, dict) else None
