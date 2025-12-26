"""Chat session domain entity."""

from dataclasses import dataclass, field
from datetime import datetime
from typing import List, Optional, Dict, Any


@dataclass
class ConversationContext:
    """Context accumulated from conversation."""

    topics: List[str] = field(default_factory=list)  # Main topics discussed
    entities: Dict[str, Any] = field(default_factory=dict)  # Key entities extracted
    unresolved_questions: List[str] = field(
        default_factory=list
    )  # Questions not fully answered
    last_intent: Optional[str] = None

    def add_topic(self, topic: str) -> None:
        if topic not in self.topics:
            self.topics.append(topic)

    def add_entity(self, key: str, value: Any) -> None:
        self.entities[key] = value

    def to_dict(self) -> Dict[str, Any]:
        return {
            "topics": self.topics,
            "entities": self.entities,
            "unresolved_questions": self.unresolved_questions,
            "last_intent": self.last_intent,
        }


@dataclass
class ChatSession:
    """
    Pure domain chat session entity.

    Represents a conversation session with business rules
    for session lifecycle, message management, and context tracking.
    """

    # Identity
    id: str
    user_id: str

    # Info
    title: str = "New Conversation"
    summary: Optional[str] = None

    # Conversation context (for memory)
    context: ConversationContext = field(default_factory=ConversationContext)

    # Metadata
    metadata: Dict[str, Any] = field(default_factory=dict)
    tags: List[str] = field(default_factory=list)

    # Status
    is_archived: bool = False
    is_deleted: bool = False

    # Statistics
    message_count: int = 0
    last_message_at: Optional[datetime] = None

    # Summary generation tracking
    last_summary_at: Optional[datetime] = None
    summary_message_count: int = 0  # Message count when summary was generated

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

    def needs_summary_update(self, threshold: int = 5) -> bool:
        """Check if summary needs to be regenerated."""
        messages_since_summary = self.message_count - self.summary_message_count
        return messages_since_summary >= threshold

    def update_summary_tracking(self) -> None:
        """Update tracking after summary generation."""
        self.last_summary_at = datetime.now()
        self.summary_message_count = self.message_count
        self.updated_at = datetime.now()

    def add_topic(self, topic: str) -> None:
        """Add a topic to conversation context."""
        self.context.add_topic(topic)
        self.updated_at = datetime.now()

    def add_context_entity(self, key: str, value: Any) -> None:
        """Add an entity to conversation context."""
        self.context.add_entity(key, value)
        self.updated_at = datetime.now()

    def get_context_for_llm(self) -> str:
        """Get context summary for LLM prompt building."""
        parts = []
        if self.summary:
            parts.append(f"Session Summary: {self.summary}")
        if self.context.topics:
            parts.append(f"Topics Discussed: {', '.join(self.context.topics)}")
        if self.context.entities:
            entities_str = ", ".join(
                f"{k}: {v}" for k, v in self.context.entities.items()
            )
            parts.append(f"Key Information: {entities_str}")
        return "\n".join(parts)

    def __repr__(self) -> str:
        return f"ChatSession(id={self.id}, title={self.title}, messages={self.message_count})"
