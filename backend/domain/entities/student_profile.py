"""Student profile entity for personalization."""

from dataclasses import dataclass, field
from datetime import datetime
from typing import List, Optional, Dict, Any
import re
from enum import Enum


class StudentLevel(Enum):
    """Student academic level."""

    FRESHMAN = "freshman"  # Năm 1
    SOPHOMORE = "sophomore"  # Năm 2
    JUNIOR = "junior"  # Năm 3
    SENIOR = "senior"  # Năm 4
    GRADUATE = "graduate"  # Cao học
    ALUMNI = "alumni"  # Cựu sinh viên


class InteractionType(Enum):
    """Type of interaction for learning."""

    QUESTION = "question"
    FILE_DOWNLOAD = "file_download"
    FEEDBACK = "feedback"
    SEARCH = "search"


@dataclass
class InteractionHistory:
    """Single interaction record."""

    interaction_type: InteractionType
    topic: str
    timestamp: datetime = field(default_factory=datetime.now)
    metadata: Dict[str, Any] = field(default_factory=dict)

    def to_dict(self) -> Dict[str, Any]:
        return {
            "type": self.interaction_type.value,
            "topic": self.topic,
            "timestamp": self.timestamp.isoformat(),
            "metadata": self.metadata,
        }


@dataclass
class TopicInterest:
    """Topic interest score."""

    topic: str
    score: float = 0.0  # 0.0 - 1.0
    interaction_count: int = 0
    last_accessed: Optional[datetime] = None
    source: str = "chat"

    def increment(self) -> None:
        """Increment interest score."""
        self.interaction_count += 1
        self.last_accessed = datetime.now()
        # Decay-based scoring
        self.score = min(1.0, self.score + 0.1)

    def decay(self, factor: float = 0.95) -> None:
        """Apply decay to interest score."""
        self.score *= factor


@dataclass
class StudentProfile:
    """
    Student profile for personalization.

    Tracks student's learning preferences, interests, and history
    to provide personalized responses.
    """

    # Identity
    id: str
    user_id: str  # Links to auth user

    # Student info
    student_id: Optional[str] = None  # MSV: B21DCCN123
    name: Optional[str] = None
    email: Optional[str] = None
    phone: Optional[str] = None
    gender: Optional[str] = None
    date_of_birth: Optional[str] = None
    address: Optional[str] = None
    level: StudentLevel = StudentLevel.FRESHMAN
    major: Optional[str] = None  # CNTT, ATTT, etc.
    class_name: Optional[str] = None  # D21CQCN01-N
    faculty: Optional[str] = None
    year: Optional[int] = None  # Derived from student_id if available

    # Learning preferences
    preferred_language: str = "vi"
    preferred_detail_level: str = "medium"  # brief, medium, detailed
    topics_of_interest: List[TopicInterest] = field(default_factory=list)
    interest_decay_factor: float = 0.95
    interest_min_score: float = 0.05
    interest_stale_days: int = 90
    personality_summary: Optional[str] = None
    personality_traits: List[str] = field(default_factory=list)

    # Interaction history (recent)
    interaction_history: List[InteractionHistory] = field(default_factory=list)
    max_history_items: int = 100

    # Statistics
    total_questions: int = 0
    total_downloads: int = 0
    total_sessions: int = 0

    # Timestamps
    created_at: datetime = field(default_factory=datetime.now)
    updated_at: datetime = field(default_factory=datetime.now)
    last_active_at: Optional[datetime] = None

    # Methods

    def record_interaction(
        self,
        interaction_type: InteractionType,
        topic: str,
        metadata: Optional[Dict[str, Any]] = None,
    ) -> None:
        """Record a new interaction."""
        self.apply_interest_decay()

        interaction = InteractionHistory(
            interaction_type=interaction_type,
            topic=topic,
            metadata=metadata or {},
        )

        self.interaction_history.append(interaction)

        # Trim history if needed
        if len(self.interaction_history) > self.max_history_items:
            self.interaction_history = self.interaction_history[
                -self.max_history_items :
            ]

        # Update topic interest
        source = (metadata or {}).get("source", "chat")
        self._update_topic_interest(topic, source)

        # Update stats
        if interaction_type == InteractionType.QUESTION:
            self.total_questions += 1
        elif interaction_type == InteractionType.FILE_DOWNLOAD:
            self.total_downloads += 1

        self.last_active_at = datetime.now()
        self.updated_at = datetime.now()

    def record_interest_batch(self, items: List[Dict[str, Any]]) -> None:
        """Record multiple interest updates with a single decay step."""
        if not items:
            return

        self.apply_interest_decay()

        for item in items:
            topic = item.get("topic")
            if not topic:
                continue
            metadata = item.get("metadata") or {}
            interaction = InteractionHistory(
                interaction_type=InteractionType.SEARCH,
                topic=topic,
                metadata=metadata,
            )
            self.interaction_history.append(interaction)
            if len(self.interaction_history) > self.max_history_items:
                self.interaction_history = self.interaction_history[
                    -self.max_history_items :
                ]
            source = metadata.get("source", "chat")
            self._update_topic_interest(topic, source)

        self.last_active_at = datetime.now()
        self.updated_at = datetime.now()

    def _update_topic_interest(self, topic: str, source: str = "chat") -> None:
        """Update topic interest score."""
        for ti in self.topics_of_interest:
            if ti.topic.lower() == topic.lower():
                ti.increment()
                ti.source = source or ti.source
                return

        # New topic
        self.topics_of_interest.append(
            TopicInterest(
                topic=topic,
                score=0.2,
                interaction_count=1,
                last_accessed=datetime.now(),
                source=source or "chat",
            )
        )

    def get_top_interests(self, n: int = 5) -> List[TopicInterest]:
        """Get top N topics of interest."""
        sorted_topics = sorted(
            self.topics_of_interest, key=lambda t: t.score, reverse=True
        )
        return sorted_topics[:n]

    def get_recent_topics(self, n: int = 5) -> List[str]:
        """Get recently accessed topics."""
        recent = [h.topic for h in self.interaction_history[-n:]]
        return list(dict.fromkeys(recent))  # Unique, preserving order

    def get_personalization_context(self) -> Dict[str, Any]:
        """Get context for personalized responses."""
        return {
            "level": self.level.value,
            "major": self.major,
            "preferred_detail": self.preferred_detail_level,
            "top_interests": [t.topic for t in self.get_top_interests(3)],
            "recent_topics": self.get_recent_topics(3),
        }

    def apply_interest_decay(self) -> None:
        """Apply decay to all interest scores (call periodically)."""
        now = datetime.now()
        for ti in self.topics_of_interest:
            if ti.last_accessed:
                days = (now - ti.last_accessed).days
                if days > 0:
                    ti.decay(self.interest_decay_factor**days)

        # Remove very low scores
        self.topics_of_interest = [
            ti
            for ti in self.topics_of_interest
            if ti.score >= self.interest_min_score
            and (
                not ti.last_accessed
                or (now - ti.last_accessed).days < self.interest_stale_days
            )
        ]

    def get_academic_progress(self) -> Dict[str, Optional[int]]:
        """Derive academic year/semester from student_id."""
        intake_year = self._parse_intake_year(self.student_id)
        if not intake_year:
            return {"intake_year": None, "current_year": None, "current_semester": None}

        now = datetime.now()
        current_year = max(1, now.year - intake_year + 1)
        current_year = min(current_year, 5)

        # Semester heuristic: Aug-Dec -> semester 1, Jan-Jul -> semester 2
        semester_in_year = 1 if now.month >= 8 else 2
        current_semester = min((current_year - 1) * 2 + semester_in_year, 9)

        return {
            "intake_year": intake_year,
            "current_year": current_year,
            "current_semester": current_semester,
        }

    @staticmethod
    def _parse_intake_year(student_id: Optional[str]) -> Optional[int]:
        """Parse intake year from student_id like B22DCVT303 -> 2022."""
        if not student_id:
            return None
        match = re.match(r"^[A-Za-z](\d{2})", student_id.strip())
        if not match:
            return None
        return 2000 + int(match.group(1))

    def to_prompt_context(self) -> str:
        """Generate context string for LLM prompts."""
        parts = []

        if self.level:
            level_vi = {
                StudentLevel.FRESHMAN: "sinh viên năm 1",
                StudentLevel.SOPHOMORE: "sinh viên năm 2",
                StudentLevel.JUNIOR: "sinh viên năm 3",
                StudentLevel.SENIOR: "sinh viên năm 4",
                StudentLevel.GRADUATE: "học viên cao học",
                StudentLevel.ALUMNI: "cựu sinh viên",
            }
            parts.append(f"Đang là {level_vi.get(self.level, 'sinh viên')}")

        if self.major:
            parts.append(f"ngành {self.major}")

        interests = [t.topic for t in self.get_top_interests(3)]
        if interests:
            parts.append(f"quan tâm đến: {', '.join(interests)}")

        if self.personality_summary:
            parts.append(f"tính cách: {self.personality_summary}")
        elif self.personality_traits:
            parts.append(f"tính cách: {', '.join(self.personality_traits[:3])}")

        return "; ".join(parts) if parts else ""

    def __repr__(self) -> str:
        return f"StudentProfile(id={self.id}, student_id={self.student_id}, level={self.level.value})"
