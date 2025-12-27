"""Service interfaces - Ports for external services."""

from .llm_service import ILLMService
from .embedding_service import IEmbeddingService
from .vector_store_service import IVectorStoreService
from .storage_service import IStorageService
from .stt_service import ISTTService
from .web_search_service import (
    IWebSearchService,
    WebSearchResponse,
    SearchResult as WebSearchResult,
)
from .rag_service import IRAGService, IndexDocumentInput, IndexDocumentOutput
from .orchestrator_service import IOrchestratorService
from .tool_executor_service import IToolExecutorService, IToolHandler

__all__ = [
    "ILLMService",
    "IEmbeddingService",
    "IVectorStoreService",
    "IStorageService",
    "ISTTService",
    "IWebSearchService",
    "WebSearchResponse",
    "WebSearchResult",
    # RAG service
    "IRAGService",
    "IndexDocumentInput",
    "IndexDocumentOutput",
    # Orchestration
    "IOrchestratorService",
    "IToolExecutorService",
    "IToolHandler",
]
