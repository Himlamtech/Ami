"""MongoDB Orchestration Log Repository implementation."""

from typing import Optional, List
from datetime import datetime
from motor.motor_asyncio import AsyncIOMotorDatabase
from bson import ObjectId

from app.domain.entities.orchestration_result import (
    OrchestrationResult,
    VectorSearchReference,
    OrchestrationMetrics,
)
from app.domain.entities.tool_call import ToolCall, ToolArguments
from app.domain.enums.tool_type import ToolType, ToolExecutionStatus
from app.application.interfaces.repositories.orchestration_log_repository import (
    IOrchestrationLogRepository,
)
from app.infrastructure.persistence.mongodb.models import (
    OrchestrationLogInDB,
    ToolCallInDB,
    VectorSearchReferenceInDB,
    OrchestrationMetricsInDB,
)


class MongoDBOrchestrationLogRepository(IOrchestrationLogRepository):
    """MongoDB implementation of Orchestration Log Repository."""

    def __init__(self, db: AsyncIOMotorDatabase):
        self.db = db
        self.collection = db["orchestration_logs"]

    # ===== Mappers =====

    def _to_model(self, entity: OrchestrationResult) -> dict:
        """Convert domain entity to MongoDB document."""
        tool_calls = []
        for tc in entity.tool_calls:
            tool_calls.append(
                ToolCallInDB(
                    tool_type=tc.tool_type.value,
                    arguments=tc.arguments.to_dict() if tc.arguments else {},
                    execution_status=tc.execution_status.value,
                    result=tc.result,
                    error=tc.error,
                    execution_time_ms=tc.execution_time_ms,
                    started_at=tc.started_at,
                    completed_at=tc.completed_at,
                ).dict()
            )

        vector_ref = None
        if entity.vector_reference:
            vector_ref = VectorSearchReferenceInDB(
                top_score=entity.vector_reference.top_score,
                avg_score=entity.vector_reference.avg_score,
                chunk_count=entity.vector_reference.chunk_count,
                has_high_confidence=entity.vector_reference.has_high_confidence,
                confidence_threshold=entity.vector_reference.confidence_threshold,
                sample_chunks=entity.vector_reference.sample_chunks,
            ).dict()

        metrics = None
        if entity.metrics:
            metrics = OrchestrationMetricsInDB(
                decision_time_ms=entity.metrics.decision_time_ms,
                tool_execution_time_ms=entity.metrics.tool_execution_time_ms,
                synthesis_time_ms=entity.metrics.synthesis_time_ms,
                total_time_ms=entity.metrics.total_time_ms,
                tokens_used=entity.metrics.tokens_used,
            ).dict()

        return {
            "query": entity.query,
            "session_id": entity.session_id,
            "user_id": entity.user_id,
            "tool_calls": tool_calls,
            "primary_tool": entity.primary_tool.value if entity.primary_tool else None,
            "final_answer": entity.final_answer,
            "success": entity.success,
            "error": entity.error,
            "vector_reference": vector_ref,
            "metrics": metrics,
            "created_at": entity.created_at or datetime.now(),
            "updated_at": datetime.now(),
        }

    def _to_entity(self, doc: dict) -> OrchestrationResult:
        """Convert MongoDB document to domain entity."""
        tool_calls = []
        for tc_dict in doc.get("tool_calls", []):
            tool_calls.append(
                ToolCall(
                    tool_type=ToolType(tc_dict["tool_type"]),
                    arguments=ToolArguments.from_dict(tc_dict.get("arguments", {})),
                    execution_status=ToolExecutionStatus(
                        tc_dict.get("execution_status", "pending")
                    ),
                    result=tc_dict.get("result"),
                    error=tc_dict.get("error"),
                    execution_time_ms=tc_dict.get("execution_time_ms"),
                    started_at=tc_dict.get("started_at"),
                    completed_at=tc_dict.get("completed_at"),
                )
            )

        vector_ref = None
        if doc.get("vector_reference"):
            vr = doc["vector_reference"]
            vector_ref = VectorSearchReference(
                top_score=vr.get("top_score", 0.0),
                avg_score=vr.get("avg_score", 0.0),
                chunk_count=vr.get("chunk_count", 0),
                has_high_confidence=vr.get("has_high_confidence", False),
                confidence_threshold=vr.get("confidence_threshold", 0.7),
                sample_chunks=vr.get("sample_chunks", []),
            )

        metrics = None
        if doc.get("metrics"):
            m = doc["metrics"]
            metrics = OrchestrationMetrics(
                decision_time_ms=m.get("decision_time_ms", 0.0),
                tool_execution_time_ms=m.get("tool_execution_time_ms", 0.0),
                synthesis_time_ms=m.get("synthesis_time_ms", 0.0),
                total_time_ms=m.get("total_time_ms", 0.0),
                tokens_used=m.get("tokens_used", 0),
            )

        primary_tool = None
        if doc.get("primary_tool"):
            primary_tool = ToolType(doc["primary_tool"])

        return OrchestrationResult(
            id=str(doc.get("_id", "")),
            query=doc["query"],
            session_id=doc.get("session_id"),
            user_id=doc.get("user_id"),
            tool_calls=tool_calls,
            primary_tool=primary_tool,
            final_answer=doc.get("final_answer"),
            success=doc.get("success", True),
            error=doc.get("error"),
            vector_reference=vector_ref,
            metrics=metrics,
            created_at=doc.get("created_at"),
            updated_at=doc.get("updated_at"),
        )

    # ===== CRUD Operations =====

    async def create(self, result: OrchestrationResult) -> OrchestrationResult:
        """Save orchestration result."""
        doc = self._to_model(result)
        inserted = await self.collection.insert_one(doc)
        result.id = str(inserted.inserted_id)
        return result

    async def get_by_id(self, log_id: str) -> Optional[OrchestrationResult]:
        """Get log by ID."""
        try:
            doc = await self.collection.find_one({"_id": ObjectId(log_id)})
        except Exception:
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
    ) -> List[OrchestrationResult]:
        """List orchestration logs by user."""
        query = {"user_id": user_id}

        if date_from or date_to:
            query["created_at"] = {}
            if date_from:
                query["created_at"]["$gte"] = date_from
            if date_to:
                query["created_at"]["$lte"] = date_to

        cursor = (
            self.collection.find(query).sort("created_at", -1).skip(skip).limit(limit)
        )

        results = []
        async for doc in cursor:
            results.append(self._to_entity(doc))
        return results

    async def list_by_session(
        self,
        session_id: str,
        skip: int = 0,
        limit: int = 100,
    ) -> List[OrchestrationResult]:
        """List orchestration logs by session."""
        cursor = (
            self.collection.find({"session_id": session_id})
            .sort("created_at", -1)
            .skip(skip)
            .limit(limit)
        )

        results = []
        async for doc in cursor:
            results.append(self._to_entity(doc))
        return results

    async def list_by_tool_type(
        self,
        tool_type: str,
        skip: int = 0,
        limit: int = 100,
        date_from: Optional[datetime] = None,
        date_to: Optional[datetime] = None,
    ) -> List[OrchestrationResult]:
        """List logs by primary tool used."""
        query = {"primary_tool": tool_type}

        if date_from or date_to:
            query["created_at"] = {}
            if date_from:
                query["created_at"]["$gte"] = date_from
            if date_to:
                query["created_at"]["$lte"] = date_to

        cursor = (
            self.collection.find(query).sort("created_at", -1).skip(skip).limit(limit)
        )

        results = []
        async for doc in cursor:
            results.append(self._to_entity(doc))
        return results

    # ===== Analytics Operations =====

    async def count_by_tool_type(
        self,
        date_from: Optional[datetime] = None,
        date_to: Optional[datetime] = None,
    ) -> dict:
        """Count orchestrations by tool type."""
        match_stage = {}
        if date_from or date_to:
            match_stage["created_at"] = {}
            if date_from:
                match_stage["created_at"]["$gte"] = date_from
            if date_to:
                match_stage["created_at"]["$lte"] = date_to

        pipeline = []
        if match_stage:
            pipeline.append({"$match": match_stage})

        pipeline.extend(
            [
                {"$group": {"_id": "$primary_tool", "count": {"$sum": 1}}},
                {"$sort": {"count": -1}},
            ]
        )

        cursor = self.collection.aggregate(pipeline)
        result = {}
        async for doc in cursor:
            tool_type = doc["_id"] or "unknown"
            result[tool_type] = doc["count"]
        return result

    async def get_average_latency(
        self,
        date_from: Optional[datetime] = None,
        date_to: Optional[datetime] = None,
    ) -> dict:
        """Get average latency metrics."""
        match_stage = {"metrics": {"$exists": True, "$ne": None}}
        if date_from or date_to:
            match_stage["created_at"] = {}
            if date_from:
                match_stage["created_at"]["$gte"] = date_from
            if date_to:
                match_stage["created_at"]["$lte"] = date_to

        pipeline = [
            {"$match": match_stage},
            {
                "$group": {
                    "_id": None,
                    "avg_decision_time": {"$avg": "$metrics.decision_time_ms"},
                    "avg_tool_execution_time": {
                        "$avg": "$metrics.tool_execution_time_ms"
                    },
                    "avg_synthesis_time": {"$avg": "$metrics.synthesis_time_ms"},
                    "avg_total_time": {"$avg": "$metrics.total_time_ms"},
                    "total_queries": {"$sum": 1},
                }
            },
        ]

        cursor = self.collection.aggregate(pipeline)
        async for doc in cursor:
            return {
                "avg_decision_time_ms": doc.get("avg_decision_time", 0),
                "avg_tool_execution_time_ms": doc.get("avg_tool_execution_time", 0),
                "avg_synthesis_time_ms": doc.get("avg_synthesis_time", 0),
                "avg_total_time_ms": doc.get("avg_total_time", 0),
                "total_queries": doc.get("total_queries", 0),
            }

        return {
            "avg_decision_time_ms": 0,
            "avg_tool_execution_time_ms": 0,
            "avg_synthesis_time_ms": 0,
            "avg_total_time_ms": 0,
            "total_queries": 0,
        }

    async def list_failed(
        self,
        skip: int = 0,
        limit: int = 100,
        date_from: Optional[datetime] = None,
        date_to: Optional[datetime] = None,
    ) -> List[OrchestrationResult]:
        """List failed orchestration attempts."""
        query = {"success": False}

        if date_from or date_to:
            query["created_at"] = {}
            if date_from:
                query["created_at"]["$gte"] = date_from
            if date_to:
                query["created_at"]["$lte"] = date_to

        cursor = (
            self.collection.find(query).sort("created_at", -1).skip(skip).limit(limit)
        )

        results = []
        async for doc in cursor:
            results.append(self._to_entity(doc))
        return results
