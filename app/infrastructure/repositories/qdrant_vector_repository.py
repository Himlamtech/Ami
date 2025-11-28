"""Qdrant Vector Repository - Adapter for Qdrant vector store."""

from typing import List, Dict, Any, Optional
from app.application.interfaces.services.vector_store_service import IVectorStoreService

# Import existing Qdrant implementation
try:
    from app.infrastructure.vector_stores.qdrant import QdrantVectorStore as _QdrantImpl
except ImportError:
    _QdrantImpl = None


class QdrantVectorRepository(IVectorStoreService):
    """
    Qdrant vector repository implementing IVectorStoreService.
    
    This is an adapter that wraps the existing Qdrant implementation
    to conform to the new interface.
    """
    
    def __init__(self, client=None):
        if _QdrantImpl:
            self._impl = _QdrantImpl(client=client) if client else _QdrantImpl()
        else:
            self._impl = None
    
    async def add_documents(
        self,
        documents: List[Dict[str, Any]],
        embeddings: List[List[float]],
        collection: str = "default",
        doc_metadata: Optional[Dict[str, Any]] = None,
    ) -> List[str]:
        """Add documents with embeddings to vector store."""
        if not self._impl:
            raise RuntimeError("Qdrant implementation not available")
        
        # Call existing implementation
        return await self._impl.add_documents(
            documents=documents,
            embeddings=embeddings,
            collection=collection,
        )
    
    async def search(
        self,
        query_embedding: List[float],
        top_k: int = 5,
        collection: Optional[str] = None,
        metadata_filter: Optional[Dict[str, Any]] = None,
        similarity_threshold: float = 0.0,
    ) -> List[Dict[str, Any]]:
        """Search for similar vectors."""
        if not self._impl:
            raise RuntimeError("Qdrant implementation not available")
        
        # Call existing implementation
        return await self._impl.search(
            query_embedding=query_embedding,
            top_k=top_k,
            collection=collection or "default",
            similarity_threshold=similarity_threshold,
        )
    
    async def delete(self, doc_ids: List[str]) -> None:
        """Delete vectors by IDs."""
        if not self._impl:
            raise RuntimeError("Qdrant implementation not available")
        
        # Call existing implementation
        await self._impl.delete(doc_ids=doc_ids)
    
    async def get_collection_info(self, collection: str) -> Dict[str, Any]:
        """Get collection information."""
        if not self._impl:
            return {"error": "Qdrant not available"}
        
        # Simple info - can be enhanced
        return {
            "collection": collection,
            "status": "available",
        }
    
    async def list_collections(self) -> List[str]:
        """List all collections."""
        if not self._impl:
            return []
        
        # Return default collections
        return ["default", "web_content"]
