"""MongoDB File Repository implementation."""

from typing import Optional, List
from motor.motor_asyncio import AsyncIOMotorDatabase
from bson import ObjectId

from app.domain.entities.file_metadata import FileMetadata
from app.domain.enums.file_type import FileType
from app.application.interfaces.repositories.file_repository import IFileRepository


class MongoDBFileRepository(IFileRepository):
    """MongoDB implementation of File Repository."""

    def __init__(self, db: AsyncIOMotorDatabase):
        self.db = db
        self.collection = db["file_metadata"]

    async def create(self, file_metadata: FileMetadata) -> FileMetadata:
        """Create file metadata."""
        # Simple dict conversion (can use mapper if needed)
        file_dict = {
            "user_id": file_metadata.user_id,
            "filename": file_metadata.filename,
            "original_name": file_metadata.original_name,
            "mime_type": file_metadata.mime_type,
            "size": file_metadata.size,
            "url": file_metadata.url,
            "file_type": file_metadata.file_type.value,
            "session_id": file_metadata.session_id,
            "status": file_metadata.status,
            "created_at": file_metadata.created_at,
        }

        result = await self.collection.insert_one(file_dict)
        file_metadata.id = str(result.inserted_id)
        return file_metadata

    async def get_by_id(self, file_id: str) -> Optional[FileMetadata]:
        """Get file by ID."""
        try:
            doc = await self.collection.find_one({"_id": ObjectId(file_id)})
        except:
            return None

        if not doc:
            return None

        # Convert back to entity (simplified)
        return self._doc_to_entity(doc)

    async def update(self, file_metadata: FileMetadata) -> FileMetadata:
        """Update file metadata."""
        file_dict = {
            "status": file_metadata.status,
            "updated_at": file_metadata.updated_at,
        }

        await self.collection.update_one(
            {"_id": ObjectId(file_metadata.id)}, {"$set": file_dict}
        )

        return file_metadata

    async def delete(self, file_id: str) -> bool:
        """Soft delete file."""
        result = await self.collection.update_one(
            {"_id": ObjectId(file_id)}, {"$set": {"is_deleted": True}}
        )
        return result.modified_count > 0

    async def list_by_user(
        self,
        user_id: str,
        skip: int = 0,
        limit: int = 100,
        file_type: Optional[FileType] = None,
    ) -> List[FileMetadata]:
        """List files by user."""
        query = {"user_id": user_id, "is_deleted": False}
        if file_type:
            query["file_type"] = file_type.value

        cursor = (
            self.collection.find(query).sort("created_at", -1).skip(skip).limit(limit)
        )
        files = []

        async for doc in cursor:
            files.append(self._doc_to_entity(doc))

        return files

    async def list_by_session(
        self,
        session_id: str,
        skip: int = 0,
        limit: int = 100,
    ) -> List[FileMetadata]:
        """List files by session."""
        cursor = (
            self.collection.find({"session_id": session_id}).skip(skip).limit(limit)
        )
        files = []

        async for doc in cursor:
            files.append(self._doc_to_entity(doc))

        return files

    async def count_by_user(
        self,
        user_id: str,
        file_type: Optional[FileType] = None,
    ) -> int:
        """Count files by user."""
        query = {"user_id": user_id}
        if file_type:
            query["file_type"] = file_type.value

        return await self.collection.count_documents(query)

    async def get_total_size_by_user(self, user_id: str) -> int:
        """Get total file size for user."""
        pipeline = [
            {"$match": {"user_id": user_id}},
            {"$group": {"_id": None, "total": {"$sum": "$size"}}},
        ]

        result = await self.collection.aggregate(pipeline).to_list(1)
        return result[0]["total"] if result else 0

    async def exists(self, file_id: str) -> bool:
        """Check if file exists."""
        try:
            count = await self.collection.count_documents({"_id": ObjectId(file_id)})
            return count > 0
        except:
            return False

    def _doc_to_entity(self, doc: dict) -> FileMetadata:
        """Convert MongoDB doc to entity."""
        from datetime import datetime

        return FileMetadata(
            id=str(doc["_id"]),
            user_id=doc["user_id"],
            filename=doc["filename"],
            original_name=doc.get("original_name"),
            mime_type=doc.get("mime_type", ""),
            size=doc.get("size", 0),
            url=doc.get("url", ""),
            file_type=FileType(doc.get("file_type", "uploaded")),
            session_id=doc.get("session_id"),
            status=doc.get("status", "processed"),
            created_at=doc.get("created_at", datetime.now()),
            updated_at=doc.get("updated_at", datetime.now()),
        )
