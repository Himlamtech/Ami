"""Feedback service for learning from user feedback."""

from dataclasses import dataclass, field
from datetime import datetime
from typing import List, Optional, Dict, Any
from enum import Enum


class FeedbackType(Enum):
    """Type of feedback."""
    HELPFUL = "helpful"
    NOT_HELPFUL = "not_helpful"
    INCORRECT = "incorrect"
    INCOMPLETE = "incomplete"
    RATING = "rating"  # 1-5 star


class FeedbackCategory(Enum):
    """Category for feedback."""
    ACCURACY = "accuracy"
    RELEVANCE = "relevance"
    COMPLETENESS = "completeness"
    CLARITY = "clarity"
    SPEED = "speed"


@dataclass
class MessageFeedback:
    """Feedback for a single message."""
    id: str
    session_id: str
    message_id: str
    user_id: str
    
    feedback_type: FeedbackType
    rating: Optional[int] = None  # 1-5
    categories: List[FeedbackCategory] = field(default_factory=list)
    comment: Optional[str] = None
    
    # Context
    query: Optional[str] = None
    response: Optional[str] = None
    sources_used: List[str] = field(default_factory=list)
    
    # Timestamps
    created_at: datetime = field(default_factory=datetime.now)


@dataclass
class FeedbackStats:
    """Statistics for feedback."""
    total_feedbacks: int = 0
    helpful_count: int = 0
    not_helpful_count: int = 0
    average_rating: float = 0.0
    
    category_scores: Dict[str, float] = field(default_factory=dict)
    common_issues: List[str] = field(default_factory=list)


class FeedbackService:
    """
    Service for collecting and analyzing user feedback.
    
    Uses feedback to improve responses over time.
    """
    
    def __init__(self, db):
        """Initialize with database connection."""
        self.collection = db["message_feedbacks"]
        self.stats_collection = db["feedback_stats"]
    
    async def submit_feedback(
        self,
        session_id: str,
        message_id: str,
        user_id: str,
        feedback_type: FeedbackType,
        rating: Optional[int] = None,
        categories: Optional[List[FeedbackCategory]] = None,
        comment: Optional[str] = None,
        query: Optional[str] = None,
        response: Optional[str] = None,
        sources_used: Optional[List[str]] = None,
    ) -> MessageFeedback:
        """Submit feedback for a message."""
        import uuid
        
        feedback = MessageFeedback(
            id=str(uuid.uuid4()),
            session_id=session_id,
            message_id=message_id,
            user_id=user_id,
            feedback_type=feedback_type,
            rating=rating,
            categories=categories or [],
            comment=comment,
            query=query,
            response=response,
            sources_used=sources_used or [],
        )
        
        # Save to database
        doc = {
            "_id": feedback.id,
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
            "created_at": feedback.created_at,
        }
        
        await self.collection.insert_one(doc)
        
        # Update stats
        await self._update_stats(feedback)
        
        return feedback
    
    async def _update_stats(self, feedback: MessageFeedback) -> None:
        """Update aggregate statistics."""
        update_ops: Dict[str, Any] = {
            "$inc": {"total_feedbacks": 1}
        }
        
        if feedback.feedback_type == FeedbackType.HELPFUL:
            update_ops["$inc"]["helpful_count"] = 1
        elif feedback.feedback_type == FeedbackType.NOT_HELPFUL:
            update_ops["$inc"]["not_helpful_count"] = 1
        
        await self.stats_collection.update_one(
            {"_id": "global"},
            update_ops,
            upsert=True
        )
    
    async def get_feedback_for_session(self, session_id: str) -> List[MessageFeedback]:
        """Get all feedback for a session."""
        cursor = self.collection.find({"session_id": session_id})
        feedbacks = []
        
        async for doc in cursor:
            feedbacks.append(self._doc_to_feedback(doc))
        
        return feedbacks
    
    async def get_feedback_for_message(self, message_id: str) -> Optional[MessageFeedback]:
        """Get feedback for a specific message."""
        doc = await self.collection.find_one({"message_id": message_id})
        if not doc:
            return None
        return self._doc_to_feedback(doc)
    
    async def get_stats(self) -> FeedbackStats:
        """Get overall feedback statistics."""
        stats_doc = await self.stats_collection.find_one({"_id": "global"})
        
        if not stats_doc:
            return FeedbackStats()
        
        # Calculate average rating
        avg_rating = 0.0
        if stats_doc.get("total_ratings", 0) > 0:
            avg_rating = stats_doc.get("rating_sum", 0) / stats_doc["total_ratings"]
        
        return FeedbackStats(
            total_feedbacks=stats_doc.get("total_feedbacks", 0),
            helpful_count=stats_doc.get("helpful_count", 0),
            not_helpful_count=stats_doc.get("not_helpful_count", 0),
            average_rating=avg_rating,
        )
    
    async def get_negative_feedback_samples(
        self,
        limit: int = 10,
    ) -> List[MessageFeedback]:
        """Get samples of negative feedback for analysis."""
        cursor = self.collection.find({
            "feedback_type": {"$in": ["not_helpful", "incorrect", "incomplete"]}
        }).sort("created_at", -1).limit(limit)
        
        feedbacks = []
        async for doc in cursor:
            feedbacks.append(self._doc_to_feedback(doc))
        
        return feedbacks
    
    async def get_feedback_for_topic(
        self,
        topic: str,
        limit: int = 20,
    ) -> List[MessageFeedback]:
        """Get feedback related to a topic (via query text search)."""
        cursor = self.collection.find({
            "query": {"$regex": topic, "$options": "i"}
        }).limit(limit)
        
        feedbacks = []
        async for doc in cursor:
            feedbacks.append(self._doc_to_feedback(doc))
        
        return feedbacks
    
    def _doc_to_feedback(self, doc: dict) -> MessageFeedback:
        """Convert document to feedback entity."""
        return MessageFeedback(
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
            created_at=doc.get("created_at", datetime.now()),
        )
    
    def analyze_feedback_for_prompt(
        self,
        feedbacks: List[MessageFeedback],
    ) -> str:
        """Analyze feedback to generate prompt improvements."""
        if not feedbacks:
            return ""
        
        issues = []
        negative_count = 0
        
        for fb in feedbacks:
            if fb.feedback_type in [FeedbackType.NOT_HELPFUL, FeedbackType.INCORRECT]:
                negative_count += 1
                if fb.comment:
                    issues.append(fb.comment)
        
        if negative_count == 0:
            return ""
        
        # Build improvement hints
        hints = []
        
        if FeedbackCategory.ACCURACY in [c for fb in feedbacks for c in fb.categories]:
            hints.append("Cần kiểm tra độ chính xác của thông tin.")
        
        if FeedbackCategory.COMPLETENESS in [c for fb in feedbacks for c in fb.categories]:
            hints.append("Cần trả lời đầy đủ hơn.")
        
        if FeedbackCategory.CLARITY in [c for fb in feedbacks for c in fb.categories]:
            hints.append("Cần diễn đạt rõ ràng, dễ hiểu hơn.")
        
        return " ".join(hints)
