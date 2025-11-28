"""Document domain entity - Pure business logic."""

from dataclasses import dataclass, field
from datetime import datetime
from typing import List, Optional, Dict, Any


@dataclass
class Document:
    """
    Pure domain document entity.
    
    Represents a document in the knowledge base with business rules
    for document lifecycle, versioning, and metadata management.
    """
    
    # Identity
    id: str
    
    # Core Info
    title: str
    file_name: str
    collection: str = "default"
    
    # Content
    content: Optional[str] = None
    
    # Metadata
    metadata: Dict[str, Any] = field(default_factory=dict)
    tags: List[str] = field(default_factory=list)
    
    # Chunking Info
    chunk_count: int = 0
    vector_ids: List[str] = field(default_factory=list)
    
    # Storage Info
    file_path: Optional[str] = None
    file_size: Optional[int] = None
    mime_type: Optional[str] = None
    
    # Status
    is_active: bool = True
    
    # Ownership
    created_by: Optional[str] = None  # User ID
    
    # Timestamps
    created_at: datetime = field(default_factory=datetime.now)
    updated_at: datetime = field(default_factory=datetime.now)
    
    # Business Logic Methods
    
    def add_tag(self, tag: str) -> None:
        """Add a tag to document."""
        if tag not in self.tags:
            self.tags.append(tag)
            self.updated_at = datetime.now()
    
    def remove_tag(self, tag: str) -> None:
        """Remove a tag from document."""
        if tag in self.tags:
            self.tags.remove(tag)
            self.updated_at = datetime.now()
    
    def update_metadata(self, new_metadata: Dict[str, Any]) -> None:
        """Update document metadata."""
        self.metadata.update(new_metadata)
        self.updated_at = datetime.now()
    
    def set_vector_ids(self, vector_ids: List[str]) -> None:
        """Set vector IDs after embedding."""
        self.vector_ids = vector_ids
        self.chunk_count = len(vector_ids)
        self.updated_at = datetime.now()
    
    def archive(self) -> None:
        """Archive document (soft delete)."""
        self.is_active = False
        self.updated_at = datetime.now()
    
    def restore(self) -> None:
        """Restore archived document."""
        self.is_active = True
        self.updated_at = datetime.now()
    
    def is_owned_by(self, user_id: str) -> bool:
        """Check if document is owned by given user."""
        return self.created_by == user_id
    
    def is_in_collection(self, collection: str) -> bool:
        """Check if document belongs to collection."""
        return self.collection == collection
    
    def has_tag(self, tag: str) -> bool:
        """Check if document has a specific tag."""
        return tag in self.tags
    
    def is_embedded(self) -> bool:
        """Check if document has been embedded (has vector IDs)."""
        return len(self.vector_ids) > 0
    
    def get_age_days(self) -> int:
        """Get document age in days."""
        age = datetime.now() - self.created_at
        return age.days
    
    def __repr__(self) -> str:
        return f"Document(id={self.id}, title={self.title}, collection={self.collection})"
