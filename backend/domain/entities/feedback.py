"""Feedback domain entity for collecting user feedback."""

from dataclasses import dataclass, field
from datetime import datetime
from typing import List, Optional, Dict, Any
from enum import Enum


class FeedbackType(Enum):
    """Type of feedback."""

    HELPFUL = "helpful"
    NOT_HELPFUL = "not_helpful"
    INCORRECT = "incorrect"
    INCOMPLETE = "incomplete"
    RATING = "rating"  # 1-5 star


class FeedbackCategory(Enum):
    """Category for detailed feedback."""

    ACCURACY = "accuracy"
    RELEVANCE = "relevance"
    COMPLETENESS = "completeness"
    CLARITY = "clarity"
    SPEED = "speed"


class FeedbackStatus(Enum):
    """Status of feedback review."""

    PENDING = "pending"
    REVIEWED = "reviewed"
    ACTIONED = "actioned"  # Action taken based on feedback
    DISMISSED = "dismissed"


@dataclass
class Feedback:
    """
    Feedback domain entity.

    Represents user feedback on AI responses for quality improvement.
    """

    # Identity
    id: str
    session_id: str
    message_id: str
    user_id: str

    # Feedback data
    feedback_type: FeedbackType
    rating: Optional[int] = None  # 1-5 for RATING type
    categories: List[FeedbackCategory] = field(default_factory=list)
    comment: Optional[str] = None

    # Context (for analysis)
    query: Optional[str] = None
    response: Optional[str] = None
    sources_used: List[str] = field(default_factory=list)

    # Review status (for admin)
    status: FeedbackStatus = FeedbackStatus.PENDING
    reviewed_by: Optional[str] = None
    reviewed_at: Optional[datetime] = None
    review_notes: Optional[str] = None
    linked_gap_id: Optional[str] = None  # Link to knowledge gap if created

    # Timestamps
    created_at: datetime = field(default_factory=datetime.now)
    updated_at: datetime = field(default_factory=datetime.now)

    # Business Logic Methods

    def is_negative(self) -> bool:
        """Check if feedback is negative."""
        return self.feedback_type in [
            FeedbackType.NOT_HELPFUL,
            FeedbackType.INCORRECT,
            FeedbackType.INCOMPLETE,
        ] or (self.rating is not None and self.rating <= 2)

    def is_positive(self) -> bool:
        """Check if feedback is positive."""
        return self.feedback_type == FeedbackType.HELPFUL or (
            self.rating is not None and self.rating >= 4
        )

    def mark_reviewed(self, reviewer_id: str, notes: Optional[str] = None) -> None:
        """Mark feedback as reviewed."""
        self.status = FeedbackStatus.REVIEWED
        self.reviewed_by = reviewer_id
        self.reviewed_at = datetime.now()
        self.review_notes = notes
        self.updated_at = datetime.now()

    def mark_actioned(self, gap_id: Optional[str] = None) -> None:
        """Mark feedback as actioned."""
        self.status = FeedbackStatus.ACTIONED
        self.linked_gap_id = gap_id
        self.updated_at = datetime.now()

    def dismiss(self, notes: Optional[str] = None) -> None:
        """Dismiss feedback."""
        self.status = FeedbackStatus.DISMISSED
        self.review_notes = notes
        self.updated_at = datetime.now()

    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary."""
        return {
            "id": self.id,
            "session_id": self.session_id,
            "message_id": self.message_id,
            "user_id": self.user_id,
            "feedback_type": self.feedback_type.value,
            "rating": self.rating,
            "categories": [c.value for c in self.categories],
            "comment": self.comment,
            "query": self.query,
            "response": self.response,
            "sources_used": self.sources_used,
            "status": self.status.value,
            "reviewed_by": self.reviewed_by,
            "reviewed_at": self.reviewed_at.isoformat() if self.reviewed_at else None,
            "review_notes": self.review_notes,
            "linked_gap_id": self.linked_gap_id,
            "created_at": self.created_at.isoformat(),
            "updated_at": self.updated_at.isoformat(),
        }

    def __repr__(self) -> str:
        return f"Feedback(id={self.id}, type={self.feedback_type.value}, status={self.status.value})"
