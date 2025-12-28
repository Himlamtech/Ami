"""AMI API key middleware."""

from fastapi import Request, HTTPException, status
from typing import Callable
import logging

from config import app_config

logger = logging.getLogger(__name__)


EXEMPT_PREFIXES = (
    "/health",
    "/docs",
    "/redoc",
    "/openapi.json",
)


async def ami_api_key_middleware(request: Request, call_next: Callable):
    """
    Middleware để bảo vệ API bằng AMI API key.
    Header yêu cầu: X-AMI-API-Key
    """
    path = request.url.path
    if path.startswith(EXEMPT_PREFIXES):
        return await call_next(request)

    required_key = app_config.ami_api_key
    if not required_key:
        logger.warning("AMI API key not configured; rejecting request to %s", path)
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail="AMI API key not configured",
        )

    provided_key = request.headers.get("X-AMI-API-Key")
    if not provided_key or provided_key != required_key:
        logger.warning("Invalid AMI API key for %s", path)
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid AMI API key",
        )

    return await call_next(request)
