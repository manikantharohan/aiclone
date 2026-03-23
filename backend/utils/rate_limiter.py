from __future__ import annotations

import time
from dataclasses import dataclass
from typing import Dict, List

from fastapi import HTTPException, Request, status, WebSocket

from config import get_settings


settings = get_settings()


@dataclass
class RateLimitConfig:
    requests_per_minute: int


class InMemoryRateLimiter:
    """
    Very simple in-memory IP-based rate limiter.

    NOTE: This is per-process and non-distributed. For production multi-instance
    deployments, use a shared store like Redis.
    """

    def __init__(self, cfg: RateLimitConfig) -> None:
        self.cfg = cfg
        self._requests: Dict[str, List[float]] = {}

    def is_allowed(self, key: str) -> bool:
        now = time.time()
        window_start = now - 60.0

        timestamps = self._requests.get(key, [])
        # Drop timestamps older than 60 seconds
        timestamps = [ts for ts in timestamps if ts >= window_start]

        if len(timestamps) >= self.cfg.requests_per_minute:
            self._requests[key] = timestamps
            return False

        timestamps.append(now)
        self._requests[key] = timestamps
        return True


rate_limiter = InMemoryRateLimiter(
    RateLimitConfig(
        requests_per_minute=settings.RATE_LIMIT_REQUESTS_PER_MINUTE,
    )
)


def get_client_ip(request: Request) -> str:
    """
    Extract a best-effort client IP from the incoming request, considering
    common proxy headers.
    """
    x_forwarded_for = request.headers.get("x-forwarded-for")
    if x_forwarded_for:
        # Could be a list of IPs; take the first one
        return x_forwarded_for.split(",")[0].strip()

    x_real_ip = request.headers.get("x-real-ip")
    if x_real_ip:
        return x_real_ip.strip()

    client_host = request.client.host if request.client else "unknown"
    return client_host


def get_client_ip_ws(websocket: WebSocket) -> str:
    """
    Extract client IP from a WebSocket connection.
    """
    x_forwarded_for = websocket.headers.get("x-forwarded-for")
    if x_forwarded_for:
        return x_forwarded_for.split(",")[0].strip()

    x_real_ip = websocket.headers.get("x-real-ip")
    if x_real_ip:
        return x_real_ip.strip()

    client = websocket.client
    return client.host if client else "unknown"


def enforce_rate_limit(request: Request) -> None:
    ip = get_client_ip(request)
    if not rate_limiter.is_allowed(ip):
        raise HTTPException(
            status_code=status.HTTP_429_TOO_MANY_REQUESTS,
            detail="Too many requests. Please slow down.",
        )


def enforce_rate_limit_ip(ip: str) -> None:
    if not rate_limiter.is_allowed(ip):
        raise HTTPException(
            status_code=status.HTTP_429_TOO_MANY_REQUESTS,
            detail="Too many requests. Please slow down.",
        )

