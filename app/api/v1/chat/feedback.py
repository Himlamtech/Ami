"""Feedback routes (user-facing)."""

from typing import List, Optional

from fastapi import APIRouter, HTTPException

from app.application.services.feedback_service import (
    FeedbackService,
    FeedbackType,
    FeedbackCategory,
)
from app.config.services import ServiceRegistry
from app.api.schemas.feedback_dto import (
    SubmitFeedbackRequest,
    FeedbackResponse,
    FeedbackStatsResponse,
)

router = APIRouter(prefix="/feedback", tags=["Feedback"])


def _get_feedback_service():
    return FeedbackService(factory.db)


@router.post("/submit", response_model=FeedbackResponse)
async def submit_feedback(request: SubmitFeedbackRequest):
    """Submit feedback for a message."""
    service = _get_feedback_service()

    try:
        fb_type = FeedbackType(request.feedback_type)
    except ValueError:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Invalid feedback type: {request.feedback_type}",
        )

    categories: List[FeedbackCategory] = []
    if request.categories:
        for cat in request.categories:
            try:
                categories.append(FeedbackCategory(cat))
            except ValueError:
                continue

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
    service = _get_feedback_service()

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
    service = _get_feedback_service()

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
    service = _get_feedback_service()
    stats = await service.get_stats()

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
    service = _get_feedback_service()
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
    service = _get_feedback_service()
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


__all__ = ["router"]
