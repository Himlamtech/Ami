"""Chat repository interface."""

from abc import ABC, abstractmethod
from typing import Optional, List
from app.domain.entities.chat_session import ChatSession
from app.domain.entities.chat_message import ChatMessage


class IChatRepository(ABC):
    """
    Repository interface for Chat entities (sessions and messages).
    
    Handles both ChatSession and ChatMessage persistence.
    """
    
    # ===== Chat Session Methods =====
    
    @abstractmethod
    async def create_session(self, session: ChatSession) -> ChatSession:
        """Create new chat session."""
        pass
    
    @abstractmethod
    async def get_session_by_id(self, session_id: str) -> Optional[ChatSession]:
        """Get chat session by ID."""
        pass
    
    @abstractmethod
    async def update_session(self, session: ChatSession) -> ChatSession:
        """Update existing chat session."""
        pass
    
    @abstractmethod
    async def delete_session(self, session_id: str) -> bool:
        """Delete chat session (soft delete)."""
        pass
    
    @abstractmethod
    async def list_sessions_by_user(
        self,
        user_id: str,
        skip: int = 0,
        limit: int = 100,
        include_archived: bool = False,
    ) -> List[ChatSession]:
        """List all sessions for a user."""
        pass
    
    @abstractmethod
    async def count_sessions_by_user(
        self,
        user_id: str,
        include_archived: bool = False,
    ) -> int:
        """Count sessions for a user."""
        pass
    
    # ===== Chat Message Methods =====
    
    @abstractmethod
    async def create_message(self, message: ChatMessage) -> ChatMessage:
        """Create new chat message."""
        pass
    
    @abstractmethod
    async def get_message_by_id(self, message_id: str) -> Optional[ChatMessage]:
        """Get chat message by ID."""
        pass
    
    @abstractmethod
    async def update_message(self, message: ChatMessage) -> ChatMessage:
        """Update existing chat message."""
        pass
    
    @abstractmethod
    async def delete_message(self, message_id: str) -> bool:
        """Delete chat message (soft delete)."""
        pass
    
    @abstractmethod
    async def list_messages_by_session(
        self,
        session_id: str,
        skip: int = 0,
        limit: int = 100,
        include_deleted: bool = False,
    ) -> List[ChatMessage]:
        """List all messages in a session."""
        pass
    
    @abstractmethod
    async def count_messages_by_session(
        self,
        session_id: str,
        include_deleted: bool = False,
    ) -> int:
        """Count messages in a session."""
        pass
    
    @abstractmethod
    async def get_recent_messages(
        self,
        session_id: str,
        limit: int = 10,
    ) -> List[ChatMessage]:
        """
        Get recent messages from a session.
        
        Args:
            session_id: Session ID
            limit: Number of recent messages to return
            
        Returns:
            List of recent messages (ordered by created_at desc)
        """
        pass
