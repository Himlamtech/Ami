"""MongoDB Usage Metrics Repository implementations."""

from typing import Optional, List
from datetime import datetime, timedelta
from motor.motor_asyncio import AsyncIOMotorDatabase
from bson import ObjectId

from domain.entities.usage_metric import (
    UsageMetric,
    LLMUsage,
    DailyUsageStats,
    RequestStatus,
    LLMProvider,
)
from application.interfaces.repositories.usage_repository import (
    IUsageMetricRepository,
    ILLMUsageRepository,
    IDailyStatsRepository,
)


class MongoDBUsageMetricRepository(IUsageMetricRepository):
    """MongoDB implementation of UsageMetric Repository."""

    def __init__(self, db: AsyncIOMotorDatabase):
        self.db = db
        self.collection = db["usage_metrics"]

    # ===== Mappers =====

    def _to_entity(self, doc: dict) -> UsageMetric:
        """Convert MongoDB document to UsageMetric entity."""
        return UsageMetric(
            id=str(doc["_id"]),
            endpoint=doc["endpoint"],
            method=doc["method"],
            user_id=doc.get("user_id"),
            session_id=doc.get("session_id"),
            latency_ms=doc.get("latency_ms", 0),
            status=RequestStatus(doc.get("status", "success")),
            status_code=doc.get("status_code", 200),
            error_message=doc.get("error_message"),
            request_size_bytes=doc.get("request_size_bytes", 0),
            response_size_bytes=doc.get("response_size_bytes", 0),
            ip_address=doc.get("ip_address"),
            user_agent=doc.get("user_agent"),
            timestamp=doc.get("timestamp", datetime.now()),
        )

    def _to_doc(self, metric: UsageMetric) -> dict:
        """Convert UsageMetric entity to MongoDB document."""
        return {
            "endpoint": metric.endpoint,
            "method": metric.method,
            "user_id": metric.user_id,
            "session_id": metric.session_id,
            "latency_ms": metric.latency_ms,
            "status": metric.status.value,
            "status_code": metric.status_code,
            "error_message": metric.error_message,
            "request_size_bytes": metric.request_size_bytes,
            "response_size_bytes": metric.response_size_bytes,
            "ip_address": metric.ip_address,
            "user_agent": metric.user_agent,
            "timestamp": metric.timestamp,
        }

    # ===== CRUD Operations =====

    async def create(self, metric: UsageMetric) -> UsageMetric:
        """Create new usage metric."""
        doc = self._to_doc(metric)
        result = await self.collection.insert_one(doc)
        metric.id = str(result.inserted_id)
        return metric

    async def get_by_id(self, metric_id: str) -> Optional[UsageMetric]:
        """Get metric by ID."""
        try:
            doc = await self.collection.find_one({"_id": ObjectId(metric_id)})
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
    ) -> List[UsageMetric]:
        """List metrics by user."""
        query = {"user_id": user_id}
        if date_from:
            query.setdefault("timestamp", {})["$gte"] = date_from
        if date_to:
            query.setdefault("timestamp", {})["$lte"] = date_to

        cursor = (
            self.collection.find(query).sort("timestamp", -1).skip(skip).limit(limit)
        )

        metrics = []
        async for doc in cursor:
            metrics.append(self._to_entity(doc))
        return metrics

    async def list_by_endpoint(
        self,
        endpoint: str,
        skip: int = 0,
        limit: int = 100,
        date_from: Optional[datetime] = None,
        date_to: Optional[datetime] = None,
    ) -> List[UsageMetric]:
        """List metrics by endpoint."""
        query = {"endpoint": {"$regex": endpoint}}
        if date_from:
            query.setdefault("timestamp", {})["$gte"] = date_from
        if date_to:
            query.setdefault("timestamp", {})["$lte"] = date_to

        cursor = (
            self.collection.find(query).sort("timestamp", -1).skip(skip).limit(limit)
        )

        metrics = []
        async for doc in cursor:
            metrics.append(self._to_entity(doc))
        return metrics

    async def get_slow_requests(
        self,
        threshold_ms: int = 3000,
        limit: int = 100,
        date_from: Optional[datetime] = None,
        date_to: Optional[datetime] = None,
    ) -> List[UsageMetric]:
        """Get slow requests above threshold."""
        query = {"latency_ms": {"$gte": threshold_ms}}
        if date_from:
            query.setdefault("timestamp", {})["$gte"] = date_from
        if date_to:
            query.setdefault("timestamp", {})["$lte"] = date_to

        cursor = self.collection.find(query).sort("latency_ms", -1).limit(limit)

        metrics = []
        async for doc in cursor:
            metrics.append(self._to_entity(doc))
        return metrics

    async def get_error_requests(
        self,
        limit: int = 100,
        date_from: Optional[datetime] = None,
        date_to: Optional[datetime] = None,
    ) -> List[UsageMetric]:
        """Get requests with errors."""
        query = {"status": {"$ne": "success"}}
        if date_from:
            query.setdefault("timestamp", {})["$gte"] = date_from
        if date_to:
            query.setdefault("timestamp", {})["$lte"] = date_to

        cursor = self.collection.find(query).sort("timestamp", -1).limit(limit)

        metrics = []
        async for doc in cursor:
            metrics.append(self._to_entity(doc))
        return metrics

    # ===== Analytics Operations =====

    async def get_overview_stats(
        self,
        date_from: Optional[datetime] = None,
        date_to: Optional[datetime] = None,
    ) -> dict:
        """Get overview statistics."""
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
                    "total_requests": {"$sum": 1},
                    "unique_users": {"$addToSet": "$user_id"},
                    "unique_sessions": {"$addToSet": "$session_id"},
                    "avg_latency_ms": {"$avg": "$latency_ms"},
                    "error_count": {
                        "$sum": {"$cond": [{"$ne": ["$status", "success"]}, 1, 0]}
                    },
                }
            }
        )

        result = await self.collection.aggregate(pipeline).to_list(1)

        if not result:
            return {
                "total_requests": 0,
                "unique_users": 0,
                "unique_sessions": 0,
                "avg_latency_ms": 0.0,
                "error_count": 0,
                "error_rate": 0.0,
            }

        data = result[0]
        total = data["total_requests"]
        error_count = data["error_count"]

        return {
            "total_requests": total,
            "unique_users": len([u for u in data["unique_users"] if u]),
            "unique_sessions": len([s for s in data["unique_sessions"] if s]),
            "avg_latency_ms": round(data["avg_latency_ms"] or 0, 2),
            "error_count": error_count,
            "error_rate": round(error_count / total, 4) if total > 0 else 0.0,
        }

    async def get_latency_percentiles(
        self,
        date_from: Optional[datetime] = None,
        date_to: Optional[datetime] = None,
    ) -> dict:
        """Get latency percentiles."""
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
                {"$sort": {"latency_ms": 1}},
                {"$group": {"_id": None, "latencies": {"$push": "$latency_ms"}}},
            ]
        )

        result = await self.collection.aggregate(pipeline).to_list(1)

        if not result or not result[0]["latencies"]:
            return {"p50": 0, "p75": 0, "p90": 0, "p95": 0, "p99": 0}

        latencies = result[0]["latencies"]
        n = len(latencies)

        def percentile(p):
            idx = int(n * p / 100)
            return latencies[min(idx, n - 1)]

        return {
            "p50": percentile(50),
            "p75": percentile(75),
            "p90": percentile(90),
            "p95": percentile(95),
            "p99": percentile(99),
        }

    async def get_requests_by_endpoint(
        self,
        date_from: Optional[datetime] = None,
        date_to: Optional[datetime] = None,
    ) -> List[dict]:
        """Get request counts by endpoint."""
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
                        "_id": "$endpoint",
                        "count": {"$sum": 1},
                        "avg_latency": {"$avg": "$latency_ms"},
                    }
                },
                {"$sort": {"count": -1}},
            ]
        )

        results = await self.collection.aggregate(pipeline).to_list(None)

        return [
            {
                "endpoint": item["_id"],
                "count": item["count"],
                "avg_latency": round(item["avg_latency"] or 0, 2),
            }
            for item in results
        ]

    async def get_hourly_distribution(
        self,
        date_from: Optional[datetime] = None,
        date_to: Optional[datetime] = None,
    ) -> List[dict]:
        """Get requests by hour of day."""
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
                        "_id": {"$hour": "$timestamp"},
                        "count": {"$sum": 1},
                    }
                },
                {"$sort": {"_id": 1}},
            ]
        )

        results = await self.collection.aggregate(pipeline).to_list(None)

        return [{"hour": item["_id"], "count": item["count"]} for item in results]


class MongoDBLLMUsageRepository(ILLMUsageRepository):
    """MongoDB implementation of LLMUsage Repository."""

    def __init__(self, db: AsyncIOMotorDatabase):
        self.db = db
        self.collection = db["llm_usage"]

    # ===== Mappers =====

    def _to_entity(self, doc: dict) -> LLMUsage:
        """Convert MongoDB document to LLMUsage entity."""
        return LLMUsage(
            id=str(doc["_id"]),
            provider=LLMProvider(doc["provider"]),
            model=doc["model"],
            input_tokens=doc.get("input_tokens", 0),
            output_tokens=doc.get("output_tokens", 0),
            total_tokens=doc.get("total_tokens", 0),
            input_cost=doc.get("input_cost", 0.0),
            output_cost=doc.get("output_cost", 0.0),
            total_cost=doc.get("total_cost", 0.0),
            use_case=doc.get("use_case", "chat"),
            user_id=doc.get("user_id"),
            session_id=doc.get("session_id"),
            message_id=doc.get("message_id"),
            latency_ms=doc.get("latency_ms", 0),
            timestamp=doc.get("timestamp", datetime.now()),
        )

    def _to_doc(self, usage: LLMUsage) -> dict:
        """Convert LLMUsage entity to MongoDB document."""
        return {
            "provider": usage.provider.value,
            "model": usage.model,
            "input_tokens": usage.input_tokens,
            "output_tokens": usage.output_tokens,
            "total_tokens": usage.total_tokens,
            "input_cost": usage.input_cost,
            "output_cost": usage.output_cost,
            "total_cost": usage.total_cost,
            "use_case": usage.use_case,
            "user_id": usage.user_id,
            "session_id": usage.session_id,
            "message_id": usage.message_id,
            "latency_ms": usage.latency_ms,
            "timestamp": usage.timestamp,
        }

    # ===== CRUD Operations =====

    async def create(self, usage: LLMUsage) -> LLMUsage:
        """Create new LLM usage record."""
        doc = self._to_doc(usage)
        result = await self.collection.insert_one(doc)
        usage.id = str(result.inserted_id)
        return usage

    async def get_by_id(self, usage_id: str) -> Optional[LLMUsage]:
        """Get usage by ID."""
        try:
            doc = await self.collection.find_one({"_id": ObjectId(usage_id)})
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
    ) -> List[LLMUsage]:
        """List usage by user."""
        query = {"user_id": user_id}
        if date_from:
            query.setdefault("timestamp", {})["$gte"] = date_from
        if date_to:
            query.setdefault("timestamp", {})["$lte"] = date_to

        cursor = (
            self.collection.find(query).sort("timestamp", -1).skip(skip).limit(limit)
        )

        usages = []
        async for doc in cursor:
            usages.append(self._to_entity(doc))
        return usages

    async def list_by_provider(
        self,
        provider: LLMProvider,
        skip: int = 0,
        limit: int = 100,
        date_from: Optional[datetime] = None,
        date_to: Optional[datetime] = None,
    ) -> List[LLMUsage]:
        """List usage by provider."""
        query = {"provider": provider.value}
        if date_from:
            query.setdefault("timestamp", {})["$gte"] = date_from
        if date_to:
            query.setdefault("timestamp", {})["$lte"] = date_to

        cursor = (
            self.collection.find(query).sort("timestamp", -1).skip(skip).limit(limit)
        )

        usages = []
        async for doc in cursor:
            usages.append(self._to_entity(doc))
        return usages

    # ===== Analytics Operations =====

    async def get_cost_summary(
        self,
        date_from: Optional[datetime] = None,
        date_to: Optional[datetime] = None,
    ) -> dict:
        """Get cost summary."""
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
                    "total_cost": {"$sum": "$total_cost"},
                    "total_tokens": {"$sum": "$total_tokens"},
                    "total_input_tokens": {"$sum": "$input_tokens"},
                    "total_output_tokens": {"$sum": "$output_tokens"},
                }
            }
        )

        result = await self.collection.aggregate(pipeline).to_list(1)

        if not result:
            return {
                "total_cost": 0.0,
                "total_tokens": 0,
                "total_input_tokens": 0,
                "total_output_tokens": 0,
            }

        data = result[0]
        return {
            "total_cost": round(data["total_cost"], 4),
            "total_tokens": data["total_tokens"],
            "total_input_tokens": data["total_input_tokens"],
            "total_output_tokens": data["total_output_tokens"],
        }

    async def get_cost_by_provider(
        self,
        date_from: Optional[datetime] = None,
        date_to: Optional[datetime] = None,
    ) -> List[dict]:
        """Get cost breakdown by provider."""
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
                        "_id": "$provider",
                        "cost": {"$sum": "$total_cost"},
                        "tokens": {"$sum": "$total_tokens"},
                    }
                },
                {"$sort": {"cost": -1}},
            ]
        )

        results = await self.collection.aggregate(pipeline).to_list(None)

        total_cost = sum(item["cost"] for item in results) or 1

        return [
            {
                "provider": item["_id"],
                "cost": round(item["cost"], 4),
                "tokens": item["tokens"],
                "percentage": round(item["cost"] / total_cost * 100, 2),
            }
            for item in results
        ]

    async def get_cost_by_model(
        self,
        date_from: Optional[datetime] = None,
        date_to: Optional[datetime] = None,
    ) -> List[dict]:
        """Get cost breakdown by model."""
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
                        "_id": "$model",
                        "cost": {"$sum": "$total_cost"},
                        "tokens": {"$sum": "$total_tokens"},
                    }
                },
                {"$sort": {"cost": -1}},
            ]
        )

        results = await self.collection.aggregate(pipeline).to_list(None)

        total_cost = sum(item["cost"] for item in results) or 1

        return [
            {
                "model": item["_id"],
                "cost": round(item["cost"], 4),
                "tokens": item["tokens"],
                "percentage": round(item["cost"] / total_cost * 100, 2),
            }
            for item in results
        ]

    async def get_cost_by_use_case(
        self,
        date_from: Optional[datetime] = None,
        date_to: Optional[datetime] = None,
    ) -> List[dict]:
        """Get cost breakdown by use case."""
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
                        "_id": "$use_case",
                        "cost": {"$sum": "$total_cost"},
                        "tokens": {"$sum": "$total_tokens"},
                    }
                },
                {"$sort": {"cost": -1}},
            ]
        )

        results = await self.collection.aggregate(pipeline).to_list(None)

        total_cost = sum(item["cost"] for item in results) or 1

        return [
            {
                "use_case": item["_id"],
                "cost": round(item["cost"], 4),
                "tokens": item["tokens"],
                "percentage": round(item["cost"] / total_cost * 100, 2),
            }
            for item in results
        ]

    async def get_daily_costs(
        self,
        days: int = 30,
    ) -> List[dict]:
        """Get daily cost trends."""
        start_date = datetime.now() - timedelta(days=days)

        pipeline = [
            {"$match": {"timestamp": {"$gte": start_date}}},
            {
                "$group": {
                    "_id": {
                        "$dateToString": {"format": "%Y-%m-%d", "date": "$timestamp"}
                    },
                    "cost": {"$sum": "$total_cost"},
                    "tokens": {"$sum": "$total_tokens"},
                }
            },
            {"$sort": {"_id": 1}},
        ]

        results = await self.collection.aggregate(pipeline).to_list(None)

        return [
            {
                "date": item["_id"],
                "cost": round(item["cost"], 4),
                "tokens": item["tokens"],
            }
            for item in results
        ]


class MongoDBDailyStatsRepository(IDailyStatsRepository):
    """MongoDB implementation of DailyUsageStats Repository."""

    def __init__(self, db: AsyncIOMotorDatabase):
        self.db = db
        self.collection = db["daily_stats"]

    def _to_entity(self, doc: dict) -> DailyUsageStats:
        """Convert MongoDB document to DailyUsageStats entity."""
        return DailyUsageStats(
            id=str(doc["_id"]),
            date=doc["date"],
            total_requests=doc.get("total_requests", 0),
            successful_requests=doc.get("successful_requests", 0),
            error_requests=doc.get("error_requests", 0),
            unique_users=doc.get("unique_users", 0),
            unique_sessions=doc.get("unique_sessions", 0),
            avg_latency_ms=doc.get("avg_latency_ms", 0.0),
            p50_latency_ms=doc.get("p50_latency_ms", 0.0),
            p95_latency_ms=doc.get("p95_latency_ms", 0.0),
            p99_latency_ms=doc.get("p99_latency_ms", 0.0),
            total_tokens=doc.get("total_tokens", 0),
            total_cost=doc.get("total_cost", 0.0),
            cost_by_provider=doc.get("cost_by_provider", {}),
            cost_by_model=doc.get("cost_by_model", {}),
            cost_by_use_case=doc.get("cost_by_use_case", {}),
            requests_by_endpoint=doc.get("requests_by_endpoint", {}),
        )

    def _to_doc(self, stats: DailyUsageStats) -> dict:
        """Convert DailyUsageStats entity to MongoDB document."""
        return {
            "date": stats.date,
            "total_requests": stats.total_requests,
            "successful_requests": stats.successful_requests,
            "error_requests": stats.error_requests,
            "unique_users": stats.unique_users,
            "unique_sessions": stats.unique_sessions,
            "avg_latency_ms": stats.avg_latency_ms,
            "p50_latency_ms": stats.p50_latency_ms,
            "p95_latency_ms": stats.p95_latency_ms,
            "p99_latency_ms": stats.p99_latency_ms,
            "total_tokens": stats.total_tokens,
            "total_cost": stats.total_cost,
            "cost_by_provider": stats.cost_by_provider,
            "cost_by_model": stats.cost_by_model,
            "cost_by_use_case": stats.cost_by_use_case,
            "requests_by_endpoint": stats.requests_by_endpoint,
        }

    async def upsert(self, stats: DailyUsageStats) -> DailyUsageStats:
        """Create or update daily stats."""
        doc = self._to_doc(stats)
        result = await self.collection.update_one(
            {"date": stats.date},
            {"$set": doc},
            upsert=True,
        )
        if result.upserted_id:
            stats.id = str(result.upserted_id)
        return stats

    async def get_by_date(self, date: datetime) -> Optional[DailyUsageStats]:
        """Get stats for a specific date."""
        # Normalize to start of day
        start = date.replace(hour=0, minute=0, second=0, microsecond=0)
        end = start + timedelta(days=1)

        doc = await self.collection.find_one({"date": {"$gte": start, "$lt": end}})
        if not doc:
            return None
        return self._to_entity(doc)

    async def get_range(
        self,
        date_from: datetime,
        date_to: datetime,
    ) -> List[DailyUsageStats]:
        """Get stats for a date range."""
        cursor = self.collection.find(
            {"date": {"$gte": date_from, "$lte": date_to}}
        ).sort("date", 1)

        stats = []
        async for doc in cursor:
            stats.append(self._to_entity(doc))
        return stats

    async def get_summary(
        self,
        days: int = 30,
    ) -> dict:
        """Get summary for last N days."""
        start_date = datetime.now() - timedelta(days=days)

        pipeline = [
            {"$match": {"date": {"$gte": start_date}}},
            {
                "$group": {
                    "_id": None,
                    "total_requests": {"$sum": "$total_requests"},
                    "total_errors": {"$sum": "$error_requests"},
                    "avg_latency": {"$avg": "$avg_latency_ms"},
                    "total_cost": {"$sum": "$total_cost"},
                    "total_tokens": {"$sum": "$total_tokens"},
                }
            },
        ]

        result = await self.collection.aggregate(pipeline).to_list(1)

        if not result:
            return {
                "total_requests": 0,
                "total_errors": 0,
                "avg_latency_ms": 0.0,
                "total_cost": 0.0,
                "total_tokens": 0,
                "error_rate": 0.0,
            }

        data = result[0]
        total = data["total_requests"]

        return {
            "total_requests": total,
            "total_errors": data["total_errors"],
            "avg_latency_ms": round(data["avg_latency"] or 0, 2),
            "total_cost": round(data["total_cost"], 4),
            "total_tokens": data["total_tokens"],
            "error_rate": round(data["total_errors"] / total, 4) if total > 0 else 0.0,
        }
