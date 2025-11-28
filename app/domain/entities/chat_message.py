"""Chat message domain entity."""

from dataclasses import dataclass, field
from datetime import datetime
from typing import List, Optional, Dict, Any
from app.domain.enums.chat_message_role import ChatMessageRole


@dataclass
class ChatMessage:
    """
    Pure domain chat message entity.
    
    Represents a single message in a conversation with business rules
    for message lifecycle and attachments.
    """
    
    # Identity
    id: str
    session_id: str
    
    # Content
    role: ChatMessageRole
    content: str
    
    # Attachments
    attachments: List[Dict[str, Any]] = field(default_factory=list)
    
    # Metadata
    metadata: Dict[str, Any] = field(default_factory=dict)
    
    # Status
    is_deleted: bool = False
    
    # Timestamps
    created_at: datetime = field(default_factory=datetime.now)
    edited_at: Optional[datetime] = None
    
    # Business Logic Methods
    
    def edit_content(self, new_content: str) -> None:
        """Edit message content."""
        self.content = new_content
        self.edited_at = datetime.now()
    
    def add_attachment(self, attachment: Dict[str, Any]) -> None:
        """Add an attachment to message."""
        self.attachments.append(attachment)
        self.edited_at = datetime.now()
    
    def delete(self) -> None:
        """Soft delete message."""
        self.is_deleted = True
        self.edited_at = datetime.now()
    
    def is_from_user(self) -> bool:
        """Check if message is from user."""
        return self.role == ChatMessageRole.USER
    
    def is_from_assistant(self) -> bool:
        """Check if message is from assistant."""
        return self.role == ChatMessageRole.ASSISTANT
    
    def is_system(self) -> bool:
        """Check if message is a system message."""
        return self.role == ChatMessageRole.SYSTEM
    
    def has_attachments(self) -> bool:
        """Check if message has attachments."""
        return len(self.attachments) > 0
    
    def was_edited(self) -> bool:
        """Check if message was edited."""
        return self.edited_at is not None
    
    def get_word_count(self) -> int:
        """Get approximate word count."""
        return len(self.content.split())
    
    def __repr__(self) -> str:
        preview = self.content[:50] + "..." if len(self.content) > 50 else self.content
        return f"ChatMessage(role={self.role.value}, content='{preview}')"
