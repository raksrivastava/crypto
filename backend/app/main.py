import logging

from fastapi import FastAPI, HTTPException, Request
from fastapi.exceptions import RequestValidationError
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse

from app.cache.redis_cache import InMemoryRedisCache
from app.config import settings
from app.crypto.decryptor import PayloadDecryptor
from app.crypto.keys import load_key_pair
from app.events.kafka_publisher import MockKafkaPublisher
from app.exceptions import EventPublishError
from app.rate_limit.middleware import PartnerRateLimitMiddleware
from app.rate_limit.sliding_window import SlidingWindowRateLimiter
from app.routers import keys, secure_payload

logging.basicConfig(level=logging.INFO)

app = FastAPI(title="UIDAI Sandbox E2EE Payload Simulator")

app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.cors_allowed_origins,
    allow_methods=["GET", "POST"],
    allow_headers=["*"],
)

_key_pair = load_key_pair(settings.rsa_key_size)
_cache = InMemoryRedisCache()
_limiter = SlidingWindowRateLimiter(
    cache=_cache,
    max_requests=settings.rate_limit_max_requests,
    window_seconds=settings.rate_limit_window_seconds,
)
app.add_middleware(PartnerRateLimitMiddleware, limiter=_limiter)

app.include_router(secure_payload.build_router(PayloadDecryptor(_key_pair), MockKafkaPublisher(), settings.kafka_topic))
app.include_router(keys.build_router(_key_pair))


@app.exception_handler(HTTPException)
async def http_exception_handler(request: Request, exc: HTTPException) -> JSONResponse:
    return JSONResponse(status_code=exc.status_code, content={"data": None, "message": exc.detail})


@app.exception_handler(RequestValidationError)
async def validation_exception_handler(request: Request, exc: RequestValidationError) -> JSONResponse:
    return JSONResponse(status_code=400, content={"data": None, "message": "Malformed request payload"})


@app.exception_handler(EventPublishError)
async def event_publish_exception_handler(request: Request, exc: EventPublishError) -> JSONResponse:
    return JSONResponse(status_code=502, content={"data": None, "message": str(exc)})


@app.exception_handler(Exception)
async def unhandled_exception_handler(request: Request, exc: Exception) -> JSONResponse:
    logging.getLogger("sandbox.errors").exception("Unhandled error while processing %s", request.url.path)
    return JSONResponse(status_code=500, content={"data": None, "message": "Internal server error"})


@app.get("/health")
def health() -> dict:
    return {"status": "ok"}
