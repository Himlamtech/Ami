"""Verify JWT token use case."""

from typing import Optional
from app.domain.entities.user import User
from app.domain.exceptions.user_exceptions import (
    UserNotFoundException,
    UserNotActiveException,
    InvalidCredentialsException,
)
from app.application.interfaces.repositories.user_repository import IUserRepository


class VerifyTokenUseCase:
    """
    Use Case: Verify JWT token and return user.
    
    Business Rules:
    1. Token must be valid
    2. User must exist
    3. User must be active
    
    Single Responsibility: Token validation and user retrieval
    """
    
    def __init__(
        self,
        user_repository: IUserRepository,
        jwt_handler,  # Will be properly typed in infrastructure
    ):
        self.user_repo = user_repository
        self.jwt_handler = jwt_handler
    
    async def execute(self, token: str) -> User:
        """
        Verify token and return user.
        
        Args:
            token: JWT token
            
        Returns:
            User entity
            
        Raises:
            InvalidCredentialsException: Invalid token
            UserNotFoundException: User not found
            UserNotActiveException: User is inactive
        """
        # 1. Decode and validate token
        try:
            payload = self.jwt_handler.decode_token(token)
        except Exception:
            raise InvalidCredentialsException("Invalid or expired token")
        
        # 2. Extract username from payload
        username = payload.get("sub")
        if not username:
            raise InvalidCredentialsException("Invalid token payload")
        
        # 3. Get user from repository
        user = await self.user_repo.get_by_username(username)
        if not user:
            raise UserNotFoundException(username=username)
        
        # 4. Check if user is active
        if not user.is_active:
            raise UserNotActiveException(username=username)
        
        return user
