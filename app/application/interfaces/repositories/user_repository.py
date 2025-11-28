"""User repository interface."""

from abc import ABC, abstractmethod
from typing import Optional, List
from app.domain.entities.user import User


class IUserRepository(ABC):
    """
    Repository interface for User entity.
    
    Defines contract for user data access without coupling to specific database.
    Infrastructure layer will implement this interface.
    """
    
    @abstractmethod
    async def create(self, user: User) -> User:
        """
        Create new user.
        
        Args:
            user: User entity to create
            
        Returns:
            Created user with generated ID
            
        Raises:
            UserAlreadyExistsException: If user with same username/email exists
        """
        pass
    
    @abstractmethod
    async def get_by_id(self, user_id: str) -> Optional[User]:
        """
        Get user by ID.
        
        Args:
            user_id: User ID
            
        Returns:
            User entity if found, None otherwise
        """
        pass
    
    @abstractmethod
    async def get_by_username(self, username: str) -> Optional[User]:
        """
        Get user by username.
        
        Args:
            username: Username
            
        Returns:
            User entity if found, None otherwise
        """
        pass
    
    @abstractmethod
    async def get_by_email(self, email: str) -> Optional[User]:
        """
        Get user by email.
        
        Args:
            email: Email address
            
        Returns:
            User entity if found, None otherwise
        """
        pass
    
    @abstractmethod
    async def update(self, user: User) -> User:
        """
        Update existing user.
        
        Args:
            user: User entity with updated data
            
        Returns:
            Updated user
            
        Raises:
            UserNotFoundException: If user not found
        """
        pass
    
    @abstractmethod
    async def delete(self, user_id: str) -> bool:
        """
        Delete user.
        
        Args:
            user_id: User ID
            
        Returns:
            True if deleted, False if not found
        """
        pass
    
    @abstractmethod
    async def list_users(
        self,
        skip: int = 0,
        limit: int = 100,
        is_active: Optional[bool] = None,
    ) -> List[User]:
        """
        List all users with pagination.
        
        Args:
            skip: Number of users to skip
            limit: Maximum number of users to return
            is_active: Filter by active status (None = all users)
            
        Returns:
            List of user entities
        """
        pass
    
    @abstractmethod
    async def count(self, is_active: Optional[bool] = None) -> int:
        """
        Count total users.
        
        Args:
            is_active: Filter by active status (None = all users)
            
        Returns:
            Total count
        """
        pass
    
    @abstractmethod
    async def exists_by_username(self, username: str) -> bool:
        """
        Check if user exists by username.
        
        Args:
            username: Username to check
            
        Returns:
            True if exists, False otherwise
        """
        pass
    
    @abstractmethod
    async def exists_by_email(self, email: str) -> bool:
        """
        Check if user exists by email.
        
        Args:
            email: Email to check
            
        Returns:
            True if exists, False otherwise
        """
        pass
