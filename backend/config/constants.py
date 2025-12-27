"""
Business constants - Application-wide business rules and constants.

These are domain constants that should not change frequently and represent
business rules, limits, and thresholds.
"""

from pydantic import Field, BaseModel


class PaginationConstants(BaseModel):
    """Pagination and limit defaults."""

    # Default pagination limits
    default_page_size: int = Field(
        default=50, ge=1, le=1000, description="Default page size for list operations"
    )
    max_page_size: int = Field(
        default=1000, ge=1, description="Maximum allowed page size"
    )
    bookmark_default_limit: int = Field(default=50, ge=1, le=500)
    message_default_limit: int = Field(default=100, ge=1, le=500)
    chat_history_max_items: int = Field(default=100, ge=10)


class CrawlerConstants(BaseModel):
    """Web crawler and data source constants."""

    # Crawling limits
    crawler_default_max_depth: int = Field(default=2, ge=1, le=10)
    crawler_default_max_pages: int = Field(default=50, ge=1, le=10000)
    crawler_default_timeout_ms: int = Field(default=30000, ge=5000)
    crawler_default_rate_limit: int = Field(
        default=10, ge=1, description="Requests per minute"
    )

    # Data source constants
    data_source_max_consecutive_failures: int = Field(
        default=5, ge=1, description="Auto-pause after this many failures"
    )
    data_source_default_interval_hours: int = Field(default=6, ge=1, le=168)


class MonitorConstants(BaseModel):
    """Monitoring and health check constants."""

    monitor_default_max_failures: int = Field(default=5, ge=1)
    monitor_default_interval_hours: int = Field(default=6, ge=1)


class ContentConstants(BaseModel):
    """Content and document constants."""

    # Document chunking
    chunk_default_size: int = Field(default=512, ge=100, le=4000)
    chunk_default_overlap: int = Field(default=50, ge=0, le=500)
    chunk_min_size: int = Field(default=100)
    chunk_max_size: int = Field(default=4000)

    # File constraints
    max_file_size_mb: int = Field(default=100, ge=1)
    max_message_length: int = Field(default=5000, ge=100)


class LLMConstants(BaseModel):
    """LLM and AI-related constants."""

    # Generation limits
    llm_max_tokens: int = Field(default=100000, ge=100)
    llm_default_temperature: float = Field(default=0.7, ge=0.0, le=2.0)

    # RAG configuration
    rag_default_top_k: int = Field(default=5, ge=1, le=50)
    rag_default_similarity_threshold: float = Field(default=0.7, ge=0.0, le=1.0)
    rag_strict_similarity_threshold: float = Field(default=0.75, ge=0.0, le=1.0)


class ApprovalConstants(BaseModel):
    """Content approval and feedback constants."""

    # Auto-approval thresholds
    auto_approve_similarity_threshold: float = Field(default=0.95, ge=0.0, le=1.0)
    auto_approve_new_content_score: float = Field(default=0.9, ge=0.0, le=1.0)
    auto_approve_update_score: float = Field(default=0.85, ge=0.0, le=1.0)

    # Pending update expiration
    pending_update_expiry_days: int = Field(default=7, ge=1, le=90)

    # Feedback ratings
    feedback_negative_rating_threshold: int = Field(default=2, ge=1, le=5)
    feedback_positive_rating_threshold: int = Field(default=4, ge=1, le=5)


class UserConstants(BaseModel):
    """User profile and behavior constants."""

    # User profile
    user_max_history_items: int = Field(default=100, ge=10, le=1000)
    user_preferred_language: str = Field(default="vi")

    # Topic decay
    topic_decay_factor: float = Field(default=0.95, ge=0.0, le=1.0)
    topic_interaction_boost: float = Field(default=1.1, ge=1.0, le=2.0)


# Singleton instances
pagination_config = PaginationConstants()
crawler_config = CrawlerConstants()
monitor_config = MonitorConstants()
content_config = ContentConstants()
llm_config = LLMConstants()
approval_config = ApprovalConstants()
user_config = UserConstants()
