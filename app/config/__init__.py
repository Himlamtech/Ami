"""
Configuration package - Centralized application configuration.

All configurations are loaded from environment variables.
Secrets (.env) -> Config modules -> Infrastructure services

Usage:
    from app.config import app_config, mongodb_config, openai_config
    
    # Access settings directly
    port = app_config.app_port
    mongo_url = mongodb_config.get_connection_url()
    
Structure:
    - base.py: Core app settings (port, debug, CORS)
    - persistence.py: MongoDB, Qdrant, MinIO
    - ai.py: LLM providers, embeddings, RAG
    - external.py: Third-party APIs (Firecrawl)
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
]
