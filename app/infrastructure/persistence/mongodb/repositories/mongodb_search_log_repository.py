"""MongoDB Search Log and Knowledge Gap Repository implementations."""

from typing import Optional, List
from datetime import datetime, timedelta
from motor.motor_asyncio import AsyncIOMotorDatabase
from bson import ObjectId
import uuid

from app.domain.entities.search_log import (
    SearchLog,
    SearchResult,
    KnowledgeGap,
    SearchResultQuality,
    GapStatus,
)
from app.application.interfaces.repositories.search_log_repository import (
    ISearchLogRepository,
    IKnowledgeGapRepository,
)


class MongoDBSearchLogRepository(ISearchLogRepository):
    """MongoDB implementation of SearchLog Repository."""

    def __init__(self, db: AsyncIOMotorDatabase):
        self.db = db
        self.collection = db["search_logs"]

    # ===== Mappers =====

    def _to_entity(self, doc: dict) -> SearchLog:
        """Convert MongoDB document to SearchLog entity."""
        results = [
            SearchResult(
                document_id=r.get("document_id", ""),
                chunk_id=r.get("chunk_id"),
                title=r.get("title"),
                score=r.get("score", 0.0),
            )
            for r in doc.get("results", [])
        ]

        return SearchLog(
            id=str(doc["_id"]),
            query=doc["query"],
            user_id=doc.get("user_id"),
            session_id=doc.get("session_id"),
            message_id=doc.get("message_id"),
            results=results,
            top_score=doc.get("top_score", 0.0),
            result_count=doc.get("result_count", 0),
            result_quality=SearchResultQuality(doc.get("result_quality", "none")),
            used_web_fallback=doc.get("used_web_fallback", False),
            web_search_query=doc.get("web_search_query"),
            collection=doc.get("collection"),
            search_latency_ms=doc.get("search_latency_ms", 0),
            timestamp=doc.get("timestamp", datetime.now()),
        )

    def _to_doc(self, log: SearchLog) -> dict:
        """Convert SearchLog entity to MongoDB document."""
        return {
            "query": log.query,
            "user_id": log.user_id,
            "session_id": log.session_id,
            "message_id": log.message_id,
            "results": [r.to_dict() for r in log.results],
            "top_score": log.top_score,
            "result_count": log.result_count,
            "result_quality": log.result_quality.value,
            "used_web_fallback": log.used_web_fallback,
            "web_search_query": log.web_search_query,
            "collection": log.collection,
            "search_latency_ms": log.search_latency_ms,
            "timestamp": log.timestamp,
        }

    # ===== CRUD Operations =====

    async def create(self, log: SearchLog) -> SearchLog:
        """Create new search log."""
        doc = self._to_doc(log)
        result = await self.collection.insert_one(doc)
        log.id = str(result.inserted_id)
        return log

    async def get_by_id(self, log_id: str) -> Optional[SearchLog]:
        """Get log by ID."""
        try:
            doc = await self.collection.find_one({"_id": ObjectId(log_id)})
        except:
            return None
        if not doc:
            return None
        return self._to_entity(doc)

    # ===== Query Operations =====

    async def list_by_user(
        self,
        user_id: str,
        skip: int = 0,
        limit: int = 100,
        date_from: Optional[datetime] = None,
        date_to: Optional[datetime] = None,
    ) -> List[SearchLog]:
        """List logs by user."""
        query = {"user_id": user_id}
        if date_from:
            query.setdefault("timestamp", {})["$gte"] = date_from
        if date_to:
            query.setdefault("timestamp", {})["$lte"] = date_to

        cursor = (
            self.collection.find(query).sort("timestamp", -1).skip(skip).limit(limit)
        )

        logs = []
        async for doc in cursor:
            logs.append(self._to_entity(doc))
        return logs

    async def list_by_session(
        self,
        session_id: str,
        skip: int = 0,
        limit: int = 100,
    ) -> List[SearchLog]:
        """List logs by session."""
        cursor = (
            self.collection.find({"session_id": session_id})
            .sort("timestamp", -1)
            .skip(skip)
            .limit(limit)
        )

        logs = []
        async for doc in cursor:
            logs.append(self._to_entity(doc))
        return logs

    async def list_low_quality(
        self,
        quality: SearchResultQuality = SearchResultQuality.LOW,
        skip: int = 0,
        limit: int = 100,
        date_from: Optional[datetime] = None,
        date_to: Optional[datetime] = None,
    ) -> List[SearchLog]:
        """List logs with low quality results."""
        quality_values = ["low", "none"]
        if quality == SearchResultQuality.MEDIUM:
            quality_values = ["medium", "low", "none"]

        query = {"result_quality": {"$in": quality_values}}
        if date_from:
            query.setdefault("timestamp", {})["$gte"] = date_from
        if date_to:
            query.setdefault("timestamp", {})["$lte"] = date_to

        cursor = (
            self.collection.find(query).sort("timestamp", -1).skip(skip).limit(limit)
        )

        logs = []
        async for doc in cursor:
            logs.append(self._to_entity(doc))
        return logs

    async def list_with_fallback(
        self,
        skip: int = 0,
        limit: int = 100,
        date_from: Optional[datetime] = None,
        date_to: Optional[datetime] = None,
    ) -> List[SearchLog]:
        """List logs that used web fallback."""
        query = {"used_web_fallback": True}
        if date_from:
            query.setdefault("timestamp", {})["$gte"] = date_from
        if date_to:
            query.setdefault("timestamp", {})["$lte"] = date_to

        cursor = (
            self.collection.find(query).sort("timestamp", -1).skip(skip).limit(limit)
        )

        logs = []
        async for doc in cursor:
            logs.append(self._to_entity(doc))
        return logs

    # ===== Analytics Operations =====

    async def get_quality_distribution(
        self,
        date_from: Optional[datetime] = None,
        date_to: Optional[datetime] = None,
    ) -> dict:
        """Get distribution of result quality."""
        match_stage = {}
        if date_from:
            match_stage.setdefault("timestamp", {})["$gte"] = date_from
        if date_to:
            match_stage.setdefault("timestamp", {})["$lte"] = date_to

        pipeline = []
        if match_stage:
            pipeline.append({"$match": match_stage})

        pipeline.extend(
            [
                {
                    "$group": {
                        "_id": "$result_quality",
                        "count": {"$sum": 1},
                    }
                }
            ]
        )

        results = await self.collection.aggregate(pipeline).to_list(None)

        distribution = {"high": 0, "medium": 0, "low": 0, "none": 0, "total": 0}
        for item in results:
            if item["_id"] in distribution:
                distribution[item["_id"]] = item["count"]
            distribution["total"] += item["count"]

        return distribution

    async def get_fallback_rate(
        self,
        date_from: Optional[datetime] = None,
        date_to: Optional[datetime] = None,
    ) -> float:
        """Get percentage of queries using web fallback."""
        match_stage = {}
        if date_from:
            match_stage.setdefault("timestamp", {})["$gte"] = date_from
        if date_to:
            match_stage.setdefault("timestamp", {})["$lte"] = date_to

        pipeline = []
        if match_stage:
            pipeline.append({"$match": match_stage})

        pipeline.append(
            {
                "$group": {
                    "_id": None,
                    "total": {"$sum": 1},
                    "fallback_count": {"$sum": {"$cond": ["$used_web_fallback", 1, 0]}},
                }
            }
        )

        result = await self.collection.aggregate(pipeline).to_list(1)

        if not result or result[0]["total"] == 0:
            return 0.0

        return round(result[0]["fallback_count"] / result[0]["total"], 4)

    async def get_avg_score_by_collection(
        self,
        date_from: Optional[datetime] = None,
        date_to: Optional[datetime] = None,
    ) -> List[dict]:
        """Get average score by collection."""
        match_stage = {"collection": {"$ne": None}}
        if date_from:
            match_stage.setdefault("timestamp", {})["$gte"] = date_from
        if date_to:
            match_stage.setdefault("timestamp", {})["$lte"] = date_to

        pipeline = [
            {"$match": match_stage},
            {
                "$group": {
                    "_id": "$collection",
                    "avg_score": {"$avg": "$top_score"},
                    "query_count": {"$sum": 1},
                }
            },
            {"$sort": {"query_count": -1}},
        ]

        results = await self.collection.aggregate(pipeline).to_list(None)

        return [
            {
                "collection": item["_id"],
                "avg_score": round(item["avg_score"], 3),
                "query_count": item["query_count"],
            }
            for item in results
        ]

    async def get_gap_candidates(
        self,
        min_queries: int = 3,
        max_score: float = 0.5,
        days: int = 30,
    ) -> List[dict]:
        """Get queries that might indicate knowledge gaps."""
        start_date = datetime.now() - timedelta(days=days)

        pipeline = [
            {
                "$match": {
                    "timestamp": {"$gte": start_date},
                    "top_score": {"$lt": max_score},
                }
            },
            {
                "$group": {
                    "_id": {"$toLower": {"$substr": ["$query", 0, 100]}},
                    "count": {"$sum": 1},
                    "avg_score": {"$avg": "$top_score"},
                    "samples": {"$push": "$query"},
                }
            },
            {"$match": {"count": {"$gte": min_queries}}},
            {"$sort": {"count": -1}},
            {"$limit": 50},
        ]

        results = await self.collection.aggregate(pipeline).to_list(None)

        return [
            {
                "query_pattern": item["_id"],
                "count": item["count"],
                "avg_score": round(item["avg_score"], 3),
                "samples": list(set(item["samples"]))[:5],
            }
            for item in results
        ]

    # ===== Aliases for admin routes =====

    async def find_low_confidence(
        self,
        threshold: float = 0.5,
        date_from: Optional[datetime] = None,
        limit: int = 100,
        skip: int = 0,
    ) -> List[SearchLog]:
        """Find queries with low confidence scores."""
        query: dict = {"top_score": {"$lt": threshold}}
        if date_from:
            query["timestamp"] = {"$gte": date_from}

        cursor = (
            self.collection.find(query).sort("timestamp", -1).skip(skip).limit(limit)
        )

        logs = []
        async for doc in cursor:
            logs.append(self._to_entity(doc))
        return logs

    async def find_by_user(
        self,
        user_id: str,
        limit: int = 100,
    ) -> List[SearchLog]:
        """Alias for list_by_user."""
        return await self.list_by_user(user_id, limit=limit)

    async def get_topic_stats(
        self,
        date_from: Optional[datetime] = None,
        date_to: Optional[datetime] = None,
    ) -> List[dict]:
        """Get topic statistics from queries."""
        match_stage: dict = {}
        if date_from:
            match_stage["timestamp"] = {"$gte": date_from}
        if date_to:
            if "timestamp" in match_stage:
                match_stage["timestamp"]["$lte"] = date_to
            else:
                match_stage["timestamp"] = {"$lte": date_to}

        pipeline = []
        if match_stage:
            pipeline.append({"$match": match_stage})

        pipeline.extend(
            [
                {
                    "$group": {
                        "_id": "$collection",
                        "count": {"$sum": 1},
                        "avg_score": {"$avg": "$top_score"},
                    }
                },
                {"$sort": {"count": -1}},
                {"$limit": 50},
            ]
        )

        results = await self.collection.aggregate(pipeline).to_list(None)

        return [
            {
                "topic": item["_id"] or "unknown",
                "count": item["count"],
                "avg_score": round(item["avg_score"], 3) if item["avg_score"] else 0,
            }
            for item in results
        ]


class MongoDBKnowledgeGapRepository(IKnowledgeGapRepository):
    """MongoDB implementation of KnowledgeGap Repository."""

    def __init__(self, db: AsyncIOMotorDatabase):
        self.db = db
        self.collection = db["knowledge_gaps"]

    # ===== Mappers =====

    def _to_entity(self, doc: dict) -> KnowledgeGap:
        """Convert MongoDB document to KnowledgeGap entity."""
        return KnowledgeGap(
            id=str(doc["_id"]),
            topic=doc["topic"],
            description=doc.get("description"),
            query_count=doc.get("query_count", 0),
            avg_score=doc.get("avg_score", 0.0),
            sample_queries=doc.get("sample_queries", []),
            status=GapStatus(doc.get("status", "detected")),
            priority=doc.get("priority", 0),
            resolved_by_document_id=doc.get("resolved_by_document_id"),
            resolved_by=doc.get("resolved_by"),
            resolved_at=doc.get("resolved_at"),
            resolution_notes=doc.get("resolution_notes"),
            first_detected_at=doc.get("first_detected_at", datetime.now()),
            last_query_at=doc.get("last_query_at", datetime.now()),
            updated_at=doc.get("updated_at", datetime.now()),
        )

    def _to_doc(self, gap: KnowledgeGap) -> dict:
        """Convert KnowledgeGap entity to MongoDB document."""
        return {
            "topic": gap.topic,
            "description": gap.description,
            "query_count": gap.query_count,
            "avg_score": gap.avg_score,
            "sample_queries": gap.sample_queries,
            "status": gap.status.value,
            "priority": gap.priority,
            "resolved_by_document_id": gap.resolved_by_document_id,
            "resolved_by": gap.resolved_by,
            "resolved_at": gap.resolved_at,
            "resolution_notes": gap.resolution_notes,
            "first_detected_at": gap.first_detected_at,
            "last_query_at": gap.last_query_at,
            "updated_at": gap.updated_at,
        }

    # ===== CRUD Operations =====

    async def create(self, gap: KnowledgeGap) -> KnowledgeGap:
        """Create new knowledge gap."""
        doc = self._to_doc(gap)
        result = await self.collection.insert_one(doc)
        gap.id = str(result.inserted_id)
        return gap

    async def get_by_id(self, gap_id: str) -> Optional[KnowledgeGap]:
        """Get gap by ID."""
        try:
            doc = await self.collection.find_one({"_id": ObjectId(gap_id)})
        except:
            return None
        if not doc:
            return None
        return self._to_entity(doc)

    async def update(self, gap: KnowledgeGap) -> KnowledgeGap:
        """Update existing gap."""
        doc = self._to_doc(gap)
        doc["updated_at"] = datetime.now()
        await self.collection.update_one({"_id": ObjectId(gap.id)}, {"$set": doc})
        return gap

    async def delete(self, gap_id: str) -> bool:
        """Delete gap."""
        result = await self.collection.delete_one({"_id": ObjectId(gap_id)})
        return result.deleted_count > 0

    # ===== Query Operations =====

    async def find_by_topic(self, topic: str) -> Optional[KnowledgeGap]:
        """Find gap by topic (for deduplication)."""
        # Case-insensitive partial match
        doc = await self.collection.find_one(
            {"topic": {"$regex": f"^{topic}$", "$options": "i"}}
        )
        if not doc:
            return None
        return self._to_entity(doc)

    async def list_all(
        self,
        skip: int = 0,
        limit: int = 100,
        status: Optional[GapStatus] = None,
        min_priority: int = 0,
    ) -> List[KnowledgeGap]:
        """List all gaps with filters."""
        query = {"priority": {"$gte": min_priority}}
        if status:
            query["status"] = status.value

        cursor = (
            self.collection.find(query)
            .sort(
                [
                    ("priority", -1),
                    ("query_count", -1),
                ]
            )
            .skip(skip)
            .limit(limit)
        )

        gaps = []
        async for doc in cursor:
            gaps.append(self._to_entity(doc))
        return gaps

    async def count_by_status(self) -> dict:
        """Count gaps by status."""
        pipeline = [
            {
                "$group": {
                    "_id": "$status",
                    "count": {"$sum": 1},
                }
            }
        ]

        results = await self.collection.aggregate(pipeline).to_list(None)

        counts = {
            "detected": 0,
            "todo": 0,
            "in_progress": 0,
            "resolved": 0,
            "dismissed": 0,
        }
        for item in results:
            if item["_id"] in counts:
                counts[item["_id"]] = item["count"]

        return counts

    async def get_top_gaps(
        self,
        limit: int = 10,
        status: Optional[GapStatus] = None,
    ) -> List[KnowledgeGap]:
        """Get top gaps by priority and query count."""
        query = {}
        if status:
            query["status"] = status.value
        else:
            # Exclude resolved and dismissed by default
            query["status"] = {"$nin": ["resolved", "dismissed"]}

        cursor = (
            self.collection.find(query)
            .sort(
                [
                    ("priority", -1),
                    ("query_count", -1),
                ]
            )
            .limit(limit)
        )

        gaps = []
        async for doc in cursor:
            gaps.append(self._to_entity(doc))
        return gaps

    # ===== Update Operations =====

    async def add_query_to_gap(
        self,
        gap_id: str,
        query: str,
        score: float,
    ) -> KnowledgeGap:
        """Add a query to an existing gap."""
        gap = await self.get_by_id(gap_id)
        if not gap:
            raise ValueError(f"Gap {gap_id} not found")

        gap.add_query(query, score)
        return await self.update(gap)

    async def find_or_create_gap(
        self,
        topic: str,
        query: str,
        score: float,
    ) -> KnowledgeGap:
        """Find existing gap or create new one."""
        existing = await self.find_by_topic(topic)

        if existing:
            existing.add_query(query, score)
            return await self.update(existing)

        # Create new gap
        gap = KnowledgeGap(
            id=str(uuid.uuid4()),
            topic=topic,
            query_count=1,
            avg_score=score,
            sample_queries=[query],
        )
        gap._update_priority()

        return await self.create(gap)

    # ===== Aliases for admin routes =====

    async def find_all(self, limit: int = 100) -> List[KnowledgeGap]:
        """Alias for list_all."""
        return await self.list_all(limit=limit)

    async def find_by_id(self, gap_id: str) -> Optional[KnowledgeGap]:
        """Alias for get_by_id."""
        return await self.get_by_id(gap_id)

    async def save(self, gap: KnowledgeGap) -> KnowledgeGap:
        """Alias for create."""
        return await self.create(gap)
