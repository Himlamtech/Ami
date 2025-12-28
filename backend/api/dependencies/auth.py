"""Admin authentication - role-based auth for admin routes."""

from fastapi import Header, HTTPException, status
from typing import Optional
from bson import ObjectId

from infrastructure.persistence.mongodb.client import get_database


async def verify_admin_api_key(
    x_user_id: Optional[str] = Header(None, alias="X-User-ID"),
) -> bool:
    """
    Verify admin/manager access from user role.

    Admin operations (document management, crawling, etc.) require admin or manager role.

    Usage:
        @router.post("/documents")
        async def create_document(
            is_admin: bool = Depends(verify_admin_api_key),
        ):
            ...
    """
    if not x_user_id:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="X-User-ID header is required for admin operations",
        )

    db = await get_database()
    try:
        user = await db.users.find_one({"_id": ObjectId(x_user_id)})
    except Exception:
        user = None

    if not user or not user.get("is_active", True):
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="User not allowed",
        )

    role = user.get("role", "user")
    if role not in ("admin", "manager"):
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Admin access required",
        )

    return True


def get_user_id(x_user_id: Optional[str] = Header(None, alias="X-User-ID")) -> str:
    """
    Get user ID from request header.

    The parent app should pass user_id via X-User-ID header.
    This is used for user-specific operations like chat history.
    Returns 'anonymous' if header is not provided.
    """
    return x_user_id or "anonymous"


def get_optional_user_id(
    x_user_id: Optional[str] = Header(None, alias="X-User-ID")
) -> Optional[str]:
    """
    Get optional user ID from request header.

    Returns None if header is not provided.
    Useful for endpoints that work with or without user context.
    """
    return x_user_id
