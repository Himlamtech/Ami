"""Admin Audit Log Routes - UC-022: Audit Log & Change Tracking."""

from fastapi import APIRouter, Depends, Query, HTTPException, status
from typing import Optional, List
from datetime import datetime
from bson import ObjectId

from api.dependencies.auth import verify_admin_api_key
from api.schemas.audit_log_dto import AuditLogResponse
from infrastructure.persistence.mongodb.client import get_database
from config import mongodb_config

router = APIRouter(prefix="/admin/audit-logs", tags=["Admin - Audit Logs"])


@router.get("", response_model=List[AuditLogResponse])
async def list_audit_logs(
    actor_id: Optional[str] = None,
    action: Optional[str] = None,
    target_type: Optional[str] = None,
    start_date: Optional[str] = None,
    end_date: Optional[str] = None,
    page: int = Query(default=1, ge=1),
    limit: int = Query(default=50, ge=1, le=200),
    is_admin: bool = Depends(verify_admin_api_key),
):
    query = {}
    if actor_id:
        query["actor_id"] = actor_id
    if action:
        query["action"] = action
    if target_type:
        query["target_type"] = target_type
    if start_date or end_date:
        query["timestamp"] = {}
        if start_date:
            query["timestamp"]["$gte"] = datetime.fromisoformat(start_date)
        if end_date:
            query["timestamp"]["$lte"] = datetime.fromisoformat(end_date)

    skip = (page - 1) * limit
    db = await get_database()
    cursor = (
        db[mongodb_config.collection_audit_logs]
        .find(query)
        .sort("timestamp", -1)
        .skip(skip)
        .limit(limit)
    )

    logs = []
    async for doc in cursor:
        logs.append(
            AuditLogResponse(
                id=str(doc.get("_id")),
                actor_id=doc.get("actor_id", ""),
                actor_role=doc.get("actor_role", ""),
                action=doc.get("action", ""),
                target_type=doc.get("target_type", ""),
                target_id=doc.get("target_id"),
                status_code=doc.get("status_code", 0),
                ip=doc.get("ip"),
                user_agent=doc.get("user_agent"),
                request_id=doc.get("request_id"),
                timestamp=doc.get("timestamp", datetime.now()),
            )
        )

    return logs


@router.get("/{log_id}", response_model=AuditLogResponse)
async def get_audit_log(
    log_id: str,
    is_admin: bool = Depends(verify_admin_api_key),
):
    db = await get_database()
    doc = await db[mongodb_config.collection_audit_logs].find_one(
        {"_id": ObjectId(log_id)}
    )
    if not doc:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Audit log not found",
        )

    return AuditLogResponse(
        id=str(doc.get("_id")),
        actor_id=doc.get("actor_id", ""),
        actor_role=doc.get("actor_role", ""),
        action=doc.get("action", ""),
        target_type=doc.get("target_type", ""),
        target_id=doc.get("target_id"),
        status_code=doc.get("status_code", 0),
        ip=doc.get("ip"),
        user_agent=doc.get("user_agent"),
        request_id=doc.get("request_id"),
        timestamp=doc.get("timestamp", datetime.now()),
    )
