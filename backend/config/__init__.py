"""
Configuration package - Centralized application configuration.

All configurations are loaded from environment variables.
Secrets (.env) -> Config modules -> Infrastructure services

Usage:
    from config import app_config, mongodb_config, openai_config
    from config import pagination_config, crawler_config, content_config

    # Access settings directly
    port = app_config.BACKEND_PORT
    mongo_url = mongodb_config.get_connection_url()
    limit = pagination_config.default_page_size

Structure:
    - base.py: Core app settings (port, debug, CORS)
    - persistence.py: MongoDB, Qdrant, MinIO (with collection names)
    - ai.py: LLM providers, embeddings, RAG
    - external.py: Third-party APIs (Firecrawl)
    - constants.py: Business constants (pagination, crawler, content limits, etc.)
"""

# Base/App config
from .base import app_config, AppConfig

# Persistence configs
from .persistence import (
    mongodb_config,
    qdrant_config,
    minio_config,
    MongoDBConfig,
    QdrantConfig,
    MinIOConfig,
)

# AI configs
from .ai import (
    openai_config,
    anthropic_config,
    gemini_config,
    embedding_config,
    stt_config,
    rag_config,
    OpenAIConfig,
    AnthropicConfig,
    GeminiConfig,
    EmbeddingConfig,
    STTConfig,
    RAGConfig,
)

# External service configs
from .external import firecrawl_config, FirecrawlConfig

# Business constants
from .constants import (
    pagination_config,
    crawler_config,
    monitor_config,
    content_config,
    llm_config,
    approval_config,
    user_config,
    PaginationConstants,
    CrawlerConstants,
    MonitorConstants,
    ContentConstants,
    LLMConstants,
    ApprovalConstants,
    UserConstants,
)

# Service Registry
from .services import ServiceRegistry
from .logging_config import setup_logging

__all__ = [
    # App
    "app_config",
    "AppConfig",
    # Persistence
    "mongodb_config",
    "qdrant_config",
    "minio_config",
    "MongoDBConfig",
    "QdrantConfig",
    "MinIOConfig",
    # AI
    "openai_config",
    "anthropic_config",
    "gemini_config",
    "embedding_config",
    "stt_config",
    "rag_config",
    "OpenAIConfig",
    "AnthropicConfig",
    "GeminiConfig",
    "EmbeddingConfig",
    "STTConfig",
    "RAGConfig",
    # External
    "firecrawl_config",
    "FirecrawlConfig",
    # Business Constants
    "pagination_config",
    "crawler_config",
    "monitor_config",
    "content_config",
    "llm_config",
    "approval_config",
    "user_config",
    "PaginationConstants",
    "CrawlerConstants",
    "MonitorConstants",
    "ContentConstants",
    "LLMConstants",
    "ApprovalConstants",
    "UserConstants",
    # Service Registry
    "ServiceRegistry",
    # Logging
    "setup_logging",
]
