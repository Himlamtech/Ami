"""Admin Users Routes - UC-A-005: User & Profile Management."""

from fastapi import APIRouter, Depends, HTTPException, status, Query
from typing import Optional
from datetime import datetime, timedelta

from api.dependencies.auth import verify_admin_api_key
from api.schemas.admin_dto import (
    AdminUserResponse,
    UserDetailResponse,
    UserSessionResponse,
    UserAnalysisResponse,
    UserInsightsResponse,
)
from config.services import ServiceRegistry


router = APIRouter(prefix="/admin/users", tags=["Admin - User Management"])


@router.get("", response_model=list[AdminUserResponse])
async def list_users(
    major: Optional[str] = None,
    level: Optional[str] = None,
    active_since: Optional[str] = None,  # e.g., "7d", "30d"
    sort_by: str = Query(
        default="last_active", pattern="^(last_active|sessions_count|created_at)$"
    ),
    sort_order: str = Query(default="desc", pattern="^(asc|desc)$"),
    page: int = Query(default=1, ge=1),
    limit: int = Query(default=20, ge=1, le=100),
    is_admin: bool = Depends(verify_admin_api_key),
):
    """
    List all users with filtering and sorting.
    """
    profile_repo = ServiceRegistry.get_student_profile_repository()
    chat_repo = ServiceRegistry.get_chat_repository()

    skip = (page - 1) * limit

    # Parse active_since to date
    date_filter = None
    if active_since:
        days = int(active_since.rstrip("d"))
        date_filter = datetime.now() - timedelta(days=days)

    # Get profiles with filters
    profiles = await profile_repo.find_all(
        major=major,
        level=level,
        skip=skip,
        limit=limit,
    )

    result = []
    for profile in profiles:
        # Get session count for each user
        session_count = await chat_repo.count_by_user_id(profile.user_id)

        # Get last session date
        sessions = await chat_repo.find_by_user_id(profile.user_id, limit=1)
        last_active = sessions[0].updated_at if sessions else profile.updated_at

        # Filter by active_since if needed
        if date_filter and last_active < date_filter:
            continue

        result.append(
            AdminUserResponse(
                user_id=profile.user_id,
                major=profile.major,
                level=profile.level.value,
                interests=[t.topic for t in profile.topics_of_interest[:5]],
                sessions_count=session_count,
                last_active=last_active,
                created_at=profile.created_at,
            )
        )

    # Sort
    reverse = sort_order == "desc"
    if sort_by == "last_active":
        result.sort(key=lambda x: x.last_active or datetime.min, reverse=reverse)
    elif sort_by == "sessions_count":
        result.sort(key=lambda x: x.sessions_count, reverse=reverse)
    elif sort_by == "created_at":
        result.sort(key=lambda x: x.created_at or datetime.min, reverse=reverse)

    return result[:limit]


@router.get("/{user_id}", response_model=UserDetailResponse)
async def get_user_detail(
    user_id: str,
    is_admin: bool = Depends(verify_admin_api_key),
):
    """
    Get detailed information about a specific user.
    """
    profile_repo = ServiceRegistry.get_student_profile_repository()
    chat_repo = ServiceRegistry.get_chat_repository()
    feedback_repo = ServiceRegistry.get_feedback_repository()

    profile = await profile_repo.find_by_user_id(user_id)
    if not profile:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="User not found",
        )

    # Get stats
    sessions_count = await chat_repo.count_by_user_id(user_id)
    sessions = await chat_repo.find_by_user_id(user_id, limit=100)

    # Count messages from message count in sessions
    total_messages = profile.total_questions

    # Get feedback stats
    feedbacks = await feedback_repo.find_by_user_id(user_id, limit=100)
    positive_count = sum(1 for f in feedbacks if f.is_positive())
    negative_count = sum(1 for f in feedbacks if f.is_negative())

    return UserDetailResponse(
        user_id=profile.user_id,
        major=profile.major,
        level=profile.level.value,
        interests=[t.topic for t in profile.topics_of_interest],
        preferences={
            "language": profile.preferred_language,
            "detail_level": profile.preferred_detail_level,
        },
        sessions_count=sessions_count,
        total_messages=total_messages,
        positive_feedback=positive_count,
        negative_feedback=negative_count,
        last_active=sessions[0].updated_at if sessions else profile.updated_at,
        created_at=profile.created_at,
    )


@router.get("/{user_id}/sessions", response_model=list[UserSessionResponse])
async def get_user_sessions(
    user_id: str,
    page: int = Query(default=1, ge=1),
    limit: int = Query(default=20, ge=1, le=100),
    is_admin: bool = Depends(verify_admin_api_key),
):
    """
    Get all sessions for a specific user.
    """
    profile_repo = ServiceRegistry.get_student_profile_repository()
    chat_repo = ServiceRegistry.get_chat_repository()

    # Verify user exists
    profile = await profile_repo.find_by_user_id(user_id)
    if not profile:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="User not found",
        )

    skip = (page - 1) * limit
    sessions = await chat_repo.find_by_user_id(user_id, skip=skip, limit=limit)

    return [
        UserSessionResponse(
            session_id=str(session.id),
            title=session.title,
            message_count=session.message_count,
            created_at=session.created_at,
            updated_at=session.updated_at,
            is_archived=getattr(session, "is_archived", False),
        )
        for session in sessions
    ]


@router.get("/{user_id}/analyze", response_model=UserAnalysisResponse)
async def analyze_user(
    user_id: str,
    is_admin: bool = Depends(verify_admin_api_key),
):
    """
    Analyze user behavior and patterns.

    - Query patterns
    - Topic interests
    - Engagement metrics
    """
    profile_repo = ServiceRegistry.get_student_profile_repository()
    chat_repo = ServiceRegistry.get_chat_repository()
    search_log_repo = ServiceRegistry.get_search_log_repository()

    profile = await profile_repo.find_by_user_id(user_id)
    if not profile:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="User not found",
        )

    # Get all sessions
    sessions = await chat_repo.find_by_user_id(user_id, limit=100)

    # Calculate engagement metrics from profile and session data
    total_queries = profile.total_questions

    # Get search logs to analyze topics
    search_logs = await search_log_repo.find_by_user(user_id, limit=200)

    # Extract topics from queries
    topic_counts = {}
    for log in search_logs:
        # Simple topic extraction - can be improved with NLP
        words = log.query.lower().split()
        for word in words:
            if len(word) > 3:  # Skip short words
                topic_counts[word] = topic_counts.get(word, 0) + 1

    # Sort by frequency
    top_topics = sorted(topic_counts.items(), key=lambda x: -x[1])[:20]

    # Calculate activity by day of week
    activity_by_day = [0] * 7
    for session in sessions:
        day = session.created_at.weekday()
        activity_by_day[day] += 1

    # Calculate average messages per session
    avg_messages = total_queries / len(sessions) if sessions else 0

    return UserAnalysisResponse(
        user_id=user_id,
        total_sessions=len(sessions),
        total_queries=total_queries,
        avg_queries_per_session=round(avg_messages, 2),
        top_topics=[{"topic": t[0], "count": t[1]} for t in top_topics[:10]],
        activity_by_day={
            "monday": activity_by_day[0],
            "tuesday": activity_by_day[1],
            "wednesday": activity_by_day[2],
            "thursday": activity_by_day[3],
            "friday": activity_by_day[4],
            "saturday": activity_by_day[5],
            "sunday": activity_by_day[6],
        },
        engagement_score=min(100, total_queries * 2 + len(sessions) * 5),
    )


@router.get("/{user_id}/preferences")
async def get_user_preferences(
    user_id: str,
    is_admin: bool = Depends(verify_admin_api_key),
):
    """
    Get user's preferences and settings.
    """
    profile_repo = ServiceRegistry.get_student_profile_repository()

    profile = await profile_repo.find_by_user_id(user_id)
    if not profile:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="User not found",
        )

    return {
        "user_id": user_id,
        "preferences": {
            "language": profile.preferred_language,
            "detail_level": profile.preferred_detail_level,
        },
        "interests": [t.topic for t in profile.topics_of_interest],
        "major": profile.major,
        "level": profile.level.value,
    }


@router.patch("/{user_id}/preferences")
async def update_user_preferences(
    user_id: str,
    preferences: dict,
    is_admin: bool = Depends(verify_admin_api_key),
):
    """
    Update user preferences (admin override).
    """
    profile_repo = ServiceRegistry.get_student_profile_repository()

    profile = await profile_repo.find_by_user_id(user_id)
    if not profile:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="User not found",
        )

    # Update specific preference fields
    if "language" in preferences:
        profile.preferred_language = preferences["language"]
    if "detail_level" in preferences:
        profile.preferred_detail_level = preferences["detail_level"]
    profile.updated_at = datetime.now()

    await profile_repo.update(profile)

    return {
        "status": "ok",
        "user_id": user_id,
        "updated_preferences": {
            "language": profile.preferred_language,
            "detail_level": profile.preferred_detail_level,
        },
    }


@router.get("/insights/active", response_model=UserInsightsResponse)
async def get_active_users_insights(
    period: str = Query(default="week", pattern="^(day|week|month)$"),
    is_admin: bool = Depends(verify_admin_api_key),
):
    """
    Get insights about active users.

    - DAU/WAU/MAU
    - New vs returning users
    - User growth trends
    """
    profile_repo = ServiceRegistry.get_student_profile_repository()
    chat_repo = ServiceRegistry.get_chat_repository()

    now = datetime.now()
    days = {"day": 1, "week": 7, "month": 30}[period]
    date_from = now - timedelta(days=days)

    # Get all profiles
    all_profiles = await profile_repo.find_all(limit=10000)

    # Get recent sessions
    recent_sessions = await chat_repo.find_recent(date_from=date_from, limit=10000)

    # Count unique active users
    active_user_ids = set(s.user_id for s in recent_sessions)

    # Count new users in period
    new_users = [p for p in all_profiles if p.created_at and p.created_at >= date_from]

    # User distribution by major
    by_major = {}
    for p in all_profiles:
        major = p.major or "unknown"
        by_major[major] = by_major.get(major, 0) + 1

    # User distribution by level
    by_level = {}
    for p in all_profiles:
        level = p.level or "unknown"
        by_level[level] = by_level.get(level, 0) + 1

    return UserInsightsResponse(
        period=period,
        total_users=len(all_profiles),
        active_users=len(active_user_ids),
        new_users=len(new_users),
        returning_users=len(active_user_ids) - len(new_users),
        by_major=by_major,
        by_level=by_level,
    )
