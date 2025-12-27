"""Use case: Extract long-term profile memory from chat."""

from dataclasses import dataclass, field
from typing import Optional, Dict, Any, List
import logging

from application.interfaces.repositories.student_profile_repository import (
    IStudentProfileRepository,
)
from application.interfaces.repositories.chat_repository import IChatRepository
from application.interfaces.services.llm_service import ILLMService
from application.services.conversation_context_service import (
    ConversationContextService,
)
from application.use_cases.personalization.profile_memory_helpers import (
    DEFAULT_MIN_CONFIDENCE,
    DEFAULT_MIN_INFERRED_CONFIDENCE,
    DEFAULT_OVERWRITE_CONFIDENCE,
    MAX_CONTEXT_MESSAGES,
    MAX_INTERESTS,
    MAX_TRAITS,
    MAX_SUMMARY_CHARS,
    build_profile_memory_prompt,
    parse_json,
    parse_value,
    normalize_text,
    normalize_detail_level,
    normalize_language,
    should_apply,
    validate_field,
)
from domain.entities.student_profile import StudentProfile
from domain.enums.llm_mode import LLMMode

logger = logging.getLogger(__name__)


@dataclass
class ProfileMemoryExtractionInput:
    """Input for profile memory extraction."""

    user_id: Optional[str]
    session_id: Optional[str]
    user_message: str
    assistant_message: str
    conversation_history: List[Dict[str, Any]] = field(default_factory=list)
    allow_inference: bool = True
    llm_mode: LLMMode = LLMMode.QA
    min_confidence: float = DEFAULT_MIN_CONFIDENCE
    min_inferred_confidence: float = DEFAULT_MIN_INFERRED_CONFIDENCE
    overwrite_confidence: float = DEFAULT_OVERWRITE_CONFIDENCE


@dataclass
class ProfileMemoryExtractionOutput:
    """Output from profile memory extraction."""

    profile: Optional[StudentProfile]
    extraction: Dict[str, Any]
    applied_updates: Dict[str, Any]


class ExtractProfileMemoryUseCase:
    """Extract profile memory with AI and update student profile."""

    def __init__(
        self,
        profile_repository: IStudentProfileRepository,
        llm_service: ILLMService,
        chat_repository: Optional[IChatRepository] = None,
    ):
        self.profile_repository = profile_repository
        self.llm_service = llm_service
        self.chat_repository = chat_repository
        self.context_service = (
            ConversationContextService(chat_repository) if chat_repository else None
        )

    async def execute(
        self, input_data: ProfileMemoryExtractionInput
    ) -> ProfileMemoryExtractionOutput:
        user_id = await self._resolve_user_id(input_data)
        if not user_id:
            logger.debug("Skip profile memory extraction: missing user_id")
            return ProfileMemoryExtractionOutput(
                profile=None, extraction={}, applied_updates={}
            )

        profile = await self.profile_repository.get_or_create(user_id)
        context_text = await self._build_context(input_data)
        prompt = build_profile_memory_prompt(
            profile=profile,
            allow_inference=input_data.allow_inference,
            context_text=context_text,
            user_message=input_data.user_message,
            assistant_message=input_data.assistant_message,
        )
        extraction = await self._extract_with_llm(prompt, input_data.llm_mode)

        applied_updates = self._apply_extraction(profile, extraction, input_data)
        if applied_updates:
            await self.profile_repository.update(profile)

        return ProfileMemoryExtractionOutput(
            profile=profile,
            extraction=extraction,
            applied_updates=applied_updates,
        )

    async def _resolve_user_id(
        self, input_data: ProfileMemoryExtractionInput
    ) -> Optional[str]:
        if input_data.user_id:
            return input_data.user_id
        if not (self.chat_repository and input_data.session_id):
            return None
        session = await self.chat_repository.get_session_by_id(input_data.session_id)
        return session.user_id if session else None

    async def _build_context(self, input_data: ProfileMemoryExtractionInput) -> str:
        if self.context_service and input_data.session_id:
            try:
                window = await self.context_service.build_context_window(
                    input_data.session_id,
                    max_messages=MAX_CONTEXT_MESSAGES,
                )
                return window.get_context_string()
            except Exception as exc:  # pragma: no cover - best effort
                logger.debug("Context window build failed: %s", exc)

        if not input_data.conversation_history:
            return ""

        lines = []
        for message in input_data.conversation_history[-MAX_CONTEXT_MESSAGES:]:
            role = (message.get("role") or "").lower()
            content = (message.get("content") or "").strip()
            if not content:
                continue
            role_label = "User" if role == "user" else "Assistant"
            lines.append(f"{role_label}: {content}")
        return "\n\n".join(lines)

    async def _extract_with_llm(self, prompt: str, mode: LLMMode) -> Dict[str, Any]:
        try:
            raw = await self.llm_service.generate(
                prompt=prompt,
                mode=mode,
                temperature=0.2,
                max_tokens=800,
            )
        except Exception as exc:
            logger.warning("LLM extraction failed: %s", exc)
            return {}

        parsed = parse_json(raw or "")
        if not parsed:
            logger.debug("LLM extraction returned invalid JSON")
        return parsed

    def _apply_extraction(
        self,
        profile: StudentProfile,
        extraction: Dict[str, Any],
        input_data: ProfileMemoryExtractionInput,
    ) -> Dict[str, Any]:
        updates: Dict[str, Any] = {}
        personal_info = extraction.get("personal_info", {}) or {}

        for field in (
            "name",
            "student_id",
            "class_name",
            "email",
            "phone",
            "gender",
            "date_of_birth",
            "address",
            "major",
            "faculty",
        ):
            value, confidence, inferred = parse_value(personal_info.get(field))
            value = normalize_text(value)
            if not self._should_apply(
                getattr(profile, field),
                value,
                confidence,
                inferred,
                input_data,
            ):
                continue
            if not validate_field(field, value):
                continue
            setattr(profile, field, value)
            updates[field] = value

        if "student_id" in updates and profile.year is None:
            progress = profile.get_academic_progress()
            if progress.get("current_year"):
                profile.year = progress["current_year"]
                updates["year"] = profile.year

        preferences = extraction.get("preferences", {}) or {}
        detail_value, detail_conf, detail_infer = parse_value(
            preferences.get("detail_level")
        )
        detail_value = normalize_detail_level(detail_value)
        if self._should_apply(
            profile.preferred_detail_level,
            detail_value,
            detail_conf,
            detail_infer,
            input_data,
        ):
            profile.preferred_detail_level = detail_value
            updates["preferred_detail_level"] = detail_value

        lang_value, lang_conf, lang_infer = parse_value(preferences.get("language"))
        lang_value = normalize_language(lang_value)
        if self._should_apply(
            profile.preferred_language,
            lang_value,
            lang_conf,
            lang_infer,
            input_data,
        ):
            profile.preferred_language = lang_value
            updates["preferred_language"] = lang_value

        interests = extraction.get("interests", []) or []
        applied_interests = self._apply_interests(profile, interests, input_data)
        if applied_interests:
            updates["interests"] = applied_interests

        personality = extraction.get("personality", {}) or {}
        self._apply_personality(profile, personality, input_data, updates)

        return updates

    def _apply_interests(
        self,
        profile: StudentProfile,
        interests: List[Dict[str, Any]],
        input_data: ProfileMemoryExtractionInput,
    ) -> List[str]:
        candidates = []
        for item in interests:
            if not isinstance(item, dict):
                continue
            topic = normalize_text(item.get("topic"))
            confidence = float(item.get("confidence", 0) or 0)
            inferred = bool(item.get("inferred", False))
            if not self._should_apply(None, topic, confidence, inferred, input_data):
                continue
            candidates.append(
                {
                    "topic": topic,
                    "confidence": confidence,
                    "category": item.get("category"),
                }
            )

        if not candidates:
            return []

        candidates.sort(key=lambda item: item["confidence"], reverse=True)
        chosen = candidates[:MAX_INTERESTS]
        applied = []
        batch_items = []
        for item in chosen:
            source = "memory"
            if item.get("category"):
                source = f"memory:{item['category']}"
            batch_items.append(
                {
                    "topic": item["topic"],
                    "metadata": {"source": source, "confidence": item["confidence"]},
                }
            )
            applied.append(item["topic"])
        profile.record_interest_batch(batch_items)
        return applied

    def _apply_personality(
        self,
        profile: StudentProfile,
        personality: Dict[str, Any],
        input_data: ProfileMemoryExtractionInput,
        updates: Dict[str, Any],
    ) -> None:
        summary_value, summary_conf, summary_infer = parse_value(
            personality.get("summary")
        )
        summary_value = normalize_text(summary_value)
        if self._should_apply(
            profile.personality_summary,
            summary_value,
            summary_conf,
            summary_infer,
            input_data,
        ):
            trimmed = summary_value[:MAX_SUMMARY_CHARS]
            profile.personality_summary = trimmed
            updates["personality_summary"] = trimmed

        traits = personality.get("traits", []) or []
        new_traits = []
        for trait in traits:
            value, conf, inferred = parse_value(trait)
            value = normalize_text(value)
            if not self._should_apply(None, value, conf, inferred, input_data):
                continue
            new_traits.append(value)

        if not new_traits:
            return

        existing = {t.lower(): t for t in profile.personality_traits}
        for trait in new_traits:
            if trait.lower() not in existing:
                existing[trait.lower()] = trait

        merged = list(existing.values())[:MAX_TRAITS]
        profile.personality_traits = merged
        updates["personality_traits"] = merged

    def _should_apply(
        self,
        current: Optional[str],
        value: Optional[str],
        confidence: float,
        inferred: bool,
        input_data: ProfileMemoryExtractionInput,
    ) -> bool:
        if inferred and not input_data.allow_inference:
            return False
        return should_apply(
            current,
            value,
            confidence,
            inferred,
            input_data.min_confidence,
            input_data.min_inferred_confidence,
            input_data.overwrite_confidence,
        )
