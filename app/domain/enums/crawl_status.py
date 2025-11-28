"""Crawl status enumerations."""

from enum import Enum


class CrawlStatus(str, Enum):
    """Status of a crawl task."""
    
    PENDING = "pending"
    IN_PROGRESS = "in_progress"
    COMPLETED = "completed"
    FAILED = "failed"
    SKIPPED = "skipped"


class CrawlJobStatus(str, Enum):
    """Status of a crawl job."""
    
    PENDING = "pending"
    RUNNING = "running"
    COMPLETED = "completed"
    FAILED = "failed"
    CANCELLED = "cancelled"
    SCHEDULED = "scheduled"


class CrawlJobType(str, Enum):
    """Type of crawl job."""
    
    SCRAPE = "scrape"  # Single page scrape
    CRAWL = "crawl"    # Multi-page crawl
    BATCH = "batch"    # Batch crawl from CSV
