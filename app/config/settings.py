"""
Configuration management using pydantic-settings.
Loads settings from environment variables with validation.
"""

import os
from typing import Literal

from dotenv import load_dotenv
from pydantic import Field
from pydantic_settings import BaseSettings, SettingsConfigDict

load_dotenv()


class Settings(BaseSettings):
    """Application settings loaded from environment variables."""

    model_config = SettingsConfigDict(
        env_file=".env", env_file_encoding="utf-8", extra="ignore", case_sensitive=False
    )

    # Application
    app_name: str = "AMI RAG System"
    debug: bool = False

    # LLM Provider API Keys
    openai_api_key: str = os.getenv("OPENAI_API_KEY", "")
    gemini_api_key: str = os.getenv("GEMINI_API_KEY", "")
    anthropic_api_key: str = os.getenv("ANTHROPIC_API_KEY", "")

    # PostgreSQL Configuration
    postgres_host: str = os.getenv("POSTGRES_HOST", "localhost")
    postgres_port: int = os.getenv("POSTGRES_PORT", 5432)
    postgres_user: str = os.getenv("POSTGRES_USER", "postgres")
    postgres_password: str = os.getenv("POSTGRES_PASSWORD", "postgres")
    postgres_db: str = os.getenv("POSTGRES_DB", "ami_rag")
    postgres_min_pool_size: int = os.getenv("POSTGRES_MIN_POOL_SIZE", 5)
    postgres_max_pool_size: int = os.getenv("POSTGRES_MAX_POOL_SIZE", 20)

    # Redis Configuration
    redis_host: str = Field(default="localhost")
    redis_port: int = Field(default=6379, ge=1, le=65535)
    redis_password: str = Field(default="redis_password")
    redis_db: int = Field(default=0, ge=0)
    redis_max_connections: int = Field(default=50, ge=1)

    # ChromaDB Configuration
    chroma_host: str = Field(default="localhost")
    chroma_port: int = Field(default=8000, ge=1, le=65535)
    chroma_persist_dir: str = Field(default="./chroma_data")

    # Default Providers
    default_embedding_provider: Literal["openai", "huggingface"] = "openai"
    default_llm_provider: Literal["openai", "gemini", "anthropic"] = "openai"
    default_vector_store: Literal["pgvector", "chromadb"] = "pgvector"

    # Embedding Models
    openai_embedding_model: str = os.getenv(
        "OPENAI_EMBEDDING_MODEL", "text-embedding-3-small"
    )
    huggingface_embedding_model: str = os.getenv(
        "HUGGINGFACE_EMBEDDING_MODEL", "dangvantuan/vietnamese-document-embedding"
    )
    embedding_dimension: int = 1536  # for OpenAI text-embedding-3-small

    # Chunking Configuration
    chunk_size: int = Field(default=512, ge=100, le=2000)
    chunk_overlap: int = Field(default=50, ge=0, le=500)

    # RAG Configuration
    retrieval_top_k: int = Field(default=5, ge=1, le=20)
    similarity_threshold: float = Field(default=0.7, ge=0.0, le=1.0)

    # Cache Configuration
    cache_ttl: int = Field(default=3600, ge=0)  # seconds
    enable_cache: bool = True

    @property
    def postgres_url(self) -> str:
        """AsyncPG database URL for PostgreSQL."""
        return f"postgresql://{self.postgres_user}:{self.postgres_password}@{self.postgres_host}:{self.postgres_port}/{self.postgres_db}"

    @property
    def postgres_asyncpg_url(self) -> str:
        """AsyncPG specific database URL."""
        return f"postgresql+asyncpg://{self.postgres_user}:{self.postgres_password}@{self.postgres_host}:{self.postgres_port}/{self.postgres_db}"

    @property
    def redis_url(self) -> str:
        """Redis connection URL."""
        if self.redis_password:
            return f"redis://:{self.redis_password}@{self.redis_host}:{self.redis_port}/{self.redis_db}"
        return f"redis://{self.redis_host}:{self.redis_port}/{self.redis_db}"

    @property
    def chroma_url(self) -> str:
        """ChromaDB HTTP API URL."""
        return f"http://{self.chroma_host}:{self.chroma_port}"


settings = Settings()
