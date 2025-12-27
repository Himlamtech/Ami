"""Personalization service for adapting responses to user."""

from typing import Dict, Any, Optional, List
from dataclasses import dataclass

from domain.entities.student_profile import (
    StudentProfile,
    StudentLevel,
    InteractionType,
)
from application.interfaces.repositories.student_profile_repository import (
    IStudentProfileRepository,
)


@dataclass
class PersonalizedContext:
    """Context for personalized responses."""

    user_greeting: str
    detail_level: str
    topic_hints: List[str]
    prompt_additions: str
    suggested_topics: List[str]


class PersonalizationService:
    """
    Service for personalizing responses based on student profile.

    Adapts responses to student's level, interests, and preferences.
    """

    def __init__(self, profile_repository: IStudentProfileRepository):
        self.profile_repository = profile_repository

    async def get_or_create_profile(self, user_id: str) -> StudentProfile:
        """Get or create student profile."""
        return await self.profile_repository.get_or_create(user_id)

    async def record_question(
        self,
        user_id: str,
        question: str,
        topic: str,
        metadata: Optional[Dict[str, Any]] = None,
    ) -> None:
        """Record a question interaction."""
        profile = await self.get_or_create_profile(user_id)
        profile.record_interaction(
            interaction_type=InteractionType.QUESTION,
            topic=topic,
            metadata=metadata,
        )
        await self.profile_repository.update(profile)

    async def record_download(
        self,
        user_id: str,
        document_name: str,
        topic: str,
    ) -> None:
        """Record a file download interaction."""
        profile = await self.get_or_create_profile(user_id)
        profile.record_interaction(
            interaction_type=InteractionType.FILE_DOWNLOAD,
            topic=topic,
            metadata={"document": document_name},
        )
        await self.profile_repository.update(profile)

    async def get_personalized_context(self, user_id: str) -> PersonalizedContext:
        """Get personalized context for response generation."""
        profile = await self.get_or_create_profile(user_id)
        profile.apply_interest_decay()
        await self.profile_repository.update(profile)

        # Build greeting
        greeting = self._build_greeting(profile)

        # Determine detail level
        detail_level = profile.preferred_detail_level

        # Get topic hints
        topic_hints = [t.topic for t in profile.get_top_interests(5)]

        # Build prompt additions
        prompt_additions = self._build_prompt_additions(profile)

        # Suggest related topics
        suggested = self._suggest_related_topics(profile)

        return PersonalizedContext(
            user_greeting=greeting,
            detail_level=detail_level,
            topic_hints=topic_hints,
            prompt_additions=prompt_additions,
            suggested_topics=suggested,
        )

    def _build_greeting(self, profile: StudentProfile) -> str:
        """Build personalized greeting."""
        if profile.name:
            return f"Chào {profile.name}"
        return "Chào bạn"

    def _build_prompt_additions(self, profile: StudentProfile) -> str:
        """Build additions to LLM prompt based on profile."""
        parts = []

        # Level-based instructions
        level_instructions = {
            StudentLevel.FRESHMAN: "Giải thích chi tiết các khái niệm cơ bản, sử dụng ngôn ngữ đơn giản.",
            StudentLevel.SOPHOMORE: "Giải thích rõ ràng, có thể dùng một số thuật ngữ chuyên ngành.",
            StudentLevel.JUNIOR: "Trả lời chuyên sâu, sử dụng thuật ngữ chuyên ngành.",
            StudentLevel.SENIOR: "Trả lời ngắn gọn, chuyên sâu, tập trung vào thực hành.",
            StudentLevel.GRADUATE: "Trả lời học thuật, chuyên sâu, có thể đề cập nghiên cứu.",
            StudentLevel.ALUMNI: "Trả lời thực tiễn, hướng nghề nghiệp.",
        }

        if profile.level in level_instructions:
            parts.append(level_instructions[profile.level])

        # Detail level
        detail_instructions = {
            "brief": "Trả lời ngắn gọn, đi thẳng vào vấn đề.",
            "medium": "Trả lời đầy đủ nhưng súc tích.",
            "detailed": "Trả lời chi tiết, có ví dụ minh họa.",
        }

        if profile.preferred_detail_level in detail_instructions:
            parts.append(detail_instructions[profile.preferred_detail_level])

        # Major context
        if profile.major:
            parts.append(f"Sinh viên ngành {profile.major}.")

        if profile.personality_summary:
            parts.append(f"Tính cách: {profile.personality_summary}.")
        elif profile.personality_traits:
            traits = ", ".join(profile.personality_traits[:3])
            parts.append(f"Tính cách: {traits}.")

        return " ".join(parts)

    def _suggest_related_topics(self, profile: StudentProfile) -> List[str]:
        """Suggest related topics based on interests."""
        top_interests = [t.topic for t in profile.get_top_interests(3)]

        # Topic relationships (simple mapping)
        related_topics = {
            "đăng ký học": ["lịch học", "học phí", "thời khóa biểu"],
            "học phí": ["học bổng", "miễn giảm", "thanh toán"],
            "thủ tục": ["mẫu đơn", "phòng đào tạo", "giấy tờ"],
            "mẫu đơn": ["thủ tục", "phòng đào tạo"],
            "điểm": ["học bổng", "cảnh báo học vụ", "bảng điểm"],
            "tốt nghiệp": ["bằng", "đồ án", "thực tập"],
        }

        suggestions = set()
        for topic in top_interests:
            topic_lower = topic.lower()
            for key, related in related_topics.items():
                if key in topic_lower:
                    suggestions.update(related)

        return list(suggestions)[:5]

    async def update_profile_info(
        self,
        user_id: str,
        student_id: Optional[str] = None,
        name: Optional[str] = None,
        email: Optional[str] = None,
        phone: Optional[str] = None,
        gender: Optional[str] = None,
        date_of_birth: Optional[str] = None,
        address: Optional[str] = None,
        major: Optional[str] = None,
        faculty: Optional[str] = None,
        year: Optional[int] = None,
        level: Optional[StudentLevel] = None,
        class_name: Optional[str] = None,
    ) -> StudentProfile:
        """Update student profile information."""
        profile = await self.get_or_create_profile(user_id)

        if student_id is not None:
            profile.student_id = student_id
        if name is not None:
            profile.name = name
        if email is not None:
            profile.email = email
        if phone is not None:
            profile.phone = phone
        if gender is not None:
            profile.gender = gender
        if date_of_birth is not None:
            profile.date_of_birth = date_of_birth
        if address is not None:
            profile.address = address
        if major is not None:
            profile.major = major
        if faculty is not None:
            profile.faculty = faculty
        if year is not None:
            profile.year = year
        if level is not None:
            profile.level = level
        if class_name is not None:
            profile.class_name = class_name

        if profile.year is None:
            progress = profile.get_academic_progress()
            if progress.get("current_year"):
                profile.year = progress["current_year"]

        return await self.profile_repository.update(profile)

    async def set_preferences(
        self,
        user_id: str,
        detail_level: Optional[str] = None,
        language: Optional[str] = None,
    ) -> StudentProfile:
        """Set user preferences."""
        profile = await self.get_or_create_profile(user_id)

        if detail_level and detail_level in ["brief", "medium", "detailed"]:
            profile.preferred_detail_level = detail_level
        if language:
            profile.preferred_language = language

        return await self.profile_repository.update(profile)
