"""Document DTOs."""

from pydantic import BaseModel
from typing import Optional, List, Dict, Any
from datetime import datetime


class UploadDocumentRequest(BaseModel):
    """Upload document request."""

    collection: str = "default"
    chunk_size: Optional[int] = 512
    chunk_overlap: Optional[int] = 50


class DocumentResponse(BaseModel):
    """Document response."""

    id: str
    title: str
    file_name: str
    collection: str
    chunk_count: int
    is_active: bool
    created_at: datetime

    class Config:
        from_attributes = True


class DocumentListResponse(BaseModel):
    """Document list response."""

    documents: List[DocumentResponse]
    total: int
    skip: int
    limit: int


class QueryRequest(BaseModel):
    """RAG query request."""

    query: str
    collection: Optional[str] = "default"
    top_k: int = 5
    similarity_threshold: float = 0.0
    include_sources: bool = True
    stream: bool = False


class QueryResponse(BaseModel):
    """RAG query response."""

    answer: str
    sources: List[Dict[str, Any]] = []
    metadata: Dict[str, Any] = {}
