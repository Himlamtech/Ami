"""
Provider factory for creating instances of different providers.
Follows Factory Pattern and Open/Closed Principle with proper database client management.
"""

import logging
from typing import Any, Dict, Type

from app.config.settings import settings
from app.core.interfaces import (
    IDocumentProcessor,
    IEmbeddingProvider,
    ILLMProvider,
    IVectorStore,
)
from app.infrastructure.databases.chroma_client import ChromaClient
from app.infrastructure.databases.postgres_client import PostgresClient
from app.infrastructure.databases.redis_client import RedisClient
from app.infrastructure.embeddings.huggingface_embeddings import HuggingFaceEmbeddings
from app.infrastructure.embeddings.openai_embeddings import OpenAIEmbeddings
from app.infrastructure.llms.anthropic_llm import AnthropicLLM
from app.infrastructure.llms.gemini_llm import GeminiLLM
from app.infrastructure.llms.openai_llm import OpenAILLM
from app.infrastructure.tools.markitdown_processor import MarkItDownProcessor
from app.infrastructure.vector_stores.chroma_store import ChromaStore
from app.infrastructure.vector_stores.pgvector_store import PgVectorStore

logger = logging.getLogger(__name__)


class ProviderFactory:
    """Factory for creating and managing provider instances with singleton pattern."""

    _embedding_providers: Dict[str, Type[IEmbeddingProvider]] = {
        "openai": OpenAIEmbeddings,
        "huggingface": HuggingFaceEmbeddings,
    }

    _llm_providers: Dict[str, Type[ILLMProvider]] = {
        "openai": OpenAILLM,
        "gemini": GeminiLLM,
        "anthropic": AnthropicLLM,
    }

    _vector_stores: Dict[str, Type[IVectorStore]] = {
        "pgvector": PgVectorStore,
        "chromadb": ChromaStore,
    }

    _instances: Dict[str, Any] = {}

    @classmethod
    def get_embedding_provider(cls, provider_name: str) -> IEmbeddingProvider:
        """
        Get embedding provider instance (singleton).

        Args:
            provider_name: Name of provider ('openai' or 'huggingface')

        Returns:
            IEmbeddingProvider instance
        """
        cache_key = f"embedding_{provider_name}"
        if cache_key not in cls._instances:
            logger.info(f"Creating embedding provider: {provider_name}")

            if provider_name == "openai":
                if not settings.openai_api_key:
                    raise ValueError("OpenAI API key not configured")
                cls._instances[cache_key] = OpenAIEmbeddings(
                    api_key=settings.openai_api_key,
                    model=settings.openai_embedding_model,
                )
            elif provider_name == "huggingface":
                cls._instances[cache_key] = HuggingFaceEmbeddings(
                    model_name=settings.huggingface_embedding_model
                )
            else:
                raise ValueError(f"Unknown embedding provider: {provider_name}")

        return cls._instances[cache_key]

    @classmethod
    def get_llm_provider(cls, provider_name: str) -> ILLMProvider:
        """
        Get LLM provider instance (singleton).

        Args:
            provider_name: Name of provider ('openai', 'gemini', or 'anthropic')

        Returns:
            ILLMProvider instance
        """
        cache_key = f"llm_{provider_name}"
        if cache_key not in cls._instances:
            logger.info(f"Creating LLM provider: {provider_name}")

            if provider_name == "openai":
                if not settings.openai_api_key:
                    raise ValueError("OpenAI API key not configured")
                cls._instances[cache_key] = OpenAILLM(api_key=settings.openai_api_key)
            elif provider_name == "gemini":
                if not settings.gemini_api_key:
                    raise ValueError("Gemini API key not configured")
                cls._instances[cache_key] = GeminiLLM(api_key=settings.gemini_api_key)
            elif provider_name == "anthropic":
                if not settings.anthropic_api_key:
                    raise ValueError("Anthropic API key not configured")
                cls._instances[cache_key] = AnthropicLLM(
                    api_key=settings.anthropic_api_key
                )
            else:
                raise ValueError(f"Unknown LLM provider: {provider_name}")

        return cls._instances[cache_key]

    @classmethod
    async def get_vector_store(cls, store_name: str) -> IVectorStore:
        """
        Get vector store instance (singleton).

        Args:
            store_name: Name of vector store ('pgvector' or 'chromadb')

        Returns:
            IVectorStore instance
        """
        cache_key = f"vector_{store_name}"
        if cache_key not in cls._instances:
            logger.info(f"Creating vector store: {store_name}")

            if store_name == "pgvector":
                # Get PostgresClient
                postgres_client = await cls.get_postgres_client()
                store = PgVectorStore(postgres_client)
                await store.initialize()
                cls._instances[cache_key] = store

            elif store_name == "chromadb" or store_name == "chroma":
                # Get ChromaClient
                chroma_client = await cls.get_chroma_client()
                store = ChromaStore(chroma_client)
                await store.initialize()
                cls._instances[cache_key] = store
            else:
                raise ValueError(f"Unknown vector store: {store_name}")

        return cls._instances[cache_key]

    @classmethod
    async def get_postgres_client(cls) -> PostgresClient:
        """
        Get PostgresClient instance (singleton).

        Returns:
            PostgresClient instance with connection pool
        """
        if "postgres" not in cls._instances:
            logger.info("Creating PostgresClient")
            client = PostgresClient(
                host=settings.postgres_host,
                port=settings.postgres_port,
                user=settings.postgres_user,
                password=settings.postgres_password,
                database=settings.postgres_db,
                min_pool_size=settings.postgres_min_pool_size,
                max_pool_size=settings.postgres_max_pool_size,
            )
            await client.connect()
            cls._instances["postgres"] = client
            logger.info("✓ PostgresClient connected")

        return cls._instances["postgres"]

    @classmethod
    async def get_redis_client(cls) -> RedisClient:
        """
        Get RedisClient instance (singleton).

        Returns:
            RedisClient instance with connection pool
        """
        if "redis" not in cls._instances:
            logger.info("Creating RedisClient")
            client = RedisClient(
                host=settings.redis_host,
                port=settings.redis_port,
                password=settings.redis_password,
                db=settings.redis_db,
                max_connections=settings.redis_max_connections,
            )
            await client.connect()
            cls._instances["redis"] = client
            logger.info("✓ RedisClient connected")

        return cls._instances["redis"]

    @classmethod
    async def get_chroma_client(cls) -> ChromaClient:
        """
        Get ChromaClient instance (singleton).

        Returns:
            ChromaClient instance
        """
        if "chroma" not in cls._instances:
            logger.info("Creating ChromaClient")
            client = ChromaClient(host=settings.chroma_host, port=settings.chroma_port)
            await client.connect()
            cls._instances["chroma"] = client
            logger.info("✓ ChromaClient connected")

        return cls._instances["chroma"]

    @classmethod
    def get_document_processor(cls) -> IDocumentProcessor:
        """
        Get document processor instance (singleton).

        Returns:
            IDocumentProcessor instance
        """
        if "processor" not in cls._instances:
            logger.info("Creating MarkItDownProcessor")
            cls._instances["processor"] = MarkItDownProcessor()

        return cls._instances["processor"]

    @classmethod
    async def cleanup(cls):
        """Cleanup all connections and instances."""
        logger.info("Cleaning up ProviderFactory instances...")

        # Close database connections
        if "postgres" in cls._instances:
            await cls._instances["postgres"].disconnect()
            logger.info("✓ PostgresClient disconnected")

        if "redis" in cls._instances:
            await cls._instances["redis"].disconnect()
            logger.info("✓ RedisClient disconnected")

        if "chroma" in cls._instances:
            # ChromaClient may not have explicit disconnect
            pass

        # Clear all instances
        cls._instances.clear()
        logger.info("✓ All instances cleared")
