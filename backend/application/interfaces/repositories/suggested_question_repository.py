"""Suggested question repository interface."""

from abc import ABC, abstractmethod
from typing import List, Optional

from domain.entities.suggested_question import SuggestedQuestion


class ISuggestedQuestionRepository(ABC):
    """Repository interface for question bank storage."""

    @abstractmethod
    async def create(self, question: SuggestedQuestion) -> SuggestedQuestion:
        """Create a suggested question."""
        pass

    @abstractmethod
    async def get_by_id(self, question_id: str) -> Optional[SuggestedQuestion]:
        """Get a question by ID."""
        pass

    @abstractmethod
    async def get_by_ids(self, question_ids: List[str]) -> List[SuggestedQuestion]:
        """Get questions by ID list."""
        pass

    @abstractmethod
    async def find_by_text(self, text: str) -> Optional[SuggestedQuestion]:
        """Find a question by text."""
        pass

    @abstractmethod
    async def list_active(self, limit: int = 10) -> List[SuggestedQuestion]:
        """List active questions."""
        pass
