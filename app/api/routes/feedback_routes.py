"""Feedback API routes."""

from fastapi import APIRouter, HTTPException, status
from pydantic import BaseModel, Field
from typing import Optional, List

from app.application.services.feedback_service import (
    FeedbackService,
    FeedbackType,
    FeedbackCategory,
)


# ===== DTOs =====

class SubmitFeedbackRequest(BaseModel):
    """Request to submit feedback."""
    session_id: str
    message_id: str
    user_id: str
    feedback_type: str = Field(
        ...,
        description="helpful, not_helpful, incorrect, incomplete, rating"
    )
    rating: Optional[int] = Field(None, ge=1, le=5)
    categories: Optional[List[str]] = Field(
        None,
        description="accuracy, relevance, completeness, clarity, speed"
    )
    comment: Optional[str] = None
    query: Optional[str] = None
    response: Optional[str] = None


class FeedbackResponse(BaseModel):
    """Feedback response."""
    id: str
    session_id: str
    message_id: str
    feedback_type: str
    rating: Optional[int] = None
    comment: Optional[str] = None


class FeedbackStatsResponse(BaseModel):
    """Feedback statistics response."""
    total_feedbacks: int
    helpful_count: int
    not_helpful_count: int
    average_rating: float
    helpful_ratio: float


# ===== Router =====

router = APIRouter(prefix="/feedback", tags=["Feedback"])


def get_feedback_service():
    """Get feedback service dependency."""
    from app.infrastructure.factory.provider_factory import ProviderFactory
    factory = ProviderFactory()
    return FeedbackService(factory.mongodb_database)


@router.post("/submit", response_model=FeedbackResponse)
async def submit_feedback(request: SubmitFeedbackRequest):
    """Submit feedback for a message."""
    service = get_feedback_service()
    
    # Parse feedback type
    try:
        fb_type = FeedbackType(request.feedback_type)
    except ValueError:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Invalid feedback type: {request.feedback_type}"
        )
    
    # Parse categories
    categories = []
    if request.categories:
        for cat in request.categories:
            try:
                categories.append(FeedbackCategory(cat))
            except ValueError:
                pass  # Skip invalid categories
    
    feedback = await service.submit_feedback(
        session_id=request.session_id,
        message_id=request.message_id,
        user_id=request.user_id,
        feedback_type=fb_type,
        rating=request.rating,
        categories=categories,
        comment=request.comment,
        query=request.query,
        response=request.response,
    )
    
    return FeedbackResponse(
        id=feedback.id,
        session_id=feedback.session_id,
        message_id=feedback.message_id,
        feedback_type=feedback.feedback_type.value,
        rating=feedback.rating,
        comment=feedback.comment,
    )


@router.post("/helpful/{message_id}")
async def mark_helpful(
    message_id: str,
    session_id: str,
    user_id: str,
):
    """Quick action: mark message as helpful."""
    service = get_feedback_service()
    
    feedback = await service.submit_feedback(
        session_id=session_id,
        message_id=message_id,
        user_id=user_id,
        feedback_type=FeedbackType.HELPFUL,
    )
    
    return {"status": "ok", "feedback_id": feedback.id}


@router.post("/not-helpful/{message_id}")
async def mark_not_helpful(
    message_id: str,
    session_id: str,
    user_id: str,
    comment: Optional[str] = None,
):
    """Quick action: mark message as not helpful."""
    service = get_feedback_service()
    
    feedback = await service.submit_feedback(
        session_id=session_id,
        message_id=message_id,
        user_id=user_id,
        feedback_type=FeedbackType.NOT_HELPFUL,
        comment=comment,
    )
    
    return {"status": "ok", "feedback_id": feedback.id}


@router.get("/stats", response_model=FeedbackStatsResponse)
async def get_feedback_stats():
    """Get overall feedback statistics."""
    service = get_feedback_service()
    stats = await service.get_stats()
    
    # Calculate helpful ratio
    total = stats.helpful_count + stats.not_helpful_count
    ratio = stats.helpful_count / total if total > 0 else 0.0
    
    return FeedbackStatsResponse(
        total_feedbacks=stats.total_feedbacks,
        helpful_count=stats.helpful_count,
        not_helpful_count=stats.not_helpful_count,
        average_rating=stats.average_rating,
        helpful_ratio=ratio,
    )


@router.get("/session/{session_id}", response_model=List[FeedbackResponse])
async def get_session_feedback(session_id: str):
    """Get all feedback for a session."""
    service = get_feedback_service()
    feedbacks = await service.get_feedback_for_session(session_id)
    
    return [
        FeedbackResponse(
            id=fb.id,
            session_id=fb.session_id,
            message_id=fb.message_id,
            feedback_type=fb.feedback_type.value,
            rating=fb.rating,
            comment=fb.comment,
        )
        for fb in feedbacks
    ]


@router.get("/message/{message_id}")
async def get_message_feedback(message_id: str):
    """Get feedback for a specific message."""
    service = get_feedback_service()
    feedback = await service.get_feedback_for_message(message_id)
    
    if not feedback:
        return {"feedback": None}
    
    return {
        "feedback": FeedbackResponse(
            id=feedback.id,
            session_id=feedback.session_id,
            message_id=feedback.message_id,
            feedback_type=feedback.feedback_type.value,
            rating=feedback.rating,
            comment=feedback.comment,
        )
    }
