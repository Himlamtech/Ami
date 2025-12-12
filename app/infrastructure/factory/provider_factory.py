"""Provider Factory for Dependency Injection.

Centralized factory for creating service instances.
All config is loaded from settings.py.
"""

from motor.motor_asyncio import AsyncIOMotorDatabase

# Repositories (from persistence layer)
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

# LLM providers - lazy import inside get_llm_service() to avoid missing dependencies
from app.domain.enums.llm_mode import LLMMode
from app.application.interfaces.services.llm_service import ILLMService

OpenAILLMService = None
AnthropicLLMService = None
GeminiLLMService = None

# External services (lazy imports to avoid circular dependencies)
try:
    from app.infrastructure.ai.embeddings import (
        HuggingFaceEmbeddings as EmbeddingService,
    )
except ImportError:
    EmbeddingService = None

try:
    from app.infrastructure.persistence.qdrant import (
        QdrantVectorStore as VectorStoreService,
    )
except ImportError:
    VectorStoreService = None

try:
    from app.infrastructure.persistence.minio import MinIOStorage
except ImportError:
    MinIOStorage = None

try:
    from app.infrastructure.scheduling import APSchedulerService
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
        self._student_profile_repo = None
        self._feedback_repo = None
        self._usage_metric_repo = None
        self._llm_usage_repo = None
        self._daily_stats_repo = None
        self._search_log_repo = None
        self._knowledge_gap_repo = None
        self._bookmark_repo = None
        self._llm_instances = {}
        self._embedding_service = None
        self._vector_store = None
        self._storage_service = None
        self._scheduler_service = None
        self._rag_service = None

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

    def get_student_profile_repository(self) -> MongoDBStudentProfileRepository:
        if self._student_profile_repo is None:
            self._student_profile_repo = MongoDBStudentProfileRepository(self.db)
        return self._student_profile_repo

    def get_feedback_repository(self) -> MongoDBFeedbackRepository:
        if self._feedback_repo is None:
            self._feedback_repo = MongoDBFeedbackRepository(self.db)
        return self._feedback_repo

    def get_usage_metric_repository(self) -> MongoDBUsageMetricRepository:
        if self._usage_metric_repo is None:
            self._usage_metric_repo = MongoDBUsageMetricRepository(self.db)
        return self._usage_metric_repo

    def get_llm_usage_repository(self) -> MongoDBLLMUsageRepository:
        if self._llm_usage_repo is None:
            self._llm_usage_repo = MongoDBLLMUsageRepository(self.db)
        return self._llm_usage_repo

    def get_daily_stats_repository(self) -> MongoDBDailyStatsRepository:
        if self._daily_stats_repo is None:
            self._daily_stats_repo = MongoDBDailyStatsRepository(self.db)
        return self._daily_stats_repo

    def get_search_log_repository(self) -> MongoDBSearchLogRepository:
        if self._search_log_repo is None:
            self._search_log_repo = MongoDBSearchLogRepository(self.db)
        return self._search_log_repo

    def get_knowledge_gap_repository(self) -> MongoDBKnowledgeGapRepository:
        if self._knowledge_gap_repo is None:
            self._knowledge_gap_repo = MongoDBKnowledgeGapRepository(self.db)
        return self._knowledge_gap_repo

    def get_bookmark_repository(self) -> MongoDBBookmarkRepository:
        if self._bookmark_repo is None:
            self._bookmark_repo = MongoDBBookmarkRepository(self.db)
        return self._bookmark_repo

    # ===== LLM Services =====

    def get_llm_service(
        self,
        provider: str = "openai",
        default_mode: LLMMode = LLMMode.QA,
    ) -> ILLMService:
        """
        Get LLM service instance.
        Config is loaded from settings.py automatically.

        Args:
            provider: "openai", "anthropic", "gemini"
            default_mode: QA or REASONING
        """
        provider = provider.lower()

        # Return cached instance
        if provider in self._llm_instances:
            return self._llm_instances[provider]
        global OpenAILLMService, AnthropicLLMService, GeminiLLMService

        # Lazy import LLM providers to avoid missing optional dependencies
        if provider == "openai":
            if OpenAILLMService is None:
                from app.infrastructure.ai.llm.openai_llm import (
                    OpenAILLMService as OpenAIImpl,
                )

                OpenAILLMService = OpenAIImpl
            llm = OpenAILLMService(default_mode=default_mode)
        elif provider == "anthropic":
            if AnthropicLLMService is None:
                from app.infrastructure.ai.llm.anthropic_llm import (
                    AnthropicLLMService as AnthropicImpl,
                )

                AnthropicLLMService = AnthropicImpl
            llm = AnthropicLLMService(default_mode=default_mode)
        elif provider == "gemini":
            if GeminiLLMService is None:
                from app.infrastructure.ai.llm.gemini_llm import (
                    GeminiLLMService as GeminiImpl,
                )

                GeminiLLMService = GeminiImpl
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
            from app.config import qdrant_config

            # QdrantVectorStore auto-creates client from config
            self._vector_store = VectorStoreService(
                default_collection=qdrant_config.collection_name
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

    def get_rag_service(self):
        """
        Get unified RAG service.

        Combines embedding, vector store, and chunking into a single facade.
        """
        if self._rag_service is None:
            embedding = self.get_embedding_service()
            vector_store = self.get_vector_store()

            if embedding and vector_store:
                from app.infrastructure.rag import RAGService
                from app.domain.value_objects.rag_models import (
                    ChunkingConfig,
                    RAGSearchConfig,
                )
                from app.config import rag_config

                # Use config defaults
                default_chunking = ChunkingConfig(
                    chunk_size=rag_config.chunk_size,
                    chunk_overlap=rag_config.chunk_overlap,
                )
                default_search = RAGSearchConfig(
                    top_k=rag_config.top_k,
                    score_threshold=rag_config.similarity_threshold,
                )

                self._rag_service = RAGService(
                    embedding_service=embedding,
                    vector_store=vector_store,
                    default_chunking=default_chunking,
                    default_search=default_search,
                )

        return self._rag_service


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
