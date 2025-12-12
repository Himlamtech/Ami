"""Vector store service interface - Full-featured for admin management."""

from abc import ABC, abstractmethod
from typing import Any, Dict, List, Optional, Tuple


class IVectorStoreService(ABC):
    """
    Interface for vector storage with full CRUD and admin operations.

    Groups:
    - Health: is_healthy
    - Collection: create, delete, list, info
    - Document: add, search, get, update, delete
    - Pagination: scroll
    """

    # =============================================
    # HEALTH CHECK
    # =============================================

    @abstractmethod
    def is_healthy(self) -> bool:
        """Check if vector store is healthy."""
        pass

    # =============================================
    # COLLECTION MANAGEMENT
    # =============================================

    @abstractmethod
    def collection_exists(self, collection_name: str) -> bool:
        """Check if collection exists."""
        pass

    @abstractmethod
    def create_collection(
        self, collection_name: str, vector_size: Optional[int] = None
    ) -> bool:
        """Create a new collection."""
        pass

    @abstractmethod
    def delete_collection(self, collection_name: str) -> bool:
        """Delete a collection."""
        pass

    @abstractmethod
    def list_collections(self) -> List[str]:
        """List all collection names."""
        pass

    @abstractmethod
    def get_collection_info(
        self, collection_name: Optional[str] = None
    ) -> Dict[str, Any]:
        """Get collection statistics."""
        pass

    # =============================================
    # DOCUMENT OPERATIONS - CREATE
    # =============================================

    @abstractmethod
    async def add_documents(
        self,
        documents: List[Dict[str, Any]],
        embeddings: List[List[float]],
        collection: Optional[str] = None,
    ) -> List[str]:
        """Add documents with embeddings. Returns list of IDs."""
        pass

    # =============================================
    # DOCUMENT OPERATIONS - READ/SEARCH
    # =============================================

    @abstractmethod
    async def search(
        self,
        query_embedding: List[float],
        top_k: int = 5,
        collection: Optional[str] = None,
        score_threshold: Optional[float] = None,
        metadata_filter: Optional[Dict[str, Any]] = None,
    ) -> List[Dict[str, Any]]:
        """Search similar vectors."""
        pass

    @abstractmethod
    def scroll(
        self,
        collection: Optional[str] = None,
        limit: int = 100,
        offset: Optional[str] = None,
        metadata_filter: Optional[Dict[str, Any]] = None,
    ) -> Tuple[List[Dict[str, Any]], Optional[str]]:
        """Scroll/paginate through documents."""
        pass

    @abstractmethod
    def get_by_id(
        self, point_id: str, collection: Optional[str] = None
    ) -> Optional[Dict[str, Any]]:
        """Get document by ID."""
        pass

    # =============================================
    # DOCUMENT OPERATIONS - UPDATE
    # =============================================

    @abstractmethod
    def update_metadata(
        self,
        point_id: str,
        metadata: Dict[str, Any],
        collection: Optional[str] = None,
    ) -> bool:
        """Update document metadata."""
        pass

    @abstractmethod
    def update_vector(
        self,
        point_id: str,
        new_vector: List[float],
        collection: Optional[str] = None,
    ) -> bool:
        """Update document vector."""
        pass

    # =============================================
    # DOCUMENT OPERATIONS - DELETE
    # =============================================

    @abstractmethod
    async def delete(
        self, doc_ids: List[str], collection: Optional[str] = None
    ) -> None:
        """Delete documents by IDs."""
        pass

    @abstractmethod
    def delete_by_filter(
        self,
        metadata_filter: Dict[str, Any],
        collection: Optional[str] = None,
    ) -> bool:
        """Bulk delete documents matching filter."""
        pass
