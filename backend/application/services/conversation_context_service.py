"""Conversation context service for memory management."""

from dataclasses import dataclass
from typing import List, Dict, Any, Optional
import re
import logging

from app.domain.entities.chat_session import ChatSession
from app.domain.entities.chat_message import ChatMessage, MessageIntent, EntityMention
from app.application.interfaces.repositories.chat_repository import IChatRepository
from app.application.interfaces.services.llm_service import ILLMService

logger = logging.getLogger(__name__)


# Vietnamese entity patterns
ENTITY_PATTERNS = {
    "student_id": r"\b[BDA]\d{2}[A-Z]{4}\d{3}\b",  # B21DCCN123
    "course_code": r"\b[A-Z]{2,4}\d{3,4}\b",  # INT1234
    "phone": r"\b0\d{9,10}\b",
    "email": r"\b[\w.-]+@[\w.-]+\.\w+\b",
    "date": r"\b\d{1,2}/\d{1,2}/\d{4}\b",
}

# Intent detection keywords (Vietnamese)
INTENT_KEYWORDS = {
    MessageIntent.FILE_REQUEST: [
        "mẫu đơn",
        "tải file",
        "download",
        "xin mẫu",
        "cho mẫu",
        "file",
        "form",
    ],
    MessageIntent.CLARIFICATION: [
        "nghĩa là gì",
        "có nghĩa là",
        "giải thích",
        "nói rõ hơn",
        "ý bạn là",
    ],
    MessageIntent.FEEDBACK: [
        "cảm ơn",
        "thanks",
        "ok",
        "được rồi",
        "hiểu rồi",
        "tốt lắm",
    ],
    MessageIntent.GREETING: ["xin chào", "chào bạn", "hello", "hi ", "hey"],
    MessageIntent.GOODBYE: ["tạm biệt", "bye", "goodbye", "hẹn gặp lại"],
}


@dataclass
class ContextWindow:
    """Sliding window of recent messages for context."""

    messages: List[ChatMessage]
    max_tokens: int = 2000
    max_messages: int = 10

    def get_context_string(self) -> str:
        """Build context string from messages."""
        parts = []
        for msg in self.messages[-self.max_messages :]:
            role = "User" if msg.is_from_user() else "Assistant"
            parts.append(f"{role}: {msg.content}")
        return "\n\n".join(parts)

    def get_recent_entities(self) -> Dict[str, Any]:
        """Extract entities from recent messages."""
        entities = {}
        for msg in self.messages:
            for entity in msg.entity_mentions:
                entities[entity.entity_type] = entity.value
        return entities


class ConversationContextService:
    """
    Service for managing conversation context and memory.

    Responsibilities:
    1. Build context window from recent messages
    2. Detect user intent
    3. Extract entities from messages
    4. Generate session summaries
    5. Track conversation topics
    """

    def __init__(
        self,
        chat_repository: IChatRepository,
        llm_service: Optional[ILLMService] = None,
    ):
        self.chat_repo = chat_repository
        self.llm_service = llm_service

    async def build_context_window(
        self,
        session_id: str,
        max_messages: int = 10,
    ) -> ContextWindow:
        """
        Build context window from recent messages.

        Args:
            session_id: Chat session ID
            max_messages: Maximum messages to include

        Returns:
            ContextWindow with recent messages
        """
        messages = await self.chat_repo.get_recent_messages(
            session_id=session_id,
            limit=max_messages,
        )

        # Convert to domain entities if needed
        chat_messages = []
        for msg_dict in messages:
            if isinstance(msg_dict, ChatMessage):
                chat_messages.append(msg_dict)
            else:
                # Assume dict format
                chat_messages.append(self._dict_to_message(msg_dict))

        return ContextWindow(messages=chat_messages, max_messages=max_messages)

    def detect_intent(self, message: str) -> MessageIntent:
        """
        Detect user intent from message content.

        Args:
            message: User message text

        Returns:
            Detected MessageIntent
        """
        message_lower = message.lower()

        # Check intent keywords
        for intent, keywords in INTENT_KEYWORDS.items():
            for keyword in keywords:
                if keyword in message_lower:
                    return intent

        # Default to question if has question mark
        if "?" in message:
            return MessageIntent.QUESTION

        return MessageIntent.OTHER

    def extract_entities(self, message: str) -> List[EntityMention]:
        """
        Extract entities from message using patterns.

        Args:
            message: Message text

        Returns:
            List of extracted EntityMention
        """
        entities = []

        for entity_type, pattern in ENTITY_PATTERNS.items():
            matches = re.finditer(pattern, message, re.IGNORECASE)
            for match in matches:
                entities.append(
                    EntityMention(
                        entity_type=entity_type,
                        value=match.group(),
                        start_pos=match.start(),
                        end_pos=match.end(),
                    )
                )

        return entities

    async def generate_session_summary(
        self,
        session: ChatSession,
        messages: List[ChatMessage],
    ) -> str:
        """
        Generate summary of conversation.

        Args:
            session: Chat session
            messages: Messages to summarize

        Returns:
            Summary string
        """
        if not self.llm_service:
            # Fallback to simple summary
            return self._simple_summary(messages)

        # Build prompt for LLM
        messages_text = "\n".join(
            [
                f"{'User' if m.is_from_user() else 'Assistant'}: {m.content}"
                for m in messages[-20:]  # Last 20 messages
            ]
        )

        prompt = f"""Tóm tắt ngắn gọn cuộc hội thoại sau bằng tiếng Việt (tối đa 3 câu):

{messages_text}

Tóm tắt:"""

        try:
            summary = await self.llm_service.generate(
                prompt=prompt,
                max_tokens=150,
                temperature=0.3,
            )
            return summary.strip()
        except Exception as e:
            logger.error(f"Summary generation failed: {e}")
            return self._simple_summary(messages)

    def _simple_summary(self, messages: List[ChatMessage]) -> str:
        """Generate simple rule-based summary."""
        user_messages = [m for m in messages if m.is_from_user()]
        if not user_messages:
            return "Cuộc hội thoại trống"

        # Extract main topics from user questions
        topics = []
        for msg in user_messages[:5]:  # First 5 user messages
            # Simple: take first 50 chars of each question
            preview = msg.content[:50].strip()
            if preview:
                topics.append(preview)

        if topics:
            return f"Các câu hỏi chính: {'; '.join(topics)}"
        return f"Cuộc hội thoại với {len(messages)} tin nhắn"

    async def update_session_context(
        self,
        session: ChatSession,
        message: ChatMessage,
    ) -> None:
        """
        Update session context after new message.

        Args:
            session: Chat session to update
            message: New message
        """
        # Detect and set intent
        if message.is_from_user():
            intent = self.detect_intent(message.content)
            message.set_intent(intent)
            session.context.last_intent = intent.value

        # Extract entities
        entities = self.extract_entities(message.content)
        for entity in entities:
            message.add_entity(entity)
            session.add_context_entity(entity.entity_type, entity.value)

        # Update topics (simple extraction - keywords from questions)
        if message.is_from_user() and "?" in message.content:
            # Extract key words as topics
            words = message.content.replace("?", "").split()
            key_words = [w for w in words if len(w) > 3][:3]
            for word in key_words:
                session.add_topic(word)

    def build_context_prompt(
        self,
        session: ChatSession,
        context_window: ContextWindow,
        current_query: str,
    ) -> str:
        """
        Build context-aware prompt for LLM.

        Args:
            session: Chat session with context
            context_window: Recent messages
            current_query: Current user query

        Returns:
            Context-enhanced prompt
        """
        parts = []

        # Add session context
        session_context = session.get_context_for_llm()
        if session_context:
            parts.append(f"[Conversation Context]\n{session_context}\n")

        # Add recent conversation
        recent = context_window.get_context_string()
        if recent:
            parts.append(f"[Recent Conversation]\n{recent}\n")

        # Add current query
        parts.append(f"[Current Question]\n{current_query}")

        return "\n".join(parts)

    def _dict_to_message(self, msg_dict: Dict[str, Any]) -> ChatMessage:
        """Convert dict to ChatMessage."""
        from app.domain.enums.chat_message_role import ChatMessageRole
        from datetime import datetime

        role_str = msg_dict.get("role", "user")
        role = ChatMessageRole(role_str) if isinstance(role_str, str) else role_str

        created_at = msg_dict.get("created_at")
        if created_at is None:
            created_at = datetime.now()

        return ChatMessage(
            id=msg_dict.get("id", ""),
            session_id=msg_dict.get("session_id", ""),
            role=role,
            content=msg_dict.get("content", ""),
            created_at=created_at,
        )
