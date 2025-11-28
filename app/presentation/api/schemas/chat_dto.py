"""Chat DTOs."""

from pydantic import BaseModel
from typing import Optional, List, Dict, Any
from datetime import datetime


class CreateSessionRequest(BaseModel):
    """Create chat session request."""
    title: Optional[str] = "New Conversation"


class SendMessageRequest(BaseModel):
    """Send message request."""
    session_id: str
    content: str
    role: str = "user"


class ChatMessageResponse(BaseModel):
    """Chat message response."""
    id: str
    session_id: str
    role: str
    content: str
    created_at: datetime
    
    class Config:
        from_attributes = True


class ChatSessionResponse(BaseModel):
    """Chat session response."""
    id: str
    user_id: str
    title: str
    message_count: int
    created_at: datetime
    updated_at: datetime
    
    class Config:
        from_attributes = True


class ChatHistoryResponse(BaseModel):
    """Chat history response."""
    session: ChatSessionResponse
    messages: List[ChatMessageResponse]
    total: int
