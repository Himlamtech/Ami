"""Chat message role enumeration."""

from enum import Enum


class ChatMessageRole(str, Enum):
    """Message role in conversation."""

    SYSTEM = "system"
    USER = "user"
    ASSISTANT = "assistant"
