"""Monitor target DTOs."""

from datetime import datetime
from typing import Optional, Dict, List
from pydantic import BaseModel, Field


class MonitorTargetRequest(BaseModel):
    name: str
    url: str
    collection: str = "default"
    category: str = "general"
    interval_hours: int = Field(default=6, ge=1, le=168)
    selector: Optional[str] = None
    metadata: Optional[Dict[str, str]] = None


class MonitorTargetUpdateRequest(BaseModel):
    name: Optional[str] = None
    url: Optional[str] = None
    collection: Optional[str] = None
    category: Optional[str] = None
    interval_hours: Optional[int] = Field(None, ge=1, le=168)
    selector: Optional[str] = None
    metadata: Optional[Dict[str, str]] = None
    is_active: Optional[bool] = None


class MonitorTargetResponse(BaseModel):
    id: str
    name: str
    url: str
    collection: str
    category: str
    interval_hours: int
    selector: Optional[str]
    is_active: bool
    last_checked_at: Optional[datetime]
    last_success_at: Optional[datetime]
    last_error: Optional[str]
    consecutive_failures: int
    metadata: Dict[str, str]
    created_at: datetime
    updated_at: datetime


class MonitorTargetListResponse(BaseModel):
    items: List[MonitorTargetResponse]
    total: int
    skip: int
    limit: int
