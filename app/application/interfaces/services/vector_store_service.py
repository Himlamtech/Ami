"""Vector store service interface."""

from abc import ABC, abstractmethod
from typing import Any, Dict, List, Optional


class IVectorStoreService(ABC):
    """
    Interface for vector storage and retrieval.
    
    Renamed from IVectorStore for consistency.
    """
    
    @abstractmethod
    async def add_documents(
        self,
        documents: List[Dict[str, Any]],
        embeddings: List[List[float]],
        collection: str = "default",
        doc_metadata: Optional[Dict[str, Any]] = None,
    ) -> List[str]:
        """
        Add documents with embeddings to vector store.
        
        Args:
            documents: List of document dicts with content and metadata
            embeddings: Corresponding embedding vectors
            collection: Collection name
            doc_metadata: Optional shared metadata for all documents
            
        Returns:
            List of vector IDs
        """
        pass
    
    @abstractmethod
    async def search(
        self,
        query_embedding: List[float],
        top_k: int = 5,
        collection: Optional[str] = None,
        metadata_filter: Optional[Dict[str, Any]] = None,
        similarity_threshold: float = 0.0,
    ) -> List[Dict[str, Any]]:
        """
        Search for similar vectors.
        
        Args:
            query_embedding: Query embedding vector
            top_k: Number of results to return
            collection: Optional collection filter
            metadata_filter: Optional metadata filter
            similarity_threshold: Minimum similarity score
            
        Returns:
            List of search results with content, metadata, and score
        """
        pass
    
    @abstractmethod
    async def delete(self, doc_ids: List[str]) -> None:
        """
        Delete vectors by IDs.
        
        Args:
            doc_ids: List of vector IDs to delete
        """
        pass
    
    @abstractmethod
    async def get_collection_info(self, collection: str) -> Dict[str, Any]:
        """
        Get collection information.
        
        Args:
            collection: Collection name
            
        Returns:
            Dict with collection stats (count, dimension, etc.)
        """
        pass
    
    @abstractmethod
    async def list_collections(self) -> List[str]:
        """
        List all collections.
        
        Returns:
            List of collection names
        """
        pass
