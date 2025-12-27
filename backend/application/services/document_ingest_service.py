"""Document ingestion service orchestrating dedup + pending creation."""

from dataclasses import dataclass
from typing import Dict, Optional
import logging

from application.interfaces.repositories.pending_update_repository import (
    IPendingUpdateRepository,
)
from application.interfaces.repositories.document_repository import (
    IDocumentRepository,
)
from application.services.document_resolver import DocumentResolver
from application.use_cases.sync.change_detector import ChangeDetectorUseCase
from domain.entities.pending_update import PendingUpdate
from domain.enums.data_source import (
    DataCategory,
    PendingStatus,
    UpdateDetectionType,
)

logger = logging.getLogger(__name__)


@dataclass
class IngestPayload:
    source_id: str
    title: str
    content: str
    source_url: str
    collection: str
    category: DataCategory
    metadata: Optional[Dict] = None
    priority: int = 5


class DocumentIngestService:
    """Service for ingesting raw crawled content into pending updates."""

    def __init__(
        self,
        pending_repo: IPendingUpdateRepository,
        document_repo: IDocumentRepository,
        resolver: DocumentResolver,
    ):
        self.pending_repo = pending_repo
        self.document_repo = document_repo
        self.resolver = resolver

    async def ingest(self, payload: IngestPayload) -> PendingUpdate:
        content_hash = ChangeDetectorUseCase.compute_content_hash(payload.content)

        if await self.pending_repo.check_duplicate(content_hash):
            return await self._create_duplicate_pending(
                payload, content_hash, "Duplicate content hash in pending queue"
            )

        existing_docs = await self.document_repo.search_by_metadata(
            metadata_filter={"content_hash": content_hash},
            collection=payload.collection,
        )
        if existing_docs:
            return await self._create_duplicate_pending(
                payload,
                content_hash,
                "Duplicate existing document content hash",
                matched_doc_id=existing_docs[0].id,
            )

        resolution = await self.resolver.resolve(
            title=payload.title,
            content=payload.content,
            collection=payload.collection,
            source_url=payload.source_url,
            category=payload.category.value,
        )

        metadata = dict(payload.metadata or {})
        metadata.setdefault("collection", payload.collection)
        metadata.setdefault("source_url", payload.source_url)
        metadata.setdefault("summary", resolution.summary)

        pending = PendingUpdate(
            id="",
            source_id=payload.source_id,
            title=payload.title,
            content=payload.content,
            content_hash=content_hash,
            source_url=payload.source_url,
            category=payload.category,
            detection_type=resolution.action,
            similarity_score=(
                resolution.candidates[0].score if resolution.candidates else 0.0
            ),
            matched_doc_id=resolution.updated_id,
            matched_doc_ids=[c.id for c in resolution.candidates if c.id is not None],
            llm_analysis=resolution.reason,
            llm_summary=resolution.summary,
            status=(
                PendingStatus.REJECTED
                if resolution.action == UpdateDetectionType.UNRELATED
                else PendingStatus.PENDING
            ),
            auto_approve_score=0.0,
            auto_action_reason=(
                resolution.reason
                if resolution.action == UpdateDetectionType.UNRELATED
                else None
            ),
            metadata=metadata,
            priority=payload.priority,
        )

        return await self.pending_repo.create(pending)

    async def _create_duplicate_pending(
        self,
        payload: IngestPayload,
        content_hash: str,
        reason: str,
        matched_doc_id: Optional[str] = None,
    ) -> PendingUpdate:
        duplicate = PendingUpdate(
            id="",
            source_id=payload.source_id,
            title=payload.title,
            content=payload.content,
            content_hash=content_hash,
            source_url=payload.source_url,
            category=payload.category,
            detection_type=UpdateDetectionType.DUPLICATE,
            similarity_score=1.0,
            matched_doc_id=matched_doc_id,
            status=PendingStatus.REJECTED,
            llm_summary=payload.content[:200],
            auto_action_reason=reason,
            metadata=dict(payload.metadata or {}),
            priority=payload.priority,
        )
        logger.info(
            "Duplicate content detected for monitor target %s", payload.source_url
        )
        return await self.pending_repo.create(duplicate)
