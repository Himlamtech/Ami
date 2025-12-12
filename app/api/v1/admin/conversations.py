"""Admin Conversations Routes - UC-A-001: Quản lý Conversation History."""

from fastapi import APIRouter, Depends, HTTPException, status, Query
from typing import Optional
from datetime import datetime

from app.api.dependencies.auth import verify_admin_api_key
from app.api.schemas.admin_dto import (
    AdminSessionResponse,
    AdminSessionListResponse,
    AdminMessageResponse,
    AdminSessionDetailResponse,
    ExportRequest,
    ExportResponse,
)
from app.config.services import ServiceRegistry


router = APIRouter(prefix="/admin/conversations", tags=["Admin - Conversations"])


@router.get("", response_model=AdminSessionListResponse)
async def list_conversations(
    page: int = Query(default=1, ge=1),
    limit: int = Query(default=20, ge=1, le=100),
    user_id: Optional[str] = None,
    date_from: Optional[datetime] = None,
    date_to: Optional[datetime] = None,
    status: Optional[str] = Query(default=None, pattern="^(active|archived|deleted)$"),
    has_feedback: Optional[bool] = None,
    is_admin: bool = Depends(verify_admin_api_key),
):
    """
    List all conversations (admin view).

    Supports filtering by:
    - user_id: Filter by specific user
    - date_from/date_to: Date range
    - status: active, archived, or deleted
    - has_feedback: Has any feedback (positive or negative)
    """
    chat_repo = ServiceRegistry.get_chat_repository()

    skip = (page - 1) * limit

    # Build is_archived filter based on status
    is_archived = None
    if status == "archived":
        is_archived = True
    elif status == "active":
        is_archived = False

    # Get sessions with admin filters
    sessions = await chat_repo.find_all_sessions(
        skip=skip,
        limit=limit,
        user_id=user_id,
        date_from=date_from,
        date_to=date_to,
        is_archived=is_archived,
    )

    total = await chat_repo.count_all_sessions(
        user_id=user_id,
        date_from=date_from,
        date_to=date_to,
        is_archived=is_archived,
    )

    # Build response
    items = []
    for session in sessions:
        # Determine status
        if getattr(session, "is_deleted", False):
            session_status = "deleted"
        elif getattr(session, "is_archived", False):
            session_status = "archived"
        else:
            session_status = "active"

        items.append(
            AdminSessionResponse(
                id=session.id,
                user_id=session.user_id,
                user_name=None,  # Could be populated from profile
                title=session.title,
                message_count=session.message_count,
                status=session_status,
                has_negative_feedback=False,  # TODO: Check feedback
                last_activity=session.updated_at,
                created_at=session.created_at,
            )
        )

    return AdminSessionListResponse(
        items=items,
        total=total,
        page=page,
        pages=(total + limit - 1) // limit,
        limit=limit,
    )


@router.get("/{session_id}", response_model=AdminSessionDetailResponse)
async def get_conversation_detail(
    session_id: str,
    is_admin: bool = Depends(verify_admin_api_key),
):
    """Get detailed conversation view including messages and user profile."""
    chat_repo = ServiceRegistry.get_chat_repository()
    profile_repo = ServiceRegistry.get_student_profile_repository()

    # Get session
    session = await chat_repo.get_session_by_id(session_id)
    if not session:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Session not found",
        )

    # Get messages
    messages = await chat_repo.list_messages_by_session(
        session_id=session_id,
        limit=1000,
        include_deleted=False,
    )

    # Get user profile
    user_profile = None
    try:
        profile = await profile_repo.get_by_user_id(session.user_id)
        if profile:
            user_profile = {
                "id": profile.id,
                "user_id": profile.user_id,
                "name": profile.name,
                "student_id": profile.student_id,
                "major": profile.major,
                "level": profile.level.value,
            }
    except:
        pass

    # Determine status
    if session.is_deleted:
        session_status = "deleted"
    elif session.is_archived:
        session_status = "archived"
    else:
        session_status = "active"

    return AdminSessionDetailResponse(
        session=AdminSessionResponse(
            id=session.id,
            user_id=session.user_id,
            user_name=user_profile.get("name") if user_profile else None,
            title=session.title,
            message_count=session.message_count,
            status=session_status,
            has_negative_feedback=False,
            last_activity=session.last_message_at or session.updated_at,
            created_at=session.created_at,
        ),
        messages=[
            AdminMessageResponse(
                id=msg.id,
                role=msg.role.value,
                content=msg.content,
                sources=(
                    [ref.to_dict() for ref in msg.context_refs]
                    if msg.context_refs
                    else []
                ),
                feedback=None,  # TODO: Get feedback
                created_at=msg.created_at,
            )
            for msg in messages
        ],
        user_profile=user_profile,
    )


@router.get("/{session_id}/messages")
async def get_conversation_messages(
    session_id: str,
    page: int = Query(default=1, ge=1),
    limit: int = Query(default=50, ge=1, le=100),
    is_admin: bool = Depends(verify_admin_api_key),
):
    """Get paginated messages for a conversation."""
    chat_repo = ServiceRegistry.get_chat_repository()

    skip = (page - 1) * limit

    messages = await chat_repo.list_messages_by_session(
        session_id=session_id,
        skip=skip,
        limit=limit,
    )

    total = await chat_repo.count_messages_by_session(session_id)

    return {
        "items": [
            AdminMessageResponse(
                id=msg.id,
                role=msg.role.value,
                content=msg.content,
                sources=[],
                feedback=None,
                created_at=msg.created_at,
            )
            for msg in messages
        ],
        "total": total,
        "page": page,
        "pages": (total + limit - 1) // limit,
        "limit": limit,
    }


@router.post("/{session_id}/archive", status_code=status.HTTP_200_OK)
async def archive_conversation(
    session_id: str,
    is_admin: bool = Depends(verify_admin_api_key),
):
    """Archive a conversation."""
    chat_repo = ServiceRegistry.get_chat_repository()

    session = await chat_repo.get_session_by_id(session_id)
    if not session:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Session not found",
        )

    session.archive()
    await chat_repo.update_session(session)

    return {"status": "archived", "session_id": session_id}


@router.post("/{session_id}/restore", status_code=status.HTTP_200_OK)
async def restore_conversation(
    session_id: str,
    is_admin: bool = Depends(verify_admin_api_key),
):
    """Restore an archived conversation."""
    chat_repo = ServiceRegistry.get_chat_repository()

    session = await chat_repo.get_session_by_id(session_id)
    if not session:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Session not found",
        )

    session.unarchive()
    await chat_repo.update_session(session)

    return {"status": "restored", "session_id": session_id}


@router.delete("/{session_id}", status_code=status.HTTP_200_OK)
async def delete_conversation(
    session_id: str,
    is_admin: bool = Depends(verify_admin_api_key),
):
    """Delete a conversation (soft delete)."""
    chat_repo = ServiceRegistry.get_chat_repository()

    success = await chat_repo.delete_session(session_id)
    if not success:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Session not found",
        )

    return {"status": "deleted", "session_id": session_id}


@router.post("/export", response_model=ExportResponse)
async def export_conversations(
    request: ExportRequest,
    is_admin: bool = Depends(verify_admin_api_key),
):
    """
    Export multiple conversations.

    Formats: json, pdf, csv
    Returns export ID to track download status.
    """
    import uuid
    from app.application.services.chat_history_service import ChatHistoryService
    chat_repo = ServiceRegistry.get_chat_repository()

    export_id = str(uuid.uuid4())

    # For now, return immediate JSON export
    # TODO: Implement async export with file storage for PDF/CSV
    if request.format == "json":
        exports = []
        for session_id in request.session_ids:
            service = ChatHistoryService(chat_repo)
            try:
                data = await service.export_session_history(session_id, format="json")
                exports.append(data)
            except ValueError:
                continue

        # Store export data (could be stored in file/cache)
        # For MVP, we'll just return status
        return ExportResponse(
            export_id=export_id,
            status="completed",
            download_url=None,  # TODO: Implement file storage
        )

    return ExportResponse(
        export_id=export_id,
        status="pending",
        download_url=None,
    )
