"""Bookmark DTOs for API request/response."""

from pydantic import BaseModel, Field
from typing import Optional, List, Dict, Any
from datetime import datetime


# ===== Request DTOs =====


class CreateBookmarkRequest(BaseModel):
    """Request to create a bookmark."""

    session_id: str
    message_id: str
    query: str
    response: str
    title: Optional[str] = None
    tags: Optional[List[str]] = None
    notes: Optional[str] = None
    folder: Optional[str] = None
    sources: Optional[List[Dict[str, Any]]] = None
    artifacts: Optional[List[Dict[str, Any]]] = None


class UpdateBookmarkRequest(BaseModel):
    """Request to update a bookmark."""

    title: Optional[str] = None
    tags: Optional[List[str]] = None
    notes: Optional[str] = None
    folder: Optional[str] = None
    is_pinned: Optional[bool] = None


class SearchBookmarksRequest(BaseModel):
    """Request to search bookmarks."""

    query: Optional[str] = None
    tags: Optional[List[str]] = None
    folder: Optional[str] = None
    skip: int = Field(default=0, ge=0)
    limit: int = Field(default=50, ge=1, le=100)


# ===== Response DTOs =====


class BookmarkResponse(BaseModel):
    """Bookmark response."""

    id: str
    user_id: str
    session_id: str
    message_id: str
    query: str
    response: str
    title: Optional[str] = None
    tags: List[str] = []
    notes: Optional[str] = None
    folder: Optional[str] = None
    sources: List[Dict[str, Any]] = []
    artifacts: List[Dict[str, Any]] = []
    is_pinned: bool = False
    is_archived: bool = False
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True


class BookmarkListResponse(BaseModel):
    """List of bookmarks response."""

    bookmarks: List[BookmarkResponse]
    total: int
    skip: int
    limit: int


class BookmarkTagsResponse(BaseModel):
    """User's bookmark tags."""

    tags: List[str]
    total: int


class BookmarkFoldersResponse(BaseModel):
    """User's bookmark folders."""

    folders: List[str]
    total: int


class BookmarkExportResponse(BaseModel):
    """Exported bookmarks."""

    format: str
    content: str
    filename: str
