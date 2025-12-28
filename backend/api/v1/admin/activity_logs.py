"""Admin activity log routes."""

from datetime import datetime, timedelta
from typing import Optional, Dict, Any, List

from fastapi import APIRouter, Depends, Query
from bson import ObjectId

from api.dependencies.auth import verify_admin_api_key
from infrastructure.persistence.mongodb.client import get_database
from config import mongodb_config


router = APIRouter(prefix="/admin/activity-logs", tags=["Admin - Activity Logs"])


def _map_action_type(action: str) -> str:
    action_lower = action.lower()
    if "login" in action_lower:
        return "login"
    if "logout" in action_lower:
        return "logout"
    if "feedback" in action_lower:
        return "feedback"
    if "profile" in action_lower:
        return "profile"
    if "bookmark" in action_lower:
        return "bookmark"
    if "error" in action_lower:
        return "error"
    return "chat"


@router.get("")
async def list_activity_logs(
    search: Optional[str] = None,
    action_type: Optional[str] = Query(default=None, alias="action_type"),
    date_range: Optional[str] = Query(default=None, alias="date_range"),
    user_id: Optional[str] = None,
    is_admin: bool = Depends(verify_admin_api_key),
):
    db = await get_database()
    query: Dict[str, Any] = {}

    if user_id:
        query["actor_id"] = user_id

    if date_range in {"today", "week"}:
        now = datetime.now()
        start = datetime(now.year, now.month, now.day)
        if date_range == "week":
            start = now - timedelta(days=7)
        query["timestamp"] = {"$gte": start}

    logs_cursor = (
        db[mongodb_config.collection_audit_logs]
        .find(query)
        .sort("timestamp", -1)
        .limit(200)
    )

    logs: List[Dict[str, Any]] = []
    actor_ids = set()

    async for doc in logs_cursor:
        actor_id = doc.get("actor_id", "")
        actor_ids.add(actor_id)
        logs.append(doc)

    users = {}
    if actor_ids:
        cursor = db.users.find({"_id": {"$in": [ObjectId(uid) for uid in actor_ids if ObjectId.is_valid(uid)]}})
        async for user in cursor:
            users[str(user["_id"])] = user

    response_items = []
    for doc in logs:
        actor_id = doc.get("actor_id", "")
        user_doc = users.get(actor_id, {})
        action = doc.get("action", "")
        mapped_action = _map_action_type(action)

        if action_type and action_type != "all" and mapped_action != action_type:
            continue

        user_name = user_doc.get("full_name") or user_doc.get("username") or "Unknown"
        user_email = user_doc.get("email", "unknown")

        text_blob = f"{user_name} {user_email} {action}".lower()
        if search and search.lower() not in text_blob:
            continue

        response_items.append(
            {
                "id": str(doc.get("_id")),
                "user_id": actor_id,
                "user_name": user_name,
                "user_email": user_email,
                "action": action,
                "action_type": mapped_action,
                "details": doc.get("target_type", ""),
                "metadata": {
                    "status_code": doc.get("status_code"),
                    "request_id": doc.get("request_id"),
                },
                "ip_address": doc.get("ip"),
                "user_agent": doc.get("user_agent"),
                "session_id": None,
                "created_at": doc.get("timestamp", datetime.now()).isoformat(),
            }
        )

    today_start = datetime.now().replace(hour=0, minute=0, second=0, microsecond=0)
    total_today = sum(
        1
        for item in response_items
        if datetime.fromisoformat(item["created_at"]) >= today_start
    )
    total_week = len(response_items)
    unique_users_today = len(
        {
            item["user_id"]
            for item in response_items
            if datetime.fromisoformat(item["created_at"]) >= today_start
        }
    )
    errors_today = sum(
        1
        for item in response_items
        if item["action_type"] == "error"
        and datetime.fromisoformat(item["created_at"]) >= today_start
    )

    return {
        "data": response_items,
        "stats": {
            "total_today": total_today,
            "total_week": total_week,
            "unique_users_today": unique_users_today,
            "errors_today": errors_today,
        },
    }
