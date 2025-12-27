"""Ingest crawled content use case leveraging DocumentIngestService."""

from dataclasses import dataclass
from typing import Optional, Dict, Any

from application.services.document_ingest_service import (
    DocumentIngestService,
    IngestPayload,
)
from domain.enums.data_source import DataCategory
from domain.entities.pending_update import PendingUpdate


@dataclass
class IngestPendingUpdateInput:
    source_id: str
    title: str
    content: str
    source_url: str
    collection: str = "default"
    category: DataCategory = DataCategory.GENERAL
    metadata: Optional[Dict[str, Any]] = None
    priority: int = 5


@dataclass
class IngestPendingUpdateOutput:
    pending: PendingUpdate


class IngestPendingUpdateUseCase:
    """Thin wrapper orchestrating DocumentIngestService."""

    def __init__(self, ingest_service: DocumentIngestService):
        self.ingest_service = ingest_service

    async def execute(
        self, input_data: IngestPendingUpdateInput
    ) -> IngestPendingUpdateOutput:
        pending = await self.ingest_service.ingest(
            IngestPayload(
                source_id=input_data.source_id,
                title=input_data.title,
                content=input_data.content,
                source_url=input_data.source_url,
                collection=input_data.collection,
                category=input_data.category,
                metadata=input_data.metadata,
                priority=input_data.priority,
            )
        )
        return IngestPendingUpdateOutput(pending=pending)
