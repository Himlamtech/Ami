"""Feedback repository interface."""

from abc import ABC, abstractmethod
from typing import Optional, List
from datetime import datetime

from app.domain.entities.feedback import Feedback, FeedbackType, FeedbackStatus


class IFeedbackRepository(ABC):
    """
    Repository interface for Feedback entity.

    Handles feedback persistence and analytics queries.
    """

    # ===== CRUD Operations =====

    @abstractmethod
    async def create(self, feedback: Feedback) -> Feedback:
        """Create new feedback."""
        pass

    @abstractmethod
    async def get_by_id(self, feedback_id: str) -> Optional[Feedback]:
        """Get feedback by ID."""
        pass

    @abstractmethod
    async def update(self, feedback: Feedback) -> Feedback:
        """Update existing feedback."""
        pass

    @abstractmethod
    async def delete(self, feedback_id: str) -> bool:
        """Delete feedback."""
        pass

    # ===== Query Operations =====

    @abstractmethod
    async def get_by_message_id(self, message_id: str) -> Optional[Feedback]:
        """Get feedback for a specific message."""
        pass

    @abstractmethod
    async def list_by_session(
        self,
        session_id: str,
        skip: int = 0,
        limit: int = 100,
    ) -> List[Feedback]:
        """List all feedback for a session."""
        pass

    @abstractmethod
    async def list_by_user(
        self,
        user_id: str,
        skip: int = 0,
        limit: int = 100,
    ) -> List[Feedback]:
        """List all feedback from a user."""
        pass

    # ===== Admin Query Operations =====

    @abstractmethod
    async def list_all(
        self,
        skip: int = 0,
        limit: int = 100,
        feedback_type: Optional[FeedbackType] = None,
        status: Optional[FeedbackStatus] = None,
        date_from: Optional[datetime] = None,
        date_to: Optional[datetime] = None,
        is_negative: Optional[bool] = None,
    ) -> List[Feedback]:
        """List all feedback with filters (admin)."""
        pass

    @abstractmethod
    async def count_all(
        self,
        feedback_type: Optional[FeedbackType] = None,
        status: Optional[FeedbackStatus] = None,
        date_from: Optional[datetime] = None,
        date_to: Optional[datetime] = None,
        is_negative: Optional[bool] = None,
    ) -> int:
        """Count all feedback with filters."""
        pass

    @abstractmethod
    async def get_negative_feedback(
        self,
        skip: int = 0,
        limit: int = 100,
        reviewed: Optional[bool] = None,
    ) -> List[Feedback]:
        """Get negative feedback for review."""
        pass

    # ===== Analytics Operations =====

    @abstractmethod
    async def get_stats(
        self,
        date_from: Optional[datetime] = None,
        date_to: Optional[datetime] = None,
    ) -> dict:
        """
        Get feedback statistics.

        Returns:
            {
                "total": int,
                "helpful_count": int,
                "not_helpful_count": int,
                "avg_rating": float,
                "by_type": {type: count},
                "by_category": {category: count},
            }
        """
        pass

    @abstractmethod
    async def get_trends(
        self,
        days: int = 30,
        group_by: str = "day",
    ) -> List[dict]:
        """
        Get feedback trends over time.

        Returns list of {date, total, helpful, not_helpful, avg_rating}
        """
        pass

    @abstractmethod
    async def get_top_issues(
        self,
        limit: int = 10,
        days: int = 30,
    ) -> List[dict]:
        """
        Get top issues from negative feedback.

        Returns list of {topic, count, samples}
        """
        pass
