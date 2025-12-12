"""Document domain entity - Pure business logic."""

from dataclasses import dataclass, field
from datetime import datetime
from typing import List, Optional, Dict, Any
from enum import Enum


class ArtifactType(Enum):
    """Types of downloadable artifacts."""

    DOCUMENT = "document"  # Word, PDF documents
    SPREADSHEET = "spreadsheet"  # Excel files
    PRESENTATION = "presentation"  # PowerPoint
    IMAGE = "image"  # Images
    FORM = "form"  # Fillable forms
    TEMPLATE = "template"  # Document templates
    OTHER = "other"


@dataclass
class Artifact:
    """
    Represents a downloadable/viewable artifact attached to a document.

    Used for: Forms, templates, images, and other files that should be
    returned to users instead of just text descriptions.
    """

    url: str  # MinIO URL: "minio://bucket/path/file.docx"
    artifact_type: ArtifactType  # Type classification
    file_name: str  # Original filename
    mime_type: str  # "application/vnd.openxmlformats..."
    size_bytes: int = 0  # File size
    preview_url: Optional[str] = None  # URL to preview image (for PDFs, docs)
    is_fillable: bool = False  # Can be auto-filled with user data
    fill_fields: List[str] = field(default_factory=list)  # Fields that can be filled

    def get_extension(self) -> str:
        """Get file extension from filename."""
        return self.file_name.split(".")[-1].lower() if "." in self.file_name else ""

    def is_previewable(self) -> bool:
        """Check if artifact can be previewed inline."""
        previewable_types = ["pdf", "png", "jpg", "jpeg", "gif", "webp"]
        return self.get_extension() in previewable_types

    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary for serialization."""
        return {
            "url": self.url,
            "artifact_type": self.artifact_type.value,
            "file_name": self.file_name,
            "mime_type": self.mime_type,
            "size_bytes": self.size_bytes,
            "preview_url": self.preview_url,
            "is_fillable": self.is_fillable,
            "fill_fields": self.fill_fields,
        }


@dataclass
class Document:
    """
    Pure domain document entity.

    Represents a document in the knowledge base with business rules
    for document lifecycle, versioning, and metadata management.
    """

    # Core Info
    title: str
    file_name: str = ""
    source: Optional[str] = None
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

    # Artifact Info (downloadable files attached to this document)
    artifacts: List[Artifact] = field(default_factory=list)
    primary_artifact_index: int = -1  # Index of main artifact (-1 = none)

    # Status
    is_active: bool = True

    # Ownership
    created_by: Optional[str] = None  # User ID

    # Timestamps
    created_at: datetime = field(default_factory=datetime.now)
    updated_at: datetime = field(default_factory=datetime.now)

    # Identity
    id: Optional[str] = None

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

    def add_artifact(self, artifact: Artifact, is_primary: bool = False) -> None:
        """Add an artifact to the document."""
        self.artifacts.append(artifact)
        if is_primary or len(self.artifacts) == 1:
            self.primary_artifact_index = len(self.artifacts) - 1
        self.updated_at = datetime.now()

    def get_primary_artifact(self) -> Optional[Artifact]:
        """Get the primary artifact if exists."""
        if 0 <= self.primary_artifact_index < len(self.artifacts):
            return self.artifacts[self.primary_artifact_index]
        return None

    def has_artifacts(self) -> bool:
        """Check if document has any artifacts."""
        return len(self.artifacts) > 0

    def get_artifacts_by_type(self, artifact_type: ArtifactType) -> List[Artifact]:
        """Get all artifacts of a specific type."""
        return [a for a in self.artifacts if a.artifact_type == artifact_type]

    def has_fillable_form(self) -> bool:
        """Check if document has a fillable form artifact."""
        return any(a.is_fillable for a in self.artifacts)

    def get_age_days(self) -> int:
        """Get document age in days."""
        age = datetime.now() - self.created_at
        return age.days

    def __repr__(self) -> str:
        return (
            f"Document(id={self.id}, title={self.title}, collection={self.collection})"
        )
