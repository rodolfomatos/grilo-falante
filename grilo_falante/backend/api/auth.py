"""
API Authentication and Rate Limiting Middleware

Provides:
- Bearer token authentication
- Rate limiting per API token
- Prompt injection filtering
"""

import time
from collections import defaultdict
from collections import deque
from typing import Optional

from fastapi import HTTPException, Request, Response
from starlette.middleware.base import BaseHTTPMiddleware
from starlette.responses import JSONResponse

from grilo_falante.config import settings


SKIP_AUTH_PATHS = {
    "/health",
    "/docs",
    "/openapi.json",
    "/redoc",
    "/",
}

PROMPT_INJECTION_PATTERNS = [
    r"ignore\s+previous\s+instructions",
    r"ignore\s+all\s+previous",
    r"disregard\s+your\s+instructions",
    r"you\s+are\s+now\s+(?:a|an)\s+",
    r"forget\s+everything",
    r"new\s+system\s*[:]",
    r"new\s+instruction",
]


class RateLimiter:
    """Simple in-memory rate limiter."""

    def __init__(self, requests_per_minute: int = 60):
        self.requests_per_minute = requests_per_minute
        self._tokens: dict[str, deque] = defaultdict(lambda: deque(maxlen=requests_per_minute))

    def is_allowed(self, key: str) -> bool:
        now = time.time()
        cutoff = now - 60

        while self._tokens[key] and self._tokens[key][0] < cutoff:
            self._tokens[key].popleft()

        if len(self._tokens[key]) >= self.requests_per_minute:
            return False

        self._tokens[key].append(now)
        return True

    def get_remaining(self, key: str) -> int:
        now = time.time()
        cutoff = now - 60

        while self._tokens[key] and self._tokens[key][0] < cutoff:
            self._tokens[key].popleft()

        return self.requests_per_minute - len(self._tokens[key])


_rate_limiter = RateLimiter(requests_per_minute=settings.api_rate_limit)


def check_prompt_injection(content: str) -> bool:
    """Check if content contains prompt injection patterns."""
    import re

    content_lower = content.lower()
    for pattern in PROMPT_INJECTION_PATTERNS:
        if re.search(pattern, content_lower):
            return True
    return False


def extract_bearer_token(authorization: Optional[str]) -> Optional[str]:
    """Extract token from Authorization header."""
    if not authorization:
        return None
    if not authorization.startswith("Bearer "):
        return None
    return authorization[7:]


class AuthMiddleware(BaseHTTPMiddleware):
    """Authentication middleware for Grilo Falante API."""

    async def dispatch(self, request: Request, call_next) -> Response:
        path = request.url.path

        if path in SKIP_AUTH_PATHS or path.startswith("/public"):
            return await call_next(request)

        if not settings.requires_api_token:
            return await call_next(request)

        auth_header = request.headers.get("authorization")
        token = extract_bearer_token(auth_header)

        if not token:
            return JSONResponse(
                status_code=401,
                content={"detail": "Missing or invalid Authorization header. Use: Bearer <token>"},
                headers={"WWW-Authenticate": "Bearer"},
            )

        if token != settings.api_token:
            return JSONResponse(
                status_code=401,
                content={"detail": "Invalid API token"},
            )

        remaining = _rate_limiter.get_remaining(token)
        if remaining <= 0:
            return JSONResponse(
                status_code=429,
                content={"detail": "Rate limit exceeded. Try again in a minute."},
                headers={"Retry-After": "60"},
            )

        if not _rate_limiter.is_allowed(token):
            return JSONResponse(
                status_code=429,
                content={"detail": "Rate limit exceeded. Try again in a minute."},
                headers={"Retry-After": "60"},
            )

        response = await call_next(request)
        response.headers["X-RateLimit-Remaining"] = str(_rate_limiter.get_remaining(token))
        return response


async def verify_api_key(request: Request) -> str:
    """
    Dependency for endpoints that require API key authentication.
    Returns the validated token.
    """
    if not settings.requires_api_token:
        return "no-auth"

    auth_header = request.headers.get("authorization")
    token = extract_bearer_token(auth_header)

    if not token:
        raise HTTPException(
            status_code=401,
            detail="Missing or invalid Authorization header. Use: Bearer <token>",
            headers={"WWW-Authenticate": "Bearer"},
        )

    if token != settings.api_token:
        raise HTTPException(status_code=401, detail="Invalid API token")

    if not _rate_limiter.is_allowed(token):
        raise HTTPException(
            status_code=429,
            detail="Rate limit exceeded",
            headers={"Retry-After": "60"},
        )

    return token
