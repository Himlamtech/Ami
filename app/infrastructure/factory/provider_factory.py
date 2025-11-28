"""Provider Factory for Dependency Injection.

This factory creates and manages instances of repositories and services,
implementing the Dependency Inversion Principle.
"""

from motor.motor_asyncio import AsyncIOMotorDatabase

# Repositories
from app.infrastructure.repositories.mongodb_user_repository import MongoDBUserRepository
from app.infrastructure.repositories.mongodb_chat_repository import MongoDBChatRepository
from app.infrastructure.repositories.mongodb_document_repository import MongoDBDocumentRepository
from app.infrastructure.repositories.mongodb_file_repository import MongoDBFileRepository
from app.infrastructure.repositories.mongodb_crawler_repository import MongoDBCrawlerRepository

# Auth
from app.infrastructure.auth import JWTHandler, PasswordHasher

# External services (if available)
try:
    from app.infrastructure.llms.openai_provider import OpenAIProvider as LLMService
except ImportError:
    LLMService = None

try:
    from app.infrastructure.embeddings.sentence_transformer import SentenceTransformerEmbedding as EmbeddingService
except ImportError:
    EmbeddingService = None

try:
    from app.infrastructure.vector_stores.qdrant import QdrantVectorStore as VectorStoreService
except ImportError:
    VectorStoreService = None


class ProviderFactory:
    """
    Factory for creating service instances.
    
    Centralizes dependency injection and instance management.
    """
    
    def __init__(self, db: AsyncIOMotorDatabase):
        self.db = db
        
        # Singleton instances
        self._user_repo = None
        self._chat_repo = None
        self._document_repo = None
        self._file_repo = None
        self._crawler_repo = None
        self._password_hasher = None
        self._jwt_handler = None
        self._llm_service = None
        self._embedding_service = None
        self._vector_store = None
    
    # ===== Repositories =====
    
    def get_user_repository(self) -> MongoDBUserRepository:
        """Get user repository instance."""
        if self._user_repo is None:
            self._user_repo = MongoDBUserRepository(self.db)
        return self._user_repo
    
    def get_chat_repository(self) -> MongoDBChatRepository:
        """Get chat repository instance."""
        if self._chat_repo is None:
            self._chat_repo = MongoDBChatRepository(self.db)
        return self._chat_repo
    
    def get_document_repository(self) -> MongoDBDocumentRepository:
        """Get document repository instance."""
        if self._document_repo is None:
            self._document_repo = MongoDBDocumentRepository(self.db)
        return self._document_repo
    
    def get_file_repository(self) -> MongoDBFileRepository:
        """Get file repository instance."""
        if self._file_repo is None:
            self._file_repo = MongoDBFileRepository(self.db)
        return self._file_repo
    
    def get_crawler_repository(self) -> MongoDBCrawlerRepository:
        """Get crawler repository instance."""
        if self._crawler_repo is None:
            self._crawler_repo = MongoDBCrawlerRepository(self.db)
        return self._crawler_repo
    
    # ===== Auth =====
    
    def get_password_hasher(self) -> PasswordHasher:
        """Get password hasher instance."""
        if self._password_hasher is None:
            self._password_hasher = PasswordHasher()
        return self._password_hasher
    
    def get_jwt_handler(self) -> JWTHandler:
        """Get JWT handler instance."""
        if self._jwt_handler is None:
            self._jwt_handler = JWTHandler()
        return self._jwt_handler
    
    # ===== External Services =====
    
    def get_llm_service(self):
        """Get LLM service instance."""
        if self._llm_service is None and LLMService:
            self._llm_service = LLMService()
        return self._llm_service
    
    def get_embedding_service(self):
        """Get embedding service instance."""
        if self._embedding_service is None and EmbeddingService:
            self._embedding_service = EmbeddingService()
        return self._embedding_service
    
    def get_vector_store(self):
        """Get vector store instance."""
        if self._vector_store is None and VectorStoreService:
            self._vector_store = VectorStoreService()
        return self._vector_store
    
    # ===== Use Cases =====
    
    def create_login_use_case(self):
        """Create LoginUserUseCase with dependencies."""
        from app.application.use_cases.auth import LoginUserUseCase
        
        return LoginUserUseCase(
            user_repository=self.get_user_repository(),
            password_hasher=self.get_password_hasher(),
        )
    
    def create_register_use_case(self):
        """Create RegisterUserUseCase with dependencies."""
        from app.application.use_cases.auth import RegisterUserUseCase
        
        return RegisterUserUseCase(
            user_repository=self.get_user_repository(),
            password_hasher=self.get_password_hasher(),
        )
    
    def create_verify_token_use_case(self):
        """Create VerifyTokenUseCase with dependencies."""
        from app.application.use_cases.auth import VerifyTokenUseCase
        
        return VerifyTokenUseCase(
            user_repository=self.get_user_repository(),
            jwt_handler=self.get_jwt_handler(),
        )


# Global factory instance (will be initialized in main.py)
_factory: ProviderFactory = None


def initialize_factory(db: AsyncIOMotorDatabase):
    """Initialize global factory instance."""
    global _factory
    _factory = ProviderFactory(db)


def get_factory() -> ProviderFactory:
    """Get global factory instance."""
    if _factory is None:
        raise RuntimeError("Factory not initialized. Call initialize_factory() first.")
    return _factory
