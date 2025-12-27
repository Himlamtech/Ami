"""Profile DTOs for user-facing APIs."""

from pydantic import BaseModel, Field
from typing import Optional, List, Dict, Any


class TopicInterestResponse(BaseModel):
    topic: str
    score: float
    last_accessed: Optional[str] = None
    source: str = "chat"


class StudentProfileResponse(BaseModel):
    id: str
    user_id: str
    student_id: Optional[str] = None
    name: Optional[str] = None
    email: Optional[str] = None
    phone: Optional[str] = None
    gender: Optional[str] = None
    date_of_birth: Optional[str] = None
    address: Optional[str] = None
    level: str
    major: Optional[str] = None
    class_name: Optional[str] = None
    faculty: Optional[str] = None
    year: Optional[int] = None
    intake_year: Optional[int] = None
    current_year: Optional[int] = None
    current_semester: Optional[int] = None
    preferred_detail_level: str
    personality_summary: Optional[str] = None
    personality_traits: List[str] = []
    top_interests: List[str] = []
    interests: List[TopicInterestResponse] = []
    total_questions: int = 0
    total_downloads: int = 0


class UpdateProfileRequest(BaseModel):
    student_id: Optional[str] = None
    name: Optional[str] = None
    email: Optional[str] = None
    phone: Optional[str] = None
    gender: Optional[str] = None
    date_of_birth: Optional[str] = None
    address: Optional[str] = None
    major: Optional[str] = None
    faculty: Optional[str] = None
    year: Optional[int] = None
    level: Optional[str] = None
    class_name: Optional[str] = None


class SetPreferencesRequest(BaseModel):
    detail_level: Optional[str] = Field(
        None,
        description="brief, medium, or detailed",
    )
    language: Optional[str] = Field(None, description="vi or en")


class PersonalizedContextResponse(BaseModel):
    greeting: str
    detail_level: str
    topic_hints: List[str]
    suggested_topics: List[str]


class InteractionRecord(BaseModel):
    topic: str
    interaction_type: str = "question"
    metadata: Optional[Dict[str, Any]] = None


__all__ = [
    "TopicInterestResponse",
    "StudentProfileResponse",
    "UpdateProfileRequest",
    "SetPreferencesRequest",
    "PersonalizedContextResponse",
    "InteractionRecord",
]
