"""Chat response value objects for rich content delivery."""

from dataclasses import dataclass, field
from typing import List, Optional, Dict, Any
from enum import Enum
from datetime import datetime


class ResponseIntent(Enum):
    """Intent classification for response type."""
    GENERAL_ANSWER = "general_answer"
    FILE_REQUEST = "file_request"
    FORM_REQUEST = "form_request"
    PROCEDURE_GUIDE = "procedure_guide"
    CONTACT_INFO = "contact_info"
    NAVIGATION = "navigation"


class SourceType(Enum):
    """Type of knowledge source used."""
    DOCUMENT = "document"
    WEB_SEARCH = "web_search"
    DIRECT_KNOWLEDGE = "direct_knowledge"


@dataclass
class SourceReference:
    """Reference to a knowledge source used in response."""
    source_type: SourceType
    document_id: Optional[str] = None
    title: Optional[str] = None
    url: Optional[str] = None
    chunk_text: Optional[str] = None
    relevance_score: float = 0.0
    
    def to_dict(self) -> Dict[str, Any]:
        return {
            "source_type": self.source_type.value,
            "document_id": self.document_id,
            "title": self.title,
            "url": self.url,
            "chunk_text": self.chunk_text,
            "relevance_score": self.relevance_score
        }


@dataclass
class ArtifactReference:
    """Reference to a downloadable artifact in response."""
    artifact_id: str
    document_id: str
    file_name: str
    artifact_type: str
    download_url: str
    preview_url: Optional[str] = None
    size_bytes: int = 0
    is_fillable: bool = False
    fill_fields: List[str] = field(default_factory=list)
    
    def to_dict(self) -> Dict[str, Any]:
        return {
            "artifact_id": self.artifact_id,
            "document_id": self.document_id,
            "file_name": self.file_name,
            "artifact_type": self.artifact_type,
            "download_url": self.download_url,
            "preview_url": self.preview_url,
            "size_bytes": self.size_bytes,
            "is_fillable": self.is_fillable,
            "fill_fields": self.fill_fields
        }
    
    @property
    def size_display(self) -> str:
        """Human readable file size."""
        if self.size_bytes < 1024:
            return f"{self.size_bytes} B"
        elif self.size_bytes < 1024 * 1024:
            return f"{self.size_bytes / 1024:.1f} KB"
        else:
            return f"{self.size_bytes / (1024 * 1024):.1f} MB"


@dataclass
class RichChatResponse:
    """Rich chat response with artifacts and sources."""
    
    # Core response
    content: str
    intent: ResponseIntent = ResponseIntent.GENERAL_ANSWER
    
    # Artifacts (downloadable files)
    artifacts: List[ArtifactReference] = field(default_factory=list)
    
    # Source references
    sources: List[SourceReference] = field(default_factory=list)
    
    # Metadata
    model_used: str = ""
    processing_time_ms: float = 0.0
    tokens_used: int = 0
    thinking_content: Optional[str] = None
    
    # Timestamps
    created_at: datetime = field(default_factory=datetime.now)
    
    def has_artifacts(self) -> bool:
        """Check if response has any artifacts."""
        return len(self.artifacts) > 0
    
    def has_fillable_form(self) -> bool:
        """Check if response has a fillable form."""
        return any(a.is_fillable for a in self.artifacts)
    
    def get_fillable_forms(self) -> List[ArtifactReference]:
        """Get all fillable form artifacts."""
        return [a for a in self.artifacts if a.is_fillable]
    
    def add_artifact(self, artifact: ArtifactReference) -> None:
        """Add an artifact to response."""
        self.artifacts.append(artifact)
    
    def add_source(self, source: SourceReference) -> None:
        """Add a source reference."""
        self.sources.append(source)
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary for API response."""
        return {
            "content": self.content,
            "intent": self.intent.value,
            "artifacts": [a.to_dict() for a in self.artifacts],
            "sources": [s.to_dict() for s in self.sources],
            "metadata": {
                "model_used": self.model_used,
                "processing_time_ms": self.processing_time_ms,
                "tokens_used": self.tokens_used,
                "has_thinking": self.thinking_content is not None
            },
            "created_at": self.created_at.isoformat()
        }
    
    @classmethod
    def simple_response(cls, content: str, model: str = "") -> "RichChatResponse":
        """Create a simple text-only response."""
        return cls(content=content, model_used=model)
    
    @classmethod
    def with_artifact(
        cls,
        content: str,
        artifact: ArtifactReference,
        intent: ResponseIntent = ResponseIntent.FILE_REQUEST
    ) -> "RichChatResponse":
        """Create a response with a single artifact."""
        return cls(
            content=content,
            intent=intent,
            artifacts=[artifact]
        )
