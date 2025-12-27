"""Chat history and session routes."""

from fastapi import APIRouter, Depends, HTTPException, status, Query
from typing import List, Optional
import json

from api.schemas.chat_dto import (
    CreateSessionRequest,
    SendMessageRequest,
    ChatSessionResponse,
    ChatMessageResponse,
    ChatHistoryResponse,
)
from api.dependencies.auth import get_user_id
from application.use_cases.chat import (
    CreateSessionInput,
    SendMessageInput,
    GetHistoryInput,
)
from domain.enums.chat_message_role import ChatMessageRole
from domain.exceptions.chat_exceptions import ChatSessionNotFoundException
from config.services import ServiceRegistry


router = APIRouter(prefix="/chat", tags=["chat"])


@router.post("/sessions", response_model=ChatSessionResponse)
async def create_session(
    request: CreateSessionRequest,
    user_id: str = Depends(get_user_id),
):
    """Create new chat session."""
    from application.use_cases.chat import CreateSessionUseCase

    chat_repo = ServiceRegistry.get_chat_repository()
    use_case = CreateSessionUseCase(chat_repo)

    result = await use_case.execute(
        CreateSessionInput(
            user_id=user_id,
            title=request.title,
        )
    )

    return ChatSessionResponse(
        id=result.session.id,
        user_id=result.session.user_id,
        title=result.session.title,
        message_count=result.session.message_count,
        created_at=result.session.created_at,
        updated_at=result.session.updated_at,
    )


@router.post("/messages", response_model=ChatMessageResponse)
async def send_message(request: SendMessageRequest):
    """Send message in chat session."""
    from application.use_cases.chat import SendMessageUseCase

    try:
        chat_repo = ServiceRegistry.get_chat_repository()
        use_case = SendMessageUseCase(chat_repo)

        result = await use_case.execute(
            SendMessageInput(
                session_id=request.session_id,
                role=ChatMessageRole(request.role),
                content=request.content,
                attachments=request.attachments,
                metadata=request.metadata,
            )
        )

        return ChatMessageResponse(
            id=result.message.id,
            session_id=result.message.session_id,
            role=result.message.role.value,
            content=result.message.content,
            created_at=result.message.created_at,
            attachments=result.message.attachments,
            metadata=result.message.metadata,
        )

    except ChatSessionNotFoundException as e:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=str(e))


@router.get("/sessions/{session_id}/history", response_model=ChatHistoryResponse)
async def get_history(session_id: str, limit: int = 50, skip: int = 0):
    """Get chat history for session."""
    from application.use_cases.chat import GetHistoryUseCase

    try:
        chat_repo = ServiceRegistry.get_chat_repository()
        use_case = GetHistoryUseCase(chat_repo)

        result = await use_case.execute(
            GetHistoryInput(
                session_id=session_id,
                limit=limit,
                skip=skip,
            )
        )

        return ChatHistoryResponse(
            session=ChatSessionResponse(
                id=result.session.id,
                user_id=result.session.user_id,
                title=result.session.title,
                message_count=result.session.message_count,
                created_at=result.session.created_at,
                updated_at=result.session.updated_at,
            ),
            messages=[
                ChatMessageResponse(
                    id=msg.id,
                    session_id=msg.session_id,
                    role=msg.role.value,
                    content=msg.content,
                    created_at=msg.created_at,
                    attachments=msg.attachments,
                    metadata=msg.metadata,
                )
                for msg in result.messages
            ],
            total=result.total_messages,
        )

    except ChatSessionNotFoundException as e:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=str(e))


@router.get("/sessions", response_model=List[ChatSessionResponse])
async def list_sessions(
    user_id: str = Depends(get_user_id),
    skip: int = 0,
    limit: int = 100,
):
    """List chat sessions for user."""
    chat_repo = ServiceRegistry.get_chat_repository()

    sessions = await chat_repo.list_sessions_by_user(
        user_id=user_id,
        skip=skip,
        limit=limit,
    )

    return [
        ChatSessionResponse(
            id=session.id,
            user_id=session.user_id,
            title=session.title,
            message_count=session.message_count,
            created_at=session.created_at,
            updated_at=session.updated_at,
        )
        for session in sessions
    ]


# ===== UC-U-005: Enhanced Conversation Management =====


@router.get("/sessions/search")
async def search_sessions(
    user_id: str = Depends(get_user_id),
    q: Optional[str] = Query(default=None, description="Search query in title"),
    include_archived: bool = Query(
        default=False, description="Include archived sessions"
    ),
    skip: int = Query(default=0, ge=0),
    limit: int = Query(default=50, ge=1, le=100),
):
    """Search chat sessions by title."""
    chat_repo = ServiceRegistry.get_chat_repository()

    sessions = await chat_repo.list_sessions_by_user(
        user_id=user_id,
        skip=skip,
        limit=limit,
        include_archived=include_archived,
    )

    # Filter by query if provided
    if q:
        q_lower = q.lower()
        sessions = [s for s in sessions if q_lower in s.title.lower()]

    total = await chat_repo.count_sessions_by_user(user_id, include_archived)

    return {
        "sessions": [
            ChatSessionResponse(
                id=session.id,
                user_id=session.user_id,
                title=session.title,
                message_count=session.message_count,
                created_at=session.created_at,
                updated_at=session.updated_at,
            )
            for session in sessions
        ],
        "total": total,
        "skip": skip,
        "limit": limit,
    }


@router.put("/sessions/{session_id}/rename")
async def rename_session(
    session_id: str,
    title: str = Query(..., min_length=1, max_length=200),
    user_id: str = Depends(get_user_id),
):
    """Rename a chat session."""
    chat_repo = ServiceRegistry.get_chat_repository()

    session = await chat_repo.get_session_by_id(session_id)
    if not session:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="Session not found"
        )

    if session.user_id != user_id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN, detail="Access denied"
        )

    session.update_title(title)
    updated = await chat_repo.update_session(session)

    return ChatSessionResponse(
        id=updated.id,
        user_id=updated.user_id,
        title=updated.title,
        message_count=updated.message_count,
        created_at=updated.created_at,
        updated_at=updated.updated_at,
    )


@router.post("/sessions/{session_id}/archive")
async def archive_session(
    session_id: str,
    user_id: str = Depends(get_user_id),
):
    """Archive a chat session."""
    chat_repo = ServiceRegistry.get_chat_repository()

    session = await chat_repo.get_session_by_id(session_id)
    if not session:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="Session not found"
        )

    if session.user_id != user_id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN, detail="Access denied"
        )

    await chat_repo.archive_session(session_id)
    return {"status": "archived", "session_id": session_id}


@router.post("/sessions/{session_id}/unarchive")
async def unarchive_session(
    session_id: str,
    user_id: str = Depends(get_user_id),
):
    """Restore an archived chat session."""
    chat_repo = ServiceRegistry.get_chat_repository()

    session = await chat_repo.get_session_by_id(session_id)
    if not session:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="Session not found"
        )

    if session.user_id != user_id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN, detail="Access denied"
        )

    await chat_repo.restore_session(session_id)
    return {"status": "restored", "session_id": session_id}


@router.delete("/sessions/{session_id}")
async def delete_session(
    session_id: str,
    user_id: str = Depends(get_user_id),
    permanent: bool = Query(default=False, description="Permanently delete"),
):
    """Delete a chat session."""
    chat_repo = ServiceRegistry.get_chat_repository()

    session = await chat_repo.get_session_by_id(session_id)
    if not session:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="Session not found"
        )

    if session.user_id != user_id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN, detail="Access denied"
        )

    if permanent:
        await chat_repo.hard_delete_session(session_id)
        return {"status": "deleted_permanently", "session_id": session_id}
    else:
        await chat_repo.delete_session(session_id)
        return {"status": "deleted", "session_id": session_id}


@router.get("/sessions/{session_id}/export")
async def export_session(
    session_id: str,
    user_id: str = Depends(get_user_id),
    format: str = Query(default="json", description="Export format: json or markdown"),
):
    """Export a chat session."""
    chat_repo = ServiceRegistry.get_chat_repository()

    session = await chat_repo.get_session_by_id(session_id)
    if not session:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="Session not found"
        )

    if session.user_id != user_id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN, detail="Access denied"
        )

    messages = await chat_repo.list_messages_by_session(session_id, limit=10000)

    if format == "markdown":
        lines = [
            f"# {session.title}\n",
            f"**Created:** {session.created_at.strftime('%Y-%m-%d %H:%M')}\n",
            f"**Messages:** {session.message_count}\n\n",
            "---\n\n",
        ]

        for msg in messages:
            role_label = (
                "🧑 **User**" if msg.role.value == "user" else "🤖 **Assistant**"
            )
            lines.append(f"{role_label} ({msg.created_at.strftime('%H:%M')})\n\n")
            lines.append(f"{msg.content}\n\n")
            lines.append("---\n\n")

        content = "".join(lines)
        return {
            "format": "markdown",
            "content": content,
            "filename": f"conversation_{session_id}.md",
        }
    else:
        # JSON format
        data = {
            "session": {
                "id": session.id,
                "title": session.title,
                "created_at": session.created_at.isoformat(),
                "updated_at": session.updated_at.isoformat(),
                "message_count": session.message_count,
            },
            "messages": [
                {
                    "id": msg.id,
                    "role": msg.role.value,
                    "content": msg.content,
                    "created_at": msg.created_at.isoformat(),
                }
                for msg in messages
            ],
        }

        return {
            "format": "json",
            "content": json.dumps(data, indent=2, ensure_ascii=False),
            "filename": f"conversation_{session_id}.json",
        }


@router.get("/sessions/archived")
async def list_archived_sessions(
    user_id: str = Depends(get_user_id),
    skip: int = Query(default=0, ge=0),
    limit: int = Query(default=50, ge=1, le=100),
):
    """List archived chat sessions."""
    chat_repo = ServiceRegistry.get_chat_repository()

    # Get all sessions including archived, then filter to only archived
    sessions = await chat_repo.list_sessions_by_user(
        user_id=user_id,
        skip=0,
        limit=10000,  # Get all to filter
        include_archived=True,
    )

    archived_sessions = [s for s in sessions if s.is_archived]

    # Apply pagination
    paginated = archived_sessions[skip : skip + limit]

    return {
        "sessions": [
            ChatSessionResponse(
                id=session.id,
                user_id=session.user_id,
                title=session.title,
                message_count=session.message_count,
                created_at=session.created_at,
                updated_at=session.updated_at,
            )
            for session in paginated
        ],
        "total": len(archived_sessions),
        "skip": skip,
        "limit": limit,
    }


__all__ = ["router"]
