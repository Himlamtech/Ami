"""Admin authentication - Simple API Key based auth for admin routes."""

from fastapi import Header, HTTPException, status, Depends
from typing import Optional

from app.config.settings import settings


def verify_admin_api_key(
    x_admin_api_key: Optional[str] = Header(None, alias="X-Admin-API-Key")
) -> bool:
    """
    Verify admin API key from request header.
    
    Admin operations (document management, crawling, etc.) require this key.
    The key should be set in environment variable ADMIN_API_KEY.
    
    Usage:
        @router.post("/documents")
        async def create_document(
            is_admin: bool = Depends(verify_admin_api_key),
        ):
            ...
    """
    if not x_admin_api_key:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="X-Admin-API-Key header is required for admin operations",
        )
    
    if x_admin_api_key != settings.admin_api_key:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Invalid admin API key",
        )
    
    return True


def get_user_id(
    x_user_id: Optional[str] = Header(None, alias="X-User-ID")
) -> str:
    """
    Get user ID from request header.
    
    The parent app should pass user_id via X-User-ID header.
    This is used for user-specific operations like chat history.
    """
    if not x_user_id:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="X-User-ID header is required",
        )
    return x_user_id


def get_optional_user_id(
    x_user_id: Optional[str] = Header(None, alias="X-User-ID")
) -> Optional[str]:
    """
    Get optional user ID from request header.
    
    Returns None if header is not provided.
    Useful for endpoints that work with or without user context.
    """
    return x_user_id
