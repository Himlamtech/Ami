"""MongoDB Pending Update Repository implementation."""

from typing import Optional, List, Dict, Any
from datetime import datetime
from motor.motor_asyncio import AsyncIOMotorDatabase
from bson import ObjectId

from app.domain.entities.pending_update import PendingUpdate
from app.domain.enums.data_source import (
    PendingStatus,
    DataCategory,
    UpdateDetectionType,
)
from app.application.interfaces.repositories.pending_update_repository import (
    IPendingUpdateRepository,
)


class MongoDBPendingUpdateRepository(IPendingUpdateRepository):
    """MongoDB implementation of PendingUpdate Repository."""

    def __init__(self, db: AsyncIOMotorDatabase):
        self.db = db
        self.collection = db["pending_updates"]

    async def create(self, pending: PendingUpdate) -> PendingUpdate:
        """Create new pending update."""
        doc = self._entity_to_doc(pending)
        result = await self.collection.insert_one(doc)
        pending.id = str(result.inserted_id)
        return pending

    async def get_by_id(self, pending_id: str) -> Optional[PendingUpdate]:
        """Get pending update by ID."""
        try:
            doc = await self.collection.find_one({"_id": ObjectId(pending_id)})
        except Exception:
            return None

        if not doc:
            return None

        return self._doc_to_entity(doc)

    async def update(self, pending: PendingUpdate) -> PendingUpdate:
        """Update pending update."""
        doc = self._entity_to_doc(pending)
        doc.pop("_id", None)

        await self.collection.update_one({"_id": ObjectId(pending.id)}, {"$set": doc})

        return pending

    async def delete(self, pending_id: str) -> bool:
        """Delete pending update."""
        result = await self.collection.delete_one({"_id": ObjectId(pending_id)})
        return result.deleted_count > 0

    async def list(
        self,
        skip: int = 0,
        limit: int = 100,
        status: Optional[PendingStatus] = None,
        source_id: Optional[str] = None,
        category: Optional[DataCategory] = None,
        detection_type: Optional[UpdateDetectionType] = None,
    ) -> List[PendingUpdate]:
        """List pending updates with filters."""
        query = self._build_query(status, source_id, category, detection_type)

        cursor = (
            self.collection.find(query)
            .sort([("priority", 1), ("created_at", -1)])
            .skip(skip)
            .limit(limit)
        )

        items = []
        async for doc in cursor:
            items.append(self._doc_to_entity(doc))

        return items

    async def count(
        self,
        status: Optional[PendingStatus] = None,
        source_id: Optional[str] = None,
        category: Optional[DataCategory] = None,
    ) -> int:
        """Count pending updates with filters."""
        query = self._build_query(status, source_id, category, None)
        return await self.collection.count_documents(query)

    async def get_pending_queue(
        self,
        skip: int = 0,
        limit: int = 50,
    ) -> List[PendingUpdate]:
        """Get pending items sorted by priority and date."""
        return await self.list(
            skip=skip,
            limit=limit,
            status=PendingStatus.PENDING,
        )

    async def check_duplicate(self, content_hash: str) -> bool:
        """Check if content already exists by hash."""
        doc = await self.collection.find_one(
            {
                "content_hash": content_hash,
                "status": {
                    "$in": [PendingStatus.PENDING.value, PendingStatus.APPROVED.value]
                },
            }
        )
        return doc is not None

    async def bulk_approve(self, pending_ids: List[str], reviewer_id: str) -> int:
        """Bulk approve pending updates."""
        now = datetime.now()
        object_ids = [ObjectId(pid) for pid in pending_ids]

        result = await self.collection.update_many(
            {"_id": {"$in": object_ids}, "status": PendingStatus.PENDING.value},
            {
                "$set": {
                    "status": PendingStatus.APPROVED.value,
                    "reviewed_by": reviewer_id,
                    "reviewed_at": now,
                }
            },
        )

        return result.modified_count

    async def bulk_reject(self, pending_ids: List[str], reviewer_id: str) -> int:
        """Bulk reject pending updates."""
        now = datetime.now()
        object_ids = [ObjectId(pid) for pid in pending_ids]

        result = await self.collection.update_many(
            {"_id": {"$in": object_ids}, "status": PendingStatus.PENDING.value},
            {
                "$set": {
                    "status": PendingStatus.REJECTED.value,
                    "reviewed_by": reviewer_id,
                    "reviewed_at": now,
                }
            },
        )

        return result.modified_count

    async def expire_old(self) -> int:
        """Mark expired items as EXPIRED."""
        now = datetime.now()

        result = await self.collection.update_many(
            {"status": PendingStatus.PENDING.value, "expires_at": {"$lt": now}},
            {"$set": {"status": PendingStatus.EXPIRED.value}},
        )

        return result.modified_count

    async def get_stats(self) -> Dict[str, Any]:
        """Get approval queue statistics."""
        pipeline = [
            {
                "$facet": {
                    "by_status": [{"$group": {"_id": "$status", "count": {"$sum": 1}}}],
                    "by_category": [
                        {"$match": {"status": PendingStatus.PENDING.value}},
                        {"$group": {"_id": "$category", "count": {"$sum": 1}}},
                    ],
                    "by_detection_type": [
                        {"$match": {"status": PendingStatus.PENDING.value}},
                        {"$group": {"_id": "$detection_type", "count": {"$sum": 1}}},
                    ],
                    "by_source": [
                        {"$match": {"status": PendingStatus.PENDING.value}},
                        {"$group": {"_id": "$source_id", "count": {"$sum": 1}}},
                    ],
                }
            }
        ]

        result = await self.collection.aggregate(pipeline).to_list(1)

        if not result:
            return {
                "total_pending": 0,
                "total_approved": 0,
                "total_rejected": 0,
                "by_category": {},
                "by_detection_type": {},
                "by_source": {},
            }

        data = result[0]

        # Parse status counts
        status_counts = {
            item["_id"]: item["count"] for item in data.get("by_status", [])
        }

        return {
            "total_pending": status_counts.get(PendingStatus.PENDING.value, 0),
            "total_approved": status_counts.get(PendingStatus.APPROVED.value, 0),
            "total_rejected": status_counts.get(PendingStatus.REJECTED.value, 0),
            "by_category": {
                item["_id"]: item["count"] for item in data.get("by_category", [])
            },
            "by_detection_type": {
                item["_id"]: item["count"] for item in data.get("by_detection_type", [])
            },
            "by_source": {
                item["_id"]: item["count"] for item in data.get("by_source", [])
            },
        }

    def _build_query(
        self,
        status: Optional[PendingStatus] = None,
        source_id: Optional[str] = None,
        category: Optional[DataCategory] = None,
        detection_type: Optional[UpdateDetectionType] = None,
    ) -> dict:
        """Build MongoDB query from filters."""
        query = {}
        if status:
            query["status"] = status.value
        if source_id:
            query["source_id"] = source_id
        if category:
            query["category"] = category.value
        if detection_type:
            query["detection_type"] = detection_type.value
        return query

    def _entity_to_doc(self, pending: PendingUpdate) -> dict:
        """Convert entity to MongoDB document."""
        doc = {
            "source_id": pending.source_id,
            "title": pending.title,
            "content": pending.content,
            "content_hash": pending.content_hash,
            "source_url": pending.source_url,
            "category": pending.category.value,
            "detection_type": pending.detection_type.value,
            "similarity_score": pending.similarity_score,
            "matched_doc_id": pending.matched_doc_id,
            "matched_doc_ids": pending.matched_doc_ids,
            "llm_analysis": pending.llm_analysis,
            "llm_summary": pending.llm_summary,
            "diff_summary": pending.diff_summary,
            "raw_file_path": pending.raw_file_path,
            "status": pending.status.value,
            "reviewed_by": pending.reviewed_by,
            "reviewed_at": pending.reviewed_at,
            "review_note": pending.review_note,
            "auto_approve_score": pending.auto_approve_score,
            "auto_action_reason": pending.auto_action_reason,
            "metadata": pending.metadata,
            "priority": pending.priority,
            "created_at": pending.created_at,
            "expires_at": pending.expires_at,
        }

        if pending.id:
            doc["_id"] = ObjectId(pending.id)

        return doc

    def _doc_to_entity(self, doc: dict) -> PendingUpdate:
        """Convert MongoDB document to entity."""
        from datetime import timedelta

        return PendingUpdate(
            id=str(doc["_id"]),
            source_id=doc["source_id"],
            title=doc["title"],
            content=doc["content"],
            content_hash=doc["content_hash"],
            source_url=doc["source_url"],
            category=DataCategory(doc.get("category", "general")),
            detection_type=UpdateDetectionType(doc.get("detection_type", "new")),
            similarity_score=doc.get("similarity_score", 0.0),
            matched_doc_id=doc.get("matched_doc_id"),
            matched_doc_ids=doc.get("matched_doc_ids", []),
            llm_analysis=doc.get("llm_analysis"),
            llm_summary=doc.get("llm_summary"),
            diff_summary=doc.get("diff_summary"),
            raw_file_path=doc.get("raw_file_path"),
            status=PendingStatus(doc.get("status", "pending")),
            reviewed_by=doc.get("reviewed_by"),
            reviewed_at=doc.get("reviewed_at"),
            review_note=doc.get("review_note"),
            auto_approve_score=doc.get("auto_approve_score", 0.0),
            auto_action_reason=doc.get("auto_action_reason"),
            metadata=doc.get("metadata", {}),
            priority=doc.get("priority", 5),
            created_at=doc.get("created_at", datetime.now()),
            expires_at=doc.get("expires_at", datetime.now() + timedelta(days=7)),
        )
