"""MonitorTarget domain entity."""

from dataclasses import dataclass, field
from datetime import datetime, timedelta
from typing import Optional, Dict


@dataclass
class MonitorTarget:
    """
    Represents a URL or portal that should be monitored periodically.
    """

    id: str
    name: str
    url: str
    collection: str = "default"
    category: str = "general"

    # Crawl configuration
    interval_hours: int = 6
    is_active: bool = True
    selector: Optional[str] = None  # optional CSS selector for content

    # State
    last_checked_at: Optional[datetime] = None
    last_success_at: Optional[datetime] = None
    last_error: Optional[str] = None
    consecutive_failures: int = 0
    max_failures: int = 5
    last_content_hash: Optional[str] = None
    metadata: Dict[str, str] = field(default_factory=dict)

    # Audit
    created_at: datetime = field(default_factory=datetime.now)
    updated_at: datetime = field(default_factory=datetime.now)

    def should_check(self, now: Optional[datetime] = None) -> bool:
        """Determine if monitor should run (based on interval and status)."""
        if not self.is_active:
            return False
        if self.last_checked_at is None:
            return True

        now = now or datetime.now()
        due_time = self.last_checked_at + timedelta(hours=self.interval_hours)
        return now >= due_time

    def mark_success(self, content_hash: Optional[str] = None) -> None:
        """Update monitor state after successful check."""
        now = datetime.now()
        self.last_checked_at = now
        self.last_success_at = now
        self.consecutive_failures = 0
        self.last_error = None
        if content_hash:
            self.last_content_hash = content_hash
        self.updated_at = now

    def mark_failure(self, error: str) -> None:
        """Update monitor state after failure."""
        now = datetime.now()
        self.last_checked_at = now
        self.consecutive_failures += 1
        self.last_error = error
        if self.consecutive_failures >= self.max_failures:
            self.is_active = False
        self.updated_at = now
