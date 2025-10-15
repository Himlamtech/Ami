"""
ChromaDB vector store client.
HTTP client for ChromaDB with collection management.
"""

import logging
from typing import Any, Dict, List, Optional

import chromadb
import httpx
from chromadb.config import Settings as ChromaSettings

logger = logging.getLogger(__name__)


class ChromaClient:
    """
    ChromaDB client for vector storage and similarity search.
    Uses HTTP client for production deployment flexibility.
    """

    def __init__(
        self,
        host: str = "localhost",
        port: int = 8000,
        persist_dir: Optional[str] = None,
    ):
        self.host = host
        self.port = port
        self.persist_dir = persist_dir
        self._client: Optional[chromadb.HttpClient] = None

    async def connect(self) -> None:
        """Initialize ChromaDB client."""
        try:
            # Use HTTP client for remote ChromaDB server
            self._client = chromadb.HttpClient(host=self.host, port=self.port)

            # Test connection by getting heartbeat
            await self.health_check()
            logger.info(f"ChromaDB connected: {self.host}:{self.port}")

        except Exception as e:
            logger.error(f"Failed to connect to ChromaDB: {e}")
            raise

    async def disconnect(self) -> None:
        """Close ChromaDB connection."""
        # HTTP client doesn't need explicit close
        logger.info("ChromaDB client disconnected")

    async def health_check(self) -> bool:
        """Check if ChromaDB server is responsive."""
        try:
            async with httpx.AsyncClient() as client:
                response = await client.get(
                    f"http://{self.host}:{self.port}/api/v1/heartbeat"
                )
                is_healthy = response.status_code == 200
                if is_healthy:
                    logger.info("✓ ChromaDB health check passed")
                return is_healthy
        except Exception as e:
            logger.error(f"ChromaDB health check failed: {e}")
            return False

    # Collection management

    def create_collection(
        self,
        name: str,
        metadata: Optional[Dict[str, Any]] = None,
        get_or_create: bool = True,
    ) -> chromadb.Collection:
        """
        Create or get a collection.

        Args:
            name: Collection name
            metadata: Collection metadata
            get_or_create: If True, get existing collection instead of error

        Returns:
            Collection object
        """
        try:
            if get_or_create:
                collection = self._client.get_or_create_collection(
                    name=name, metadata=metadata or {}
                )
            else:
                collection = self._client.create_collection(
                    name=name, metadata=metadata or {}
                )
            logger.info(f"Collection ready: {name}")
            return collection
        except Exception as e:
            logger.error(f"Error creating collection '{name}': {e}")
            raise

    def get_collection(self, name: str) -> chromadb.Collection:
        """Get existing collection."""
        try:
            return self._client.get_collection(name=name)
        except Exception as e:
            logger.error(f"Error getting collection '{name}': {e}")
            raise

    def delete_collection(self, name: str) -> bool:
        """Delete a collection."""
        try:
            self._client.delete_collection(name=name)
            logger.info(f"Collection deleted: {name}")
            return True
        except Exception as e:
            logger.error(f"Error deleting collection '{name}': {e}")
            return False

    def list_collections(self) -> List[chromadb.Collection]:
        """List all collections."""
        try:
            return self._client.list_collections()
        except Exception as e:
            logger.error(f"Error listing collections: {e}")
            return []

    # Document operations

    def add_documents(
        self,
        collection_name: str,
        ids: List[str],
        embeddings: List[List[float]],
        documents: Optional[List[str]] = None,
        metadatas: Optional[List[Dict[str, Any]]] = None,
    ) -> bool:
        """
        Add documents to collection.

        Args:
            collection_name: Target collection name
            ids: Unique IDs for documents
            embeddings: Document embeddings
            documents: Optional document texts
            metadatas: Optional document metadata

        Returns:
            True if successful
        """
        try:
            collection = self.get_collection(collection_name)
            collection.add(
                ids=ids, embeddings=embeddings, documents=documents, metadatas=metadatas
            )
            logger.info(f"Added {len(ids)} documents to '{collection_name}'")
            return True
        except Exception as e:
            logger.error(f"Error adding documents to '{collection_name}': {e}")
            return False

    def upsert_documents(
        self,
        collection_name: str,
        ids: List[str],
        embeddings: List[List[float]],
        documents: Optional[List[str]] = None,
        metadatas: Optional[List[Dict[str, Any]]] = None,
    ) -> bool:
        """
        Upsert (update or insert) documents in collection.

        Args:
            collection_name: Target collection name
            ids: Unique IDs for documents
            embeddings: Document embeddings
            documents: Optional document texts
            metadatas: Optional document metadata

        Returns:
            True if successful
        """
        try:
            collection = self.get_collection(collection_name)
            collection.upsert(
                ids=ids, embeddings=embeddings, documents=documents, metadatas=metadatas
            )
            logger.info(f"Upserted {len(ids)} documents in '{collection_name}'")
            return True
        except Exception as e:
            logger.error(f"Error upserting documents in '{collection_name}': {e}")
            return False

    def delete_documents(
        self,
        collection_name: str,
        ids: Optional[List[str]] = None,
        where: Optional[Dict[str, Any]] = None,
    ) -> bool:
        """
        Delete documents from collection.

        Args:
            collection_name: Target collection name
            ids: Document IDs to delete
            where: Metadata filter for deletion

        Returns:
            True if successful
        """
        try:
            collection = self.get_collection(collection_name)
            collection.delete(ids=ids, where=where)
            logger.info(f"Deleted documents from '{collection_name}'")
            return True
        except Exception as e:
            logger.error(f"Error deleting documents from '{collection_name}': {e}")
            return False

    def query(
        self,
        collection_name: str,
        query_embeddings: List[List[float]],
        n_results: int = 5,
        where: Optional[Dict[str, Any]] = None,
        include: Optional[List[str]] = None,
    ) -> Dict[str, Any]:
        """
        Query collection for similar documents.

        Args:
            collection_name: Collection to search
            query_embeddings: Query embedding vectors
            n_results: Number of results per query
            where: Metadata filter
            include: Fields to include in results

        Returns:
            Query results with distances and documents
        """
        try:
            collection = self.get_collection(collection_name)
            results = collection.query(
                query_embeddings=query_embeddings,
                n_results=n_results,
                where=where,
                include=include or ["documents", "metadatas", "distances"],
            )
            return results
        except Exception as e:
            logger.error(f"Error querying collection '{collection_name}': {e}")
            return {"ids": [], "documents": [], "metadatas": [], "distances": []}

    def get_documents(
        self,
        collection_name: str,
        ids: Optional[List[str]] = None,
        where: Optional[Dict[str, Any]] = None,
        limit: Optional[int] = None,
    ) -> Dict[str, Any]:
        """
        Get documents from collection.

        Args:
            collection_name: Collection name
            ids: Document IDs to retrieve
            where: Metadata filter
            limit: Maximum number of results

        Returns:
            Retrieved documents
        """
        try:
            collection = self.get_collection(collection_name)
            return collection.get(ids=ids, where=where, limit=limit)
        except Exception as e:
            logger.error(f"Error getting documents from '{collection_name}': {e}")
            return {"ids": [], "documents": [], "metadatas": []}

    def count_documents(self, collection_name: str) -> int:
        """Get document count in collection."""
        try:
            collection = self.get_collection(collection_name)
            return collection.count()
        except Exception as e:
            logger.error(f"Error counting documents in '{collection_name}': {e}")
            return 0

    async def __aenter__(self):
        """Async context manager entry."""
        await self.connect()
        return self

    async def __aexit__(self, exc_type, exc_val, exc_tb):
        """Async context manager exit."""
        await self.disconnect()
