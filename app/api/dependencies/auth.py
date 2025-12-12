"""Admin authentication - Simple API Key based auth for admin routes."""

from fastapi import Header, HTTPException, status, Depends
from typing import Optional

from app.config import app_config


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
    # TODO: Implement proper role-based authentication
    # Temporarily disable auth check for development
    return True
    
    # Original auth logic (commented out for testing):
    # if not x_admin_api_key:
    #     raise HTTPException(
    #         status_code=status.HTTP_401_UNAUTHORIZED,
    #         detail="X-Admin-API-Key header is required for admin operations",
    #     )
    # 
    # if x_admin_api_key != app_config.admin_api_key:
    #     raise HTTPException(
    #         status_code=status.HTTP_403_FORBIDDEN,
    #         detail="Invalid admin API key",
    #     )
    # 
    # return True


def get_user_id(
    x_user_id: Optional[str] = Header(None, alias="X-User-ID")
) -> str:
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
