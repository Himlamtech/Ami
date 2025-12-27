"""Helpers for profile memory extraction."""

from typing import Optional, Any, Dict
import json
import re

from domain.entities.student_profile import StudentProfile

DEFAULT_MIN_CONFIDENCE = 0.7
DEFAULT_MIN_INFERRED_CONFIDENCE = 0.8
DEFAULT_OVERWRITE_CONFIDENCE = 0.85
MAX_CONTEXT_MESSAGES = 6
MAX_INTERESTS = 5
MAX_TRAITS = 6
MAX_SUMMARY_CHARS = 240

FIELD_TEMPLATE = {
    "value": "...",
    "confidence": 0.0,
    "evidence": "...",
    "inferred": False,
}
INTEREST_TEMPLATE = {
    "topic": "...",
    "confidence": 0.0,
    "evidence": "...",
    "category": "personal|academic|hobby|other",
    "inferred": False,
}
TRAIT_TEMPLATE = {
    "value": "...",
    "confidence": 0.0,
    "evidence": "...",
    "inferred": False,
}
PROMPT_SCHEMA = {
    "personal_info": {
        "name": FIELD_TEMPLATE,
        "student_id": FIELD_TEMPLATE,
        "class_name": FIELD_TEMPLATE,
        "email": FIELD_TEMPLATE,
        "phone": FIELD_TEMPLATE,
        "gender": FIELD_TEMPLATE,
        "date_of_birth": FIELD_TEMPLATE,
        "address": FIELD_TEMPLATE,
        "major": FIELD_TEMPLATE,
        "faculty": FIELD_TEMPLATE,
    },
    "preferences": {
        "detail_level": FIELD_TEMPLATE,
        "language": FIELD_TEMPLATE,
    },
    "interests": [INTEREST_TEMPLATE],
    "personality": {
        "summary": FIELD_TEMPLATE,
        "traits": [TRAIT_TEMPLATE],
    },
}


def build_profile_memory_prompt(
    profile: StudentProfile,
    allow_inference: bool,
    context_text: str,
    user_message: str,
    assistant_message: str,
) -> str:
    snapshot = build_profile_snapshot(profile)
    schema_json = json.dumps(PROMPT_SCHEMA, ensure_ascii=False)
    allow_text = "có" if allow_inference else "không"

    return (
        "Bạn là hệ thống trích xuất hồ sơ sinh viên từ hội thoại với AMI.\n"
        "Yêu cầu:\n"
        "- Chỉ trả về JSON hợp lệ.\n"
        "- Nếu không chắc chắn thì để null hoặc [] (không đoán bừa).\n"
        "- Cho phép suy đoán ngữ cảnh: "
        f"{allow_text} (chỉ khi rất chắc chắn).\n"
        "- Interests chỉ ghi nhận sở thích/hứng thú dài hạn; tránh chủ đề hành chính "
        "thoáng qua (học phí, thủ tục) trừ khi người dùng nói rõ đó là mối quan tâm lâu dài.\n"
        "- Mỗi mục đều có confidence 0-1 và inferred true/false.\n\n"
        f"Schema JSON:\n{schema_json}\n\n"
        f"Hồ sơ hiện tại: {snapshot}\n"
        f"Ngữ cảnh gần đây:\n{context_text}\n\n"
        "Lượt mới nhất:\n"
        f"User: {user_message}\n"
        f"Assistant: {assistant_message}\n"
        "JSON:"
    )


def build_profile_snapshot(profile: StudentProfile) -> str:
    snapshot = {
        "student_id": profile.student_id,
        "name": profile.name,
        "email": profile.email,
        "phone": profile.phone,
        "gender": profile.gender,
        "date_of_birth": profile.date_of_birth,
        "address": profile.address,
        "major": profile.major,
        "class_name": profile.class_name,
        "faculty": profile.faculty,
        "year": profile.year,
        "preferred_language": profile.preferred_language,
        "preferred_detail_level": profile.preferred_detail_level,
        "personality_summary": profile.personality_summary,
        "personality_traits": profile.personality_traits[:MAX_TRAITS],
        "top_interests": [t.topic for t in profile.get_top_interests(5)],
    }
    return json.dumps(snapshot, ensure_ascii=False)


def parse_json(raw: str) -> Dict[str, Any]:
    try:
        return json.loads(raw)
    except Exception:
        match = re.search(r"\{.*\}", raw, re.DOTALL)
        if match:
            try:
                return json.loads(match.group(0))
            except Exception:
                return {}
    return {}


def parse_value(value: Any) -> tuple[Optional[str], float, bool]:
    if isinstance(value, dict):
        raw = value.get("value")
        confidence = float(value.get("confidence", 0) or 0)
        inferred = bool(value.get("inferred", False))
        return raw, confidence, inferred
    if value is None:
        return None, 0.0, False
    return str(value), 0.5, True


def normalize_text(value: Optional[str]) -> Optional[str]:
    if not value:
        return None
    return " ".join(str(value).strip().split())


def should_apply(
    current: Optional[str],
    value: Optional[str],
    confidence: float,
    inferred: bool,
    min_confidence: float,
    min_inferred_confidence: float,
    overwrite_confidence: float,
) -> bool:
    if not value:
        return False
    min_conf = min_inferred_confidence if inferred else min_confidence
    if confidence < min_conf:
        return False
    if current and current != value:
        return confidence >= overwrite_confidence
    return True


def normalize_detail_level(value: Optional[str]) -> Optional[str]:
    if not value:
        return None
    value = value.strip().lower()
    mapping = {
        "brief": "brief",
        "ngắn gọn": "brief",
        "ngan gon": "brief",
        "short": "brief",
        "medium": "medium",
        "vừa đủ": "medium",
        "vua du": "medium",
        "detailed": "detailed",
        "chi tiết": "detailed",
        "chi tiet": "detailed",
    }
    return mapping.get(value)


def normalize_language(value: Optional[str]) -> Optional[str]:
    if not value:
        return None
    value = value.strip().lower()
    if value in ("vi", "vi-vn", "vietnamese", "viet", "việt"):
        return "vi"
    if value in ("en", "english"):
        return "en"
    return None


def validate_field(field: str, value: Optional[str]) -> bool:
    if value is None:
        return False
    if field == "student_id":
        return bool(re.match(r"^[A-Za-z]\d{2}[A-Z]{4}\d{3}$", value))
    if field == "email":
        return bool(re.match(r"^[\\w.-]+@[\\w.-]+\\.\\w+$", value))
    if field == "phone":
        return bool(re.match(r"^0\\d{9,10}$", value))
    if field == "gender":
        value_lower = value.lower()
        if value_lower in ("nam", "male", "m"):
            return True
        if value_lower in ("nữ", "nu", "female", "f"):
            return True
        if value_lower in ("khác", "khac", "other"):
            return True
        return False
    return True
