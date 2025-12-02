"""Student profile and personalization API routes."""

from fastapi import APIRouter, Depends, HTTPException, status
from pydantic import BaseModel, Field
from typing import Optional, List, Dict, Any

from app.domain.entities.student_profile import StudentLevel


# ===== DTOs =====

class StudentProfileResponse(BaseModel):
    """Student profile response."""
    id: str
    user_id: str
    student_id: Optional[str] = None
    name: Optional[str] = None
    email: Optional[str] = None
    level: str
    major: Optional[str] = None
    class_name: Optional[str] = None
    preferred_detail_level: str
    top_interests: List[str] = []
    total_questions: int = 0
    total_downloads: int = 0


class UpdateProfileRequest(BaseModel):
    """Request to update profile."""
    student_id: Optional[str] = None
    name: Optional[str] = None
    major: Optional[str] = None
    level: Optional[str] = None
    class_name: Optional[str] = None


class SetPreferencesRequest(BaseModel):
    """Request to set preferences."""
    detail_level: Optional[str] = Field(
        None,
        description="brief, medium, or detailed"
    )
    language: Optional[str] = Field(None, description="vi or en")


class PersonalizedContextResponse(BaseModel):
    """Personalized context response."""
    greeting: str
    detail_level: str
    topic_hints: List[str]
    suggested_topics: List[str]


class InteractionRecord(BaseModel):
    """Record an interaction."""
    topic: str
    interaction_type: str = "question"  # question, download, search
    metadata: Optional[Dict[str, Any]] = None


# ===== Router =====

router = APIRouter(prefix="/profile", tags=["Profile"])


def get_profile_repository():
    """Get student profile repository dependency."""
    from app.infrastructure.factory.provider_factory import ProviderFactory
    factory = ProviderFactory()
    from app.infrastructure.persistence.mongodb.repositories import MongoDBStudentProfileRepository
    return MongoDBStudentProfileRepository(factory.mongodb_database)


def get_personalization_service():
    """Get personalization service dependency."""
    from app.application.services.personalization_service import PersonalizationService
    repo = get_profile_repository()
    return PersonalizationService(repo)


@router.get("/{user_id}", response_model=StudentProfileResponse)
async def get_profile(user_id: str):
    """Get student profile by user ID."""
    service = get_personalization_service()
    profile = await service.get_or_create_profile(user_id)
    
    return StudentProfileResponse(
        id=profile.id,
        user_id=profile.user_id,
        student_id=profile.student_id,
        name=profile.name,
        email=profile.email,
        level=profile.level.value,
        major=profile.major,
        class_name=profile.class_name,
        preferred_detail_level=profile.preferred_detail_level,
        top_interests=[t.topic for t in profile.get_top_interests(5)],
        total_questions=profile.total_questions,
        total_downloads=profile.total_downloads,
    )


@router.put("/{user_id}", response_model=StudentProfileResponse)
async def update_profile(user_id: str, request: UpdateProfileRequest):
    """Update student profile."""
    service = get_personalization_service()
    
    level = None
    if request.level:
        try:
            level = StudentLevel(request.level)
        except ValueError:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"Invalid level: {request.level}"
            )
    
    profile = await service.update_profile_info(
        user_id=user_id,
        student_id=request.student_id,
        name=request.name,
        major=request.major,
        level=level,
        class_name=request.class_name,
    )
    
    return StudentProfileResponse(
        id=profile.id,
        user_id=profile.user_id,
        student_id=profile.student_id,
        name=profile.name,
        email=profile.email,
        level=profile.level.value,
        major=profile.major,
        class_name=profile.class_name,
        preferred_detail_level=profile.preferred_detail_level,
        top_interests=[t.topic for t in profile.get_top_interests(5)],
        total_questions=profile.total_questions,
        total_downloads=profile.total_downloads,
    )


@router.put("/{user_id}/preferences", response_model=StudentProfileResponse)
async def set_preferences(user_id: str, request: SetPreferencesRequest):
    """Set user preferences."""
    service = get_personalization_service()
    
    profile = await service.set_preferences(
        user_id=user_id,
        detail_level=request.detail_level,
        language=request.language,
    )
    
    return StudentProfileResponse(
        id=profile.id,
        user_id=profile.user_id,
        student_id=profile.student_id,
        name=profile.name,
        email=profile.email,
        level=profile.level.value,
        major=profile.major,
        class_name=profile.class_name,
        preferred_detail_level=profile.preferred_detail_level,
        top_interests=[t.topic for t in profile.get_top_interests(5)],
        total_questions=profile.total_questions,
        total_downloads=profile.total_downloads,
    )


@router.get("/{user_id}/context", response_model=PersonalizedContextResponse)
async def get_personalized_context(user_id: str):
    """Get personalized context for a user."""
    service = get_personalization_service()
    context = await service.get_personalized_context(user_id)
    
    return PersonalizedContextResponse(
        greeting=context.user_greeting,
        detail_level=context.detail_level,
        topic_hints=context.topic_hints,
        suggested_topics=context.suggested_topics,
    )


@router.post("/{user_id}/interactions")
async def record_interaction(user_id: str, request: InteractionRecord):
    """Record a user interaction."""
    service = get_personalization_service()
    
    if request.interaction_type == "question":
        await service.record_question(
            user_id=user_id,
            question="",  # Optional
            topic=request.topic,
            metadata=request.metadata,
        )
    elif request.interaction_type == "download":
        await service.record_download(
            user_id=user_id,
            document_name=request.metadata.get("document", "") if request.metadata else "",
            topic=request.topic,
        )
    
    return {"status": "recorded"}
