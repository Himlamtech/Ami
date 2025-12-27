"""Bookmark API routes for saving and organizing Q&A pairs."""

import json
from fastapi import APIRouter, Depends, HTTPException, status, Query
from typing import List, Optional

from app.api.dependencies.auth import get_user_id
from app.api.schemas.bookmark_dto import (
    CreateBookmarkRequest,
    UpdateBookmarkRequest,
    BookmarkResponse,
    BookmarkListResponse,
    BookmarkTagsResponse,
    BookmarkFoldersResponse,
    BookmarkExportResponse,
)
from app.domain.entities.bookmark import Bookmark
from app.config.services import ServiceRegistry


router = APIRouter(prefix="/bookmarks", tags=["Bookmarks"])


@router.post("", response_model=BookmarkResponse, status_code=status.HTTP_201_CREATED)
async def create_bookmark(
    request: CreateBookmarkRequest,
    user_id: str = Depends(get_user_id),
):
    """Create a new bookmark from a Q&A pair."""
    repo = ServiceRegistry.get_bookmark_repository()

    bookmark = Bookmark(
        user_id=user_id,
        session_id=request.session_id,
        message_id=request.message_id,
        query=request.query,
        response=request.response,
        title=request.title,
        tags=[t.lower().strip() for t in (request.tags or [])],
        notes=request.notes,
        folder=request.folder,
        sources=request.sources or [],
        artifacts=request.artifacts or [],
    )

    created = await repo.create(bookmark)
    return _to_response(created)


@router.get("", response_model=BookmarkListResponse)
async def list_bookmarks(
    user_id: str = Depends(get_user_id),
    skip: int = Query(default=0, ge=0),
    limit: int = Query(default=50, ge=1, le=100),
    include_archived: bool = Query(default=False),
):
    """List user's bookmarks (pinned first, then by date)."""
    repo = ServiceRegistry.get_bookmark_repository()

    bookmarks = await repo.get_by_user(
        user_id=user_id,
        skip=skip,
        limit=limit,
        include_archived=include_archived,
    )
    total = await repo.count_by_user(user_id, include_archived)

    return BookmarkListResponse(
        bookmarks=[_to_response(b) for b in bookmarks],
        total=total,
        skip=skip,
        limit=limit,
    )


@router.get("/pinned", response_model=List[BookmarkResponse])
async def get_pinned_bookmarks(
    user_id: str = Depends(get_user_id),
):
    """Get user's pinned bookmarks."""
    repo = ServiceRegistry.get_bookmark_repository()

    bookmarks = await repo.get_pinned(user_id)
    return [_to_response(b) for b in bookmarks]


@router.get("/tags", response_model=BookmarkTagsResponse)
async def get_user_tags(
    user_id: str = Depends(get_user_id),
):
    """Get all unique tags used by user."""
    repo = ServiceRegistry.get_bookmark_repository()

    tags = await repo.get_tags_by_user(user_id)
    return BookmarkTagsResponse(tags=tags, total=len(tags))


@router.get("/folders", response_model=BookmarkFoldersResponse)
async def get_user_folders(
    user_id: str = Depends(get_user_id),
):
    """Get all unique folders used by user."""
    repo = ServiceRegistry.get_bookmark_repository()

    folders = await repo.get_folders_by_user(user_id)
    return BookmarkFoldersResponse(folders=folders, total=len(folders))


@router.get("/search", response_model=BookmarkListResponse)
async def search_bookmarks(
    user_id: str = Depends(get_user_id),
    q: Optional[str] = Query(default=None, description="Search query"),
    tags: Optional[str] = Query(default=None, description="Comma-separated tags"),
    folder: Optional[str] = Query(default=None, description="Folder name"),
    skip: int = Query(default=0, ge=0),
    limit: int = Query(default=50, ge=1, le=100),
):
    """Search bookmarks by query, tags, or folder."""
    repo = ServiceRegistry.get_bookmark_repository()

    tag_list = None
    if tags:
        tag_list = [t.strip().lower() for t in tags.split(",") if t.strip()]

    bookmarks = await repo.search(
        user_id=user_id,
        query=q or "",
        tags=tag_list,
        folder=folder,
        skip=skip,
        limit=limit,
    )

    total = len(bookmarks)

    return BookmarkListResponse(
        bookmarks=[_to_response(b) for b in bookmarks],
        total=total,
        skip=skip,
        limit=limit,
    )


@router.get("/{bookmark_id}", response_model=BookmarkResponse)
async def get_bookmark(
    bookmark_id: str,
    user_id: str = Depends(get_user_id),
):
    """Get a specific bookmark by ID."""
    repo = ServiceRegistry.get_bookmark_repository()

    bookmark = await repo.get_by_id(bookmark_id)
    if not bookmark:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Bookmark not found",
        )

    if bookmark.user_id != user_id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Access denied",
        )

    return _to_response(bookmark)


@router.put("/{bookmark_id}", response_model=BookmarkResponse)
async def update_bookmark(
    bookmark_id: str,
    request: UpdateBookmarkRequest,
    user_id: str = Depends(get_user_id),
):
    """Update a bookmark."""
    repo = ServiceRegistry.get_bookmark_repository()

    bookmark = await repo.get_by_id(bookmark_id)
    if not bookmark:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Bookmark not found",
        )

    if bookmark.user_id != user_id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Access denied",
        )

    if request.title is not None:
        bookmark.title = request.title
    if request.tags is not None:
        bookmark.tags = [t.lower().strip() for t in request.tags]
    if request.notes is not None:
        bookmark.notes = request.notes
    if request.folder is not None:
        bookmark.folder = request.folder
    if request.is_archived is not None:
        bookmark.is_archived = request.is_archived
    if request.is_pinned is not None:
        bookmark.is_pinned = request.is_pinned

    updated = await repo.update(bookmark)

    return _to_response(updated)


@router.delete("/{bookmark_id}")
async def delete_bookmark(
    bookmark_id: str,
    user_id: str = Depends(get_user_id),
):
    """Delete a bookmark."""
    repo = ServiceRegistry.get_bookmark_repository()

    bookmark = await repo.get_by_id(bookmark_id)
    if not bookmark:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Bookmark not found",
        )

    if bookmark.user_id != user_id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Access denied",
        )

    await repo.delete(bookmark_id)
    return {"status": "deleted"}


@router.post("/{bookmark_id}/pin", response_model=BookmarkResponse)
async def pin_bookmark(
    bookmark_id: str,
    user_id: str = Depends(get_user_id),
):
    """Pin a bookmark."""
    repo = ServiceRegistry.get_bookmark_repository()

    bookmark = await repo.get_by_id(bookmark_id)
    if not bookmark:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Bookmark not found",
        )

    if bookmark.user_id != user_id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Access denied",
        )

    bookmark.is_pinned = True
    updated = await repo.update(bookmark)
    return _to_response(updated)


@router.post("/{bookmark_id}/export", response_model=BookmarkExportResponse)
async def export_bookmark(
    bookmark_id: str,
    user_id: str = Depends(get_user_id),
):
    """Export a bookmark (placeholder)."""
    repo = ServiceRegistry.get_bookmark_repository()

    bookmark = await repo.get_by_id(bookmark_id)
    if not bookmark:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Bookmark not found",
        )

    if bookmark.user_id != user_id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Access denied",
        )

    content = json.dumps(
        _to_response(bookmark).dict(), ensure_ascii=False, indent=2, default=str
    )
    return BookmarkExportResponse(
        format="json",
        content=content,
        filename=f"bookmark_{bookmark_id}.json",
    )


@router.get("/export/json", response_model=BookmarkExportResponse)
async def export_bookmarks_json(
    user_id: str = Depends(get_user_id),
):
    """Export all bookmarks as JSON."""
    repo = ServiceRegistry.get_bookmark_repository()

    bookmarks = await repo.get_by_user(
        user_id=user_id,
        skip=0,
        limit=1000,
        include_archived=True,
    )
    content = json.dumps(
        [_to_response(bookmark).dict() for bookmark in bookmarks],
        ensure_ascii=False,
        indent=2,
        default=str,
    )
    return BookmarkExportResponse(
        format="json",
        content=content,
        filename="bookmarks.json",
    )


def _to_response(bookmark: Bookmark) -> BookmarkResponse:
    """Convert Bookmark entity to response DTO."""
    return BookmarkResponse(
        id=bookmark.id,
        user_id=bookmark.user_id,
        session_id=bookmark.session_id,
        message_id=bookmark.message_id,
        query=bookmark.query,
        response=bookmark.response,
        title=bookmark.title,
        tags=bookmark.tags,
        notes=bookmark.notes,
        folder=bookmark.folder,
        sources=bookmark.sources,
        artifacts=bookmark.artifacts,
        is_pinned=getattr(bookmark, "is_pinned", False),
        is_archived=getattr(bookmark, "is_archived", False),
        created_at=bookmark.created_at,
        updated_at=bookmark.updated_at,
    )


__all__ = ["router"]
