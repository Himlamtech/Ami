"""Chat history routes - Refactored."""

from fastapi import APIRouter, Depends, HTTPException, status
from typing import List

from app.presentation.api.schemas.chat_dto import (
    CreateSessionRequest,
    SendMessageRequest,
    ChatSessionResponse,
    ChatMessageResponse,
    ChatHistoryResponse,
)
from app.application.use_cases.chat import (
    CreateSessionInput,
    SendMessageInput,
    GetHistoryInput,
)
from app.domain.enums.chat_message_role import ChatMessageRole
from app.domain.exceptions.chat_exceptions import ChatSessionNotFoundException
from app.infrastructure.factory import get_factory


router = APIRouter(prefix="/chat", tags=["chat"])


async def get_current_user_id():
    """Get current user ID from auth (simplified for now)."""
    # TODO: Implement proper auth dependency
    return "user_123"


@router.post("/sessions", response_model=ChatSessionResponse)
async def create_session(
    request: CreateSessionRequest,
    user_id: str = Depends(get_current_user_id),
):
    """Create new chat session."""
    from app.application.use_cases.chat import CreateSessionUseCase
    
    factory = get_factory()
    chat_repo = factory.get_chat_repository()
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
    from app.application.use_cases.chat import SendMessageUseCase
    
    try:
        factory = get_factory()
        chat_repo = factory.get_chat_repository()
        use_case = SendMessageUseCase(chat_repo)
        
        result = await use_case.execute(
            SendMessageInput(
                session_id=request.session_id,
                role=ChatMessageRole(request.role),
                content=request.content,
            )
        )
        
        return ChatMessageResponse(
            id=result.message.id,
            session_id=result.message.session_id,
            role=result.message.role.value,
            content=result.message.content,
            created_at=result.message.created_at,
        )
        
    except ChatSessionNotFoundException as e:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=str(e))


@router.get("/sessions/{session_id}/history", response_model=ChatHistoryResponse)
async def get_history(session_id: str, limit: int = 50, skip: int = 0):
    """Get chat history for session."""
    from app.application.use_cases.chat import GetHistoryUseCase
    
    try:
        factory = get_factory()
        chat_repo = factory.get_chat_repository()
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
                )
                for msg in result.messages
            ],
            total=result.total_messages,
        )
        
    except ChatSessionNotFoundException as e:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=str(e))


@router.get("/sessions", response_model=List[ChatSessionResponse])
async def list_sessions(
    user_id: str = Depends(get_current_user_id),
    skip: int = 0,
    limit: int = 100,
):
    """List chat sessions for user."""
    factory = get_factory()
    chat_repo = factory.get_chat_repository()
    
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
