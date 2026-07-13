"""Runtime configuration sourced from environment variables (no hardcoded secrets)."""
import os
from dataclasses import dataclass, field


def _get_int(name: str, default: int) -> int:
    return int(os.environ.get(name, default))


def _get_float(name: str, default: float) -> float:
    return float(os.environ.get(name, default))


def _get_list(name: str, default: list[str]) -> list[str]:
    raw = os.environ.get(name)
    return raw.split(",") if raw else default


@dataclass(frozen=True)
class Settings:
    rsa_key_size: int = field(default_factory=lambda: _get_int("RSA_KEY_SIZE", 2048))
    rate_limit_max_requests: int = field(default_factory=lambda: _get_int("RATE_LIMIT_MAX_REQUESTS", 10))
    rate_limit_window_seconds: float = field(default_factory=lambda: _get_float("RATE_LIMIT_WINDOW_SECONDS", 1.0))
    kafka_topic: str = field(default_factory=lambda: os.environ.get("KAFKA_TOPIC", "Secure_Payload_Received"))
    cors_allowed_origins: list[str] = field(
        default_factory=lambda: _get_list("CORS_ALLOWED_ORIGINS", ["http://localhost:5173"])
    )


settings = Settings()
