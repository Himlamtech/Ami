"""Pending update domain entity."""

from dataclasses import dataclass, field
from datetime import datetime, timedelta
from typing import Optional, Dict, Any, List

from app.domain.enums.data_source import (
    UpdateDetectionType,
    PendingStatus,
    DataCategory,
)


@dataclass
class PendingUpdate:
    """
    Pending update entity for admin approval queue.

    Represents crawled content waiting for admin review
    before being ingested into the knowledge base.
    """

    # Identity
    id: str
    source_id: str  # Reference to DataSource

    # Content
    title: str
    content: str
    content_hash: str  # SHA-256 for dedup
    source_url: str

    # Classification
    category: DataCategory = DataCategory.GENERAL

    # Detection result
    detection_type: UpdateDetectionType = UpdateDetectionType.NEW
    similarity_score: float = 0.0
    matched_doc_id: Optional[str] = None  # Existing doc if UPDATE
    matched_doc_ids: List[str] = field(default_factory=list)  # All similar docs

    # LLM Analysis
    llm_analysis: Optional[str] = None  # Why LLM thinks this is NEW/UPDATE
    llm_summary: Optional[str] = None  # Content summary
    diff_summary: Optional[str] = None  # What changed (if UPDATE)

    # Storage paths (MinIO)
    raw_file_path: Optional[str] = None  # Path in raw/ folder

    # Status
    status: PendingStatus = PendingStatus.PENDING

    # Review info
    reviewed_by: Optional[str] = None
    reviewed_at: Optional[datetime] = None
    review_note: Optional[str] = None

    # Auto-actions
    auto_approve_score: float = 0.0  # Confidence for auto-approve
    auto_action_reason: Optional[str] = None

    # Metadata
    metadata: Dict[str, Any] = field(default_factory=dict)

    # Priority (higher = more urgent)
    priority: int = 5  # 1-10

    # Timestamps
    created_at: datetime = field(default_factory=datetime.now)
    expires_at: datetime = field(
        default_factory=lambda: datetime.now() + timedelta(days=7)
    )

    # Business Logic Methods

    def approve(self, reviewer_id: str, note: Optional[str] = None) -> None:
        """Approve the pending update."""
        self.status = PendingStatus.APPROVED
        self.reviewed_by = reviewer_id
        self.reviewed_at = datetime.now()
        self.review_note = note

    def reject(self, reviewer_id: str, note: Optional[str] = None) -> None:
        """Reject the pending update."""
        self.status = PendingStatus.REJECTED
        self.reviewed_by = reviewer_id
        self.reviewed_at = datetime.now()
        self.review_note = note

    def auto_approve(self, reason: str) -> None:
        """Auto-approve based on rules."""
        self.status = PendingStatus.AUTO_APPROVED
        self.auto_action_reason = reason
        self.reviewed_at = datetime.now()

    def expire(self) -> None:
        """Mark as expired."""
        self.status = PendingStatus.EXPIRED

    def is_pending(self) -> bool:
        """Check if still pending."""
        return self.status == PendingStatus.PENDING

    def is_expired(self) -> bool:
        """Check if expired."""
        return datetime.now() > self.expires_at

    def is_update(self) -> bool:
        """Check if this is an update to existing content."""
        return self.detection_type == UpdateDetectionType.UPDATE

    def is_new(self) -> bool:
        """Check if this is new content."""
        return self.detection_type == UpdateDetectionType.NEW

    def should_auto_approve(self, threshold: float = 0.95) -> bool:
        """Check if should be auto-approved based on confidence."""
        return self.auto_approve_score >= threshold and self.detection_type in [
            UpdateDetectionType.NEW,
            UpdateDetectionType.UPDATE,
        ]

    def set_detection_result(
        self,
        detection_type: UpdateDetectionType,
        similarity_score: float,
        matched_doc_id: Optional[str] = None,
        llm_analysis: Optional[str] = None,
        diff_summary: Optional[str] = None,
    ) -> None:
        """Set detection result from Update Detector."""
        self.detection_type = detection_type
        self.similarity_score = similarity_score
        self.matched_doc_id = matched_doc_id
        self.llm_analysis = llm_analysis
        self.diff_summary = diff_summary

        # Calculate auto-approve score
        if detection_type == UpdateDetectionType.DUPLICATE:
            self.auto_approve_score = 0.0  # Never auto-approve duplicates
        elif detection_type == UpdateDetectionType.NEW and similarity_score < 0.5:
            self.auto_approve_score = 0.9  # High confidence new content
        elif detection_type == UpdateDetectionType.UPDATE and similarity_score > 0.9:
            self.auto_approve_score = 0.85  # Clear update
        else:
            self.auto_approve_score = 0.5  # Needs manual review

    def __repr__(self) -> str:
        return f"PendingUpdate(id={self.id}, type={self.detection_type.value}, status={self.status.value})"
