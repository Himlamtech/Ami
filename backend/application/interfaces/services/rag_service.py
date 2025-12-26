"""
RAG Service Interface - Unified interface for RAG operations.
Combines embedding, chunking, vector search, and context building.
"""

from abc import ABC, abstractmethod
from typing import List, Optional
from dataclasses import dataclass

from app.domain.value_objects.rag_models import (
    TextChunk,
    SearchResult,
    RAGContext,
    RAGSearchConfig,
    ChunkingConfig,
)


@dataclass
class IndexDocumentInput:
    """Input for indexing a document."""

    content: str
    source_id: str
    source_title: Optional[str] = None
    source_url: Optional[str] = None
    source_type: Optional[str] = None
    category: Optional[str] = None
    tags: Optional[List[str]] = None
    collection: str = "default"
    chunking_config: Optional[ChunkingConfig] = None


@dataclass
class IndexDocumentOutput:
    """Output from indexing a document."""

    source_id: str
    chunks_created: int
    chunk_ids: List[str]
    collection: str


class IRAGService(ABC):
    """
    Unified RAG Service Interface.

    Responsibilities:
    1. Document ingestion (chunk + embed + store)
    2. Semantic search
    3. Context building for LLM

    This is a facade over:
    - ITextChunker (chunking)
    - IEmbeddingService (embeddings)
    - IVectorStoreService (storage/search)
    """

    # =============================================
    # INDEXING
    # =============================================

    @abstractmethod
    async def index_document(
        self,
        input_data: IndexDocumentInput,
    ) -> IndexDocumentOutput:
        """
        Index a document: chunk → embed → store.

        Args:
            input_data: Document content and metadata

        Returns:
            IndexDocumentOutput with chunk IDs
        """
        pass

    @abstractmethod
    async def index_chunks(
        self,
        chunks: List[TextChunk],
        collection: str = "default",
    ) -> List[str]:
        """
        Index pre-chunked text: embed → store.

        Args:
            chunks: List of TextChunk objects
            collection: Target collection

        Returns:
            List of point IDs
        """
        pass

    @abstractmethod
    async def delete_document(
        self,
        source_id: str,
        collection: str = "default",
    ) -> int:
        """
        Delete all chunks for a document.

        Args:
            source_id: Document source ID
            collection: Target collection

        Returns:
            Number of chunks deleted
        """
        pass

    # =============================================
    # SEARCH
    # =============================================

    @abstractmethod
    async def search(
        self,
        query: str,
        config: Optional[RAGSearchConfig] = None,
    ) -> List[SearchResult]:
        """
        Search for relevant chunks.

        Args:
            query: Search query (will be embedded)
            config: Search configuration

        Returns:
            List of SearchResult
        """
        pass

    @abstractmethod
    async def search_with_embedding(
        self,
        query_embedding: List[float],
        config: Optional[RAGSearchConfig] = None,
    ) -> List[SearchResult]:
        """
        Search with pre-computed embedding.

        Args:
            query_embedding: Query vector
            config: Search configuration

        Returns:
            List of SearchResult
        """
        pass

    # =============================================
    # CONTEXT BUILDING
    # =============================================

    @abstractmethod
    async def build_context(
        self,
        query: str,
        config: Optional[RAGSearchConfig] = None,
    ) -> RAGContext:
        """
        Build RAG context for LLM.

        Performs search and builds context object.

        Args:
            query: User query
            config: Search configuration

        Returns:
            RAGContext with results and context string
        """
        pass

    # =============================================
    # UTILITIES
    # =============================================

    @abstractmethod
    async def embed_text(self, text: str) -> List[float]:
        """Get embedding for text."""
        pass

    @abstractmethod
    async def embed_batch(self, texts: List[str]) -> List[List[float]]:
        """Get embeddings for batch of texts."""
        pass

    @abstractmethod
    def chunk_text(
        self,
        text: str,
        config: Optional[ChunkingConfig] = None,
    ) -> List[TextChunk]:
        """Chunk text without indexing."""
        pass

    @abstractmethod
    def get_embedding_dimension(self) -> int:
        """Get embedding vector dimension."""
        pass
