"""Admin student profile routes."""

from datetime import datetime, timedelta
from typing import Optional, Dict, Any

from fastapi import APIRouter, Depends, Query

from api.dependencies.auth import verify_admin_api_key
from config.services import ServiceRegistry


router = APIRouter(prefix="/admin/students", tags=["Admin - Students"])


def _build_student_item(profile, sessions_count: int, last_active: datetime | None) -> Dict[str, Any]:
    total_queries = profile.total_questions or 0
    engagement_score = min(total_queries / 50, 1.0) if total_queries else 0.0

    return {
        "id": profile.id,
        "user_id": profile.user_id,
        "name": profile.name or "",
        "email": profile.email or "",
        "student_id": profile.student_id or "",
        "major": profile.major or "",
        "level": profile.level.value if profile.level else "freshman",
        "class_name": profile.class_name,
        "status": "active",
        "total_sessions": sessions_count,
        "total_queries": total_queries,
        "avg_rating": 0.0,
        "engagement_score": engagement_score,
        "last_active": (last_active or profile.updated_at).isoformat(),
        "created_at": profile.created_at.isoformat(),
    }


@router.get("")
async def list_students(
    search: Optional[str] = None,
    status: Optional[str] = None,
    major: Optional[str] = None,
    engagement: Optional[str] = None,
    is_admin: bool = Depends(verify_admin_api_key),
):
    profile_repo = ServiceRegistry.get_student_profile_repository()
    chat_repo = ServiceRegistry.get_chat_repository()

    profiles = await profile_repo.find_all(major=major)
    items = []
    now = datetime.now()
    start_today = datetime(now.year, now.month, now.day)
    month_ago = now - timedelta(days=30)

    active_today_count = 0
    engagement_sum = 0.0
    new_this_month = 0

    for profile in profiles:
        if search:
            needle = search.lower()
            hay = " ".join(
                [
                    profile.name or "",
                    profile.email or "",
                    profile.student_id or "",
                    profile.major or "",
                ]
            ).lower()
            if needle not in hay:
                continue

        sessions_count = await chat_repo.count_by_user_id(profile.user_id)
        sessions = await chat_repo.find_by_user_id(profile.user_id, limit=1)
        last_active = sessions[0].updated_at if sessions else profile.updated_at

        item = _build_student_item(profile, sessions_count, last_active)

        if engagement == "high" and item["engagement_score"] < 0.7:
            continue
        if engagement == "medium" and not (0.4 <= item["engagement_score"] < 0.7):
            continue
        if engagement == "low" and item["engagement_score"] >= 0.4:
            continue

        if status and status != "all" and item["status"] != status:
            continue

        items.append(item)

        engagement_sum += item["engagement_score"]
        if last_active and last_active >= start_today:
            active_today_count += 1
        if profile.created_at and profile.created_at >= month_ago:
            new_this_month += 1

    avg_engagement = engagement_sum / len(items) if items else 0.0

    return {
        "data": items,
        "stats": {
            "total_students": len(items),
            "active_today": active_today_count,
            "avg_engagement": avg_engagement,
            "new_this_month": new_this_month,
        },
    }
