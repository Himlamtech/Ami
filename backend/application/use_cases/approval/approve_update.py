"""Approve update use case."""

import uuid
from dataclasses import dataclass
from typing import Optional, List
from datetime import datetime

from app.domain.entities.document import Document
from app.domain.enums.data_source import UpdateDetectionType
from app.application.interfaces.repositories.pending_update_repository import (
    IPendingUpdateRepository,
)
from app.application.interfaces.repositories.document_repository import (
    IDocumentRepository,
)
from app.application.interfaces.services.embedding_service import IEmbeddingService
from app.application.interfaces.services.vector_store_service import IVectorStoreService
from app.application.interfaces.processors.text_chunker import ITextChunker
from app.domain.value_objects.chunk_config import ChunkConfig


@dataclass
class ApproveUpdateInput:
    """Input for approving an update."""

    pending_id: str
    reviewer_id: str
    note: Optional[str] = None


@dataclass
class ApproveUpdateOutput:
    """Output from approving an update."""

    success: bool
    message: str
    document_id: Optional[str] = None
    replaced_doc_id: Optional[str] = None


class ApproveUpdateUseCase:
    """
    Use case for approving a pending update.

    This will:
    1. Mark pending as approved
    2. If NEW: Create new document
    3. If UPDATE: Replace old document
    4. Trigger embedding/indexing (via document service)
    """

    def __init__(
        self,
        pending_repository: IPendingUpdateRepository,
        document_repository: IDocumentRepository,
        embedding_service: IEmbeddingService,
        vector_store_service: IVectorStoreService,
        text_chunker: ITextChunker,
    ):
        self.pending_repo = pending_repository
        self.doc_repo = document_repository
        self.embedding_service = embedding_service
        self.vector_store = vector_store_service
        self.chunker = text_chunker

    async def execute(self, input_data: ApproveUpdateInput) -> ApproveUpdateOutput:
        """Approve a pending update and ingest into knowledge base."""
        # Get pending item
        pending = await self.pending_repo.get_by_id(input_data.pending_id)
        if not pending:
            raise ValueError(f"Pending update '{input_data.pending_id}' not found")

        if not pending.is_pending():
            raise ValueError(
                f"Update already processed with status: {pending.status.value}"
            )

        # Mark as approved
        pending.approve(input_data.reviewer_id, input_data.note)
        await self.pending_repo.update(pending)

        replaced_doc_id = None

        # Handle based on detection type
        if (
            pending.detection_type == UpdateDetectionType.UPDATE
            and pending.matched_doc_id
        ):
            # Archive old document
            old_doc = await self.doc_repo.get_by_id(pending.matched_doc_id)
            if old_doc:
                old_doc.archive()
                await self.doc_repo.update(old_doc)
                replaced_doc_id = old_doc.id

        # Create new document
        pending_metadata = pending.metadata or {}

        new_doc = Document(
            id=str(uuid.uuid4()),
            title=pending.title,
            file_name=f"{pending.title[:50]}.md",
            collection=pending_metadata.get("collection", "default"),
            content=pending.content,
            metadata={
                **pending_metadata,
                "source_id": pending.source_id,
                "source_url": pending.source_url,
                "category": pending.category.value,
                "detection_type": pending.detection_type.value,
                "pending_id": pending.id,
                "supersedes_id": replaced_doc_id,
                "content_hash": pending.content_hash,
            },
            tags=[pending.category.value],
            created_by=input_data.reviewer_id,
            created_at=datetime.now(),
            updated_at=datetime.now(),
        )

        # Persist to get document ID
        created_doc = await self.doc_repo.create(new_doc)

        # Chunk and embed content
        chunk_config = self._get_chunk_config(pending.metadata)
        chunks: List[str] = self.chunker.chunk_text(
            text=created_doc.content or "",
            chunk_size=chunk_config.chunk_size,
            chunk_overlap=chunk_config.chunk_overlap,
            strategy=chunk_config.strategy,
        )

        vector_ids: List[str] = []
        if chunks:
            embeddings = await self.embedding_service.embed_batch(chunks)
            vector_payloads = [
                {
                    "content": chunk,
                    "metadata": {
                        **created_doc.metadata,
                        "document_id": created_doc.id,
                        "chunk_index": idx,
                        "title": created_doc.title,
                        "collection": created_doc.collection,
                    },
                }
                for idx, chunk in enumerate(chunks)
            ]

            vector_ids = await self.vector_store.add_documents(
                documents=vector_payloads,
                embeddings=embeddings,
                collection=created_doc.collection,
            )

        created_doc.set_vector_ids(vector_ids)
        await self.doc_repo.update(created_doc)

        return ApproveUpdateOutput(
            success=True,
            message="Update approved and document created",
            document_id=created_doc.id,
            replaced_doc_id=replaced_doc_id,
        )

    def _get_chunk_config(self, metadata: Optional[dict]) -> ChunkConfig:
        """Derive chunk config from pending metadata or defaults."""
        default = ChunkConfig.default()
        if not metadata:
            return default

        try:
            chunk_size = int(metadata.get("chunk_size", default.chunk_size))
            chunk_overlap = int(metadata.get("chunk_overlap", default.chunk_overlap))
            strategy = metadata.get("chunk_strategy", default.strategy)
            return ChunkConfig(
                chunk_size=chunk_size,
                chunk_overlap=chunk_overlap,
                strategy=strategy if strategy else default.strategy,
            )
        except Exception:
            return default
