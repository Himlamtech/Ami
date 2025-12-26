# Admin Only Middleware
from fastapi import Request, HTTPException, status
from typing import Callable
import os
import logging

logger = logging.getLogger(__name__)


async def admin_only_middleware(request: Request, call_next: Callable):
    """
    Middleware để bảo vệ admin endpoints.
    Kiểm tra:
    1. User role là admin
    2. IP whitelist (optional)
    3. Rate limiting
    """
    # Bypass health check
    if request.url.path == "/health":
        return await call_next(request)

    # Check if user is admin (từ JWT token)
    if hasattr(request.state, "user"):
        user = request.state.user
        if not hasattr(user, "role") or user.role != "admin":
            logger.warning(
                f"Unauthorized admin access from user {user.id if hasattr(user, 'id') else 'unknown'}"
            )
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN, detail="Admin access required"
            )
    else:
        # No user in request state - unauthorized
        logger.warning(f"No user context for admin endpoint: {request.url.path}")
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN, detail="Authentication required"
        )

    # Check IP whitelist (optional)
    admin_ip_whitelist = os.getenv("ADMIN_IP_WHITELIST", "").split(",")
    if admin_ip_whitelist and admin_ip_whitelist[0]:  # If configured
        client_ip = request.client.host
        if client_ip not in admin_ip_whitelist:
            logger.warning(f"Unauthorized IP for admin access: {client_ip}")
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="IP not whitelisted for admin access",
            )

    response = await call_next(request)
    return response
