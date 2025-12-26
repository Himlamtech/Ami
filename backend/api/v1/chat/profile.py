"""Student profile and personalization routes."""

from fastapi import APIRouter, HTTPException

from app.config.services import ServiceRegistry
from app.application.services.personalization_service import PersonalizationService
from app.domain.entities.student_profile import StudentLevel
from app.api.schemas.profile_dto import (
    StudentProfileResponse,
    UpdateProfileRequest,
    SetPreferencesRequest,
    PersonalizedContextResponse,
    InteractionRecord,
)

router = APIRouter(prefix="/profile", tags=["Profile"])


def _get_service() -> PersonalizationService:
    repo = ServiceRegistry.get_student_profile_repository()
    return PersonalizationService(repo)


@router.get("/{user_id}", response_model=StudentProfileResponse)
async def get_profile(user_id: str):
    service = _get_service()
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
    service = _get_service()

    level = None
    if request.level:
        try:
            level = StudentLevel(request.level)
        except ValueError:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"Invalid level: {request.level}",
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
    service = _get_service()

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
    service = _get_service()
    context = await service.get_personalized_context(user_id)

    return PersonalizedContextResponse(
        greeting=context.user_greeting,
        detail_level=context.detail_level,
        topic_hints=context.topic_hints,
        suggested_topics=context.suggested_topics,
    )


@router.post("/{user_id}/interactions")
async def record_interaction(user_id: str, request: InteractionRecord):
    service = _get_service()

    if request.interaction_type == "question":
        await service.record_question(
            user_id=user_id,
            question="",
            topic=request.topic,
            metadata=request.metadata,
        )
    elif request.interaction_type == "download":
        await service.record_download(
            user_id=user_id,
            document_name=(
                request.metadata.get("document", "") if request.metadata else ""
            ),
            topic=request.topic,
        )

    return {"status": "recorded"}


__all__ = ["router"]
