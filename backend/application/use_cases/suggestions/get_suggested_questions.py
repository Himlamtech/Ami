"""Use case: Get suggested questions for a student."""

from dataclasses import dataclass
from typing import List, Optional

from app.application.interfaces.repositories.student_profile_repository import (
    IStudentProfileRepository,
)
from app.application.interfaces.repositories.suggested_question_repository import (
    ISuggestedQuestionRepository,
)
from app.application.interfaces.services.embedding_service import IEmbeddingService
from app.application.interfaces.services.vector_store_service import IVectorStoreService
from app.domain.entities.suggested_question import SuggestedQuestion


QUESTION_COLLECTION = "suggested_questions"


@dataclass
class GetSuggestedQuestionsInput:
    user_id: str
    count: int = 3


@dataclass
class GetSuggestedQuestionsOutput:
    questions: List[SuggestedQuestion]
    source: str


class GetSuggestedQuestionsUseCase:
    """Return top suggested questions based on profile interests."""

    def __init__(
        self,
        profile_repository: IStudentProfileRepository,
        question_repository: ISuggestedQuestionRepository,
        embedding_service: IEmbeddingService,
        vector_store: IVectorStoreService,
    ):
        self.profile_repository = profile_repository
        self.question_repository = question_repository
        self.embedding_service = embedding_service
        self.vector_store = vector_store

    async def execute(
        self, input_data: GetSuggestedQuestionsInput
    ) -> GetSuggestedQuestionsOutput:
        count = max(1, input_data.count)
        profile = await self.profile_repository.get_by_user_id(input_data.user_id)
        query_text = self._build_profile_query(profile)

        if not query_text:
            questions = await self._fallback_questions(count)
            return GetSuggestedQuestionsOutput(questions=questions, source="fallback")

        try:
            query_embedding = await self.embedding_service.embed_text(query_text)
            results = await self.vector_store.search(
                query_embedding=query_embedding,
                top_k=max(10, count),
                collection=QUESTION_COLLECTION,
            )
        except Exception:
            questions = await self._fallback_questions(count)
            return GetSuggestedQuestionsOutput(questions=questions, source="fallback")

        question_ids = []
        for item in results:
            question_id = (item.get("metadata") or {}).get("question_id")
            if question_id:
                question_ids.append(str(question_id))

        question_ids = self._dedupe_ids(question_ids)
        if not question_ids:
            questions = await self._fallback_questions(count)
            return GetSuggestedQuestionsOutput(questions=questions, source="fallback")

        questions = await self.question_repository.get_by_ids(question_ids)
        ordered = self._order_questions(question_ids, questions)
        active = [q for q in ordered if q.is_active][:count]
        if not active:
            questions = await self._fallback_questions(count)
            return GetSuggestedQuestionsOutput(questions=questions, source="fallback")

        return GetSuggestedQuestionsOutput(
            questions=active,
            source="profile+embedding",
        )

    def _build_profile_query(self, profile) -> str:
        if not profile:
            return ""
        parts: List[str] = []
        if profile.major:
            parts.append(f"ngành {profile.major}")
        if profile.year:
            parts.append(f"năm {profile.year}")
        if profile.faculty:
            parts.append(f"khoa {profile.faculty}")
        interests = [t.topic for t in profile.get_top_interests(3)]
        if interests:
            parts.append(f"sở thích: {', '.join(interests)}")
        return ". ".join(parts)

    async def _fallback_questions(self, count: int) -> List[SuggestedQuestion]:
        return await self.question_repository.list_active(limit=count)

    @staticmethod
    def _dedupe_ids(question_ids: List[str]) -> List[str]:
        seen = set()
        deduped: List[str] = []
        for qid in question_ids:
            if qid in seen:
                continue
            seen.add(qid)
            deduped.append(qid)
        return deduped

    @staticmethod
    def _order_questions(
        question_ids: List[str], questions: List[SuggestedQuestion]
    ) -> List[SuggestedQuestion]:
        lookup = {q.id: q for q in questions}
        ordered = [lookup[qid] for qid in question_ids if qid in lookup]
        if ordered:
            return ordered
        return questions
