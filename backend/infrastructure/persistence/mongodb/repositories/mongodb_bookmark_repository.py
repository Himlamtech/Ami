"""MongoDB implementation of bookmark repository."""

from typing import Optional, List
from datetime import datetime, timezone

from motor.motor_asyncio import AsyncIOMotorDatabase

from app.application.interfaces.repositories.bookmark_repository import (
    IBookmarkRepository,
)
from app.domain.entities.bookmark import Bookmark
from app.config.persistence import mongodb_config


class MongoDBBookmarkRepository(IBookmarkRepository):
    """MongoDB implementation for bookmark data access."""

    def __init__(self, database: AsyncIOMotorDatabase):
        self._db = database
        self._collection = database[mongodb_config.collection_bookmarks]

    async def create(self, bookmark: Bookmark) -> Bookmark:
        """Create a new bookmark."""
        doc = self._to_document(bookmark)
        await self._collection.insert_one(doc)
        return bookmark

    async def get_by_id(self, bookmark_id: str) -> Optional[Bookmark]:
        """Get bookmark by ID."""
        doc = await self._collection.find_one({"_id": bookmark_id})
        return self._from_document(doc) if doc else None

    async def get_by_user(
        self,
        user_id: str,
        skip: int = 0,
        limit: int = 50,
        include_archived: bool = False,
    ) -> List[Bookmark]:
        """Get bookmarks for a user, sorted by pinned first, then created_at desc."""
        query = {"user_id": user_id}
        if not include_archived:
            query["is_archived"] = False

        cursor = (
            self._collection.find(query)
            .sort(
                [
                    ("is_pinned", -1),
                    ("created_at", -1),
                ]
            )
            .skip(skip)
            .limit(limit)
        )

        bookmarks = []
        async for doc in cursor:
            bookmarks.append(self._from_document(doc))
        return bookmarks

    async def search(
        self,
        user_id: str,
        query: str,
        tags: Optional[List[str]] = None,
        folder: Optional[str] = None,
        skip: int = 0,
        limit: int = 50,
    ) -> List[Bookmark]:
        """Search bookmarks by query, tags, or folder."""
        filter_query = {
            "user_id": user_id,
            "is_archived": False,
        }

        # Text search on query and response
        if query:
            filter_query["$or"] = [
                {"query": {"$regex": query, "$options": "i"}},
                {"response": {"$regex": query, "$options": "i"}},
                {"title": {"$regex": query, "$options": "i"}},
                {"notes": {"$regex": query, "$options": "i"}},
            ]

        # Filter by tags
        if tags:
            filter_query["tags"] = {"$all": [t.lower() for t in tags]}

        # Filter by folder
        if folder:
            filter_query["folder"] = folder

        cursor = (
            self._collection.find(filter_query)
            .sort(
                [
                    ("is_pinned", -1),
                    ("created_at", -1),
                ]
            )
            .skip(skip)
            .limit(limit)
        )

        bookmarks = []
        async for doc in cursor:
            bookmarks.append(self._from_document(doc))
        return bookmarks

    async def update(self, bookmark: Bookmark) -> Bookmark:
        """Update an existing bookmark."""
        bookmark.updated_at = datetime.now(timezone.utc)
        doc = self._to_document(bookmark)
        await self._collection.replace_one({"_id": bookmark.id}, doc)
        return bookmark

    async def delete(self, bookmark_id: str) -> bool:
        """Delete a bookmark."""
        result = await self._collection.delete_one({"_id": bookmark_id})
        return result.deleted_count > 0

    async def count_by_user(self, user_id: str, include_archived: bool = False) -> int:
        """Count bookmarks for a user."""
        query = {"user_id": user_id}
        if not include_archived:
            query["is_archived"] = False
        return await self._collection.count_documents(query)

    async def get_tags_by_user(self, user_id: str) -> List[str]:
        """Get all unique tags used by a user."""
        pipeline = [
            {"$match": {"user_id": user_id}},
            {"$unwind": "$tags"},
            {"$group": {"_id": "$tags"}},
            {"$sort": {"_id": 1}},
        ]
        tags = []
        async for doc in self._collection.aggregate(pipeline):
            tags.append(doc["_id"])
        return tags

    async def get_folders_by_user(self, user_id: str) -> List[str]:
        """Get all unique folders used by a user."""
        pipeline = [
            {"$match": {"user_id": user_id, "folder": {"$ne": None}}},
            {"$group": {"_id": "$folder"}},
            {"$sort": {"_id": 1}},
        ]
        folders = []
        async for doc in self._collection.aggregate(pipeline):
            folders.append(doc["_id"])
        return folders

    async def get_pinned(self, user_id: str) -> List[Bookmark]:
        """Get pinned bookmarks for a user."""
        cursor = self._collection.find(
            {
                "user_id": user_id,
                "is_pinned": True,
                "is_archived": False,
            }
        ).sort("created_at", -1)

        bookmarks = []
        async for doc in cursor:
            bookmarks.append(self._from_document(doc))
        return bookmarks

    # ========== Internal Methods ==========

    def _to_document(self, bookmark: Bookmark) -> dict:
        """Convert Bookmark entity to MongoDB document."""
        return {
            "_id": bookmark.id,
            "user_id": bookmark.user_id,
            "session_id": bookmark.session_id,
            "message_id": bookmark.message_id,
            "query": bookmark.query,
            "response": bookmark.response,
            "title": bookmark.title,
            "tags": bookmark.tags,
            "notes": bookmark.notes,
            "folder": bookmark.folder,
            "sources": bookmark.sources,
            "artifacts": bookmark.artifacts,
            "is_pinned": bookmark.is_pinned,
            "is_archived": bookmark.is_archived,
            "created_at": bookmark.created_at,
            "updated_at": bookmark.updated_at,
        }

    def _from_document(self, doc: dict) -> Bookmark:
        """Convert MongoDB document to Bookmark entity."""
        return Bookmark(
            id=str(doc["_id"]),
            user_id=doc.get("user_id", ""),
            session_id=doc.get("session_id", ""),
            message_id=doc.get("message_id", ""),
            query=doc.get("query", ""),
            response=doc.get("response", ""),
            title=doc.get("title"),
            tags=doc.get("tags", []),
            notes=doc.get("notes"),
            folder=doc.get("folder"),
            sources=doc.get("sources", []),
            artifacts=doc.get("artifacts", []),
            is_pinned=doc.get("is_pinned", False),
            is_archived=doc.get("is_archived", False),
            created_at=doc.get("created_at", datetime.now(timezone.utc)),
            updated_at=doc.get("updated_at", datetime.now(timezone.utc)),
        )
