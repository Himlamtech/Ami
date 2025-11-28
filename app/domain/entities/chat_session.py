"""Chat session domain entity."""

from dataclasses import dataclass, field
from datetime import datetime
from typing import List, Optional, Dict, Any


@dataclass
class ChatSession:
    """
    Pure domain chat session entity.
    
    Represents a conversation session with business rules
    for session lifecycle and message management.
    """
    
    # Identity
    id: str
    user_id: str
    
    # Info
    title: str = "New Conversation"
    summary: Optional[str] = None
    
    # Metadata
    metadata: Dict[str, Any] = field(default_factory=dict)
    tags: List[str] = field(default_factory=list)
    
    # Status
    is_archived: bool = False
    is_deleted: bool = False
    
    # Statistics
    message_count: int = 0
    last_message_at: Optional[datetime] = None
    
    # Timestamps
    created_at: datetime = field(default_factory=datetime.now)
    updated_at: datetime = field(default_factory=datetime.now)
    
    # Business Logic Methods
    
    def update_title(self, title: str) -> None:
        """Update session title."""
        self.title = title
        self.updated_at = datetime.now()
    
    def update_summary(self, summary: str) -> None:
        """Update session summary."""
        self.summary = summary
        self.updated_at = datetime.now()
    
    def add_message(self) -> None:
        """Increment message count when a new message is added."""
        self.message_count += 1
        self.last_message_at = datetime.now()
        self.updated_at = datetime.now()
    
    def archive(self) -> None:
        """Archive session."""
        self.is_archived = True
        self.updated_at = datetime.now()
    
    def unarchive(self) -> None:
        """Restore archived session."""
        self.is_archived = False
        self.updated_at = datetime.now()
    
    def delete(self) -> None:
        """Soft delete session."""
        self.is_deleted = True
        self.updated_at = datetime.now()
    
    def add_tag(self, tag: str) -> None:
        """Add a tag to session."""
        if tag not in self.tags:
            self.tags.append(tag)
            self.updated_at = datetime.now()
    
    def remove_tag(self, tag: str) -> None:
        """Remove a tag from session."""
        if tag in self.tags:
            self.tags.remove(tag)
            self.updated_at = datetime.now()
    
    def is_owned_by(self, user_id: str) -> bool:
        """Check if session belongs to user."""
        return self.user_id == user_id
    
    def is_empty(self) -> bool:
        """Check if session has no messages."""
        return self.message_count == 0
    
    def get_age_days(self) -> int:
        """Get session age in days."""
        age = datetime.now() - self.created_at
        return age.days
    
    def __repr__(self) -> str:
        return f"ChatSession(id={self.id}, title={self.title}, messages={self.message_count})"
