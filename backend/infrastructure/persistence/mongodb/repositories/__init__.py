"""MongoDB repository implementations."""

from .mongodb_document_repository import MongoDBDocumentRepository
from .mongodb_chat_repository import MongoDBChatRepository
from .mongodb_file_repository import MongoDBFileRepository
from .mongodb_crawler_repository import MongoDBCrawlerRepository
from .mongodb_data_source_repository import MongoDBDataSourceRepository
from .mongodb_pending_update_repository import MongoDBPendingUpdateRepository
from .mongodb_monitor_target_repository import MongoDBMonitorTargetRepository
from .mongodb_student_profile_repository import MongoDBStudentProfileRepository
from .mongodb_suggested_question_repository import MongoDBSuggestedQuestionRepository
from .mongodb_feedback_repository import MongoDBFeedbackRepository
from .mongodb_usage_repository import (
    MongoDBUsageMetricRepository,
    MongoDBLLMUsageRepository,
    MongoDBDailyStatsRepository,
)
from .mongodb_search_log_repository import (
    MongoDBSearchLogRepository,
    MongoDBKnowledgeGapRepository,
)
from .mongodb_bookmark_repository import MongoDBBookmarkRepository
from .mongodb_orchestration_log_repository import MongoDBOrchestrationLogRepository

__all__ = [
    # Core
    "MongoDBDocumentRepository",
    "MongoDBChatRepository",
    "MongoDBFileRepository",
    # Crawling
    "MongoDBCrawlerRepository",
    "MongoDBDataSourceRepository",
    "MongoDBPendingUpdateRepository",
    "MongoDBMonitorTargetRepository",
    # Profile
    "MongoDBStudentProfileRepository",
    "MongoDBSuggestedQuestionRepository",
    # Feedback
    "MongoDBFeedbackRepository",
    # Analytics
    "MongoDBUsageMetricRepository",
    "MongoDBLLMUsageRepository",
    "MongoDBDailyStatsRepository",
    # Knowledge
    "MongoDBSearchLogRepository",
    "MongoDBKnowledgeGapRepository",
    # Bookmarks
    "MongoDBBookmarkRepository",
    # Orchestration
    "MongoDBOrchestrationLogRepository",
]
