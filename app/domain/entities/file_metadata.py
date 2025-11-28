"""File metadata domain entity."""

from dataclasses import dataclass, field
from datetime import datetime
from typing import Optional, Dict, Any
from app.domain.enums.file_type import FileType


@dataclass
class FileMetadata:
    """
    Pure domain file metadata entity.
    
    Represents file metadata with business rules for file management,
    storage tracking, and vision analysis.
    """
    
    # Identity
    id: str
    user_id: str
    
    # File Info
    filename: str
    original_name: Optional[str] = None
    mime_type: str = ""
    size: int = 0
    
    # Storage Info
    url: str = ""
    thumbnail_url: Optional[str] = None
    storage_provider: str = "minio"
    bucket: str = ""
    path: str = ""
    
    # Dimensions (for images)
    width: Optional[int] = None
    height: Optional[int] = None
    
    # Context
    session_id: Optional[str] = None
    message_id: Optional[str] = None
    
    # Type
    file_type: FileType = FileType.UPLOADED
    
    # Generation Info (if generated image)
    generation_prompt: Optional[str] = None
    model_used: Optional[str] = None
    
    # Vision Analysis (if analyzed)
    vision_analysis: Optional[Dict[str, Any]] = None
    
    # Status
    status: str = "processed"  # pending, processing, processed, failed
    is_deleted: bool = False
    
    # Timestamps
    created_at: datetime = field(default_factory=datetime.now)
    updated_at: datetime = field(default_factory=datetime.now)
    
    # Business Logic Methods
    
    def is_image(self) -> bool:
        """Check if file is an image."""
        return self.mime_type.startswith("image/")
    
    def is_document(self) -> bool:
        """Check if file is a document."""
        doc_types = ["application/pdf", "application/msword", "text/"]
        return any(self.mime_type.startswith(t) for t in doc_types)
    
    def is_generated(self) -> bool:
        """Check if file was AI-generated."""
        return self.file_type == FileType.GENERATED
    
    def is_analyzed(self) -> bool:
        """Check if image has vision analysis."""
        return self.vision_analysis is not None
    
    def mark_as_processing(self) -> None:
        """Mark file as being processed."""
        self.status = "processing"
        self.updated_at = datetime.now()
    
    def mark_as_processed(self) -> None:
        """Mark file as successfully processed."""
        self.status = "processed"
        self.updated_at = datetime.now()
    
    def mark_as_failed(self) -> None:
        """Mark file processing as failed."""
        self.status = "failed"
        self.updated_at = datetime.now()
    
    def set_vision_analysis(self, analysis: Dict[str, Any]) -> None:
        """Set vision analysis results."""
        self.vision_analysis = analysis
        self.updated_at = datetime.now()
    
    def delete(self) -> None:
        """Soft delete file."""
        self.is_deleted = True
        self.updated_at = datetime.now()
    
    def get_size_mb(self) -> float:
        """Get file size in megabytes."""
        return self.size / (1024 * 1024)
    
    def is_owned_by(self, user_id: str) -> bool:
        """Check if file belongs to user."""
        return self.user_id == user_id
    
    def __repr__(self) -> str:
        return f"FileMetadata(id={self.id}, filename={self.filename}, type={self.file_type.value})"
