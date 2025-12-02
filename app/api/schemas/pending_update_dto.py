"""Pending update DTOs for API layer."""

from typing import Optional, List, Dict, Any
from datetime import datetime
from pydantic import BaseModel, Field


# ===== Request DTOs =====

class ApproveUpdateRequest(BaseModel):
    """Request to approve a pending update."""
    note: Optional[str] = None


class RejectUpdateRequest(BaseModel):
    """Request to reject a pending update."""
    note: Optional[str] = None


class BulkActionRequest(BaseModel):
    """Request for bulk approve/reject."""
    pending_ids: List[str] = Field(..., min_length=1)


# ===== Response DTOs =====

class PendingUpdateResponse(BaseModel):
    """Pending update response."""
    id: str
    source_id: str
    title: str
    content_preview: str  # Truncated content
    content_hash: str
    source_url: str
    category: str
    detection_type: str
    similarity_score: float
    matched_doc_id: Optional[str] = None
    llm_analysis: Optional[str] = None
    llm_summary: Optional[str] = None
    diff_summary: Optional[str] = None
    status: str
    priority: int
    auto_approve_score: float = 0.0
    reviewed_by: Optional[str] = None
    reviewed_at: Optional[datetime] = None
    review_note: Optional[str] = None
    created_at: datetime
    expires_at: datetime


class PendingUpdateDetailResponse(PendingUpdateResponse):
    """Detailed pending update response with full content."""
    content: str  # Full content
    matched_doc_ids: List[str] = []
    metadata: Dict[str, Any] = {}
    raw_file_path: Optional[str] = None


class PendingUpdateListResponse(BaseModel):
    """List pending updates response."""
    items: List[PendingUpdateResponse]
    total: int
    skip: int
    limit: int


class ApprovalActionResponse(BaseModel):
    """Response for approve/reject action."""
    success: bool
    message: str
    document_id: Optional[str] = None
    replaced_doc_id: Optional[str] = None


class BulkActionResponse(BaseModel):
    """Response for bulk actions."""
    success: bool
    processed_count: int
    message: str


class ApprovalStatsResponse(BaseModel):
    """Approval queue statistics response."""
    total_pending: int
    total_approved: int
    total_rejected: int
    by_category: Dict[str, int]
    by_detection_type: Dict[str, int]
    by_source: Dict[str, int]
