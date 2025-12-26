"""Bookmark entity for saving Q&A pairs."""

from dataclasses import dataclass, field
from datetime import datetime, timezone
from typing import Optional, List
import uuid


@dataclass
class Bookmark:
    """Represents a saved Q&A pair that user wants to keep."""

    id: str = field(default_factory=lambda: str(uuid.uuid4()))
    user_id: str = ""
    session_id: str = ""
    message_id: str = ""

    # Content
    query: str = ""
    response: str = ""

    # Organization
    title: Optional[str] = None
    tags: List[str] = field(default_factory=list)
    notes: Optional[str] = None
    folder: Optional[str] = None

    # Metadata
    sources: List[dict] = field(default_factory=list)
    artifacts: List[dict] = field(default_factory=list)

    # Status
    is_pinned: bool = False
    is_archived: bool = False

    # Timestamps
    created_at: datetime = field(default_factory=lambda: datetime.now(timezone.utc))
    updated_at: datetime = field(default_factory=lambda: datetime.now(timezone.utc))

    def __post_init__(self):
        # Auto-generate title from query if not provided
        if not self.title and self.query:
            self.title = self.query[:100] + ("..." if len(self.query) > 100 else "")

    def add_tag(self, tag: str) -> None:
        """Add a tag if not already present."""
        tag = tag.strip().lower()
        if tag and tag not in self.tags:
            self.tags.append(tag)
            self.updated_at = datetime.now(timezone.utc)

    def remove_tag(self, tag: str) -> None:
        """Remove a tag if present."""
        tag = tag.strip().lower()
        if tag in self.tags:
            self.tags.remove(tag)
            self.updated_at = datetime.now(timezone.utc)

    def pin(self) -> None:
        """Pin the bookmark."""
        self.is_pinned = True
        self.updated_at = datetime.now(timezone.utc)

    def unpin(self) -> None:
        """Unpin the bookmark."""
        self.is_pinned = False
        self.updated_at = datetime.now(timezone.utc)

    def archive(self) -> None:
        """Archive the bookmark."""
        self.is_archived = True
        self.updated_at = datetime.now(timezone.utc)

    def unarchive(self) -> None:
        """Restore the bookmark from archive."""
        self.is_archived = False
        self.updated_at = datetime.now(timezone.utc)

    def update_notes(self, notes: str) -> None:
        """Update notes."""
        self.notes = notes
        self.updated_at = datetime.now(timezone.utc)

    def to_dict(self) -> dict:
        """Convert to dictionary."""
        return {
            "id": self.id,
            "user_id": self.user_id,
            "session_id": self.session_id,
            "message_id": self.message_id,
            "query": self.query,
            "response": self.response,
            "title": self.title,
            "tags": self.tags,
            "notes": self.notes,
            "folder": self.folder,
            "sources": self.sources,
            "artifacts": self.artifacts,
            "is_pinned": self.is_pinned,
            "is_archived": self.is_archived,
            "created_at": self.created_at,
            "updated_at": self.updated_at,
        }

    @classmethod
    def from_dict(cls, data: dict) -> "Bookmark":
        """Create from dictionary."""
        return cls(
            id=data.get("id", str(uuid.uuid4())),
            user_id=data.get("user_id", ""),
            session_id=data.get("session_id", ""),
            message_id=data.get("message_id", ""),
            query=data.get("query", ""),
            response=data.get("response", ""),
            title=data.get("title"),
            tags=data.get("tags", []),
            notes=data.get("notes"),
            folder=data.get("folder"),
            sources=data.get("sources", []),
            artifacts=data.get("artifacts", []),
            is_pinned=data.get("is_pinned", False),
            is_archived=data.get("is_archived", False),
            created_at=data.get("created_at", datetime.now(timezone.utc)),
            updated_at=data.get("updated_at", datetime.now(timezone.utc)),
        )
