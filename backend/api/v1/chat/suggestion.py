"""Suggestion routes for proactive recommendations."""

from fastapi import APIRouter, Depends, Query
from datetime import datetime, timezone
import random
from typing import List

from app.api.dependencies.auth import get_user_id
from app.config.services import ServiceRegistry
from app.api.schemas.suggestion_dto import SuggestionItem, SuggestionsResponse
from app.application.use_cases.suggestions import (
    GetSuggestedQuestionsUseCase,
    GetSuggestedQuestionsInput,
)


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
    suggestions: List[SuggestionItem] = []

    try:
        if include_personalized:
            question_repo = ServiceRegistry.get_suggested_question_repository()
            profile_repo = ServiceRegistry.get_student_profile_repository()
            embedding_service = ServiceRegistry.get_embedding()
            vector_store = ServiceRegistry.get_vector_store()
            if question_repo and profile_repo and embedding_service and vector_store:
                use_case = GetSuggestedQuestionsUseCase(
                    profile_repository=profile_repo,
                    question_repository=question_repo,
                    embedding_service=embedding_service,
                    vector_store=vector_store,
                )
                output = await use_case.execute(
                    GetSuggestedQuestionsInput(
                        user_id=user_id, count=max(1, count // 2)
                    )
                )
                for item in output.questions:
                    suggestions.append(
                        SuggestionItem(
                            id=item.id,
                            text=item.text,
                            type="question",
                            category=item.category,
                            relevance_score=0.9,
                            source=output.source,
                        )
                    )

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


@router.get("/questions", response_model=SuggestionsResponse)
async def get_suggested_questions(
    user_id: str = Depends(get_user_id),
    count: int = Query(default=3, ge=1, le=10),
):
    """Get suggested questions based on profile interests and embeddings."""
    question_repo = ServiceRegistry.get_suggested_question_repository()
    profile_repo = ServiceRegistry.get_student_profile_repository()
    embedding_service = ServiceRegistry.get_embedding()
    vector_store = ServiceRegistry.get_vector_store()
    if not all([question_repo, profile_repo, embedding_service, vector_store]):
        return SuggestionsResponse(
            suggestions=[], generated_at=datetime.now(timezone.utc)
        )

    use_case = GetSuggestedQuestionsUseCase(
        profile_repository=profile_repo,
        question_repository=question_repo,
        embedding_service=embedding_service,
        vector_store=vector_store,
    )
    output = await use_case.execute(
        GetSuggestedQuestionsInput(user_id=user_id, count=count)
    )
    items = [
        SuggestionItem(
            id=q.id,
            text=q.text,
            type="question",
            category=q.category,
            relevance_score=0.9 if output.source == "profile+embedding" else 0.6,
            source=output.source,
        )
        for q in output.questions
    ]
    return SuggestionsResponse(
        suggestions=items,
        generated_at=datetime.now(timezone.utc),
    )


@router.get("/related", response_model=SuggestionsResponse)
async def get_related_suggestions(
    query: str = Query(default=""),
    count: int = Query(default=5, ge=1, le=20),
):
    """Get related suggestions based on a query string."""
    normalized = query.strip().lower()
    if normalized:
        candidates = [
            q
            for q in COMMON_QUESTIONS
            if normalized in q["text"].lower() or normalized in q["category"].lower()
        ]
    else:
        candidates = []

    if not candidates:
        candidates = COMMON_QUESTIONS

    sample = random.sample(candidates, min(count, len(candidates)))
    suggestions = [
        SuggestionItem(
            id=f"related_{idx}",
            text=item["text"],
            type="question",
            category=item["category"],
            relevance_score=0.7,
            source="related",
        )
        for idx, item in enumerate(sample)
    ]
    return SuggestionsResponse(
        suggestions=suggestions,
        generated_at=datetime.now(timezone.utc),
    )


@router.get("/popular")
async def get_popular_topics(
    count: int = Query(default=5, ge=1, le=20),
):
    """Get popular topics from common questions."""
    category_counts = {}
    for item in COMMON_QUESTIONS:
        category = item["category"]
        category_counts[category] = category_counts.get(category, 0) + 1

    ranked = sorted(category_counts.items(), key=lambda item: item[1], reverse=True)
    return [{"topic": topic, "count": value} for topic, value in ranked[:count]]


@router.get("/categories")
async def get_topic_categories():
    """Get available suggestion categories."""
    categories = sorted({item["category"] for item in COMMON_QUESTIONS})
    return categories


__all__ = ["router", "COMMON_QUESTIONS"]
