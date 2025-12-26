"""Bookmark repository interface."""

from abc import ABC, abstractmethod
from typing import Optional, List

from app.domain.entities.bookmark import Bookmark


class IBookmarkRepository(ABC):
    """Interface for bookmark data access."""

    @abstractmethod
    async def create(self, bookmark: Bookmark) -> Bookmark:
        """Create a new bookmark."""
        pass

    @abstractmethod
    async def get_by_id(self, bookmark_id: str) -> Optional[Bookmark]:
        """Get bookmark by ID."""
        pass

    @abstractmethod
    async def get_by_user(
        self,
        user_id: str,
        skip: int = 0,
        limit: int = 50,
        include_archived: bool = False,
    ) -> List[Bookmark]:
        """Get bookmarks for a user."""
        pass

    @abstractmethod
    async def search(
        self,
        user_id: str,
        query: str,
        tags: Optional[List[str]] = None,
        folder: Optional[str] = None,
        skip: int = 0,
        limit: int = 50,
    ) -> List[Bookmark]:
        """Search bookmarks by query, tags, or folder."""
        pass

    @abstractmethod
    async def update(self, bookmark: Bookmark) -> Bookmark:
        """Update an existing bookmark."""
        pass

    @abstractmethod
    async def delete(self, bookmark_id: str) -> bool:
        """Delete a bookmark."""
        pass

    @abstractmethod
    async def count_by_user(self, user_id: str, include_archived: bool = False) -> int:
        """Count bookmarks for a user."""
        pass

    @abstractmethod
    async def get_tags_by_user(self, user_id: str) -> List[str]:
        """Get all unique tags used by a user."""
        pass

    @abstractmethod
    async def get_folders_by_user(self, user_id: str) -> List[str]:
        """Get all unique folders used by a user."""
        pass

    @abstractmethod
    async def get_pinned(self, user_id: str) -> List[Bookmark]:
        """Get pinned bookmarks for a user."""
        pass
