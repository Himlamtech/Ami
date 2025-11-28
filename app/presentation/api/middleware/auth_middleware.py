"""Authentication middleware."""

from fastapi import Request, HTTPException, status
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from app.infrastructure.factory import get_factory


security = HTTPBearer()


async def verify_token_middleware(
    request: Request,
    credentials: HTTPAuthorizationCredentials = None
):
    """
    Middleware to verify JWT token.
    
    Can be used as dependency in routes that require authentication.
    """
    if not credentials:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Missing authentication token",
            headers={"WWW-Authenticate": "Bearer"},
        )
    
    try:
        factory = get_factory()
        jwt_handler = factory.get_jwt_handler()
        
        # Verify token
        payload = jwt_handler.decode_token(credentials.credentials)
        
        # Add user info to request state
        request.state.user_id = payload.get("user_id")
        request.state.username = payload.get("sub")
        request.state.role_ids = payload.get("role_ids", [])
        
        return payload
        
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid or expired token",
            headers={"WWW-Authenticate": "Bearer"},
        )


async def get_current_user(request: Request):
    """
    Dependency to get current authenticated user.
    
    Usage:
        @router.get("/protected")
        async def protected_route(user = Depends(get_current_user)):
            return {"user_id": user["user_id"]}
    """
    if not hasattr(request.state, "user_id"):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Not authenticated"
        )
    
    return {
        "user_id": request.state.user_id,
        "username": request.state.username,
        "role_ids": request.state.role_ids,
    }
