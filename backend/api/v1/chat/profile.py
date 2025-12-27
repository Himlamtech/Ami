"""Student profile and personalization routes."""

from fastapi import APIRouter, HTTPException, status

from config.services import ServiceRegistry
from application.services.personalization_service import PersonalizationService
from domain.entities.student_profile import StudentLevel
from api.schemas.profile_dto import (
    StudentProfileResponse,
    UpdateProfileRequest,
    SetPreferencesRequest,
    PersonalizedContextResponse,
    InteractionRecord,
    TopicInterestResponse,
)

router = APIRouter(prefix="/profile", tags=["Profile"])


def _get_service() -> PersonalizationService:
    repo = ServiceRegistry.get_student_profile_repository()
    return PersonalizationService(repo)


@router.get("/{user_id}", response_model=StudentProfileResponse)
async def get_profile(user_id: str):
    service = _get_service()
    profile = await service.get_or_create_profile(user_id)
    progress = profile.get_academic_progress()

    return StudentProfileResponse(
        id=profile.id,
        user_id=profile.user_id,
        student_id=profile.student_id,
        name=profile.name,
        email=profile.email,
        phone=profile.phone,
        gender=profile.gender,
        date_of_birth=profile.date_of_birth,
        address=profile.address,
        level=profile.level.value,
        major=profile.major,
        class_name=profile.class_name,
        faculty=profile.faculty,
        year=profile.year,
        intake_year=progress.get("intake_year"),
        current_year=progress.get("current_year"),
        current_semester=progress.get("current_semester"),
        preferred_detail_level=profile.preferred_detail_level,
        personality_summary=profile.personality_summary,
        personality_traits=profile.personality_traits,
        top_interests=[t.topic for t in profile.get_top_interests(5)],
        interests=[
            TopicInterestResponse(
                topic=t.topic,
                score=t.score,
                last_accessed=t.last_accessed.isoformat() if t.last_accessed else None,
                source=t.source,
            )
            for t in profile.get_top_interests(10)
        ],
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
        email=request.email,
        phone=request.phone,
        gender=request.gender,
        date_of_birth=request.date_of_birth,
        address=request.address,
        major=request.major,
        faculty=request.faculty,
        year=request.year,
        level=level,
        class_name=request.class_name,
    )
    progress = profile.get_academic_progress()

    return StudentProfileResponse(
        id=profile.id,
        user_id=profile.user_id,
        student_id=profile.student_id,
        name=profile.name,
        email=profile.email,
        phone=profile.phone,
        gender=profile.gender,
        date_of_birth=profile.date_of_birth,
        address=profile.address,
        level=profile.level.value,
        major=profile.major,
        class_name=profile.class_name,
        faculty=profile.faculty,
        year=profile.year,
        intake_year=progress.get("intake_year"),
        current_year=progress.get("current_year"),
        current_semester=progress.get("current_semester"),
        preferred_detail_level=profile.preferred_detail_level,
        personality_summary=profile.personality_summary,
        personality_traits=profile.personality_traits,
        top_interests=[t.topic for t in profile.get_top_interests(5)],
        interests=[
            TopicInterestResponse(
                topic=t.topic,
                score=t.score,
                last_accessed=t.last_accessed.isoformat() if t.last_accessed else None,
                source=t.source,
            )
            for t in profile.get_top_interests(10)
        ],
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
    progress = profile.get_academic_progress()

    return StudentProfileResponse(
        id=profile.id,
        user_id=profile.user_id,
        student_id=profile.student_id,
        name=profile.name,
        email=profile.email,
        phone=profile.phone,
        gender=profile.gender,
        date_of_birth=profile.date_of_birth,
        address=profile.address,
        level=profile.level.value,
        major=profile.major,
        class_name=profile.class_name,
        faculty=profile.faculty,
        year=profile.year,
        intake_year=progress.get("intake_year"),
        current_year=progress.get("current_year"),
        current_semester=progress.get("current_semester"),
        preferred_detail_level=profile.preferred_detail_level,
        personality_summary=profile.personality_summary,
        personality_traits=profile.personality_traits,
        top_interests=[t.topic for t in profile.get_top_interests(5)],
        interests=[
            TopicInterestResponse(
                topic=t.topic,
                score=t.score,
                last_accessed=t.last_accessed.isoformat() if t.last_accessed else None,
                source=t.source,
            )
            for t in profile.get_top_interests(10)
        ],
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
