"""File repository interface."""

from abc import ABC, abstractmethod
from typing import Optional, List
from app.domain.entities.file_metadata import FileMetadata
from app.domain.enums.file_type import FileType


class IFileRepository(ABC):
    """
    Repository interface for FileMetadata entity.

    Handles file metadata persistence (not the actual file storage).
    """

    @abstractmethod
    async def create(self, file_metadata: FileMetadata) -> FileMetadata:
        """
        Create new file metadata record.

        Args:
            file_metadata: File metadata to create

        Returns:
            Created file metadata with generated ID
        """
        pass

    @abstractmethod
    async def get_by_id(self, file_id: str) -> Optional[FileMetadata]:
        """Get file metadata by ID."""
        pass

    @abstractmethod
    async def update(self, file_metadata: FileMetadata) -> FileMetadata:
        """Update file metadata."""
        pass

    @abstractmethod
    async def delete(self, file_id: str) -> bool:
        """Delete file metadata (soft delete)."""
        pass

    @abstractmethod
    async def list_by_user(
        self,
        user_id: str,
        skip: int = 0,
        limit: int = 100,
        file_type: Optional[FileType] = None,
    ) -> List[FileMetadata]:
        """
        List files by user.

        Args:
            user_id: User ID
            skip: Number to skip
            limit: Maximum to return
            file_type: Optional filter by file type

        Returns:
            List of file metadata
        """
        pass

    @abstractmethod
    async def list_by_session(
        self,
        session_id: str,
        skip: int = 0,
        limit: int = 100,
    ) -> List[FileMetadata]:
        """List files associated with a chat session."""
        pass

    @abstractmethod
    async def count_by_user(
        self,
        user_id: str,
        file_type: Optional[FileType] = None,
    ) -> int:
        """Count files by user."""
        pass

    @abstractmethod
    async def get_total_size_by_user(self, user_id: str) -> int:
        """
        Get total file size for a user (in bytes).

        Args:
            user_id: User ID

        Returns:
            Total size in bytes
        """
        pass

    @abstractmethod
    async def exists(self, file_id: str) -> bool:
        """Check if file metadata exists."""
        pass
