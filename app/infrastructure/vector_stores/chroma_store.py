"""
ChromaDB vector store implementation.
Uses ChromaDB HTTP client for vector storage and retrieval with collection management.
"""

import logging
import uuid
from typing import Any, Dict, List, Optional

from app.core.interfaces import IVectorStore
from app.infrastructure.databases.chroma_client import ChromaClient

logger = logging.getLogger(__name__)


class ChromaStore(IVectorStore):
    """ChromaDB-based vector store with collection management."""

    def __init__(
        self, chroma_client: ChromaClient, default_collection: str = "default"
    ):
        """
        Initialize ChromaDB store.

        Args:
            chroma_client: ChromaClient instance
            default_collection: Default collection name
        """
        self.client = chroma_client
        self.default_collection = default_collection
        self._collections = {}  # Cache collection objects
        logger.info(
            f"Initialized ChromaStore with default collection: {default_collection}"
        )

    async def initialize(self):
        """Initialize default collection."""
        try:
            await self._get_or_create_collection(self.default_collection)
            logger.info("✓ ChromaStore initialized")
        except Exception as e:
            logger.error(f"Failed to initialize ChromaStore: {e}")
            raise

    async def add_documents(
        self,
        documents: List[Dict[str, Any]],
        embeddings: List[List[float]],
        collection: str = None,
        doc_metadata: Optional[Dict[str, Any]] = None,
    ) -> List[str]:
        """
        Add documents with embeddings to ChromaDB.

        Args:
            documents: List of document dicts with 'content' and 'metadata'
            embeddings: List of embedding vectors
            collection: Collection name (defaults to default_collection)
            doc_metadata: Shared metadata for documents

        Returns:
            List of document IDs
        """
        if len(documents) != len(embeddings):
            raise ValueError(f"Documents and embeddings count mismatch")

        try:
            collection_name = collection or self.default_collection
            coll = await self._get_or_create_collection(collection_name)

            doc_ids = []
            contents = []
            metadatas = []

            for doc, embedding in zip(documents, embeddings):
                doc_id = doc.get("id") or str(uuid.uuid4())
                doc_ids.append(doc_id)
                contents.append(doc["content"])

                # Merge metadata
                metadata = {**(doc.get("metadata", {})), "collection": collection_name}
                if doc_metadata:
                    metadata.update(doc_metadata)

                # ChromaDB requires metadata values to be simple types
                # Convert nested dicts to JSON strings
                clean_metadata = {}
                for k, v in metadata.items():
                    if isinstance(v, (str, int, float, bool)):
                        clean_metadata[k] = v
                    else:
                        clean_metadata[k] = str(v)

                metadatas.append(clean_metadata)

            # Add to ChromaDB
            await coll.add(
                ids=doc_ids,
                documents=contents,
                embeddings=embeddings,
                metadatas=metadatas,
            )

            logger.info(
                f"Added {len(doc_ids)} documents to collection '{collection_name}'"
            )
            return doc_ids

        except Exception as e:
            logger.error(f"Failed to add documents to ChromaDB: {e}")
            raise RuntimeError(f"Failed to add documents: {str(e)}")

    async def search(
        self,
        query_embedding: List[float],
        top_k: int = 5,
        collection: Optional[str] = None,
        similarity_threshold: float = 0.0,
        metadata_filter: Optional[Dict[str, Any]] = None,
    ) -> List[Dict[str, Any]]:
        """
        Search for similar vectors in ChromaDB.

        Args:
            query_embedding: Query embedding vector
            top_k: Number of results to return
            collection: Collection name to search in
            similarity_threshold: Minimum similarity score
            metadata_filter: Metadata filters (ChromaDB where clause)

        Returns:
            List of matching documents with similarity scores
        """
        try:
            collection_name = collection or self.default_collection
            coll = await self._get_or_create_collection(collection_name)

            # Build where clause for metadata filtering
            where_clause = metadata_filter if metadata_filter else None

            # Query ChromaDB
            results = await coll.query(
                query_embeddings=[query_embedding], n_results=top_k, where=where_clause
            )

            # Format results
            formatted_results = []
            if results and results.get("ids") and len(results["ids"]) > 0:
                for i in range(len(results["ids"][0])):
                    # ChromaDB uses L2 distance, convert to cosine similarity approximation
                    # distance = results['distances'][0][i] if results.get('distances') else 0
                    # similarity = 1 / (1 + distance)  # Convert L2 to similarity

                    # Actually ChromaDB can use cosine similarity if configured
                    # For now, assume distance is already cosine distance
                    distance = (
                        results["distances"][0][i] if results.get("distances") else 0
                    )
                    similarity = 1 - distance

                    if similarity >= similarity_threshold:
                        formatted_results.append(
                            {
                                "id": results["ids"][0][i],
                                "content": (
                                    results["documents"][0][i]
                                    if results.get("documents")
                                    else ""
                                ),
                                "metadata": (
                                    results["metadatas"][0][i]
                                    if results.get("metadatas")
                                    else {}
                                ),
                                "similarity": float(similarity),
                            }
                        )

            logger.debug(f"ChromaDB search returned {len(formatted_results)} results")
            return formatted_results

        except Exception as e:
            logger.error(f"ChromaDB search failed: {e}")
            raise RuntimeError(f"Search failed: {str(e)}")

    async def delete(self, doc_ids: List[str]) -> None:
        """
        Delete documents by IDs.

        Args:
            doc_ids: List of document IDs to delete
        """
        try:
            if not doc_ids:
                return

            # Need to search across all collections or specify collection
            # For simplicity, try default collection first
            coll = await self._get_or_create_collection(self.default_collection)
            await coll.delete(ids=doc_ids)

            logger.info(f"Deleted {len(doc_ids)} documents from ChromaDB")

        except Exception as e:
            logger.error(f"ChromaDB delete failed: {e}")
            raise RuntimeError(f"Failed to delete documents: {str(e)}")

    async def get_collections(self) -> List[str]:
        """Get list of all collections."""
        try:
            collections = await self.client.list_collections()
            return [c.name for c in collections]
        except Exception as e:
            logger.error(f"Failed to list collections: {e}")
            return []

    async def get_stats(self, collection: Optional[str] = None) -> Dict[str, Any]:
        """
        Get statistics about stored documents.

        Args:
            collection: Optional collection filter

        Returns:
            Dictionary with counts and stats
        """
        try:
            collection_name = collection or self.default_collection
            coll = await self._get_or_create_collection(collection_name)

            count = await coll.count()

            return {
                "total_documents": count,
                "total_chunks": count,  # In ChromaDB, documents are chunks
                "collection": collection_name,
            }

        except Exception as e:
            logger.error(f"Failed to get stats: {e}")
            return {"total_documents": 0, "total_chunks": 0}

    async def _get_or_create_collection(self, name: str):
        """Get or create collection by name."""
        if name in self._collections:
            return self._collections[name]

        try:
            # Try to get existing collection
            collection = await self.client.get_collection(name)
        except Exception:
            # Create if doesn't exist
            collection = await self.client.create_collection(
                name=name, metadata={"description": f"Auto-created collection: {name}"}
            )
            logger.info(f"Created new ChromaDB collection: {name}")

        self._collections[name] = collection
        return collection
