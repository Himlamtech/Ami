"""Upload document use case."""

from dataclasses import dataclass
from datetime import datetime
from typing import Optional, Dict, Any, List
from app.domain.entities.document import Document
from app.domain.value_objects.chunk_config import ChunkConfig
from app.application.interfaces.repositories.document_repository import (
    IDocumentRepository,
)
from app.application.interfaces.services.embedding_service import IEmbeddingService
from app.application.interfaces.services.vector_store_service import IVectorStoreService


@dataclass
class UploadDocumentInput:
    """Input for upload document use case."""

    title: str
    file_name: str
    content: str
    collection: str = "default"
    metadata: Optional[Dict[str, Any]] = None
    tags: Optional[List[str]] = None
    chunk_config: Optional[ChunkConfig] = None
    created_by: Optional[str] = None


@dataclass
class UploadDocumentOutput:
    """Output from upload document use case."""

    document: Document
    chunk_count: int
    vector_ids: List[str]


class UploadDocumentUseCase:
    """
    Use Case: Upload and index document.

    Business Rules:
    1. Chunk document content
    2. Generate embeddings for chunks
    3. Store vectors in vector database
    4. Store document metadata in database
    5. Link vectors to document

    Single Responsibility: Document upload and indexing workflow
    """

    def __init__(
        self,
        document_repository: IDocumentRepository,
        embedding_service: IEmbeddingService,
        vector_store_service: IVectorStoreService,
        document_chunker,  # Application service for chunking
    ):
        self.doc_repo = document_repository
        self.embedding_service = embedding_service
        self.vector_store = vector_store_service
        self.chunker = document_chunker

    async def execute(self, input_data: UploadDocumentInput) -> UploadDocumentOutput:
        """
        Upload and index document.

        Args:
            input_data: Document data

        Returns:
            UploadDocumentOutput with document and indexing results
        """
        # 1. Use chunk config or default
        chunk_config = input_data.chunk_config or ChunkConfig.default()

        # 2. Chunk document content
        chunks = self.chunker.chunk_text(
            text=input_data.content,
            chunk_size=chunk_config.chunk_size,
            chunk_overlap=chunk_config.chunk_overlap,
            strategy=chunk_config.strategy,
        )

        # 3. Create document objects for chunks
        chunk_docs = [
            {
                "content": chunk,
                "metadata": {
                    **(input_data.metadata or {}),
                    "chunk_index": i,
                    "title": input_data.title,
                    "file_name": input_data.file_name,
                },
            }
            for i, chunk in enumerate(chunks)
        ]

        # 4. Generate embeddings
        embeddings = await self.embedding_service.embed_batch(chunks)

        # 5. Store in vector database
        vector_ids = await self.vector_store.add_documents(
            documents=chunk_docs,
            embeddings=embeddings,
            collection=input_data.collection,
        )

        # 6. Create document entity
        document = Document(
            id="",  # Will be generated
            title=input_data.title,
            file_name=input_data.file_name,
            content=input_data.content,
            collection=input_data.collection,
            metadata=input_data.metadata or {},
            tags=input_data.tags or [],
            chunk_count=len(chunks),
            vector_ids=vector_ids,
            created_by=input_data.created_by,
            created_at=datetime.now(),
            updated_at=datetime.now(),
        )

        # 7. Persist document
        created_doc = await self.doc_repo.create(document)

        return UploadDocumentOutput(
            document=created_doc,
            chunk_count=len(chunks),
            vector_ids=vector_ids,
        )
