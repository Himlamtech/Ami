"""
Qdrant Vector Store - Full-featured implementation for Ami.
Supports multi-collection, CRUD operations, pagination, and more.
"""

import logging
import math
import uuid
from types import SimpleNamespace
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

from application.interfaces.services.vector_store_service import IVectorStoreService
from config import qdrant_config, embedding_config
from config.persistence import QdrantConfig

logger = logging.getLogger(__name__)


def _filter_matches(payload: Dict[str, Any], query_filter: Optional[Filter]) -> bool:
    """Check if payload satisfies the Qdrant filter."""
    if not query_filter or not getattr(query_filter, "must", None):
        return True
    for condition in getattr(query_filter, "must", []):
        key = condition.key
        value = getattr(getattr(condition, "match", None), "value", None)
        if payload.get(key) != value:
            return False
    return True


def _cosine_similarity(vec_a: List[float], vec_b: List[float]) -> float:
    """Compute cosine similarity between two vectors."""
    if not vec_a or not vec_b or len(vec_a) != len(vec_b):
        return 0.0
    dot = sum(a * b for a, b in zip(vec_a, vec_b))
    norm_a = math.sqrt(sum(a * a for a in vec_a))
    norm_b = math.sqrt(sum(b * b for b in vec_b))
    if norm_a == 0 or norm_b == 0:
        return 0.0
    return dot / (norm_a * norm_b)


class _InMemoryQdrantCollection:
    """In-memory representation of a Qdrant collection."""

    def __init__(self, name: str):
        self.name = name
        self.points: Dict[str, Dict[str, Any]] = {}
        self.order: List[str] = []

    def upsert_point(self, point_id: str, vector: List[float], payload: Dict[str, Any]):
        if point_id not in self.points:
            self.order.append(point_id)
        self.points[point_id] = {
            "vector": vector.copy(),
            "payload": dict(payload),
        }

    def delete_point(self, point_id: str):
        self.points.pop(point_id, None)
        if point_id in self.order:
            self.order.remove(point_id)

    def list_points(self, metadata_filter: Optional[Filter] = None):
        matched = []
        for point_id in self.order:
            point = self.points[point_id]
            if _filter_matches(point["payload"], metadata_filter):
                matched.append((point_id, point))
        return matched

    def get_point(self, point_id: str):
        data = self.points.get(point_id)
        if not data:
            return None
        return {
            "id": point_id,
            "vector": data["vector"],
            "payload": data["payload"],
        }


class _InMemoryQdrantClient:
    """Fallback Qdrant client backed by in-memory storage."""

    def __init__(self):
        self._collections: Dict[str, _InMemoryQdrantCollection] = {}

    def get_collections(self):
        return SimpleNamespace(
            collections=[
                SimpleNamespace(name=name) for name in self._collections.keys()
            ]
        )

    def create_collection(self, collection_name: str, **_):
        self._collections.setdefault(
            collection_name, _InMemoryQdrantCollection(collection_name)
        )

    def delete_collection(self, collection_name: str):
        self._collections.pop(collection_name, None)

    def get_collection(self, name: str):
        collection = self._collections.get(name)
        if not collection:
            raise RuntimeError(f"Collection '{name}' not found")
        return SimpleNamespace(
            points_count=len(collection.points),
            vectors_count=len(collection.points),
            status=SimpleNamespace(value="green"),
        )

    def upsert(self, collection_name: str, points: List[PointStruct], **_):
        collection = self._collections.setdefault(
            collection_name, _InMemoryQdrantCollection(collection_name)
        )
        for point in points:
            collection.upsert_point(point.id, point.vector, point.payload)

    def search(
        self,
        collection_name: str,
        query_vector: List[float],
        limit: int,
        query_filter: Optional[Filter] = None,
        score_threshold: Optional[float] = None,
        **_,
    ):
        collection = self._collections.get(collection_name)
        if not collection:
            return []

        matched = []
        for point_id, point in collection.list_points(query_filter):
            score = _cosine_similarity(query_vector, point["vector"])
            if score_threshold is not None and score < score_threshold:
                continue
            matched.append(
                SimpleNamespace(id=point_id, payload=point["payload"], score=score)
            )

        matched.sort(key=lambda item: item.score, reverse=True)
        return matched[:limit]

    def scroll(
        self,
        collection_name: str,
        limit: int,
        offset: Optional[str] = None,
        scroll_filter: Optional[Filter] = None,
        **_,
    ):
        collection = self._collections.get(collection_name)
        if not collection:
            return [], None

        start = 0
        if offset and offset in collection.order:
            start = collection.order.index(offset) + 1

        matched = []
        for point_id in collection.order[start:]:
            point = collection.points[point_id]
            if _filter_matches(point["payload"], scroll_filter):
                matched.append(SimpleNamespace(id=point_id, payload=point["payload"]))
            if len(matched) >= limit:
                break

        next_offset = None
        if matched:
            last_index = collection.order.index(matched[-1].id)
            if last_index + 1 < len(collection.order):
                next_offset = matched[-1].id
        return matched, next_offset

    def retrieve(self, collection_name: str, ids: List[str], **_):
        collection = self._collections.get(collection_name)
        if not collection:
            return []
        results = []
        for point_id in ids:
            point = collection.get_point(point_id)
            if point:
                results.append(SimpleNamespace(id=point_id, payload=point["payload"]))
        return results

    def set_payload(
        self, collection_name: str, payload: Dict[str, Any], points: List[str], **_
    ):
        collection = self._collections.get(collection_name)
        if not collection:
            return
        for point_id in points:
            point = collection.points.get(point_id)
            if point:
                point["payload"].update(payload)

    def delete(self, collection_name: str, points_selector: Any, **_):
        collection = self._collections.get(collection_name)
        if not collection:
            return
        if hasattr(points_selector, "points"):
            for point_id in points_selector.points:
                collection.delete_point(point_id)
        elif hasattr(points_selector, "filter") and points_selector.filter:
            to_delete = []
            for point_id, point in collection.points.items():
                if _filter_matches(point["payload"], points_selector.filter):
                    to_delete.append(point_id)
            for point_id in to_delete:
                collection.delete_point(point_id)


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
        self, config: QdrantConfig = None, default_collection: str = "ami_documents"
    ):
        """
        Initialize Qdrant client.

        Args:
            config: Qdrant configuration. If None, uses global qdrant_config.
            default_collection: Default collection name for operations
        """
        self.config = config or qdrant_config
        self.default_collection = default_collection
        self.vector_size = embedding_config.dimension

        try:
            self.client = QdrantClient(
                url=f"http://{self.config.host}:{self.config.port}",
                api_key=self.config.api_key if self.config.api_key else None,
                timeout=self.config.timeout,
            )
            if not (
                hasattr(self.client, "search") or hasattr(self.client, "query_points")
            ):
                raise AttributeError("Qdrant client missing search support")
            self.client.get_collections()
            self._use_in_memory = False
        except Exception as e:
            logger.warning("Qdrant connection failed, using in-memory store: %s", e)
            self.client = _InMemoryQdrantClient()
            self._use_in_memory = True

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
        self, collection_name: str, vector_size: Optional[int] = None
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

    def get_collection_info(
        self, collection_name: Optional[str] = None
    ) -> Dict[str, Any]:
        """Get collection statistics."""
        name = collection_name or self.default_collection
        try:
            info = self.client.get_collection(name)
            status = getattr(info, "status", SimpleNamespace(value="unknown")).value
            return {
                "name": name,
                "points_count": getattr(info, "points_count", 0),
                "vectors_count": getattr(info, "vectors_count", 0),
                "status": status,
            }
        except Exception as e:
            logger.error(f"Failed to get collection info: {e}")
            return {"name": name, "error": str(e)}

    # =============================================
    # DOCUMENT OPERATIONS - CREATE
    # =============================================

    async def add_documents(
        self,
        documents: Optional[List[Dict[str, Any]]] = None,
        embeddings: Optional[List[List[float]]] = None,
        *,
        vectors: Optional[List[List[float]]] = None,
        texts: Optional[List[str]] = None,
        metadatas: Optional[List[Dict[str, Any]]] = None,
        collection: Optional[str] = None,
        collection_name: Optional[str] = None,
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
        if vectors is not None:
            if not texts or len(vectors) != len(texts):
                raise ValueError("Vectors and texts count mismatch")
            documents = [
                {
                    "content": texts[idx],
                    "metadata": (
                        metadatas[idx] if metadatas and idx < len(metadatas) else {}
                    ),
                }
                for idx in range(len(vectors))
            ]
            embeddings = vectors
        elif documents is None or embeddings is None:
            raise ValueError("Documents and embeddings are required")

        if len(documents) != len(embeddings):
            raise ValueError("Documents and embeddings count mismatch")
        if not documents:
            return []

        collection_name = collection_name or collection or self.default_collection
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

                points.append(
                    PointStruct(
                        id=point_id,
                        vector=embedding,
                        payload=payload,
                    )
                )

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

    async def add_document(
        self,
        collection_name: Optional[str],
        vector: List[float],
        text: str,
        metadata: Optional[Dict[str, Any]] = None,
        *,
        collection: Optional[str] = None,
    ) -> str:
        """Add a single document for convenience."""
        docs = [{"content": text, "metadata": metadata or {}}]
        ids = await self.add_documents(
            documents=docs,
            embeddings=[vector],
            collection_name=collection_name or collection,
        )
        return ids[0]

    # =============================================
    # DOCUMENT OPERATIONS - READ/SEARCH
    # =============================================

    async def search(
        self,
        query_embedding: Optional[List[float]] = None,
        top_k: Optional[int] = None,
        collection: Optional[str] = None,
        score_threshold: Optional[float] = None,
        metadata_filter: Optional[Dict[str, Any]] = None,
        *,
        collection_name: Optional[str] = None,
        query_vector: Optional[List[float]] = None,
        limit: Optional[int] = None,
        filter_dict: Optional[Dict[str, Any]] = None,
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
        resolved_collection = collection_name or collection or self.default_collection
        actual_limit = limit or top_k or 5
        actual_filter = filter_dict or metadata_filter
        actual_vector = query_vector or query_embedding
        if not actual_vector:
            raise ValueError("Query vector is required")

        try:
            # Build filter
            query_filter = self._build_filter(actual_filter)

            if hasattr(self.client, "search"):
                results = self.client.search(
                    collection_name=resolved_collection,
                    query_vector=actual_vector,
                    limit=actual_limit,
                    query_filter=query_filter,
                    score_threshold=score_threshold,
                    with_payload=True,
                )
            else:
                response = self.client.query_points(
                    collection_name=resolved_collection,
                    query=actual_vector,
                    query_filter=query_filter,
                    limit=actual_limit,
                    score_threshold=score_threshold,
                    with_payload=True,
                )
                results = getattr(response, "points", [])

            formatted = []
            for r in results:
                payload = getattr(r, "payload", {}) or {}
                content_value = payload.get("content", "")
                formatted.append(
                    {
                        "id": str(getattr(r, "id", "")),
                        "content": content_value,
                        "text": content_value,
                        "metadata": {
                            k: v for k, v in payload.items() if k != "content"
                        },
                        "score": float(getattr(r, "score", 0.0)),
                    }
                )

            logger.debug(
                f"Search returned {len(formatted)} results from '{resolved_collection}'"
            )
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
                documents.append(
                    {
                        "id": str(p.id),
                        "content": p.payload.get("content", ""),
                        "metadata": {
                            k: v for k, v in p.payload.items() if k != "content"
                        },
                    }
                )

            return documents, next_offset

        except Exception as e:
            logger.error(f"Scroll failed: {e}")
            return [], None

    def get_by_id(
        self, point_id: str, collection: Optional[str] = None
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
                "text": p.payload.get("content", ""),
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
        collection_name: Optional[str] = None,
    ) -> None:
        """Delete documents by IDs."""
        if not doc_ids:
            return

        collection_name = collection_name or collection or self.default_collection

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

    async def delete_document(
        self, collection_name: Optional[str], doc_id: str
    ) -> bool:
        """Delete a single document."""
        try:
            await self.delete([doc_id], collection_name=collection_name)
            return True
        except Exception:
            return False

    async def delete_documents(
        self, collection_name: Optional[str], doc_ids: List[str]
    ) -> bool:
        """Delete multiple documents."""
        try:
            await self.delete(doc_ids, collection_name=collection_name)
            return True
        except Exception:
            return False

    # =============================================
    # CONVENIENCE WRAPPERS
    # =============================================

    def get_document(
        self, collection_name: Optional[str], point_id: str
    ) -> Optional[Dict[str, Any]]:
        """Alias for get_by_id."""
        return self.get_by_id(point_id, collection=collection_name)

    def update_document(
        self, collection_name: Optional[str], point_id: str, metadata: Dict[str, Any]
    ) -> bool:
        """Update document metadata via alias."""
        return self.update_metadata(point_id, metadata, collection=collection_name)

    def count_documents(self, collection_name: Optional[str] = None) -> int:
        """Return document count for collection."""
        info = self.get_collection_info(collection_name)
        return int(info.get("points_count", 0))

    def scroll_documents(
        self,
        collection_name: Optional[str] = None,
        limit: int = 100,
        offset: Optional[str] = None,
        metadata_filter: Optional[Dict[str, Any]] = None,
    ) -> Tuple[List[Dict[str, Any]], Optional[str]]:
        return self.scroll(
            collection=collection_name,
            limit=limit,
            offset=offset,
            metadata_filter=metadata_filter,
        )

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

    def _build_filter(
        self, metadata_filter: Optional[Dict[str, Any]]
    ) -> Optional[Filter]:
        """Build Qdrant filter from metadata dict."""
        if not metadata_filter:
            return None

        conditions = []
        for key, value in metadata_filter.items():
            conditions.append(FieldCondition(key=key, match=MatchValue(value=value)))

        return Filter(must=conditions) if conditions else None
