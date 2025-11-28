"""
Log Management routes for system monitoring and auditing.
Admin-only routes for viewing and managing system logs.
"""

from datetime import datetime, timedelta
from typing import Optional

from fastapi import APIRouter, Depends, HTTPException, Query, Request, status

from app.api.auth_dependencies import get_current_admin_user, get_current_user
from app.application.factory import ProviderFactory
from app.core.mongodb_models import (
    LogAction,
    LogCreate,
    LogLevel,
    LogListResponse,
    LogResponse,
    LogStatsResponse,
    UserInDB,
)

router = APIRouter(prefix="/logs", tags=["logs"])


async def create_log(
    level: LogLevel,
    action: LogAction,
    message: str,
    user_id: Optional[str] = None,
    username: Optional[str] = None,
    session_id: Optional[str] = None,
    metadata: dict = None,
    ip_address: Optional[str] = None,
    user_agent: Optional[str] = None,
):
    """
    Helper function to create a log entry.
    Can be called from other routes to log actions.
    """
    mongodb = await ProviderFactory.get_mongodb_client()
    
    log_data = {
        "level": level,
        "action": action,
        "message": message,
        "user_id": user_id,
        "username": username,
        "session_id": session_id,
        "metadata": metadata or {},
        "ip_address": ip_address,
        "user_agent": user_agent,
        "created_at": datetime.now(),
    }
    
    await mongodb.db.logs.insert_one(log_data)


@router.get("", response_model=LogListResponse)
async def list_logs(
    skip: int = Query(0, ge=0),
    limit: int = Query(50, ge=1, le=100),
    level: Optional[LogLevel] = None,
    action: Optional[LogAction] = None,
    user_id: Optional[str] = None,
    username: Optional[str] = None,
    start_date: Optional[datetime] = None,
    end_date: Optional[datetime] = None,
    search: Optional[str] = None,
    current_admin: UserInDB = Depends(get_current_admin_user),
):
    """
    List all logs with filtering and pagination (Admin only).
    
    Filters:
    - level: Filter by log level (debug, info, warning, error, critical)
    - action: Filter by action type
    - user_id: Filter by user ID
    - username: Filter by username
    - start_date: Filter logs after this date
    - end_date: Filter logs before this date
    - search: Search in message field
    """
    mongodb = await ProviderFactory.get_mongodb_client()
    
    # Build query
    query = {}
    
    if level:
        query["level"] = level
    
    if action:
        query["action"] = action
    
    if user_id:
        query["user_id"] = user_id
    
    if username:
        query["username"] = {"$regex": username, "$options": "i"}
    
    if start_date or end_date:
        query["created_at"] = {}
        if start_date:
            query["created_at"]["$gte"] = start_date
        if end_date:
            query["created_at"]["$lte"] = end_date
    
    if search:
        query["message"] = {"$regex": search, "$options": "i"}
    
    # Get total count
    total = await mongodb.db.logs.count_documents(query)
    
    # Get logs with pagination
    cursor = mongodb.db.logs.find(query).sort("created_at", -1).skip(skip).limit(limit)
    logs_data = await cursor.to_list(length=limit)
    
    # Convert to response models
    logs = []
    for log in logs_data:
        logs.append(
            LogResponse(
                id=str(log["_id"]),
                level=log["level"],
                action=log["action"],
                message=log["message"],
                user_id=log.get("user_id"),
                username=log.get("username"),
                session_id=log.get("session_id"),
                metadata=log.get("metadata", {}),
                ip_address=log.get("ip_address"),
                user_agent=log.get("user_agent"),
                created_at=log["created_at"],
            )
        )
    
    return LogListResponse(
        logs=logs,
        total=total,
        skip=skip,
        limit=limit,
    )


@router.get("/stats", response_model=LogStatsResponse)
async def get_log_stats(
    days: int = Query(7, ge=1, le=90),
    current_admin: UserInDB = Depends(get_current_admin_user),
):
    """
    Get log statistics for the last N days (Admin only).
    
    Returns:
    - Total logs
    - Breakdown by level
    - Breakdown by action
    - Recent errors count
    - Active users count
    """
    mongodb = await ProviderFactory.get_mongodb_client()
    
    # Calculate date range
    end_date = datetime.now()
    start_date = end_date - timedelta(days=days)
    
    # Total logs in period
    total_logs = await mongodb.db.logs.count_documents(
        {"created_at": {"$gte": start_date, "$lte": end_date}}
    )
    
    # Breakdown by level
    level_pipeline = [
        {"$match": {"created_at": {"$gte": start_date, "$lte": end_date}}},
        {"$group": {"_id": "$level", "count": {"$sum": 1}}},
    ]
    level_results = await mongodb.db.logs.aggregate(level_pipeline).to_list(length=10)
    by_level = {item["_id"]: item["count"] for item in level_results}
    
    # Breakdown by action
    action_pipeline = [
        {"$match": {"created_at": {"$gte": start_date, "$lte": end_date}}},
        {"$group": {"_id": "$action", "count": {"$sum": 1}}},
    ]
    action_results = await mongodb.db.logs.aggregate(action_pipeline).to_list(length=50)
    by_action = {item["_id"]: item["count"] for item in action_results}
    
    # Recent errors (last 24 hours)
    error_start = datetime.now() - timedelta(hours=24)
    recent_errors = await mongodb.db.logs.count_documents(
        {
            "level": {"$in": ["error", "critical"]},
            "created_at": {"$gte": error_start},
        }
    )
    
    # Active users (users who performed actions in the period)
    active_users_pipeline = [
        {"$match": {"created_at": {"$gte": start_date, "$lte": end_date}, "user_id": {"$ne": None}}},
        {"$group": {"_id": "$user_id"}},
        {"$count": "total"},
    ]
    active_users_result = await mongodb.db.logs.aggregate(active_users_pipeline).to_list(length=1)
    active_users = active_users_result[0]["total"] if active_users_result else 0
    
    return LogStatsResponse(
        total_logs=total_logs,
        by_level=by_level,
        by_action=by_action,
        recent_errors=recent_errors,
        active_users=active_users,
    )


@router.post("", response_model=LogResponse, status_code=status.HTTP_201_CREATED)
async def create_log_entry(
    log_data: LogCreate,
    request: Request,
    current_user: UserInDB = Depends(get_current_user),
):
    """
    Create a new log entry.
    Authenticated users can create logs for their own actions.
    """
    mongodb = await ProviderFactory.get_mongodb_client()
    
    # Get client info
    ip_address = log_data.ip_address or request.client.host if request.client else None
    user_agent = log_data.user_agent or request.headers.get("user-agent")
    
    # Create log document
    log_doc = {
        "level": log_data.level,
        "action": log_data.action,
        "message": log_data.message,
        "user_id": log_data.user_id or current_user.id,
        "username": log_data.username or current_user.username,
        "session_id": log_data.session_id,
        "metadata": log_data.metadata,
        "ip_address": ip_address,
        "user_agent": user_agent,
        "created_at": datetime.now(),
    }
    
    result = await mongodb.db.logs.insert_one(log_doc)
    log_id = str(result.inserted_id)
    
    return LogResponse(
        id=log_id,
        level=log_doc["level"],
        action=log_doc["action"],
        message=log_doc["message"],
        user_id=log_doc["user_id"],
        username=log_doc["username"],
        session_id=log_doc["session_id"],
        metadata=log_doc["metadata"],
        ip_address=log_doc["ip_address"],
        user_agent=log_doc["user_agent"],
        created_at=log_doc["created_at"],
    )


@router.delete("", status_code=status.HTTP_204_NO_CONTENT)
async def clear_old_logs(
    days: int = Query(90, ge=30, le=365),
    current_admin: UserInDB = Depends(get_current_admin_user),
):
    """
    Delete logs older than N days (Admin only).
    Minimum 30 days, maximum 365 days.
    """
    mongodb = await ProviderFactory.get_mongodb_client()
    
    cutoff_date = datetime.now() - timedelta(days=days)
    
    result = await mongodb.db.logs.delete_many({"created_at": {"$lt": cutoff_date}})
    
    # Log this action
    await create_log(
        level=LogLevel.INFO,
        action=LogAction.SYSTEM_ERROR,  # Using closest available action
        message=f"Deleted {result.deleted_count} logs older than {days} days",
        user_id=current_admin.id,
        username=current_admin.username,
    )
    
    return None

