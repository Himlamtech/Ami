"""
pgvector vector store implementation.
Uses PostgreSQL with pgvector extension and asyncpg for high performance.
Compatible with the database schema defined in init_db.sql.
"""

import json
import logging
import uuid
from typing import Any, Dict, List, Optional

from app.core.interfaces import IVectorStore
from app.infrastructure.databases.postgres_client import PostgresClient

logger = logging.getLogger(__name__)


class PgVectorStore(IVectorStore):
    """pgvector-based vector store using asyncpg and PostgreSQL."""

    def __init__(self, postgres_client: PostgresClient):
        """
        Initialize pgvector store with PostgresClient.

        Args:
            postgres_client: PostgresClient instance with connection pool
        """
        self.db = postgres_client
        logger.info("Initialized PgVectorStore")

    async def initialize(self):
        """
        Verify pgvector extension and tables exist.
        Tables are created by init_db.sql on first run.
        """
        try:
            # Verify pgvector extension
            await self.db.verify_pgvector()

            # Verify tables exist
            tables = await self.db.fetch_many(
                """
                SELECT table_name 
                FROM information_schema.tables 
                WHERE table_schema = 'public' 
                AND table_name IN ('documents', 'chunks', 'embeddings', 'collections')
            """
            )

            table_names = [t["table_name"] for t in tables]
            required_tables = ["documents", "chunks", "embeddings", "collections"]

            for table in required_tables:
                if table not in table_names:
                    logger.warning(f"Table '{table}' not found. Run init_db.sql first.")

            logger.info(f"✓ Vector store initialized, found tables: {table_names}")

        except Exception as e:
            logger.error(f"Failed to initialize vector store: {e}")
            raise RuntimeError(f"Vector store initialization failed: {str(e)}")

    async def add_documents(
        self,
        documents: List[Dict[str, Any]],
        embeddings: List[List[float]],
        collection: str = "default",
        doc_metadata: Optional[Dict[str, Any]] = None,
    ) -> List[str]:
        """
        Add documents with embeddings to the store.

        This implements the full pipeline:
        1. Create/get document record
        2. Create chunk records
        3. Store embeddings

        Args:
            documents: List of document dicts with 'content' and 'metadata'
            embeddings: List of embedding vectors corresponding to documents
            collection: Collection name for grouping
            doc_metadata: Shared metadata for the parent document

        Returns:
            List of chunk IDs
        """
        if len(documents) != len(embeddings):
            raise ValueError(
                f"Documents ({len(documents)}) and embeddings ({len(embeddings)}) count mismatch"
            )

        try:
            chunk_ids = []

            # Get or create collection
            collection_id = await self._get_or_create_collection(collection)

            # Group chunks by document (assuming metadata contains doc info)
            doc_title = (
                doc_metadata.get("title", "Untitled") if doc_metadata else "Untitled"
            )
            doc_file = (
                doc_metadata.get("file_name", f"doc_{uuid.uuid4().hex[:8]}.md")
                if doc_metadata
                else f"doc_{uuid.uuid4().hex[:8]}.md"
            )

            # Create document record
            doc_id = await self._create_document_record(
                title=doc_title,
                file_name=doc_file,
                metadata={**(doc_metadata or {}), "collection": collection},
            )

            # Add document to collection
            await self._add_document_to_collection(doc_id, collection_id)

            # Insert chunks and embeddings
            for idx, (doc, embedding) in enumerate(zip(documents, embeddings)):
                content = doc["content"]
                chunk_metadata = doc.get("metadata", {})
                chunk_metadata["collection"] = collection

                # Create chunk
                chunk_id = await self._create_chunk_record(
                    document_id=doc_id,
                    content=content,
                    chunk_order=idx,
                    metadata=chunk_metadata,
                )

                # Store embedding
                await self._store_embedding(
                    chunk_id=chunk_id,
                    embedding=embedding,
                    provider="openai",  # Default, should be configurable
                    model="text-embedding-3-small",
                )

                chunk_ids.append(str(chunk_id))

            logger.info(f"Added {len(chunk_ids)} chunks to collection '{collection}'")
            return chunk_ids

        except Exception as e:
            logger.error(f"Failed to add documents: {e}")
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
        Search for similar vectors using cosine similarity.

        Args:
            query_embedding: Query embedding vector
            top_k: Number of results to return
            collection: Filter by collection name
            similarity_threshold: Minimum similarity score (0-1)
            metadata_filter: Additional metadata filters

        Returns:
            List of matching documents with content, metadata, and similarity scores
        """
        try:
            # Convert embedding to pgvector format string
            embedding_str = f"[{','.join(map(str, query_embedding))}]"

            # Build query with filters
            where_clauses = []
            params = [embedding_str, top_k]
            param_idx = 3

            if collection:
                where_clauses.append(f"c.metadata->>'collection' = ${param_idx}")
                params.append(collection)
                param_idx += 1

            if similarity_threshold > 0:
                where_clauses.append(
                    f"1 - (e.embedding <=> ${1}::vector) >= ${param_idx}"
                )
                params.append(similarity_threshold)
                param_idx += 1

            if metadata_filter:
                for key, value in metadata_filter.items():
                    where_clauses.append(f"c.metadata->>'{key}' = ${param_idx}")
                    params.append(str(value))
                    param_idx += 1

            where_clause = ""
            if where_clauses:
                where_clause = "AND " + " AND ".join(where_clauses)

            query = f"""
                SELECT 
                    e.id as embedding_id,
                    e.chunk_id,
                    c.content,
                    c.metadata as chunk_metadata,
                    c.chunk_order,
                    d.id as document_id,
                    d.title,
                    d.file_name,
                    d.metadata as document_metadata,
                    1 - (e.embedding <=> $1::vector) as similarity_score
                FROM embeddings e
                JOIN chunks c ON e.chunk_id = c.id
                JOIN documents d ON c.document_id = d.id
                WHERE 1=1 {where_clause}
                ORDER BY e.embedding <=> $1::vector
                LIMIT $2
            """

            results = await self.db.fetch_many(query, *params)

            # Format results
            formatted_results = []
            for row in results:
                formatted_results.append(
                    {
                        "id": str(row["chunk_id"]),
                        "content": row["content"],
                        "metadata": {
                            **row["chunk_metadata"],
                            "document_id": row["document_id"],
                            "document_title": row["title"],
                            "file_name": row["file_name"],
                            "chunk_order": row["chunk_order"],
                        },
                        "similarity": float(row["similarity_score"]),
                    }
                )

            logger.debug(
                f"Search returned {len(formatted_results)} results (threshold: {similarity_threshold})"
            )
            return formatted_results

        except Exception as e:
            logger.error(f"Search failed: {e}")
            raise RuntimeError(f"Vector search failed: {str(e)}")

    async def delete(self, doc_ids: List[str]) -> None:
        """
        Delete documents by chunk IDs or document IDs.
        Cascade delete will handle chunks and embeddings.

        Args:
            doc_ids: List of document or chunk IDs to delete
        """
        try:
            if not doc_ids:
                return

            # Try deleting as chunk IDs first
            deleted = await self.db.execute(
                "DELETE FROM chunks WHERE id = ANY($1::int[])",
                [int(id) for id in doc_ids if id.isdigit()],
            )

            logger.info(f"Deleted {deleted} chunks")

        except Exception as e:
            logger.error(f"Delete failed: {e}")
            raise RuntimeError(f"Failed to delete documents: {str(e)}")

    async def get_collections(self) -> List[str]:
        """Get list of all collections."""
        try:
            results = await self.db.fetch_many(
                "SELECT name FROM collections ORDER BY name"
            )
            return [r["name"] for r in results]
        except Exception as e:
            logger.error(f"Failed to get collections: {e}")
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
            stats = {}

            if collection:
                # Stats for specific collection
                doc_count = await self.db.fetch_val(
                    """SELECT COUNT(DISTINCT d.id) 
                       FROM documents d 
                       WHERE d.metadata->>'collection' = $1""",
                    collection,
                )
                chunk_count = await self.db.fetch_val(
                    """SELECT COUNT(c.id) 
                       FROM chunks c 
                       JOIN documents d ON c.document_id = d.id 
                       WHERE d.metadata->>'collection' = $1""",
                    collection,
                )
            else:
                # Overall stats
                doc_count = await self.db.fetch_val("SELECT COUNT(*) FROM documents")
                chunk_count = await self.db.fetch_val("SELECT COUNT(*) FROM chunks")

            stats = {
                "total_documents": doc_count or 0,
                "total_chunks": chunk_count or 0,
                "collection": collection or "all",
            }

            return stats

        except Exception as e:
            logger.error(f"Failed to get stats: {e}")
            return {"total_documents": 0, "total_chunks": 0}

    # Helper methods

    async def _get_or_create_collection(self, name: str) -> int:
        """Get or create collection by name."""
        existing = await self.db.fetch_one(
            "SELECT id FROM collections WHERE name = $1", name
        )

        if existing:
            return existing["id"]

        # Create new collection
        result = await self.db.fetch_one(
            "INSERT INTO collections (name, description) VALUES ($1, $2) RETURNING id",
            name,
            f"Auto-created collection: {name}",
        )
        return result["id"]

    async def _create_document_record(
        self, title: str, file_name: str, metadata: Dict[str, Any]
    ) -> int:
        """Create document record and return ID."""
        # Check if document with this file_name already exists
        existing = await self.db.fetch_one(
            "SELECT id FROM documents WHERE file_name = $1", file_name
        )

        if existing:
            logger.debug(
                f"Document with file_name '{file_name}' already exists, returning existing ID"
            )
            return existing["id"]

        result = await self.db.fetch_one(
            """INSERT INTO documents (title, file_name, metadata) 
               VALUES ($1, $2, $3) 
               RETURNING id""",
            title,
            file_name,
            json.dumps(metadata),
        )
        return result["id"]

    async def _create_chunk_record(
        self, document_id: int, content: str, chunk_order: int, metadata: Dict[str, Any]
    ) -> int:
        """Create chunk record and return ID."""
        result = await self.db.fetch_one(
            """INSERT INTO chunks (document_id, content, chunk_order, metadata)
               VALUES ($1, $2, $3, $4)
               RETURNING id""",
            document_id,
            content,
            chunk_order,
            json.dumps(metadata),
        )
        return result["id"]

    async def _store_embedding(
        self, chunk_id: int, embedding: List[float], provider: str, model: str
    ) -> None:
        """Store embedding vector for chunk."""
        embedding_str = f"[{','.join(map(str, embedding))}]"

        await self.db.execute(
            """INSERT INTO embeddings (chunk_id, embedding, embedding_provider, embedding_model)
               VALUES ($1, $2::vector, $3, $4)
               ON CONFLICT (chunk_id, embedding_provider, embedding_model) 
               DO UPDATE SET embedding = EXCLUDED.embedding""",
            chunk_id,
            embedding_str,
            provider,
            model,
        )

    async def _add_document_to_collection(
        self, document_id: int, collection_id: int
    ) -> None:
        """Add document to collection (many-to-many relationship)."""
        await self.db.execute(
            """INSERT INTO document_collections (document_id, collection_id)
               VALUES ($1, $2)
               ON CONFLICT (document_id, collection_id) DO NOTHING""",
            document_id,
            collection_id,
        )
