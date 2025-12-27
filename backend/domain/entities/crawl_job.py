"""Crawl job domain entity."""

from dataclasses import dataclass, field
from datetime import datetime
from typing import Optional, Dict, Any
from domain.enums.crawl_status import CrawlJobStatus, CrawlJobType


@dataclass
class CrawlJob:
    """
    Pure domain crawl job entity.

    Represents a web crawling job with business rules for
    job lifecycle, scheduling, and performance tracking.
    """

    # Identity
    id: str
    created_by: str  # User ID

    # Job Configuration
    job_type: CrawlJobType
    url: Optional[str] = None  # For scrape/crawl
    csv_path: Optional[str] = None  # For batch
    collection: str = "web_content"
    max_depth: int = 2
    limit: int = 10
    auto_ingest: bool = True

    # Scheduling
    schedule_cron: Optional[str] = None

    # Metadata
    metadata: Dict[str, Any] = field(default_factory=dict)

    # Status
    status: CrawlJobStatus = CrawlJobStatus.PENDING
    error: Optional[str] = None

    # Results
    total_pages: int = 0
    successful_pages: int = 0
    failed_pages: int = 0
    ingested_pages: int = 0

    # Performance
    duration_seconds: float = 0.0

    # Timestamps
    created_at: datetime = field(default_factory=datetime.now)
    started_at: Optional[datetime] = None
    completed_at: Optional[datetime] = None

    # Business Logic Methods

    def start(self) -> None:
        """Mark job as started."""
        self.status = CrawlJobStatus.RUNNING
        self.started_at = datetime.now()

    def complete(self) -> None:
        """Mark job as completed."""
        self.status = CrawlJobStatus.COMPLETED
        self.completed_at = datetime.now()
        if self.started_at:
            self.duration_seconds = (
                self.completed_at - self.started_at
            ).total_seconds()

    def fail(self, error: str) -> None:
        """Mark job as failed."""
        self.status = CrawlJobStatus.FAILED
        self.error = error
        self.completed_at = datetime.now()
        if self.started_at:
            self.duration_seconds = (
                self.completed_at - self.started_at
            ).total_seconds()

    def cancel(self) -> None:
        """Cancel running job."""
        self.status = CrawlJobStatus.CANCELLED
        self.completed_at = datetime.now()
        if self.started_at:
            self.duration_seconds = (
                self.completed_at - self.started_at
            ).total_seconds()

    def record_page_success(self, ingested: bool = False) -> None:
        """Record successful page crawl."""
        self.total_pages += 1
        self.successful_pages += 1
        if ingested:
            self.ingested_pages += 1

    def record_page_failure(self) -> None:
        """Record failed page crawl."""
        self.total_pages += 1
        self.failed_pages += 1

    def is_running(self) -> bool:
        """Check if job is currently running."""
        return self.status == CrawlJobStatus.RUNNING

    def is_completed(self) -> bool:
        """Check if job completed successfully."""
        return self.status == CrawlJobStatus.COMPLETED

    def is_failed(self) -> bool:
        """Check if job failed."""
        return self.status == CrawlJobStatus.FAILED

    def is_scheduled(self) -> bool:
        """Check if job is scheduled."""
        return self.schedule_cron is not None

    def get_success_rate(self) -> float:
        """Calculate success rate percentage."""
        if self.total_pages == 0:
            return 0.0
        return (self.successful_pages / self.total_pages) * 100

    def get_ingestion_rate(self) -> float:
        """Calculate ingestion rate percentage."""
        if self.successful_pages == 0:
            return 0.0
        return (self.ingested_pages / self.successful_pages) * 100

    def is_owned_by(self, user_id: str) -> bool:
        """Check if job belongs to user."""
        return self.created_by == user_id

    def __repr__(self) -> str:
        return f"CrawlJob(id={self.id}, type={self.job_type.value}, status={self.status.value})"
