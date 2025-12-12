"""User-facing feedback DTOs."""

from pydantic import BaseModel, Field
from typing import Optional, List


class SubmitFeedbackRequest(BaseModel):
    session_id: str
    message_id: str
    user_id: str
    feedback_type: str = Field(
        ...,
        description="helpful, not_helpful, incorrect, incomplete, rating",
    )
    rating: Optional[int] = Field(None, ge=1, le=5)
    categories: Optional[List[str]] = Field(
        None,
        description="accuracy, relevance, completeness, clarity, speed",
    )
    comment: Optional[str] = None
    query: Optional[str] = None
    response: Optional[str] = None


class FeedbackResponse(BaseModel):
    id: str
    session_id: str
    message_id: str
    feedback_type: str
    rating: Optional[int] = None
    comment: Optional[str] = None


class FeedbackStatsResponse(BaseModel):
    total_feedbacks: int
    helpful_count: int
    not_helpful_count: int
    average_rating: float
    helpful_ratio: float


__all__ = [
    "SubmitFeedbackRequest",
    "FeedbackResponse",
    "FeedbackStatsResponse",
]
