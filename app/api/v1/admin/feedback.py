"""Admin Feedback Routes - UC-A-002: Feedback Analysis Dashboard."""

from fastapi import APIRouter, Depends, HTTPException, status, Query
from typing import Optional
from datetime import datetime, timedelta

from app.api.dependencies.auth import verify_admin_api_key
from app.api.schemas.admin_dto import (
    FeedbackOverview,
    FeedbackTrend,
    FeedbackDistribution,
    FeedbackDashboardResponse,
    AdminFeedbackResponse,
    AdminFeedbackDetailResponse,
    AdminFeedbackListResponse,
    ReviewFeedbackRequest,
    FeedbackIssue,
    TopIssuesResponse,
)
from app.infrastructure.factory import get_factory
from app.domain.entities.feedback import FeedbackType, FeedbackStatus


router = APIRouter(prefix="/admin/feedback", tags=["Admin - Feedback"])


@router.get("/dashboard", response_model=FeedbackDashboardResponse)
async def get_feedback_dashboard(
    period: str = Query(default="30d", pattern="^(7d|30d|90d)$"),
    is_admin: bool = Depends(verify_admin_api_key),
):
    """
    Get feedback dashboard overview.

    Period options: 7d, 30d, 90d
    """
    factory = get_factory()
    feedback_repo = factory.get_feedback_repository()

    # Parse period
    days = {"7d": 7, "30d": 30, "90d": 90}[period]
    date_from = datetime.now() - timedelta(days=days)

    # Get current period stats
    current_stats = await feedback_repo.get_stats(date_from=date_from)

    # Get previous period for trend comparison
    prev_date_from = date_from - timedelta(days=days)
    prev_stats = await feedback_repo.get_stats(
        date_from=prev_date_from, date_to=date_from
    )

    # Calculate trend
    current_helpful = current_stats.get("helpful_count", 0)
    prev_helpful = prev_stats.get("helpful_count", 0)
    trend = 0.0
    if prev_helpful > 0:
        trend = ((current_helpful - prev_helpful) / prev_helpful) * 100

    # Calculate helpful ratio
    total = current_stats.get("total", 0)
    helpful = current_stats.get("helpful_count", 0)
    not_helpful = current_stats.get("not_helpful_count", 0)
    helpful_ratio = (
        helpful / (helpful + not_helpful) if (helpful + not_helpful) > 0 else 0.0
    )

    # Get trends
    trends_data = await feedback_repo.get_trends(days=days, group_by="day")

    return FeedbackDashboardResponse(
        overview=FeedbackOverview(
            total=total,
            helpful_count=helpful,
            not_helpful_count=not_helpful,
            helpful_ratio=round(helpful_ratio, 2),
            avg_rating=current_stats.get("avg_rating", 0.0),
            trend_vs_last_period=round(trend, 1),
        ),
        trends=[
            FeedbackTrend(
                date=t["date"],
                total=t["total"],
                helpful=t["helpful"],
                not_helpful=t["not_helpful"],
                avg_rating=t.get("avg_rating"),
            )
            for t in trends_data
        ],
        distribution=FeedbackDistribution(
            by_type=current_stats.get("by_type", {}),
            by_category=current_stats.get("by_category", {}),
        ),
    )


@router.get("/list", response_model=AdminFeedbackListResponse)
async def list_feedback(
    page: int = Query(default=1, ge=1),
    limit: int = Query(default=20, ge=1, le=100),
    feedback_type: Optional[str] = None,
    category: Optional[str] = None,
    date_from: Optional[datetime] = None,
    date_to: Optional[datetime] = None,
    reviewed: Optional[bool] = None,
    is_negative: Optional[bool] = None,
    is_admin: bool = Depends(verify_admin_api_key),
):
    """
    List all feedback with filters.

    Filters:
    - feedback_type: helpful, not_helpful, incorrect, incomplete, rating
    - category: accuracy, relevance, completeness, clarity, speed
    - date_from/date_to: Date range
    - reviewed: True/False
    - is_negative: True/False (show only negative/positive feedback)
    """
    factory = get_factory()
    feedback_repo = factory.get_feedback_repository()

    skip = (page - 1) * limit

    # Parse feedback type
    fb_type = None
    if feedback_type:
        try:
            fb_type = FeedbackType(feedback_type)
        except ValueError:
            pass

    # Parse status for reviewed filter
    status_filter = None
    if reviewed is True:
        status_filter = FeedbackStatus.REVIEWED
    elif reviewed is False:
        status_filter = FeedbackStatus.PENDING

    feedbacks = await feedback_repo.list_all(
        skip=skip,
        limit=limit,
        feedback_type=fb_type,
        status=status_filter,
        date_from=date_from,
        date_to=date_to,
        is_negative=is_negative,
    )

    total = await feedback_repo.count_all(
        feedback_type=fb_type,
        status=status_filter,
        date_from=date_from,
        date_to=date_to,
        is_negative=is_negative,
    )

    return AdminFeedbackListResponse(
        items=[
            AdminFeedbackResponse(
                id=fb.id,
                session_id=fb.session_id,
                message_id=fb.message_id,
                user_id=fb.user_id,
                feedback_type=fb.feedback_type.value,
                rating=fb.rating,
                categories=[c.value for c in fb.categories],
                comment=fb.comment,
                status=fb.status.value,
                reviewed_by=fb.reviewed_by,
                reviewed_at=fb.reviewed_at,
                created_at=fb.created_at,
            )
            for fb in feedbacks
        ],
        total=total,
        page=page,
        pages=(total + limit - 1) // limit,
        limit=limit,
    )


@router.get("/{feedback_id}", response_model=AdminFeedbackDetailResponse)
async def get_feedback_detail(
    feedback_id: str,
    is_admin: bool = Depends(verify_admin_api_key),
):
    """Get detailed feedback with message context."""
    factory = get_factory()
    feedback_repo = factory.get_feedback_repository()
    chat_repo = factory.get_chat_repository()
    profile_repo = factory.get_student_profile_repository()

    feedback = await feedback_repo.get_by_id(feedback_id)
    if not feedback:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Feedback not found",
        )

    # Get message context
    message_context = {}
    try:
        message = await chat_repo.get_message_by_id(feedback.message_id)
        if message:
            message_context = {
                "id": message.id,
                "role": message.role.value,
                "content": message.content,
                "created_at": message.created_at.isoformat(),
            }
    except:
        pass

    # Include stored query/response if available
    if feedback.query:
        message_context["query"] = feedback.query
    if feedback.response:
        message_context["response"] = feedback.response

    # Get user info
    user_info = None
    try:
        profile = await profile_repo.get_by_user_id(feedback.user_id)
        if profile:
            user_info = {
                "user_id": profile.user_id,
                "name": profile.name,
                "major": profile.major,
            }
    except:
        pass

    return AdminFeedbackDetailResponse(
        feedback=AdminFeedbackResponse(
            id=feedback.id,
            session_id=feedback.session_id,
            message_id=feedback.message_id,
            user_id=feedback.user_id,
            feedback_type=feedback.feedback_type.value,
            rating=feedback.rating,
            categories=[c.value for c in feedback.categories],
            comment=feedback.comment,
            status=feedback.status.value,
            reviewed_by=feedback.reviewed_by,
            reviewed_at=feedback.reviewed_at,
            created_at=feedback.created_at,
        ),
        message_context=message_context,
        user_info=user_info,
    )


@router.put("/{feedback_id}/review")
async def review_feedback(
    feedback_id: str,
    request: ReviewFeedbackRequest,
    is_admin: bool = Depends(verify_admin_api_key),
):
    """Mark feedback as reviewed."""
    factory = get_factory()
    feedback_repo = factory.get_feedback_repository()

    feedback = await feedback_repo.get_by_id(feedback_id)
    if not feedback:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Feedback not found",
        )

    if request.reviewed:
        feedback.mark_reviewed(
            reviewer_id="admin",  # TODO: Get actual admin ID
            notes=request.notes,
        )

    await feedback_repo.update(feedback)

    return {"status": "ok", "feedback_id": feedback_id}


@router.get("/top-issues", response_model=TopIssuesResponse)
async def get_top_issues(
    limit: int = Query(default=10, ge=1, le=50),
    period: str = Query(default="30d", pattern="^(7d|30d|90d)$"),
    is_admin: bool = Depends(verify_admin_api_key),
):
    """
    Get top issues from negative feedback.

    Analyzes negative feedback to identify common problems.
    """
    factory = get_factory()
    feedback_repo = factory.get_feedback_repository()

    days = {"7d": 7, "30d": 30, "90d": 90}[period]

    issues_data = await feedback_repo.get_top_issues(limit=limit, days=days)

    return TopIssuesResponse(
        issues=[
            FeedbackIssue(
                topic=issue["topic"],
                count=issue["count"],
                examples=issue.get("samples", []),
            )
            for issue in issues_data
        ]
    )
