"""Repository interfaces - Ports for data access."""

from .user_repository import IUserRepository
from .document_repository import IDocumentRepository
from .chat_repository import IChatRepository
from .file_repository import IFileRepository
from .crawler_repository import ICrawlerRepository

__all__ = [
    "IUserRepository",
    "IDocumentRepository",
    "IChatRepository",
    "IFileRepository",
    "ICrawlerRepository",
]
