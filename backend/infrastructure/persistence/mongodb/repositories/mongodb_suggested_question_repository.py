"""MongoDB Suggested Question Repository implementation."""

from datetime import datetime
from typing import List, Optional

from motor.motor_asyncio import AsyncIOMotorDatabase
from bson import ObjectId

from app.domain.entities.suggested_question import SuggestedQuestion
from app.application.interfaces.repositories.suggested_question_repository import (
    ISuggestedQuestionRepository,
)


class MongoDBSuggestedQuestionRepository(ISuggestedQuestionRepository):
    """MongoDB implementation for suggested questions."""

    def __init__(self, db: AsyncIOMotorDatabase):
        from app.config import mongodb_config

        self.db = db
        self.collection = db[mongodb_config.collection_suggested_questions]

    def _to_doc(self, question: SuggestedQuestion) -> dict:
        return {
            "text": question.text,
            "tags": question.tags,
            "category": question.category,
            "is_active": question.is_active,
            "created_at": question.created_at,
            "updated_at": question.updated_at,
        }

    def _from_doc(self, doc: dict) -> SuggestedQuestion:
        return SuggestedQuestion(
            id=str(doc.get("_id", "")),
            text=doc.get("text", ""),
            tags=doc.get("tags", []),
            category=doc.get("category"),
            is_active=doc.get("is_active", True),
            created_at=doc.get("created_at", datetime.now()),
            updated_at=doc.get("updated_at", datetime.now()),
        )

    async def create(self, question: SuggestedQuestion) -> SuggestedQuestion:
        doc = self._to_doc(question)
        result = await self.collection.insert_one(doc)
        question.id = str(result.inserted_id)
        return question

    async def get_by_id(self, question_id: str) -> Optional[SuggestedQuestion]:
        try:
            doc = await self.collection.find_one({"_id": ObjectId(question_id)})
        except Exception:
            doc = await self.collection.find_one({"_id": question_id})
        if not doc:
            return None
        return self._from_doc(doc)

    async def get_by_ids(self, question_ids: List[str]) -> List[SuggestedQuestion]:
        if not question_ids:
            return []
        object_ids = []
        raw_ids = []
        for qid in question_ids:
            try:
                object_ids.append(ObjectId(qid))
            except Exception:
                raw_ids.append(qid)
        query = {"$or": []}
        if object_ids:
            query["$or"].append({"_id": {"$in": object_ids}})
        if raw_ids:
            query["$or"].append({"_id": {"$in": raw_ids}})
        if not query["$or"]:
            return []
        cursor = self.collection.find(query)
        docs = await cursor.to_list(length=len(question_ids))
        return [self._from_doc(doc) for doc in docs]

    async def find_by_text(self, text: str) -> Optional[SuggestedQuestion]:
        doc = await self.collection.find_one({"text": text})
        if not doc:
            return None
        return self._from_doc(doc)

    async def list_active(self, limit: int = 10) -> List[SuggestedQuestion]:
        cursor = self.collection.find({"is_active": True}).limit(limit)
        docs = await cursor.to_list(length=limit)
        return [self._from_doc(doc) for doc in docs]
