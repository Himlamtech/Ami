"""
Persistence configuration - Database and storage settings.
Includes MongoDB, Qdrant, and MinIO configurations.

Note: pydantic-settings automatically maps environment variables to field names
(case-insensitive). For example, field `mongodb_host` maps to env var `MONGODB_HOST`.
"""

from pydantic import Field
from pydantic_settings import SettingsConfigDict
from .base import BaseConfig


class MongoDBConfig(BaseConfig):
    """MongoDB configuration."""

    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        extra="ignore",
        case_sensitive=False,
    )

    # Connection URL (takes precedence if set)
    mongodb_url: str | None = Field(default=None)

    # Individual connection parameters (used if url is not set)
    mongodb_host: str = Field(default="localhost")
    mongodb_port: int = Field(default=27017, ge=1, le=65535)
    mongo_user: str = Field(default="admin")
    mongo_password: str = Field(default="")
    mongo_db: str = Field(default="ami_db")

    # Convenience properties
    @property
    def host(self) -> str:
        return self.mongodb_host

    @property
    def port(self) -> int:
        return self.mongodb_port

    @property
    def user(self) -> str:
        return self.mongo_user

    @property
    def password(self) -> str:
        return self.mongo_password

    @property
    def database(self) -> str:
        return self.mongo_db

    def get_connection_url(self) -> str:
        """Get MongoDB connection URL."""
        if self.mongodb_url:
            return self.mongodb_url
        return f"mongodb://{self.mongo_user}:{self.mongo_password}@{self.mongodb_host}:{self.mongodb_port}/?authSource=admin"


class QdrantConfig(BaseConfig):
    """Qdrant vector database configuration."""

    qdrant_host: str = Field(default="localhost")
    qdrant_port: int = Field(default=6333, ge=1, le=65535)
    qdrant_grpc_port: int = Field(default=6334, ge=1, le=65535)
    qdrant_api_key: str = Field(default="")
    qdrant_collection_name: str = Field(default="ami_documents")
    qdrant_timeout: int = Field(default=30, ge=1)

    # Convenience properties
    @property
    def host(self) -> str:
        return self.qdrant_host

    @property
    def port(self) -> int:
        return self.qdrant_port

    @property
    def api_key(self) -> str:
        return self.qdrant_api_key

    @property
    def collection_name(self) -> str:
        return self.qdrant_collection_name

    @property
    def timeout(self) -> int:
        return self.qdrant_timeout

    @property
    def url(self) -> str:
        """Get Qdrant HTTP API URL."""
        return f"http://{self.qdrant_host}:{self.qdrant_port}"


class MinIOConfig(BaseConfig):
    """MinIO object storage configuration."""

    minio_endpoint: str = Field(default="localhost:9000")
    minio_access_key: str = Field(default="")
    minio_secret_key: str = Field(default="")
    minio_bucket: str = Field(default="ami")
    minio_secure: bool = Field(default=False)

    # Convenience properties
    @property
    def endpoint(self) -> str:
        return self.minio_endpoint

    @property
    def access_key(self) -> str:
        return self.minio_access_key

    @property
    def secret_key(self) -> str:
        return self.minio_secret_key

    @property
    def bucket(self) -> str:
        return self.minio_bucket

    @property
    def secure(self) -> bool:
        return self.minio_secure


class DocumentProcessingConfig(BaseConfig):
    """Document processing configuration."""

    chunk_size: int = Field(default=512, ge=100, le=2000)
    chunk_overlap: int = Field(default=50, ge=0, le=500)


# Singleton instances
mongodb_config = MongoDBConfig()
qdrant_config = QdrantConfig()
minio_config = MinIOConfig()
document_processing_config = DocumentProcessingConfig()
