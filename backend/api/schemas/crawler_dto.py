"""Crawler DTOs."""

from pydantic import BaseModel
from datetime import datetime


class CreateCrawlJobRequest(BaseModel):
    """Create crawl job request."""

    url: str
    collection: str = "web_content"
    max_depth: int = 2
    limit: int = 10
    auto_ingest: bool = True


class CrawlJobResponse(BaseModel):
    """Crawl job response."""

    id: str
    url: str
    status: str
    total_pages: int
    successful_pages: int
    failed_pages: int
    created_at: datetime

    class Config:
        from_attributes = True
