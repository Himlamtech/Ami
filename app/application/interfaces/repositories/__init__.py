"""Repository interfaces - Ports for data access."""

from .document_repository import IDocumentRepository
from .chat_repository import IChatRepository
from .file_repository import IFileRepository
from .crawler_repository import ICrawlerRepository
from .data_source_repository import IDataSourceRepository
from .pending_update_repository import IPendingUpdateRepository
from .student_profile_repository import IStudentProfileRepository

__all__ = [
    "IDocumentRepository",
    "IChatRepository",
    "IFileRepository",
    "ICrawlerRepository",
    "IDataSourceRepository",
    "IPendingUpdateRepository",
    "IStudentProfileRepository",
]
