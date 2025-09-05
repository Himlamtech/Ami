# app/schemas/chat.py
"""Chat API schemas."""

from datetime import datetime
from typing import Any, Dict, List, Literal, Optional
from uuid import UUID

from pydantic import BaseModel


class ChatRequest(BaseModel):
    """Request để chat với AI."""

    message: str
    model: Literal["gpt-5", "gpt-5-mini", "gpt-5-nano"] = "gpt-5-nano"
    session_id: Optional[UUID] = None
    stream: bool = False


class Message(BaseModel):
    """Format message tương thích OpenAI."""

    role: Literal["user", "assistant", "system"]
    content: str
    timestamp: datetime
    model_used: Optional[str] = None


class ChatResponse(BaseModel):
    """Response từ chat API."""

    session_id: UUID
    message: Message
    conversation_history: List[Message]
    model_used: str
    usage: Optional[Dict[str, Any]] = None


class SessionInfo(BaseModel):
    """Thông tin session."""

    session_id: UUID
    created_at: datetime
    updated_at: datetime
    message_count: int
    title: Optional[str] = None


class SessionDetail(BaseModel):
    """Chi tiết session với conversation."""

    session_info: SessionInfo
    conversation_history: List[Message]


class RAGChatRequest(BaseModel):
    """Request cho RAG chat."""

    question: str
    session_id: str


class RAGChatResponse(BaseModel):
    """Response từ RAG chat."""

    answer: str
    session_id: str
