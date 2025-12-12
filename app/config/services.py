"""Service Registry for Dependency Injection.

Simple singleton registry - no heavy factory class.
All config is loaded from app/config/*.py.
"""

import logging
from typing import Optional
from motor.motor_asyncio import AsyncIOMotorDatabase

from app.domain.enums.llm_mode import LLMMode
from app.application.interfaces.services.llm_service import ILLMService
from app.application.interfaces.services.embedding_service import IEmbeddingService
from app.application.interfaces.services.vector_store_service import IVectorStoreService
from app.application.interfaces.services.rag_service import IRAGService

# Repository imports
from app.infrastructure.persistence.mongodb.repositories import (
    MongoDBChatRepository,
    MongoDBDocumentRepository,
    MongoDBFileRepository,
    MongoDBCrawlerRepository,
    MongoDBDataSourceRepository,
    MongoDBPendingUpdateRepository,
    MongoDBFeedbackRepository,
    MongoDBUsageMetricRepository,
    MongoDBLLMUsageRepository,
    MongoDBDailyStatsRepository,
    MongoDBSearchLogRepository,
    MongoDBKnowledgeGapRepository,
    MongoDBStudentProfileRepository,
    MongoDBBookmarkRepository,
)

logger = logging.getLogger(__name__)


class ServiceRegistry:
    """
    Simple service registry with singleton caching.
    
    Usage:
        ServiceRegistry.initialize(db)
        llm = ServiceRegistry.get_llm()
        embedding = ServiceRegistry.get_embedding()
    """

    _db: Optional[AsyncIOMotorDatabase] = None
    _initialized = False

    # Singleton instances
    _llm_instances = {}
    _embedding = None
    _vector_store = None
    _storage = None
    _scheduler = None
    _rag = None

    # Repository singletons
    _chat_repo = None
    _document_repo = None
    _file_repo = None
    _crawler_repo = None
    _data_source_repo = None
    _pending_update_repo = None
    _feedback_repo = None
    _usage_metric_repo = None
    _llm_usage_repo = None
    _daily_stats_repo = None
    _search_log_repo = None
    _knowledge_gap_repo = None
    _student_profile_repo = None
    _bookmark_repo = None

    @classmethod
    def initialize(cls, db: AsyncIOMotorDatabase):
        """Initialize registry with database."""
        cls._db = db
        cls._initialized = True
        logger.info("ServiceRegistry initialized")

    @classmethod
    def _ensure_initialized(cls):
        """Check if registry is initialized."""
        if not cls._initialized or cls._db is None:
            raise RuntimeError("ServiceRegistry not initialized. Call ServiceRegistry.initialize(db) first.")

    # ===== LLM Services =====

    @classmethod
    def get_llm(cls, provider: str = "openai", mode: LLMMode = LLMMode.QA) -> ILLMService:
        """Get LLM service by provider."""
        key = f"{provider}_{mode.value}"
        
        if key in cls._llm_instances:
            return cls._llm_instances[key]

        provider = provider.lower()
        
        if provider == "openai":
            from app.infrastructure.ai.llm.openai_llm import OpenAILLMService
            llm = OpenAILLMService(default_mode=mode)
        elif provider == "anthropic":
            from app.infrastructure.ai.llm.anthropic_llm import AnthropicLLMService
            llm = AnthropicLLMService(default_mode=mode)
        elif provider == "gemini":
            from app.infrastructure.ai.llm.gemini_llm import GeminiLLMService
            llm = GeminiLLMService(default_mode=mode)
        else:
            raise ValueError(f"Unknown LLM provider: {provider}")

        cls._llm_instances[key] = llm
        return llm

    # ===== AI Services =====

    @classmethod
    def get_embedding(cls) -> IEmbeddingService:
        """Get embedding service."""
        if cls._embedding is None:
            from app.infrastructure.ai.embeddings import HuggingFaceEmbeddings
            cls._embedding = HuggingFaceEmbeddings()
        return cls._embedding

    @classmethod
    def get_vector_store(cls) -> IVectorStoreService:
        """Get vector store service."""
        if cls._vector_store is None:
            from app.infrastructure.persistence.qdrant import QdrantVectorStore
            from app.config import qdrant_config
            cls._vector_store = QdrantVectorStore(
                default_collection=qdrant_config.collection_name
            )
        return cls._vector_store

    @classmethod
    def get_storage(cls):
        """Get MinIO storage service."""
        if cls._storage is None:
            from app.infrastructure.persistence.minio import MinIOStorage
            cls._storage = MinIOStorage()
        return cls._storage

    @classmethod
    def get_scheduler(cls):
        """Get APScheduler service."""
        if cls._scheduler is None:
            from app.infrastructure.scheduling import APSchedulerService
            cls._scheduler = APSchedulerService()
        return cls._scheduler

    @classmethod
    def get_rag(cls) -> IRAGService:
        """Get RAG service (orchestrator)."""
        if cls._rag is None:
            from app.application.services.rag_service import RAGService
            from app.domain.value_objects.rag_models import ChunkingConfig, RAGSearchConfig
            from app.config import rag_config

            embedding = cls.get_embedding()
            vector_store = cls.get_vector_store()

            default_chunking = ChunkingConfig(
                chunk_size=rag_config.chunk_size,
                chunk_overlap=rag_config.chunk_overlap,
            )
            default_search = RAGSearchConfig(
                top_k=rag_config.top_k,
                score_threshold=rag_config.similarity_threshold,
            )

            cls._rag = RAGService(
                embedding_service=embedding,
                vector_store=vector_store,
                default_chunking=default_chunking,
                default_search=default_search,
            )
        return cls._rag

    # ===== Repositories =====

    @classmethod
    def get_chat_repository(cls) -> MongoDBChatRepository:
        """Get chat repository."""
        cls._ensure_initialized()
        if cls._chat_repo is None:
            cls._chat_repo = MongoDBChatRepository(cls._db)
        return cls._chat_repo

    @classmethod
    def get_document_repository(cls) -> MongoDBDocumentRepository:
        """Get document repository."""
        cls._ensure_initialized()
        if cls._document_repo is None:
            cls._document_repo = MongoDBDocumentRepository(cls._db)
        return cls._document_repo

    @classmethod
    def get_file_repository(cls) -> MongoDBFileRepository:
        """Get file repository."""
        cls._ensure_initialized()
        if cls._file_repo is None:
            cls._file_repo = MongoDBFileRepository(cls._db)
        return cls._file_repo

    @classmethod
    def get_crawler_repository(cls) -> MongoDBCrawlerRepository:
        """Get crawler repository."""
        cls._ensure_initialized()
        if cls._crawler_repo is None:
            cls._crawler_repo = MongoDBCrawlerRepository(cls._db)
        return cls._crawler_repo

    @classmethod
    def get_data_source_repository(cls) -> MongoDBDataSourceRepository:
        """Get data source repository."""
        cls._ensure_initialized()
        if cls._data_source_repo is None:
            cls._data_source_repo = MongoDBDataSourceRepository(cls._db)
        return cls._data_source_repo

    @classmethod
    def get_pending_update_repository(cls) -> MongoDBPendingUpdateRepository:
        """Get pending update repository."""
        cls._ensure_initialized()
        if cls._pending_update_repo is None:
            cls._pending_update_repo = MongoDBPendingUpdateRepository(cls._db)
        return cls._pending_update_repo

    @classmethod
    def get_feedback_repository(cls) -> MongoDBFeedbackRepository:
        """Get feedback repository."""
        cls._ensure_initialized()
        if cls._feedback_repo is None:
            cls._feedback_repo = MongoDBFeedbackRepository(cls._db)
        return cls._feedback_repo

    @classmethod
    def get_usage_metric_repository(cls) -> MongoDBUsageMetricRepository:
        """Get usage metric repository."""
        cls._ensure_initialized()
        if cls._usage_metric_repo is None:
            cls._usage_metric_repo = MongoDBUsageMetricRepository(cls._db)
        return cls._usage_metric_repo

    @classmethod
    def get_llm_usage_repository(cls) -> MongoDBLLMUsageRepository:
        """Get LLM usage repository."""
        cls._ensure_initialized()
        if cls._llm_usage_repo is None:
            cls._llm_usage_repo = MongoDBLLMUsageRepository(cls._db)
        return cls._llm_usage_repo

    @classmethod
    def get_daily_stats_repository(cls) -> MongoDBDailyStatsRepository:
        """Get daily stats repository."""
        cls._ensure_initialized()
        if cls._daily_stats_repo is None:
            cls._daily_stats_repo = MongoDBDailyStatsRepository(cls._db)
        return cls._daily_stats_repo

    @classmethod
    def get_search_log_repository(cls) -> MongoDBSearchLogRepository:
        """Get search log repository."""
        cls._ensure_initialized()
        if cls._search_log_repo is None:
            cls._search_log_repo = MongoDBSearchLogRepository(cls._db)
        return cls._search_log_repo

    @classmethod
    def get_knowledge_gap_repository(cls) -> MongoDBKnowledgeGapRepository:
        """Get knowledge gap repository."""
        cls._ensure_initialized()
        if cls._knowledge_gap_repo is None:
            cls._knowledge_gap_repo = MongoDBKnowledgeGapRepository(cls._db)
        return cls._knowledge_gap_repo

    @classmethod
    def get_student_profile_repository(cls) -> MongoDBStudentProfileRepository:
        """Get student profile repository."""
        cls._ensure_initialized()
        if cls._student_profile_repo is None:
            cls._student_profile_repo = MongoDBStudentProfileRepository(cls._db)
        return cls._student_profile_repo

    @classmethod
    def get_bookmark_repository(cls) -> MongoDBBookmarkRepository:
        """Get bookmark repository."""
        cls._ensure_initialized()
        if cls._bookmark_repo is None:
            cls._bookmark_repo = MongoDBBookmarkRepository(cls._db)
        return cls._bookmark_repo
