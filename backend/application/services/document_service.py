"""Document service - Orchestration for document operations."""

from app.domain.entities.document import Document
from app.application.interfaces.repositories.document_repository import (
    IDocumentRepository,
)
from app.application.interfaces.services.embedding_service import IEmbeddingService
from app.application.interfaces.services.vector_store_service import IVectorStoreService
from app.application.interfaces.processors.text_chunker import ITextChunker
from app.application.interfaces.processors.document_processor import IDocumentProcessor


class DocumentService:
    """
    Document service for complex document operations.

    Orchestrates multiple operations that don't fit in a single use case.
    """

    def __init__(
        self,
        document_repository: IDocumentRepository,
        embedding_service: IEmbeddingService,
        vector_store_service: IVectorStoreService,
        text_chunker: ITextChunker,
        document_processor: IDocumentProcessor = None,
    ):
        self.doc_repo = document_repository
        self.embedding_service = embedding_service
        self.vector_store = vector_store_service
        self.chunker = text_chunker
        self.processor = document_processor

    async def reindex_document(self, document_id: str) -> Document:
        """
        Reindex existing document (regenerate embeddings).

        Useful when:
        - Embedding model changes
        - Document content was updated
        - Vector store was rebuilt
        """
        # Get document
        document = await self.doc_repo.get_by_id(document_id)
        if not document:
            raise ValueError(f"Document {document_id} not found")

        # Delete old vectors
        if document.vector_ids:
            await self.vector_store.delete(document.vector_ids)

        # Re-chunk content
        chunks = self.chunker.chunk_text(
            text=document.content,
            chunk_size=512,
            chunk_overlap=50,
        )

        # Create chunk documents
        chunk_docs = [
            {
                "content": chunk,
                "metadata": {
                    **document.metadata,
                    "document_id": document.id,
                    "chunk_index": i,
                    "title": document.title,
                    "file_name": document.file_name,
                    "collection": document.collection,
                },
            }
            for i, chunk in enumerate(chunks)
        ]

        # Generate embeddings
        embeddings = await self.embedding_service.embed_batch(chunks)

        # Store in vector database
        vector_ids = await self.vector_store.add_documents(
            documents=chunk_docs,
            embeddings=embeddings,
            collection=document.collection,
        )

        # Update document with new vector IDs
        document.set_vector_ids(vector_ids)
        await self.doc_repo.update(document)

        return document

    async def bulk_delete_by_collection(self, collection: str) -> int:
        """
        Delete all documents in a collection.

        Returns number of documents deleted.
        """
        documents = await self.doc_repo.get_by_collection(collection)

        deleted_count = 0
        for doc in documents:
            # Delete vectors
            if doc.vector_ids:
                await self.vector_store.delete(doc.vector_ids)

            # Delete document
            await self.doc_repo.delete(doc.id)
            deleted_count += 1

        return deleted_count

    async def get_collection_stats(self, collection: str) -> dict:
        """Get statistics for a collection."""
        documents = await self.doc_repo.get_by_collection(collection)

        total_docs = len(documents)
        total_chunks = sum(doc.chunk_count for doc in documents)
        total_vectors = sum(len(doc.vector_ids) for doc in documents)

        return {
            "collection": collection,
            "total_documents": total_docs,
            "total_chunks": total_chunks,
            "total_vectors": total_vectors,
            "avg_chunks_per_doc": total_chunks / total_docs if total_docs > 0 else 0,
        }
