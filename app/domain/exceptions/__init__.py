"""Domain exceptions."""

from .document_exceptions import (
    DocumentNotFoundException,
    DocumentAlreadyExistsException,
    InvalidDocumentException,
    DocumentNotEmbeddedException,
)
from .chat_exceptions import (
    ChatSessionNotFoundException,
    ChatMessageNotFoundException,
    InvalidChatSessionException,
)

__all__ = [
    # Document exceptions
    "DocumentNotFoundException",
    "DocumentAlreadyExistsException",
    "InvalidDocumentException",
    "DocumentNotEmbeddedException",
    # Chat exceptions
    "ChatSessionNotFoundException",
    "ChatMessageNotFoundException",
    "InvalidChatSessionException",
]
