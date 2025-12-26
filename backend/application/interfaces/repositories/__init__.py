"""Repository interfaces - Ports for data access."""

from .document_repository import IDocumentRepository
from .chat_repository import IChatRepository
from .file_repository import IFileRepository
from .crawler_repository import ICrawlerRepository
from .data_source_repository import IDataSourceRepository
from .pending_update_repository import IPendingUpdateRepository
from .monitor_target_repository import IMonitorTargetRepository
from .student_profile_repository import IStudentProfileRepository
from .feedback_repository import IFeedbackRepository
from .usage_repository import (
    IUsageMetricRepository,
    ILLMUsageRepository,
    IDailyStatsRepository,
)
from .search_log_repository import (
    ISearchLogRepository,
    IKnowledgeGapRepository,
)
from .bookmark_repository import IBookmarkRepository

__all__ = [
    # Core
    "IDocumentRepository",
    "IChatRepository",
    "IFileRepository",
    # Crawling
    "ICrawlerRepository",
    "IDataSourceRepository",
    "IPendingUpdateRepository",
    "IMonitorTargetRepository",
    # Profile
    "IStudentProfileRepository",
    # Feedback
    "IFeedbackRepository",
    # Analytics
    "IUsageMetricRepository",
    "ILLMUsageRepository",
    "IDailyStatsRepository",
    # Knowledge
    "ISearchLogRepository",
    "IKnowledgeGapRepository",
    # Bookmarks
    "IBookmarkRepository",
]
