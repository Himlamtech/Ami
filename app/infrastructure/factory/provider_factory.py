"""Provider Factory for Dependency Injection.

Simple factory - config lấy từ settings.py
"""

from typing import Optional
from motor.motor_asyncio import AsyncIOMotorDatabase

# Repositories
from app.infrastructure.repositories.mongodb_chat_repository import MongoDBChatRepository
from app.infrastructure.repositories.mongodb_document_repository import MongoDBDocumentRepository
from app.infrastructure.repositories.mongodb_file_repository import MongoDBFileRepository
from app.infrastructure.repositories.mongodb_crawler_repository import MongoDBCrawlerRepository
from app.infrastructure.repositories.mongodb_data_source_repository import MongoDBDataSourceRepository
from app.infrastructure.repositories.mongodb_pending_update_repository import MongoDBPendingUpdateRepository

# LLM providers
from app.domain.enums.llm_mode import LLMMode
from app.infrastructure.llms import OpenAILLMService, AnthropicLLMService, GeminiLLMService
from app.application.interfaces.services.llm_service import ILLMService

# External services
try:
    from app.infrastructure.db.mongodb.embeddings.huggingface_embeddings import HuggingFaceEmbeddings as EmbeddingService
except ImportError:
    EmbeddingService = None

try:
    from app.infrastructure.vector_stores.qdrant_store import QdrantVectorStore as VectorStoreService
except ImportError:
    VectorStoreService = None

try:
    from app.infrastructure.storage.minio_storage import MinIOStorage
except ImportError:
    MinIOStorage = None

try:
    from app.infrastructure.scheduler.apscheduler_service import APSchedulerService
except ImportError:
    APSchedulerService = None


class ProviderFactory:
    """Factory for creating service instances."""
    
    def __init__(self, db: AsyncIOMotorDatabase):
        self.db = db
        
        # Singleton instances
        self._chat_repo = None
        self._document_repo = None
        self._file_repo = None
        self._crawler_repo = None
        self._data_source_repo = None
        self._pending_update_repo = None
        self._llm_instances = {}
        self._embedding_service = None
        self._vector_store = None
        self._storage_service = None
        self._scheduler_service = None
    
    # ===== Repository Properties (for easy access) =====
    
    @property
    def document_repository(self) -> MongoDBDocumentRepository:
        """Get document repository."""
        return self.get_document_repository()
    
    @property
    def chat_repository(self) -> MongoDBChatRepository:
        """Get chat repository."""
        return self.get_chat_repository()
    
    @property
    def data_source_repository(self) -> MongoDBDataSourceRepository:
        """Get data source repository."""
        return self.get_data_source_repository()
    
    @property
    def pending_update_repository(self) -> MongoDBPendingUpdateRepository:
        """Get pending update repository."""
        return self.get_pending_update_repository()
    
    # ===== Repositories =====
    
    def get_chat_repository(self) -> MongoDBChatRepository:
        if self._chat_repo is None:
            self._chat_repo = MongoDBChatRepository(self.db)
        return self._chat_repo
    
    def get_document_repository(self) -> MongoDBDocumentRepository:
        if self._document_repo is None:
            self._document_repo = MongoDBDocumentRepository(self.db)
        return self._document_repo
    
    def get_file_repository(self) -> MongoDBFileRepository:
        if self._file_repo is None:
            self._file_repo = MongoDBFileRepository(self.db)
        return self._file_repo
    
    def get_crawler_repository(self) -> MongoDBCrawlerRepository:
        if self._crawler_repo is None:
            self._crawler_repo = MongoDBCrawlerRepository(self.db)
        return self._crawler_repo
    
    def get_data_source_repository(self) -> MongoDBDataSourceRepository:
        if self._data_source_repo is None:
            self._data_source_repo = MongoDBDataSourceRepository(self.db)
        return self._data_source_repo
    
    def get_pending_update_repository(self) -> MongoDBPendingUpdateRepository:
        if self._pending_update_repo is None:
            self._pending_update_repo = MongoDBPendingUpdateRepository(self.db)
        return self._pending_update_repo
    
    # ===== LLM Services =====
    
    def get_llm_service(
        self,
        provider: str = "openai",
        default_mode: LLMMode = LLMMode.QA,
    ) -> ILLMService:
        """
        Get LLM service instance.
        Config tự động lấy từ settings.py
        
        Args:
            provider: "openai", "anthropic", "gemini"
            default_mode: QA hoặc REASONING
        """
        provider = provider.lower()
        
        # Return cached instance
        if provider in self._llm_instances:
            return self._llm_instances[provider]
        
        if provider == "openai":
            llm = OpenAILLMService(default_mode=default_mode)
        elif provider == "anthropic":
            llm = AnthropicLLMService(default_mode=default_mode)
        elif provider == "gemini":
            llm = GeminiLLMService(default_mode=default_mode)
        else:
            raise ValueError(f"Unknown provider: {provider}")
        
        self._llm_instances[provider] = llm
        return llm
    
    # ===== External Services =====
    
    def get_embedding_service(self):
        if self._embedding_service is None and EmbeddingService:
            self._embedding_service = EmbeddingService()
        return self._embedding_service
    
    def get_vector_store(self):
        if self._vector_store is None and VectorStoreService:
            from app.config.settings import settings
            
            # QdrantVectorStore tự tạo client từ settings
            self._vector_store = VectorStoreService(
                default_collection=settings.qdrant_collection_name
            )
        return self._vector_store
    
    def get_storage_service(self):
        """Get MinIO storage service."""
        if self._storage_service is None and MinIOStorage:
            self._storage_service = MinIOStorage()
        return self._storage_service
    
    def get_scheduler_service(self):
        """Get APScheduler service."""
        if self._scheduler_service is None and APSchedulerService:
            self._scheduler_service = APSchedulerService()
        return self._scheduler_service


# Global factory instance
_factory: ProviderFactory = None


def initialize_factory(db: AsyncIOMotorDatabase):
    """Initialize global factory."""
    global _factory
    _factory = ProviderFactory(db)


def get_factory() -> ProviderFactory:
    """Get global factory."""
    if _factory is None:
        raise RuntimeError("Factory not initialized.")
    return _factory
