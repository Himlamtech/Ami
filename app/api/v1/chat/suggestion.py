"""Suggestion routes for proactive recommendations."""

from fastapi import APIRouter, Depends, Query
from datetime import datetime, timezone
import random

from app.api.dependencies.auth import get_user_id
from app.infrastructure.factory import get_factory
from app.api.schemas.suggestion_dto import SuggestionItem, SuggestionsResponse


router = APIRouter(prefix="/suggestions", tags=["Suggestions"])


COMMON_QUESTIONS = [
    {"text": "Học phí học kỳ này bao nhiêu?", "category": "học phí"},
    {"text": "Lịch đăng ký học phần như thế nào?", "category": "đăng ký"},
    {"text": "Cách xin mẫu đơn nghỉ học?", "category": "thủ tục"},
    {"text": "Điểm tổng kết được tính thế nào?", "category": "điểm"},
    {"text": "Thủ tục xin cấp lại thẻ sinh viên?", "category": "thủ tục"},
    {"text": "Làm sao để đăng ký học lại?", "category": "đăng ký"},
    {"text": "Cách xin đơn vắng thi?", "category": "thủ tục"},
    {"text": "Lịch thi học kỳ khi nào?", "category": "lịch"},
    {"text": "Thủ tục làm hồ sơ tốt nghiệp?", "category": "tốt nghiệp"},
    {"text": "Chương trình đào tạo ngành CNTT?", "category": "đào tạo"},
    {"text": "Điều kiện học bổng là gì?", "category": "học bổng"},
    {"text": "Quy định điểm rèn luyện?", "category": "điểm"},
    {"text": "Phòng đào tạo ở đâu?", "category": "địa điểm"},
    {"text": "Giờ làm việc của phòng công tác sinh viên?", "category": "giờ làm việc"},
    {"text": "Cách xin bảng điểm?", "category": "thủ tục"},
]


@router.get("", response_model=SuggestionsResponse)
async def get_suggestions(
    user_id: str = Depends(get_user_id),
    count: int = Query(default=5, ge=1, le=20),
    include_popular: bool = Query(default=True),
    include_personalized: bool = Query(default=True),
):
    """Get personalized suggestions based on user profile and popular topics."""
    factory = get_factory()
    suggestions: List[SuggestionItem] = []

    try:
        if include_personalized:
            profile_repo = factory.get_student_profile_repository()
            profile = await profile_repo.find_by_user_id(user_id)

            if profile:
                interests = profile.get_top_interests(3)
                interest_topics = [i.topic for i in interests]

                for q in COMMON_QUESTIONS:
                    if q["category"] in interest_topics:
                        suggestions.append(
                            SuggestionItem(
                                id=f"profile_{len(suggestions)}",
                                text=q["text"],
                                type="question",
                                category=q["category"],
                                relevance_score=0.9,
                                source="profile",
                            )
                        )
                        if len(suggestions) >= count // 2:
                            break

        if include_popular:
            remaining = count - len(suggestions)
            already_added = [s.text for s in suggestions]
            available = [q for q in COMMON_QUESTIONS if q["text"] not in already_added]
            sample = random.sample(available, min(remaining, len(available)))

            for q in sample:
                suggestions.append(
                    SuggestionItem(
                        id=f"popular_{len(suggestions)}",
                        text=q["text"],
                        type="question",
                        category=q["category"],
                        relevance_score=0.7,
                        source="popular",
                    )
                )

    except Exception:
        sample = random.sample(COMMON_QUESTIONS, min(count, len(COMMON_QUESTIONS)))
        for i, q in enumerate(sample):
            suggestions.append(
                SuggestionItem(
                    id=f"default_{i}",
                    text=q["text"],
                    type="question",
                    category=q["category"],
                    relevance_score=0.5,
                    source="system",
                )
            )

    return SuggestionsResponse(
        suggestions=suggestions[:count],
        generated_at=datetime.now(timezone.utc),
    )


__all__ = ["router", "COMMON_QUESTIONS"]
