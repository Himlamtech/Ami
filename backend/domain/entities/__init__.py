"""Domain entities."""

from .document import Document, Artifact, ArtifactType
from .chat_session import ChatSession
from .chat_message import ChatMessage
from .file_metadata import FileMetadata
from .crawl_job import CrawlJob
from .data_source import DataSource, SourceAuth, CrawlConfig
from .pending_update import PendingUpdate
from .student_profile import (
    StudentProfile,
    StudentLevel,
    InteractionType,
    InteractionHistory,
    TopicInterest,
)
from .suggested_question import SuggestedQuestion
from .feedback import (
    Feedback,
    FeedbackType,
    FeedbackCategory,
    FeedbackStatus,
)
from .usage_metric import (
    UsageMetric,
    LLMUsage,
    DailyUsageStats,
    RequestStatus,
    LLMProvider,
)
from .search_log import (
    SearchLog,
    SearchResult,
    KnowledgeGap,
    SearchResultQuality,
    GapStatus,
)
from .bookmark import Bookmark
from .tool_call import ToolCall, ToolArguments
from .orchestration_result import (
    OrchestrationResult,
    VectorSearchReference,
    OrchestrationMetrics,
)

__all__ = [
    # Documents
    "Document",
    "Artifact",
    "ArtifactType",
    # Chat
    "ChatSession",
    "ChatMessage",
    # Files
    "FileMetadata",
    # Crawling
    "CrawlJob",
    "DataSource",
    "SourceAuth",
    "CrawlConfig",
    "PendingUpdate",
    # Profile
    "StudentProfile",
    "StudentLevel",
    "InteractionType",
    "InteractionHistory",
    "TopicInterest",
    "SuggestedQuestion",
    # Feedback
    "Feedback",
    "FeedbackType",
    "FeedbackCategory",
    "FeedbackStatus",
    # Analytics
    "UsageMetric",
    "LLMUsage",
    "DailyUsageStats",
    "RequestStatus",
    "LLMProvider",
    # Search/Knowledge
    "SearchLog",
    "SearchResult",
    "KnowledgeGap",
    "SearchResultQuality",
    "GapStatus",
    # Bookmarks
    "Bookmark",
    # Orchestration
    "ToolCall",
    "ToolArguments",
    "OrchestrationResult",
    "VectorSearchReference",
    "OrchestrationMetrics",
]
