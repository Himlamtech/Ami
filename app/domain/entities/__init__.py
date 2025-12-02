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

__all__ = [
    "Document",
    "Artifact",
    "ArtifactType",
    "ChatSession",
    "ChatMessage",
    "FileMetadata",
    "CrawlJob",
    "DataSource",
    "SourceAuth",
    "CrawlConfig",
    "PendingUpdate",
    "StudentProfile",
    "StudentLevel",
    "InteractionType",
    "InteractionHistory",
    "TopicInterest",
]
