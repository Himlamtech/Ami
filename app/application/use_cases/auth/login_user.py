"""Login user use case."""

from dataclasses import dataclass
from typing import Optional
from app.domain.entities.user import User
from app.domain.exceptions.user_exceptions import (
    UserNotFoundException,
    InvalidCredentialsException,
    UserNotActiveException,
)
from app.application.interfaces.repositories.user_repository import IUserRepository


@dataclass
class LoginUserInput:
    """Input for login use case."""
    username: str
    password: str


@dataclass
class LoginUserOutput:
    """Output from login use case."""
    user: User
    # Note: JWT token generation will be handled by infrastructure layer
    # This use case only validates credentials and returns user


class LoginUserUseCase:
    """
    Use Case: Login user and validate credentials.
    
    Business Rules:
    1. User must exist
    2. Password must match
    3. User must be active
    4. Update login tracking
    
    Single Responsibility: Handle login workflow
    """
    
    def __init__(
        self,
        user_repository: IUserRepository,
        password_hasher,  # Will be properly typed in infrastructure layer
    ):
        self.user_repo = user_repository
        self.password_hasher = password_hasher
    
    async def execute(self, input_data: LoginUserInput) -> LoginUserOutput:
        """
        Execute login use case.
        
        Args:
            input_data: Login credentials
            
        Returns:
            LoginUserOutput with user entity
            
        Raises:
            UserNotFoundException: User doesn't exist
            InvalidCredentialsException: Wrong password
            UserNotActiveException: Account is inactive
        """
        # 1. Get user from repository
        user = await self.user_repo.get_by_username(input_data.username)
        if not user:
            raise UserNotFoundException(username=input_data.username)
        
        # 2. Verify password
        if not self.password_hasher.verify(input_data.password, user.hashed_password):
            raise InvalidCredentialsException()
        
        # 3. Check if user is active
        if not user.is_active:
            raise UserNotActiveException(username=user.username)
        
        # 4. Update login tracking (business logic in domain entity)
        user.record_login()
        
        # 5. Persist login tracking
        await self.user_repo.update(user)
        
        return LoginUserOutput(user=user)
