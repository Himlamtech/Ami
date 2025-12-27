"""Student profile repository interface."""

from abc import ABC, abstractmethod
from typing import Optional, List
from domain.entities.student_profile import StudentProfile


class IStudentProfileRepository(ABC):
    """Interface for student profile persistence."""

    @abstractmethod
    async def create(self, profile: StudentProfile) -> StudentProfile:
        """Create a new student profile."""
        pass

    @abstractmethod
    async def get_by_id(self, profile_id: str) -> Optional[StudentProfile]:
        """Get profile by ID."""
        pass

    @abstractmethod
    async def get_by_user_id(self, user_id: str) -> Optional[StudentProfile]:
        """Get profile by user ID."""
        pass

    @abstractmethod
    async def get_by_student_id(self, student_id: str) -> Optional[StudentProfile]:
        """Get profile by student ID (MSV)."""
        pass

    @abstractmethod
    async def update(self, profile: StudentProfile) -> StudentProfile:
        """Update an existing profile."""
        pass

    @abstractmethod
    async def delete(self, profile_id: str) -> bool:
        """Delete a profile."""
        pass

    @abstractmethod
    async def list_by_major(self, major: str, limit: int = 50) -> List[StudentProfile]:
        """List profiles by major."""
        pass

    @abstractmethod
    async def get_or_create(self, user_id: str) -> StudentProfile:
        """Get existing profile or create new one for user."""
        pass
