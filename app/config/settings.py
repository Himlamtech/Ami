"""
Configuration management using pydantic-settings.
Simplified settings for OpenAI LLM, HuggingFace Embeddings, Qdrant, MongoDB.
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
    app_name: str = "AMI RAG System - PTIT Assistant"
    app_port: int = Field(default=11121, ge=1, le=65535)
    debug: bool = False

    # Admin API Key (for protected admin routes)
    admin_api_key: str = os.getenv("ADMIN_API_KEY","")

    # LLM Providers API Keys
    openai_api_key: str = os.getenv("OPENAI_API_KEY", "")
    anthropic_api_key: str = os.getenv("ANTHROPIC_API_KEY", "")
    gemini_api_key: str = os.getenv("GEMINI_API_KEY", "")
    
    # Firecrawl (Web Scraping)
    firecrawl_api_key: str = os.getenv("FIRECRAWL_API_KEY", "")

    # MongoDB Configuration (Document & User Management)
    mongodb_url: str | None = Field(default=os.getenv("MONGODB_URL"))  # If set, this takes precedence
    mongodb_host: str = Field(default=os.getenv("MONGODB_HOST", "localhost"))
    mongodb_port: int = Field(default=27017, ge=1, le=65535)
    mongodb_user: str = Field(default=os.getenv("MONGO_USER", "admin"))
    mongodb_password: str = Field(default=os.getenv("MONGO_PASSWORD", "admin_password"))
    mongodb_db: str = Field(default=os.getenv("MONGO_DB", "ami_db"))

    # Qdrant Configuration (Vector Store)
    qdrant_host: str = Field(default=os.getenv("QDRANT_HOST", "localhost"))
    qdrant_port: int = Field(default=6333, ge=1, le=65535)
    qdrant_grpc_port: int = Field(default=6334, ge=1, le=65535)
    qdrant_api_key: str = Field(default=os.getenv("QDRANT_API_KEY", "himlam"))
    qdrant_collection_name: str = Field(default="ami_documents")

    # MinIO Configuration (File Storage)
    minio_endpoint: str = Field(default="localhost:9000")
    minio_access_key: str = Field(default=os.getenv("MINIO_ACCESS_KEY", "admin"))
    minio_secret_key: str = Field(default=os.getenv("MINIO_SECRET_KEY", "admin_password"))
    minio_bucket: str = Field(default="ami")  # Main bucket
    minio_secure: bool = Field(default=False)  # Use HTTPS if True

    # Embedding Model (HuggingFace for Vietnamese)
    huggingface_embedding_model: str = os.getenv(
        "HUGGINGFACE_EMBEDDING_MODEL", "dangvantuan/vietnamese-document-embedding"
    )
    embedding_dimension: int = 768  # HuggingFace model dimension

    # LLM Models Configuration (2 modes: QA and Reasoning)
    # OpenAI Models
    openai_model_qa: str = os.getenv("OPENAI_MODEL_QA", "gpt-4.1-nano")
    openai_model_reasoning: str = os.getenv("OPENAI_MODEL_REASONING", "o4-mini")
    
    # Gemini Models
    gemini_model_qa: str = os.getenv("GEMINI_MODEL_QA", "gemini-2.0-flash")
    gemini_model_reasoning: str = os.getenv("GEMINI_MODEL_REASONING", "gemini-2.5-pro-preview-05-06")
    
    # Anthropic Models
    anthropic_model_qa: str = os.getenv("ANTHROPIC_MODEL_QA", "claude-3-5-haiku-20241022")
    anthropic_model_reasoning: str = os.getenv("ANTHROPIC_MODEL_REASONING", "claude-sonnet-4-20250514")
    
    # Default LLM Provider and Mode
    default_llm_provider: str = os.getenv("DEFAULT_LLM_PROVIDER", "openai")
    default_llm_mode: str = os.getenv("DEFAULT_LLM_MODE", "qa")

    # Chunking Configuration
    chunk_size: int = Field(default=512, ge=100, le=2000)
    chunk_overlap: int = Field(default=50, ge=0, le=500)

    # RAG Configuration
    retrieval_top_k: int = Field(default=5, ge=1, le=20)
    similarity_threshold: float = Field(default=0.7, ge=0.0, le=1.0)

    # CORS
    cors_origins: str = Field(default="http://localhost:11120,http://localhost:6010,http://localhost:11121,http://localhost:11120,http://localhost:11121,http://127.0.0.1:11120,http://127.0.0.1:6010,http://127.0.0.1:11121,http://127.0.0.1:11120,http://127.0.0.1:11121,http://127.0.0.1:5557")
    
    @property
    def cors_origins_list(self) -> list[str]:
        """Parse CORS origins from comma-separated string."""
        return [origin.strip() for origin in self.cors_origins.split(",")]

    def get_mongodb_url(self) -> str:
        """MongoDB connection URL with auth database."""
        # Prioritize MONGODB_URL env var (for Docker), fallback to constructed URL
        if self.mongodb_url:
            return self.mongodb_url
        return f"mongodb://{self.mongodb_user}:{self.mongodb_password}@{self.mongodb_host}:{self.mongodb_port}/?authSource=admin"

    @property
    def qdrant_url(self) -> str:
        """Qdrant HTTP API URL."""
        return f"http://{self.qdrant_host}:{self.qdrant_port}"


settings = Settings()
