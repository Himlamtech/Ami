"""Domain exceptions."""

from .user_exceptions import (
    UserNotFoundException,
    UserAlreadyExistsException,
    InvalidCredentialsException,
    UserNotActiveException,
    InsufficientPermissionsException,
)
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
    # User exceptions
    "UserNotFoundException",
    "UserAlreadyExistsException",
    "InvalidCredentialsException",
    "UserNotActiveException",
    "InsufficientPermissionsException",
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
