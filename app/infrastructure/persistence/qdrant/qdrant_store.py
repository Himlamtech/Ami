"""
Qdrant Vector Store - Full-featured implementation for Ami.
Supports multi-collection, CRUD operations, pagination, and more.
"""

import logging
import uuid
from typing import Any, Dict, List, Optional, Tuple

from qdrant_client import QdrantClient
from qdrant_client.models import (
    Distance, 
    PointStruct, 
    Filter, 
    FieldCondition, 
    MatchValue, 
    VectorParams,
    PointIdsList,
    FilterSelector,
)

from app.application.interfaces.services.vector_store_service import IVectorStoreService
from app.config import qdrant_config, embedding_config
from app.config.persistence import QdrantConfig

logger = logging.getLogger(__name__)


class QdrantVectorStore(IVectorStoreService):
    """
    Qdrant vector store with full CRUD and multi-collection support.
    
    Features:
    - Multi-collection management (create, delete, list)
    - Document CRUD (add, search, update, delete)
    - Pagination/Scroll support
    - Bulk operations
    - Health check
    """

    def __init__(
        self, 
        config: QdrantConfig = None,
        default_collection: str = "ami_documents"
    ):
        """
        Initialize Qdrant client.
        
        Args:
            config: Qdrant configuration. If None, uses global qdrant_config.
            default_collection: Default collection name for operations
        """
        self.config = config or qdrant_config
        
        # Use HTTP URL to avoid SSL issues with local Qdrant
        self.client = QdrantClient(
            url=f"http://{self.config.host}:{self.config.port}",
            api_key=self.config.api_key if self.config.api_key else None,
            timeout=self.config.timeout,
        )
        self.default_collection = default_collection
        self.vector_size = embedding_config.dimension
        
        # Ensure default collection exists
        self._ensure_collection(default_collection)
        logger.info(f"QdrantVectorStore initialized (default: {default_collection})")

    # =============================================
    # HEALTH CHECK
    # =============================================
    
    def is_healthy(self) -> bool:
        """Check if Qdrant connection is healthy."""
        try:
            self.client.get_collections()
            return True
        except Exception as e:
            logger.error(f"Health check failed: {e}")
            return False

    # =============================================
    # COLLECTION MANAGEMENT
    # =============================================
    
    def _ensure_collection(self, collection_name: str) -> None:
        """Create collection if not exists."""
        try:
            if not self.collection_exists(collection_name):
                self.create_collection(collection_name)
        except Exception as e:
            logger.error(f"Error ensuring collection '{collection_name}': {e}")

    def collection_exists(self, collection_name: str) -> bool:
        """Check if collection exists."""
        try:
            collections = self.client.get_collections().collections
            return any(c.name == collection_name for c in collections)
        except Exception as e:
            logger.error(f"Error checking collection: {e}")
            return False

    def create_collection(
        self, 
        collection_name: str, 
        vector_size: Optional[int] = None
    ) -> bool:
        """
        Create a new collection.
        
        Args:
            collection_name: Name of collection to create
            vector_size: Vector dimension (uses default if not specified)
        """
        try:
            # Check if already exists first
            if self.collection_exists(collection_name):
                logger.warning(f"Collection '{collection_name}' already exists")
                return False
                
            self.client.create_collection(
                collection_name=collection_name,
                vectors_config=VectorParams(
                    size=vector_size or self.vector_size,
                    distance=Distance.COSINE,
                ),
            )
            logger.info(f"Created collection: {collection_name}")
            return True
        except Exception as e:
            logger.error(f"Failed to create collection '{collection_name}': {e}")
            return False

    def delete_collection(self, collection_name: str) -> bool:
        """Delete a collection."""
        try:
            self.client.delete_collection(collection_name)
            logger.info(f"Deleted collection: {collection_name}")
            return True
        except Exception as e:
            logger.error(f"Failed to delete collection '{collection_name}': {e}")
            return False

    def list_collections(self) -> List[str]:
        """List all collection names."""
        try:
            collections = self.client.get_collections().collections
            return [c.name for c in collections]
        except Exception as e:
            logger.error(f"Failed to list collections: {e}")
            return []

    def get_collection_info(self, collection_name: Optional[str] = None) -> Dict[str, Any]:
        """Get collection statistics."""
        name = collection_name or self.default_collection
        try:
            info = self.client.get_collection(name)
            return {
                "name": name,
                "points_count": info.points_count,
                "vectors_count": info.vectors_count,
                "status": info.status.value,
            }
        except Exception as e:
            logger.error(f"Failed to get collection info: {e}")
            return {"name": name, "error": str(e)}

    # =============================================
    # DOCUMENT OPERATIONS - CREATE
    # =============================================

    async def add_documents(
        self,
        documents: List[Dict[str, Any]],
        embeddings: List[List[float]],
        collection: Optional[str] = None,
    ) -> List[str]:
        """
        Add documents with embeddings.
        
        Args:
            documents: List of dicts with 'content' and optional 'metadata'
            embeddings: Corresponding embedding vectors
            collection: Target collection (uses default if not specified)
        
        Returns:
            List of generated point IDs
        """
        if len(documents) != len(embeddings):
            raise ValueError("Documents and embeddings count mismatch")
        
        if not documents:
            return []

        collection_name = collection or self.default_collection
        self._ensure_collection(collection_name)

        try:
            points = []
            point_ids = []

            for doc, embedding in zip(documents, embeddings):
                point_id = str(uuid.uuid4())
                point_ids.append(point_id)

                payload = {
                    "content": doc.get("content", ""),
                    **doc.get("metadata", {}),
                }

                points.append(PointStruct(
                    id=point_id,
                    vector=embedding,
                    payload=payload,
                ))

            self.client.upsert(
                collection_name=collection_name,
                points=points,
                wait=True,
            )

            logger.info(f"Added {len(point_ids)} documents to '{collection_name}'")
            return point_ids

        except Exception as e:
            logger.error(f"Failed to add documents: {e}")
            raise RuntimeError(f"Add documents failed: {str(e)}")

    # =============================================
    # DOCUMENT OPERATIONS - READ/SEARCH
    # =============================================

    async def search(
        self,
        query_embedding: List[float],
        top_k: int = 5,
        collection: Optional[str] = None,
        score_threshold: Optional[float] = None,
        metadata_filter: Optional[Dict[str, Any]] = None,
    ) -> List[Dict[str, Any]]:
        """
        Search similar vectors.
        
        Args:
            query_embedding: Query vector
            top_k: Number of results
            collection: Target collection
            score_threshold: Minimum similarity score
            metadata_filter: Filter by metadata fields
        
        Returns:
            List of results with id, content, metadata, score
        """
        collection_name = collection or self.default_collection
        
        try:
            # Build filter
            query_filter = self._build_filter(metadata_filter)

            results = self.client.search(
                collection_name=collection_name,
                query_vector=query_embedding,
                limit=top_k,
                query_filter=query_filter,
                score_threshold=score_threshold,
                with_payload=True,
            )

            formatted = []
            for r in results:
                formatted.append({
                    "id": str(r.id),
                    "content": r.payload.get("content", ""),
                    "metadata": {k: v for k, v in r.payload.items() if k != "content"},
                    "score": float(r.score),
                })

            logger.debug(f"Search returned {len(formatted)} results from '{collection_name}'")
            return formatted

        except Exception as e:
            logger.error(f"Search failed: {e}")
            raise RuntimeError(f"Search failed: {str(e)}")

    def scroll(
        self,
        collection: Optional[str] = None,
        limit: int = 100,
        offset: Optional[str] = None,
        metadata_filter: Optional[Dict[str, Any]] = None,
    ) -> Tuple[List[Dict[str, Any]], Optional[str]]:
        """
        Scroll/paginate through documents.
        
        Args:
            collection: Target collection
            limit: Number of documents per page
            offset: Pagination offset (from previous scroll)
            metadata_filter: Filter by metadata
        
        Returns:
            Tuple of (documents, next_offset)
        """
        collection_name = collection or self.default_collection
        
        try:
            query_filter = self._build_filter(metadata_filter)
            
            points, next_offset = self.client.scroll(
                collection_name=collection_name,
                limit=limit,
                offset=offset,
                scroll_filter=query_filter,
                with_payload=True,
                with_vectors=False,
            )

            documents = []
            for p in points:
                documents.append({
                    "id": str(p.id),
                    "content": p.payload.get("content", ""),
                    "metadata": {k: v for k, v in p.payload.items() if k != "content"},
                })

            return documents, next_offset

        except Exception as e:
            logger.error(f"Scroll failed: {e}")
            return [], None

    def get_by_id(
        self, 
        point_id: str, 
        collection: Optional[str] = None
    ) -> Optional[Dict[str, Any]]:
        """Get document by ID."""
        collection_name = collection or self.default_collection
        
        try:
            points = self.client.retrieve(
                collection_name=collection_name,
                ids=[point_id],
                with_payload=True,
                with_vectors=False,
            )
            
            if not points:
                return None
            
            p = points[0]
            return {
                "id": str(p.id),
                "content": p.payload.get("content", ""),
                "metadata": {k: v for k, v in p.payload.items() if k != "content"},
            }
            
        except Exception as e:
            logger.error(f"Get by ID failed: {e}")
            return None

    # =============================================
    # DOCUMENT OPERATIONS - UPDATE
    # =============================================

    def update_metadata(
        self,
        point_id: str,
        metadata: Dict[str, Any],
        collection: Optional[str] = None,
    ) -> bool:
        """
        Update document metadata (payload).
        
        Args:
            point_id: Document ID
            metadata: New metadata to merge
            collection: Target collection
        """
        collection_name = collection or self.default_collection
        
        try:
            self.client.set_payload(
                collection_name=collection_name,
                payload=metadata,
                points=[point_id],
                wait=True,
            )
            logger.debug(f"Updated metadata for point {point_id}")
            return True
        except Exception as e:
            logger.error(f"Update metadata failed: {e}")
            return False

    def update_vector(
        self,
        point_id: str,
        new_vector: List[float],
        collection: Optional[str] = None,
    ) -> bool:
        """
        Update document vector.
        
        Args:
            point_id: Document ID
            new_vector: New embedding vector
            collection: Target collection
        """
        collection_name = collection or self.default_collection
        
        try:
            # Get existing payload
            existing = self.get_by_id(point_id, collection_name)
            if not existing:
                logger.error(f"Point {point_id} not found")
                return False
            
            # Rebuild payload
            payload = {"content": existing["content"], **existing["metadata"]}
            
            self.client.upsert(
                collection_name=collection_name,
                points=[PointStruct(id=point_id, vector=new_vector, payload=payload)],
                wait=True,
            )
            logger.debug(f"Updated vector for point {point_id}")
            return True
        except Exception as e:
            logger.error(f"Update vector failed: {e}")
            return False

    # =============================================
    # DOCUMENT OPERATIONS - DELETE
    # =============================================

    async def delete(
        self, 
        doc_ids: List[str],
        collection: Optional[str] = None,
    ) -> None:
        """Delete documents by IDs."""
        if not doc_ids:
            return

        collection_name = collection or self.default_collection

        try:
            self.client.delete(
                collection_name=collection_name,
                points_selector=PointIdsList(points=doc_ids),
                wait=True,
            )
            logger.info(f"Deleted {len(doc_ids)} documents from '{collection_name}'")

        except Exception as e:
            logger.error(f"Delete failed: {e}")
            raise RuntimeError(f"Delete failed: {str(e)}")

    def delete_by_filter(
        self,
        metadata_filter: Dict[str, Any],
        collection: Optional[str] = None,
    ) -> bool:
        """
        Bulk delete documents matching filter.
        
        Example: delete_by_filter({"user_id": "123"})
        """
        collection_name = collection or self.default_collection
        query_filter = self._build_filter(metadata_filter)
        
        if not query_filter:
            logger.warning("No filter provided for bulk delete")
            return False

        try:
            self.client.delete(
                collection_name=collection_name,
                points_selector=FilterSelector(filter=query_filter),
                wait=True,
            )
            logger.info(f"Deleted documents matching filter from '{collection_name}'")
            return True
        except Exception as e:
            logger.error(f"Bulk delete failed: {e}")
            return False

    # =============================================
    # HELPERS
    # =============================================

    def _build_filter(self, metadata_filter: Optional[Dict[str, Any]]) -> Optional[Filter]:
        """Build Qdrant filter from metadata dict."""
        if not metadata_filter:
            return None
        
        conditions = []
        for key, value in metadata_filter.items():
            conditions.append(
                FieldCondition(key=key, match=MatchValue(value=value))
            )
        
        return Filter(must=conditions) if conditions else None
