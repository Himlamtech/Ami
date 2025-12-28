"""Audit log middleware for admin actions."""

from fastapi import Request
from typing import Callable
from datetime import datetime
from bson import ObjectId
import logging

from infrastructure.persistence.mongodb.client import get_database
from config import mongodb_config

logger = logging.getLogger(__name__)


AUDITED_METHODS = {"POST", "PUT", "PATCH", "DELETE"}
ADMIN_PREFIX = "/api/v1/admin"


def _extract_target_type(path: str) -> str:
    parts = path.strip("/").split("/")
    # Expected: api/v1/admin/<resource>/...
    if len(parts) >= 4:
        return parts[3]
    return "admin"


async def audit_log_middleware(request: Request, call_next: Callable):
    response = await call_next(request)

    path = request.url.path
    if not path.startswith(ADMIN_PREFIX) or request.method not in AUDITED_METHODS:
        return response

    user_id = request.headers.get("X-User-ID")
    if not user_id:
        return response

    try:
        db = await get_database()
        user = None
        try:
            user = await db.users.find_one({"_id": ObjectId(user_id)})
        except Exception:
            user = None

        log_doc = {
            "actor_id": user_id,
            "actor_role": (user or {}).get("role", "unknown"),
            "action": f"{request.method} {path}",
            "target_type": _extract_target_type(path),
            "target_id": None,
            "status_code": response.status_code,
            "ip": request.client.host if request.client else "unknown",
            "user_agent": request.headers.get("user-agent"),
            "request_id": request.headers.get("x-request-id"),
            "timestamp": datetime.now(),
        }
        await db[mongodb_config.collection_audit_logs].insert_one(log_doc)
    except Exception as exc:
        logger.warning("Failed to write audit log: %s", exc)

    return response
