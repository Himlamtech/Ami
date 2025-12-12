"""Chat message domain entity."""

from dataclasses import dataclass, field
from datetime import datetime
from typing import List, Optional, Dict, Any
from enum import Enum
from app.domain.enums.chat_message_role import ChatMessageRole


class MessageIntent(Enum):
    """Detected intent of user message."""

    QUESTION = "question"
    FILE_REQUEST = "file_request"
    CLARIFICATION = "clarification"
    FEEDBACK = "feedback"
    GREETING = "greeting"
    GOODBYE = "goodbye"
    OTHER = "other"


@dataclass
class SourceRef:
    """Reference to a knowledge source used in response."""

    document_id: str
    chunk_id: Optional[str] = None
    title: Optional[str] = None
    relevance_score: float = 0.0

    def to_dict(self) -> Dict[str, Any]:
        return {
            "document_id": self.document_id,
            "chunk_id": self.chunk_id,
            "title": self.title,
            "relevance_score": self.relevance_score,
        }


@dataclass
class EntityMention:
    """Extracted entity from message."""

    entity_type: str  # person, location, organization, date, course, etc.
    value: str
    start_pos: int = 0
    end_pos: int = 0
    confidence: float = 1.0

    def to_dict(self) -> Dict[str, Any]:
        return {
            "entity_type": self.entity_type,
            "value": self.value,
            "start_pos": self.start_pos,
            "end_pos": self.end_pos,
            "confidence": self.confidence,
        }


@dataclass
class ChatMessage:
    """
    Pure domain chat message entity.

    Represents a single message in a conversation with business rules
    for message lifecycle, attachments, and context tracking.
    """

    # Identity
    id: str
    session_id: str

    # Content
    role: ChatMessageRole
    content: str

    # Context tracking (for conversation memory)
    intent: Optional[MessageIntent] = None
    context_refs: List[SourceRef] = field(default_factory=list)  # Sources used
    entity_mentions: List[EntityMention] = field(
        default_factory=list
    )  # Extracted entities
    parent_message_id: Optional[str] = None  # For follow-up tracking

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

    def add_source_ref(self, source: SourceRef) -> None:
        """Add a source reference."""
        self.context_refs.append(source)

    def add_entity(self, entity: EntityMention) -> None:
        """Add an extracted entity."""
        self.entity_mentions.append(entity)

    def set_intent(self, intent: MessageIntent) -> None:
        """Set message intent."""
        self.intent = intent

    def has_context_refs(self) -> bool:
        """Check if message has source references."""
        return len(self.context_refs) > 0

    def has_entities(self) -> bool:
        """Check if message has extracted entities."""
        return len(self.entity_mentions) > 0

    def get_entities_by_type(self, entity_type: str) -> List[EntityMention]:
        """Get entities of a specific type."""
        return [e for e in self.entity_mentions if e.entity_type == entity_type]

    def is_follow_up(self) -> bool:
        """Check if this is a follow-up message."""
        return self.parent_message_id is not None

    def to_context_dict(self) -> Dict[str, Any]:
        """Convert to dict for context building."""
        return {
            "role": self.role.value,
            "content": self.content,
            "intent": self.intent.value if self.intent else None,
            "entities": [e.to_dict() for e in self.entity_mentions],
            "sources": [s.to_dict() for s in self.context_refs],
        }

    def __repr__(self) -> str:
        preview = self.content[:50] + "..." if len(self.content) > 50 else self.content
        return f"ChatMessage(role={self.role.value}, content='{preview}')"
