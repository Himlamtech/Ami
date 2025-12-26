"""MongoDB repository for monitor targets."""

from typing import List, Optional
from datetime import datetime, timedelta
from bson import ObjectId
from motor.motor_asyncio import AsyncIOMotorDatabase

from app.domain.entities.monitor_target import MonitorTarget
from app.application.interfaces.repositories.monitor_target_repository import (
    IMonitorTargetRepository,
)


class MongoDBMonitorTargetRepository(IMonitorTargetRepository):
    """Mongo implementation for monitor targets."""

    def __init__(self, db: AsyncIOMotorDatabase):
        self.collection = db["monitor_targets"]

    async def create(self, target: MonitorTarget) -> MonitorTarget:
        doc = self._to_doc(target)
        doc.pop("_id", None)
        result = await self.collection.insert_one(doc)
        target.id = str(result.inserted_id)
        return target

    async def update(self, target: MonitorTarget) -> MonitorTarget:
        doc = self._to_doc(target)
        target_id = doc.pop("_id")
        await self.collection.update_one({"_id": target_id}, {"$set": doc})
        return target

    async def delete(self, target_id: str) -> bool:
        result = await self.collection.delete_one({"_id": ObjectId(target_id)})
        return result.deleted_count > 0

    async def get_by_id(self, target_id: str) -> Optional[MonitorTarget]:
        try:
            doc = await self.collection.find_one({"_id": ObjectId(target_id)})
        except Exception:
            return None
        if not doc:
            return None
        return self._to_entity(doc)

    async def list(self, skip: int = 0, limit: int = 100) -> List[MonitorTarget]:
        cursor = self.collection.find().sort("created_at", -1).skip(skip).limit(limit)
        results: List[MonitorTarget] = []
        async for doc in cursor:
            results.append(self._to_entity(doc))
        return results

    async def get_due_targets(
        self, now: Optional[datetime] = None
    ) -> List[MonitorTarget]:
        now = now or datetime.now()
        cursor = self.collection.find(
            {
                "is_active": True,
                "$or": [
                    {"last_checked_at": {"$exists": False}},
                    {"last_checked_at": None},
                    {"last_checked_at": {"$lte": now - timedelta(hours=1)}},
                ],
            }
        )
        results: List[MonitorTarget] = []
        async for doc in cursor:
            target = self._to_entity(doc)
            if target.should_check(now):
                results.append(target)
        return results

    def _to_doc(self, target: MonitorTarget) -> dict:
        doc = {
            "name": target.name,
            "url": target.url,
            "collection": target.collection,
            "category": target.category,
            "interval_hours": target.interval_hours,
            "is_active": target.is_active,
            "selector": target.selector,
            "last_checked_at": target.last_checked_at,
            "last_success_at": target.last_success_at,
            "last_error": target.last_error,
            "consecutive_failures": target.consecutive_failures,
            "max_failures": target.max_failures,
            "last_content_hash": target.last_content_hash,
            "metadata": target.metadata,
            "created_at": target.created_at,
            "updated_at": target.updated_at,
        }
        if target.id:
            try:
                doc["_id"] = ObjectId(target.id)
            except Exception:
                pass
        return doc

    def _to_entity(self, doc: dict) -> MonitorTarget:
        return MonitorTarget(
            id=str(doc["_id"]),
            name=doc["name"],
            url=doc["url"],
            collection=doc.get("collection", "default"),
            category=doc.get("category", "general"),
            interval_hours=doc.get("interval_hours", 6),
            is_active=doc.get("is_active", True),
            selector=doc.get("selector"),
            last_checked_at=doc.get("last_checked_at"),
            last_success_at=doc.get("last_success_at"),
            last_error=doc.get("last_error"),
            consecutive_failures=doc.get("consecutive_failures", 0),
            max_failures=doc.get("max_failures", 5),
            last_content_hash=doc.get("last_content_hash"),
            metadata=doc.get("metadata", {}),
            created_at=doc.get("created_at", datetime.now()),
            updated_at=doc.get("updated_at", datetime.now()),
        )
