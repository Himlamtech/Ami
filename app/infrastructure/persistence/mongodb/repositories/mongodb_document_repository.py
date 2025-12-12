"""MongoDB Document Repository implementation."""

from typing import Optional, List, Dict, Any
from motor.motor_asyncio import AsyncIOMotorDatabase
from bson import ObjectId

from app.domain.entities.document import Document
from app.application.interfaces.repositories.document_repository import (
    IDocumentRepository,
)
from app.infrastructure.persistence.mongodb.mappers import DocumentMapper
from app.infrastructure.persistence.mongodb.models import DocumentInDB


class MongoDBDocumentRepository(IDocumentRepository):
    """MongoDB implementation of Document Repository."""

    def __init__(self, db: AsyncIOMotorDatabase):
        self.db = db
        self.collection = db["documents"]

    async def create(self, document: Document) -> Document:
        """Create new document."""
        doc_model = DocumentMapper.to_model(document)
        doc_dict = doc_model.dict(by_alias=True, exclude={"id"})

        result = await self.collection.insert_one(doc_dict)
        document.id = str(result.inserted_id)
        return document

    async def get_by_id(self, document_id: str) -> Optional[Document]:
        """Get document by ID."""
        try:
            doc = await self.collection.find_one({"_id": ObjectId(document_id)})
        except:
            return None

        if not doc:
            return None

        doc["id"] = str(doc.pop("_id"))
        doc_model = DocumentInDB(**doc)
        return DocumentMapper.to_entity(doc_model)

    async def update(self, document: Document) -> Document:
        """Update document."""
        doc_model = DocumentMapper.to_model(document)
        doc_dict = doc_model.dict(by_alias=True, exclude={"id"})

        await self.collection.update_one(
            {"_id": ObjectId(document.id)}, {"$set": doc_dict}
        )

        return document

    async def delete(self, document_id: str) -> bool:
        """Delete document."""
        result = await self.collection.delete_one({"_id": ObjectId(document_id)})
        return result.deleted_count > 0

    async def list_documents(
        self,
        skip: int = 0,
        limit: int = 100,
        collection: Optional[str] = None,
        is_active: Optional[bool] = None,
        created_by: Optional[str] = None,
    ) -> List[Document]:
        """List documents with filters."""
        query = {}
        if collection:
            query["collection"] = collection
        if is_active is not None:
            query["is_active"] = is_active
        if created_by:
            query["created_by"] = created_by

        cursor = (
            self.collection.find(query).sort("created_at", -1).skip(skip).limit(limit)
        )
        documents = []

        async for doc in cursor:
            doc["id"] = str(doc.pop("_id"))
            doc_model = DocumentInDB(**doc)
            documents.append(DocumentMapper.to_entity(doc_model))

        return documents

    async def count(
        self,
        collection: Optional[str] = None,
        is_active: Optional[bool] = None,
        created_by: Optional[str] = None,
    ) -> int:
        """Count documents."""
        query = {}
        if collection:
            query["collection"] = collection
        if is_active is not None:
            query["is_active"] = is_active
        if created_by:
            query["created_by"] = created_by

        return await self.collection.count_documents(query)

    async def get_by_collection(self, collection: str) -> List[Document]:
        """Get all documents in collection."""
        return await self.list_documents(collection=collection, limit=1000)

    async def search_by_metadata(
        self,
        metadata_filter: Dict[str, Any],
        collection: Optional[str] = None,
    ) -> List[Document]:
        """Search documents by metadata."""
        query = {}
        if collection:
            query["collection"] = collection

        # Add metadata filters
        for key, value in metadata_filter.items():
            query[f"metadata.{key}"] = value

        cursor = self.collection.find(query)
        documents = []

        async for doc in cursor:
            doc["id"] = str(doc.pop("_id"))
            doc_model = DocumentInDB(**doc)
            documents.append(DocumentMapper.to_entity(doc_model))

        return documents

    async def exists(self, document_id: str) -> bool:
        """Check if document exists."""
        try:
            count = await self.collection.count_documents(
                {"_id": ObjectId(document_id)}
            )
            return count > 0
        except:
            return False
