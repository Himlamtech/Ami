"""MongoDB Feedback Repository implementation."""

from typing import Optional, List
from datetime import datetime, timedelta
from motor.motor_asyncio import AsyncIOMotorDatabase
from bson import ObjectId

from app.domain.entities.feedback import (
    Feedback,
    FeedbackType,
    FeedbackCategory,
    FeedbackStatus,
)
from app.application.interfaces.repositories.feedback_repository import (
    IFeedbackRepository,
)


class MongoDBFeedbackRepository(IFeedbackRepository):
    """MongoDB implementation of Feedback Repository."""

    def __init__(self, db: AsyncIOMotorDatabase):
        self.db = db
        self.collection = db["feedbacks"]

    # ===== Mappers =====

    def _to_entity(self, doc: dict) -> Feedback:
        """Convert MongoDB document to Feedback entity."""
        return Feedback(
            id=str(doc["_id"]),
            session_id=doc["session_id"],
            message_id=doc["message_id"],
            user_id=doc["user_id"],
            feedback_type=FeedbackType(doc["feedback_type"]),
            rating=doc.get("rating"),
            categories=[FeedbackCategory(c) for c in doc.get("categories", [])],
            comment=doc.get("comment"),
            query=doc.get("query"),
            response=doc.get("response"),
            sources_used=doc.get("sources_used", []),
            status=FeedbackStatus(doc.get("status", "pending")),
            reviewed_by=doc.get("reviewed_by"),
            reviewed_at=doc.get("reviewed_at"),
            review_notes=doc.get("review_notes"),
            linked_gap_id=doc.get("linked_gap_id"),
            created_at=doc.get("created_at", datetime.now()),
            updated_at=doc.get("updated_at", datetime.now()),
        )

    def _to_doc(self, feedback: Feedback) -> dict:
        """Convert Feedback entity to MongoDB document."""
        return {
            "session_id": feedback.session_id,
            "message_id": feedback.message_id,
            "user_id": feedback.user_id,
            "feedback_type": feedback.feedback_type.value,
            "rating": feedback.rating,
            "categories": [c.value for c in feedback.categories],
            "comment": feedback.comment,
            "query": feedback.query,
            "response": feedback.response,
            "sources_used": feedback.sources_used,
            "status": feedback.status.value,
            "reviewed_by": feedback.reviewed_by,
            "reviewed_at": feedback.reviewed_at,
            "review_notes": feedback.review_notes,
            "linked_gap_id": feedback.linked_gap_id,
            "created_at": feedback.created_at,
            "updated_at": feedback.updated_at,
        }

    # ===== CRUD Operations =====

    async def create(self, feedback: Feedback) -> Feedback:
        """Create new feedback."""
        doc = self._to_doc(feedback)
        result = await self.collection.insert_one(doc)
        feedback.id = str(result.inserted_id)
        return feedback

    async def get_by_id(self, feedback_id: str) -> Optional[Feedback]:
        """Get feedback by ID."""
        try:
            doc = await self.collection.find_one({"_id": ObjectId(feedback_id)})
        except:
            return None
        if not doc:
            return None
        return self._to_entity(doc)

    async def update(self, feedback: Feedback) -> Feedback:
        """Update existing feedback."""
        doc = self._to_doc(feedback)
        doc["updated_at"] = datetime.now()
        await self.collection.update_one({"_id": ObjectId(feedback.id)}, {"$set": doc})
        return feedback

    async def delete(self, feedback_id: str) -> bool:
        """Delete feedback."""
        result = await self.collection.delete_one({"_id": ObjectId(feedback_id)})
        return result.deleted_count > 0

    # ===== Query Operations =====

    async def get_by_message_id(self, message_id: str) -> Optional[Feedback]:
        """Get feedback for a specific message."""
        doc = await self.collection.find_one({"message_id": message_id})
        if not doc:
            return None
        return self._to_entity(doc)

    async def list_by_session(
        self,
        session_id: str,
        skip: int = 0,
        limit: int = 100,
    ) -> List[Feedback]:
        """List all feedback for a session."""
        cursor = (
            self.collection.find({"session_id": session_id})
            .sort("created_at", -1)
            .skip(skip)
            .limit(limit)
        )

        feedbacks = []
        async for doc in cursor:
            feedbacks.append(self._to_entity(doc))
        return feedbacks

    async def list_by_user(
        self,
        user_id: str,
        skip: int = 0,
        limit: int = 100,
    ) -> List[Feedback]:
        """List all feedback from a user."""
        cursor = (
            self.collection.find({"user_id": user_id})
            .sort("created_at", -1)
            .skip(skip)
            .limit(limit)
        )

        feedbacks = []
        async for doc in cursor:
            feedbacks.append(self._to_entity(doc))
        return feedbacks

    # ===== Admin Query Operations =====

    async def list_all(
        self,
        skip: int = 0,
        limit: int = 100,
        feedback_type: Optional[FeedbackType] = None,
        status: Optional[FeedbackStatus] = None,
        date_from: Optional[datetime] = None,
        date_to: Optional[datetime] = None,
        is_negative: Optional[bool] = None,
    ) -> List[Feedback]:
        """List all feedback with filters (admin)."""
        query = {}

        if feedback_type:
            query["feedback_type"] = feedback_type.value
        if status:
            query["status"] = status.value
        if date_from:
            query.setdefault("created_at", {})["$gte"] = date_from
        if date_to:
            query.setdefault("created_at", {})["$lte"] = date_to
        if is_negative is True:
            query["$or"] = [
                {"feedback_type": {"$in": ["not_helpful", "incorrect", "incomplete"]}},
                {"rating": {"$lte": 2}},
            ]
        elif is_negative is False:
            query["$or"] = [
                {"feedback_type": "helpful"},
                {"rating": {"$gte": 4}},
            ]

        cursor = (
            self.collection.find(query).sort("created_at", -1).skip(skip).limit(limit)
        )

        feedbacks = []
        async for doc in cursor:
            feedbacks.append(self._to_entity(doc))
        return feedbacks

    async def count_all(
        self,
        feedback_type: Optional[FeedbackType] = None,
        status: Optional[FeedbackStatus] = None,
        date_from: Optional[datetime] = None,
        date_to: Optional[datetime] = None,
        is_negative: Optional[bool] = None,
    ) -> int:
        """Count all feedback with filters."""
        query = {}

        if feedback_type:
            query["feedback_type"] = feedback_type.value
        if status:
            query["status"] = status.value
        if date_from:
            query.setdefault("created_at", {})["$gte"] = date_from
        if date_to:
            query.setdefault("created_at", {})["$lte"] = date_to
        if is_negative is True:
            query["$or"] = [
                {"feedback_type": {"$in": ["not_helpful", "incorrect", "incomplete"]}},
                {"rating": {"$lte": 2}},
            ]

        return await self.collection.count_documents(query)

    async def get_negative_feedback(
        self,
        skip: int = 0,
        limit: int = 100,
        reviewed: Optional[bool] = None,
    ) -> List[Feedback]:
        """Get negative feedback for review."""
        query = {
            "$or": [
                {"feedback_type": {"$in": ["not_helpful", "incorrect", "incomplete"]}},
                {"rating": {"$lte": 2}},
            ]
        }

        if reviewed is True:
            query["status"] = {"$ne": "pending"}
        elif reviewed is False:
            query["status"] = "pending"

        cursor = (
            self.collection.find(query).sort("created_at", -1).skip(skip).limit(limit)
        )

        feedbacks = []
        async for doc in cursor:
            feedbacks.append(self._to_entity(doc))
        return feedbacks

    # ===== Analytics Operations =====

    async def get_stats(
        self,
        date_from: Optional[datetime] = None,
        date_to: Optional[datetime] = None,
    ) -> dict:
        """Get feedback statistics."""
        match_stage = {}
        if date_from:
            match_stage.setdefault("created_at", {})["$gte"] = date_from
        if date_to:
            match_stage.setdefault("created_at", {})["$lte"] = date_to

        pipeline = []
        if match_stage:
            pipeline.append({"$match": match_stage})

        pipeline.extend(
            [
                {
                    "$facet": {
                        "total": [{"$count": "count"}],
                        "by_type": [
                            {"$group": {"_id": "$feedback_type", "count": {"$sum": 1}}}
                        ],
                        "by_category": [
                            {
                                "$unwind": {
                                    "path": "$categories",
                                    "preserveNullAndEmptyArrays": True,
                                }
                            },
                            {"$group": {"_id": "$categories", "count": {"$sum": 1}}},
                        ],
                        "ratings": [
                            {"$match": {"rating": {"$ne": None}}},
                            {
                                "$group": {
                                    "_id": None,
                                    "avg": {"$avg": "$rating"},
                                    "count": {"$sum": 1},
                                }
                            },
                        ],
                    }
                }
            ]
        )

        result = await self.collection.aggregate(pipeline).to_list(1)

        if not result:
            return {
                "total": 0,
                "helpful_count": 0,
                "not_helpful_count": 0,
                "avg_rating": 0.0,
                "by_type": {},
                "by_category": {},
            }

        data = result[0]
        total = data["total"][0]["count"] if data["total"] else 0

        by_type = {item["_id"]: item["count"] for item in data["by_type"]}
        by_category = {
            item["_id"]: item["count"] for item in data["by_category"] if item["_id"]
        }

        avg_rating = data["ratings"][0]["avg"] if data["ratings"] else 0.0

        return {
            "total": total,
            "helpful_count": by_type.get("helpful", 0),
            "not_helpful_count": by_type.get("not_helpful", 0),
            "avg_rating": round(avg_rating, 2) if avg_rating else 0.0,
            "by_type": by_type,
            "by_category": by_category,
        }

    async def get_trends(
        self,
        days: int = 30,
        group_by: str = "day",
    ) -> List[dict]:
        """Get feedback trends over time."""
        start_date = datetime.now() - timedelta(days=days)

        date_format = "%Y-%m-%d" if group_by == "day" else "%Y-%m-%d %H:00"

        pipeline = [
            {"$match": {"created_at": {"$gte": start_date}}},
            {
                "$group": {
                    "_id": {
                        "$dateToString": {"format": date_format, "date": "$created_at"}
                    },
                    "total": {"$sum": 1},
                    "helpful": {
                        "$sum": {
                            "$cond": [{"$eq": ["$feedback_type", "helpful"]}, 1, 0]
                        }
                    },
                    "not_helpful": {
                        "$sum": {
                            "$cond": [{"$eq": ["$feedback_type", "not_helpful"]}, 1, 0]
                        }
                    },
                    "avg_rating": {"$avg": "$rating"},
                }
            },
            {"$sort": {"_id": 1}},
        ]

        results = await self.collection.aggregate(pipeline).to_list(None)

        return [
            {
                "date": item["_id"],
                "total": item["total"],
                "helpful": item["helpful"],
                "not_helpful": item["not_helpful"],
                "avg_rating": (
                    round(item["avg_rating"], 2) if item["avg_rating"] else None
                ),
            }
            for item in results
        ]

    async def get_top_issues(
        self,
        limit: int = 10,
        days: int = 30,
    ) -> List[dict]:
        """Get top issues from negative feedback."""
        start_date = datetime.now() - timedelta(days=days)

        pipeline = [
            {
                "$match": {
                    "created_at": {"$gte": start_date},
                    "$or": [
                        {
                            "feedback_type": {
                                "$in": ["not_helpful", "incorrect", "incomplete"]
                            }
                        },
                        {"rating": {"$lte": 2}},
                    ],
                    "query": {"$ne": None},
                }
            },
            {
                "$group": {
                    "_id": {"$substr": ["$query", 0, 100]},  # Group by query prefix
                    "count": {"$sum": 1},
                    "samples": {"$push": {"query": "$query", "comment": "$comment"}},
                }
            },
            {"$sort": {"count": -1}},
            {"$limit": limit},
        ]

        results = await self.collection.aggregate(pipeline).to_list(None)

        return [
            {
                "topic": item["_id"],
                "count": item["count"],
                "samples": item["samples"][:5],  # Limit samples
            }
            for item in results
        ]

    # ===== Aliases for admin routes =====

    async def find_by_user_id(
        self,
        user_id: str,
        limit: int = 100,
    ) -> List[Feedback]:
        """Alias for list_by_user."""
        return await self.list_by_user(user_id, limit=limit)
