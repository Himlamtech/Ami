"""MongoDB Student Profile Repository implementation."""

from typing import Optional, List
from datetime import datetime
import uuid

from motor.motor_asyncio import AsyncIOMotorDatabase
from bson import ObjectId

from app.domain.entities.student_profile import (
    StudentProfile,
    StudentLevel,
    InteractionType,
    InteractionHistory,
    TopicInterest,
)
from app.application.interfaces.repositories.student_profile_repository import (
    IStudentProfileRepository,
)


class MongoDBStudentProfileRepository(IStudentProfileRepository):
    """MongoDB implementation of Student Profile Repository."""

    def __init__(self, db: AsyncIOMotorDatabase):
        self.db = db
        self.collection = db["student_profiles"]

    def _to_dict(self, profile: StudentProfile) -> dict:
        """Convert entity to MongoDB document."""
        return {
            "user_id": profile.user_id,
            "student_id": profile.student_id,
            "name": profile.name,
            "email": profile.email,
            "phone": profile.phone,
            "gender": profile.gender,
            "date_of_birth": profile.date_of_birth,
            "address": profile.address,
            "level": profile.level.value,
            "major": profile.major,
            "class_name": profile.class_name,
            "faculty": profile.faculty,
            "year": profile.year,
            "preferred_language": profile.preferred_language,
            "preferred_detail_level": profile.preferred_detail_level,
            "personality_summary": profile.personality_summary,
            "personality_traits": profile.personality_traits,
            "topics_of_interest": [
                {
                    "topic": t.topic,
                    "score": t.score,
                    "interaction_count": t.interaction_count,
                    "last_accessed": (
                        t.last_accessed.isoformat() if t.last_accessed else None
                    ),
                    "source": t.source,
                }
                for t in profile.topics_of_interest
            ],
            "interaction_history": [h.to_dict() for h in profile.interaction_history],
            "total_questions": profile.total_questions,
            "total_downloads": profile.total_downloads,
            "total_sessions": profile.total_sessions,
            "created_at": profile.created_at,
            "updated_at": profile.updated_at,
            "last_active_at": profile.last_active_at,
        }

    def _from_dict(self, doc: dict) -> StudentProfile:
        """Convert MongoDB document to entity."""
        topics = []
        for t in doc.get("topics_of_interest", []):
            last_accessed = None
            if t.get("last_accessed"):
                if isinstance(t["last_accessed"], str):
                    last_accessed = datetime.fromisoformat(t["last_accessed"])
                else:
                    last_accessed = t["last_accessed"]

            topics.append(
                TopicInterest(
                    topic=t["topic"],
                    score=t.get("score", 0.0),
                    interaction_count=t.get("interaction_count", 0),
                    last_accessed=last_accessed,
                    source=t.get("source", "chat"),
                )
            )

        history = []
        for h in doc.get("interaction_history", []):
            timestamp = h.get("timestamp")
            if isinstance(timestamp, str):
                timestamp = datetime.fromisoformat(timestamp)

            history.append(
                InteractionHistory(
                    interaction_type=InteractionType(h["type"]),
                    topic=h["topic"],
                    timestamp=timestamp or datetime.now(),
                    metadata=h.get("metadata", {}),
                )
            )

        return StudentProfile(
            id=str(doc.get("_id", doc.get("id", ""))),
            user_id=doc["user_id"],
            student_id=doc.get("student_id"),
            name=doc.get("name"),
            email=doc.get("email"),
            phone=doc.get("phone"),
            gender=doc.get("gender"),
            date_of_birth=doc.get("date_of_birth"),
            address=doc.get("address"),
            level=StudentLevel(doc.get("level", "freshman")),
            major=doc.get("major"),
            class_name=doc.get("class_name"),
            faculty=doc.get("faculty"),
            year=doc.get("year"),
            preferred_language=doc.get("preferred_language", "vi"),
            preferred_detail_level=doc.get("preferred_detail_level", "medium"),
            personality_summary=doc.get("personality_summary"),
            personality_traits=doc.get("personality_traits", []),
            topics_of_interest=topics,
            interaction_history=history,
            total_questions=doc.get("total_questions", 0),
            total_downloads=doc.get("total_downloads", 0),
            total_sessions=doc.get("total_sessions", 0),
            created_at=doc.get("created_at", datetime.now()),
            updated_at=doc.get("updated_at", datetime.now()),
            last_active_at=doc.get("last_active_at"),
        )

    async def create(self, profile: StudentProfile) -> StudentProfile:
        """Create a new student profile."""
        doc = self._to_dict(profile)
        result = await self.collection.insert_one(doc)
        profile.id = str(result.inserted_id)
        return profile

    async def get_by_id(self, profile_id: str) -> Optional[StudentProfile]:
        """Get profile by ID."""
        try:
            doc = await self.collection.find_one({"_id": ObjectId(profile_id)})
        except Exception:
            return None

        if not doc:
            return None

        return self._from_dict(doc)

    async def get_by_user_id(self, user_id: str) -> Optional[StudentProfile]:
        """Get profile by user ID."""
        doc = await self.collection.find_one({"user_id": user_id})
        if not doc:
            return None
        return self._from_dict(doc)

    async def get_by_student_id(self, student_id: str) -> Optional[StudentProfile]:
        """Get profile by student ID (MSV)."""
        doc = await self.collection.find_one({"student_id": student_id})
        if not doc:
            return None
        return self._from_dict(doc)

    async def update(self, profile: StudentProfile) -> StudentProfile:
        """Update an existing profile."""
        doc = self._to_dict(profile)
        doc["updated_at"] = datetime.now()

        await self.collection.update_one({"_id": ObjectId(profile.id)}, {"$set": doc})

        return profile

    async def delete(self, profile_id: str) -> bool:
        """Delete a profile."""
        try:
            result = await self.collection.delete_one({"_id": ObjectId(profile_id)})
            return result.deleted_count > 0
        except Exception:
            return False

    async def list_by_major(self, major: str, limit: int = 50) -> List[StudentProfile]:
        """List profiles by major."""
        cursor = self.collection.find({"major": major}).limit(limit)
        profiles = []
        async for doc in cursor:
            profiles.append(self._from_dict(doc))
        return profiles

    async def get_or_create(self, user_id: str) -> StudentProfile:
        """Get existing profile or create new one for user."""
        profile = await self.get_by_user_id(user_id)
        if profile:
            return profile

        # Create new profile
        new_profile = StudentProfile(
            id=str(uuid.uuid4()),
            user_id=user_id,
        )
        return await self.create(new_profile)

    # ===== Admin Methods =====

    async def find_all(
        self,
        major: Optional[str] = None,
        level: Optional[str] = None,
        skip: int = 0,
        limit: int = 20,
    ) -> List[StudentProfile]:
        """Find all profiles with optional filters."""
        query = {}
        if major:
            query["major"] = major
        if level:
            query["level"] = level

        cursor = self.collection.find(query).skip(skip).limit(limit)
        profiles = []
        async for doc in cursor:
            profiles.append(self._from_dict(doc))
        return profiles

    async def count_all(
        self,
        major: Optional[str] = None,
        level: Optional[str] = None,
    ) -> int:
        """Count all profiles with optional filters."""
        query = {}
        if major:
            query["major"] = major
        if level:
            query["level"] = level

        return await self.collection.count_documents(query)

    async def find_by_user_id(self, user_id: str) -> Optional[StudentProfile]:
        """Alias for get_by_user_id for admin routes consistency."""
        return await self.get_by_user_id(user_id)
