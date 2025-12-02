"""Data source domain entity."""

from dataclasses import dataclass, field
from datetime import datetime
from typing import Optional, Dict, Any

from app.domain.enums.data_source import (
    DataCategory,
    DataType,
    SourceType,
    SourceStatus,
)


@dataclass
class SourceAuth:
    """Authentication config for data source."""
    
    auth_type: str = "none"  # none, basic, bearer, cookie, custom
    username: Optional[str] = None
    password: Optional[str] = None
    token: Optional[str] = None
    cookies: Optional[Dict[str, str]] = None
    headers: Optional[Dict[str, str]] = None


@dataclass
class CrawlConfig:
    """Crawl configuration for data source."""
    
    # Selectors (for WEB_CRAWL)
    list_selector: Optional[str] = None       # CSS selector for list items
    detail_selector: Optional[str] = None     # CSS selector for content
    title_selector: Optional[str] = None
    date_selector: Optional[str] = None
    
    # Crawl behavior
    max_depth: int = 2
    max_pages: int = 50
    rate_limit: int = 10                      # requests per minute
    timeout_seconds: int = 30
    
    # Content filters
    min_content_length: int = 100
    exclude_patterns: list = field(default_factory=list)  # URL patterns to skip


@dataclass
class DataSource:
    """
    Data source entity for auto-crawling.
    
    Represents a configurable source of data (website, API, RSS)
    that can be scheduled for automatic crawling.
    """
    
    # Identity
    id: str
    name: str
    
    # Source config
    base_url: str
    source_type: SourceType = SourceType.WEB_CRAWL
    
    # Classification
    category: DataCategory = DataCategory.GENERAL
    data_type: DataType = DataType.REALTIME
    collection: str = "default"  # Target vector collection
    
    # Scheduling
    schedule_cron: str = "0 */6 * * *"  # Default: every 6 hours
    is_active: bool = True
    priority: int = 5  # 1 (highest) - 10 (lowest)
    
    # Authentication
    auth: Optional[SourceAuth] = None
    
    # Crawl config
    crawl_config: CrawlConfig = field(default_factory=CrawlConfig)
    
    # Status tracking
    status: SourceStatus = SourceStatus.ACTIVE
    error_message: Optional[str] = None
    error_count: int = 0
    max_errors: int = 5  # Auto-pause after this many consecutive errors
    
    # Sync scheduling
    sync_schedule: Optional[Dict[str, Any]] = None  # Auto-sync configuration
    last_synced_at: Optional[datetime] = None
    
    # Statistics
    total_crawls: int = 0
    total_documents: int = 0
    last_crawl_at: Optional[datetime] = None
    last_success_at: Optional[datetime] = None
    
    # Metadata
    description: Optional[str] = None
    tags: list = field(default_factory=list)
    metadata: Dict[str, Any] = field(default_factory=dict)
    
    # Ownership
    created_by: Optional[str] = None
    
    # Timestamps
    created_at: datetime = field(default_factory=datetime.now)
    updated_at: datetime = field(default_factory=datetime.now)
    
    # Business Logic Methods
    
    def activate(self) -> None:
        """Activate data source."""
        self.is_active = True
        self.status = SourceStatus.ACTIVE
        self.error_count = 0
        self.error_message = None
        self.updated_at = datetime.now()
    
    def pause(self) -> None:
        """Pause data source."""
        self.is_active = False
        self.status = SourceStatus.PAUSED
        self.updated_at = datetime.now()
    
    def record_error(self, error: str) -> None:
        """Record crawl error."""
        self.error_count += 1
        self.error_message = error
        self.updated_at = datetime.now()
        
        if self.error_count >= self.max_errors:
            self.status = SourceStatus.ERROR
            self.is_active = False
    
    def record_success(self, docs_count: int = 0) -> None:
        """Record successful crawl."""
        self.total_crawls += 1
        self.total_documents += docs_count
        self.last_crawl_at = datetime.now()
        self.last_success_at = datetime.now()
        self.error_count = 0  # Reset error count on success
        self.error_message = None
        self.status = SourceStatus.ACTIVE
        self.updated_at = datetime.now()
    
    def can_crawl(self) -> bool:
        """Check if source can be crawled."""
        return self.is_active and self.status in [SourceStatus.ACTIVE, SourceStatus.ERROR]
    
    def needs_retry(self) -> bool:
        """Check if source needs retry after error."""
        return self.status == SourceStatus.ERROR and self.error_count < self.max_errors
    
    def get_auth_headers(self) -> Dict[str, str]:
        """Get authentication headers for requests."""
        headers = {}
        if self.auth:
            if self.auth.auth_type == "bearer" and self.auth.token:
                headers["Authorization"] = f"Bearer {self.auth.token}"
            elif self.auth.headers:
                headers.update(self.auth.headers)
        return headers
    
    def __repr__(self) -> str:
        return f"DataSource(id={self.id}, name={self.name}, status={self.status.value})"
