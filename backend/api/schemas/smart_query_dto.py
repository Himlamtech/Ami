"""Smart Query DTOs for rich response with artifacts."""

from pydantic import BaseModel, Field
from typing import Optional, List, Dict, Any
from datetime import datetime
from enum import Enum


class ResponseIntentDTO(str, Enum):
    """Intent classification for response."""

    GENERAL_ANSWER = "general_answer"
    FILE_REQUEST = "file_request"
    FORM_REQUEST = "form_request"
    PROCEDURE_GUIDE = "procedure_guide"
    CONTACT_INFO = "contact_info"
    NAVIGATION = "navigation"


class SourceTypeDTO(str, Enum):
    """Type of knowledge source."""

    DOCUMENT = "document"
    WEB_SEARCH = "web_search"
    DIRECT_KNOWLEDGE = "direct_knowledge"


class SourceReferenceDTO(BaseModel):
    """Reference to a knowledge source."""

    source_type: SourceTypeDTO
    document_id: Optional[str] = None
    title: Optional[str] = None
    url: Optional[str] = None
    chunk_text: Optional[str] = None
    relevance_score: float = 0.0


class ArtifactDTO(BaseModel):
    """Artifact/file reference in response."""

    artifact_id: str
    document_id: str
    file_name: str
    artifact_type: str
    download_url: str
    preview_url: Optional[str] = None
    size_bytes: int = 0
    size_display: str = ""
    is_fillable: bool = False
    fill_fields: List[str] = Field(default_factory=list)


class SmartQueryRequest(BaseModel):
    """Request for smart query with artifact support."""

    query: str = Field(..., min_length=1, max_length=2000, description="User query")
    session_id: Optional[str] = Field(None, description="Chat session ID")
    collection: Optional[str] = Field(
        None,
        description="Document collection (defaults to configured Qdrant collection)",
    )

    # Optional user info for form auto-fill
    user_info: Optional[Dict[str, Any]] = Field(
        None, description="User info for form fill"
    )

    # RAG configuration
    enable_rag: bool = Field(True, description="Enable RAG retrieval")
    top_k: int = Field(5, ge=1, le=20, description="Number of sources to retrieve")
    similarity_threshold: float = Field(0.0, ge=0.0, le=1.0)

    # Generation configuration
    temperature: float = Field(0.7, ge=0.0, le=2.0)
    max_tokens: int = Field(1024, ge=100, le=4096)

    class Config:
        json_schema_extra = {
            "example": {
                "query": "Cho mình xin mẫu đơn nghỉ học tạm thời",
                "session_id": "session_123",
                "collection": "default",
                "enable_rag": True,
                "top_k": 5,
            }
        }


class SmartQueryMetadata(BaseModel):
    """Metadata about the query response."""

    model_used: str = ""
    processing_time_ms: float = 0.0
    tokens_used: int = 0
    sources_count: int = 0
    artifacts_count: int = 0
    has_fillable_form: bool = False


class SmartQueryResponse(BaseModel):
    """Rich response with content, artifacts, and sources."""

    session_id: Optional[str] = Field(
        None, description="Chat session ID for traceability"
    )
    message_id: Optional[str] = Field(
        None, description="Assistant message ID for traceability"
    )
    request_id: str = Field(..., description="Request ID for traceability")
    content: str = Field(..., description="Main text response")
    intent: ResponseIntentDTO = Field(
        ResponseIntentDTO.GENERAL_ANSWER, description="Detected intent"
    )

    # Artifacts (downloadable files)
    artifacts: List[ArtifactDTO] = Field(
        default_factory=list, description="Downloadable files/forms"
    )

    # Source references
    sources: List[SourceReferenceDTO] = Field(
        default_factory=list, description="Knowledge sources used"
    )

    # Metadata
    metadata: SmartQueryMetadata = Field(default_factory=SmartQueryMetadata)

    # Timestamps
    created_at: datetime = Field(default_factory=datetime.now)

    class Config:
        json_schema_extra = {
            "example": {
                "session_id": "session_123",
                "message_id": "msg_456",
                "request_id": "req_789",
                "content": "Đây là mẫu đơn nghỉ học tạm thời. Bạn có thể tải về và điền thông tin theo hướng dẫn.",
                "intent": "form_request",
                "artifacts": [
                    {
                        "artifact_id": "doc123_artifact_0",
                        "document_id": "doc123",
                        "file_name": "Mau5DonXinNgungHocNghiHocCoThoiHan.docx",
                        "artifact_type": "document",
                        "download_url": "/api/v1/files/doc123/download",
                        "size_bytes": 25600,
                        "size_display": "25.0 KB",
                        "is_fillable": True,
                        "fill_fields": ["ho_ten", "msv", "lop", "ly_do"],
                    }
                ],
                "sources": [
                    {
                        "source_type": "document",
                        "document_id": "doc123",
                        "title": "Mẫu đơn nghỉ học",
                        "relevance_score": 0.92,
                    }
                ],
                "metadata": {
                    "model_used": "gemini-2.0-flash",
                    "processing_time_ms": 1250.5,
                    "sources_count": 1,
                    "artifacts_count": 1,
                    "has_fillable_form": True,
                },
            }
        }


class ArtifactDownloadResponse(BaseModel):
    """Response for artifact download request."""

    download_url: str
    file_name: str
    mime_type: str
    size_bytes: int
    expires_at: Optional[datetime] = None
