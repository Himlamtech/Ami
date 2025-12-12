"""Data source DTOs for API layer."""

from typing import Optional, List, Dict
from datetime import datetime
from pydantic import BaseModel, Field


# ===== Request DTOs =====


class CreateDataSourceRequest(BaseModel):
    """Request to create a new data source."""

    name: str = Field(..., min_length=1, max_length=200)
    base_url: str = Field(..., min_length=1)
    source_type: str = Field(default="web_crawl")
    category: str = Field(default="general")
    data_type: str = Field(default="realtime")
    collection: str = Field(default="default")
    schedule_cron: str = Field(default="0 */6 * * *")
    priority: int = Field(default=5, ge=1, le=10)
    description: Optional[str] = None
    tags: Optional[List[str]] = None

    # Auth
    auth_type: str = Field(default="none")
    auth_username: Optional[str] = None
    auth_password: Optional[str] = None
    auth_token: Optional[str] = None
    auth_headers: Optional[Dict[str, str]] = None

    # Crawl config
    list_selector: Optional[str] = None
    detail_selector: Optional[str] = None
    title_selector: Optional[str] = None
    date_selector: Optional[str] = None
    max_depth: int = Field(default=2, ge=1, le=5)
    max_pages: int = Field(default=50, ge=1, le=500)
    rate_limit: int = Field(default=10, ge=1, le=60)


class UpdateDataSourceRequest(BaseModel):
    """Request to update a data source."""

    name: Optional[str] = None
    base_url: Optional[str] = None
    source_type: Optional[str] = None
    category: Optional[str] = None
    data_type: Optional[str] = None
    collection: Optional[str] = None
    schedule_cron: Optional[str] = None
    is_active: Optional[bool] = None
    priority: Optional[int] = Field(default=None, ge=1, le=10)
    description: Optional[str] = None
    tags: Optional[List[str]] = None

    # Auth
    auth_type: Optional[str] = None
    auth_username: Optional[str] = None
    auth_password: Optional[str] = None
    auth_token: Optional[str] = None
    auth_headers: Optional[Dict[str, str]] = None

    # Crawl config
    list_selector: Optional[str] = None
    detail_selector: Optional[str] = None
    title_selector: Optional[str] = None
    date_selector: Optional[str] = None
    max_depth: Optional[int] = Field(default=None, ge=1, le=5)
    max_pages: Optional[int] = Field(default=None, ge=1, le=500)
    rate_limit: Optional[int] = Field(default=None, ge=1, le=60)


class TestDataSourceRequest(BaseModel):
    """Request to test a data source."""

    url: str
    source_type: str = Field(default="web_crawl")
    detail_selector: Optional[str] = None
    auth_type: str = Field(default="none")
    auth_token: Optional[str] = None
    auth_headers: Optional[Dict[str, str]] = None


# ===== Response DTOs =====


class CrawlConfigResponse(BaseModel):
    """Crawl config response."""

    list_selector: Optional[str] = None
    detail_selector: Optional[str] = None
    title_selector: Optional[str] = None
    date_selector: Optional[str] = None
    max_depth: int = 2
    max_pages: int = 50
    rate_limit: int = 10


class AuthConfigResponse(BaseModel):
    """Auth config response (no sensitive data)."""

    auth_type: str = "none"
    has_credentials: bool = False


class DataSourceResponse(BaseModel):
    """Data source response."""

    id: str
    name: str
    base_url: str
    source_type: str
    category: str
    data_type: str
    collection: str
    schedule_cron: str
    is_active: bool
    priority: int
    status: str
    error_message: Optional[str] = None
    error_count: int = 0
    total_crawls: int = 0
    total_documents: int = 0
    last_crawl_at: Optional[datetime] = None
    last_success_at: Optional[datetime] = None
    description: Optional[str] = None
    tags: List[str] = []
    crawl_config: Optional[CrawlConfigResponse] = None
    auth: Optional[AuthConfigResponse] = None
    created_at: datetime
    updated_at: datetime


class DataSourceListResponse(BaseModel):
    """List data sources response."""

    sources: List[DataSourceResponse]
    total: int
    skip: int
    limit: int


class TestDataSourceResponse(BaseModel):
    """Test data source response."""

    success: bool
    content_preview: Optional[str] = None
    content_length: int = 0
    title: Optional[str] = None
    error: Optional[str] = None
    duration_seconds: float = 0.0
