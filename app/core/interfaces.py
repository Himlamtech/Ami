"""
Core abstract interfaces following Interface Segregation Principle.
Each interface defines a single, focused contract.
"""

from abc import ABC, abstractmethod
from typing import Any, Dict, List, Optional


class IEmbeddingProvider(ABC):
    """Interface for text embedding providers."""

    @abstractmethod
    async def embed_text(self, text: str) -> List[float]:
        pass

    @abstractmethod
    async def embed_batch(self, texts: List[str]) -> List[List[float]]:
        pass


class ILLMProvider(ABC):
    """Interface for large language model providers."""

    @abstractmethod
    async def generate(
        self, prompt: str, context: Optional[str] = None, **kwargs
    ) -> str:
        pass

    @abstractmethod
    async def stream_generate(
        self, prompt: str, context: Optional[str] = None, **kwargs
    ):
        pass


class IVectorStore(ABC):
    """Interface for vector storage and retrieval."""

    @abstractmethod
    async def add_documents(
        self, documents: List[Dict[str, Any]], embeddings: List[List[float]]
    ) -> List[str]:
        pass

    @abstractmethod
    async def search(
        self, query_embedding: List[float], top_k: int = 5
    ) -> List[Dict[str, Any]]:
        pass

    @abstractmethod
    async def delete(self, doc_ids: List[str]) -> None:
        pass


class IDocumentProcessor(ABC):
    """Interface for document processing."""

    @abstractmethod
    async def process(self, file_path: str) -> str:
        pass


class ICache(ABC):
    """Interface for caching operations."""

    @abstractmethod
    async def get(self, key: str) -> Optional[Any]:
        pass

    @abstractmethod
    async def set(self, key: str, value: Any, ttl: Optional[int] = None) -> None:
        pass

    @abstractmethod
    async def delete(self, key: str) -> None:
        pass


class IDatabase(ABC):
    """Interface for database operations."""

    @abstractmethod
    async def execute(self, query: str, params: Optional[Dict[str, Any]] = None) -> Any:
        pass

    @abstractmethod
    async def fetch_one(
        self, query: str, params: Optional[Dict[str, Any]] = None
    ) -> Optional[Dict[str, Any]]:
        pass

    @abstractmethod
    async def fetch_all(
        self, query: str, params: Optional[Dict[str, Any]] = None
    ) -> List[Dict[str, Any]]:
        pass
