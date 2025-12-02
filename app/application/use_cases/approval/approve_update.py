"""Approve update use case."""

import uuid
from dataclasses import dataclass
from typing import Optional
from datetime import datetime

from app.domain.entities.pending_update import PendingUpdate
from app.domain.entities.document import Document
from app.domain.enums.data_source import UpdateDetectionType
from app.application.interfaces.repositories.pending_update_repository import IPendingUpdateRepository
from app.application.interfaces.repositories.document_repository import IDocumentRepository


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
    ):
        self.pending_repo = pending_repository
        self.doc_repo = document_repository
    
    async def execute(self, input_data: ApproveUpdateInput) -> ApproveUpdateOutput:
        """Approve a pending update and ingest into knowledge base."""
        # Get pending item
        pending = await self.pending_repo.get_by_id(input_data.pending_id)
        if not pending:
            raise ValueError(f"Pending update '{input_data.pending_id}' not found")
        
        if not pending.is_pending():
            raise ValueError(f"Update already processed with status: {pending.status.value}")
        
        # Mark as approved
        pending.approve(input_data.reviewer_id, input_data.note)
        await self.pending_repo.update(pending)
        
        replaced_doc_id = None
        
        # Handle based on detection type
        if pending.detection_type == UpdateDetectionType.UPDATE and pending.matched_doc_id:
            # Archive old document
            old_doc = await self.doc_repo.get_by_id(pending.matched_doc_id)
            if old_doc:
                old_doc.archive()
                await self.doc_repo.update(old_doc)
                replaced_doc_id = old_doc.id
        
        # Create new document
        new_doc = Document(
            id=str(uuid.uuid4()),
            title=pending.title,
            file_name=f"{pending.title[:50]}.md",
            collection=pending.metadata.get("collection", "default"),
            content=pending.content,
            metadata={
                "source_id": pending.source_id,
                "source_url": pending.source_url,
                "category": pending.category.value,
                "detection_type": pending.detection_type.value,
                "pending_id": pending.id,
                "supersedes_id": replaced_doc_id,
            },
            tags=[pending.category.value],
            created_by=input_data.reviewer_id,
            created_at=datetime.now(),
            updated_at=datetime.now(),
        )
        
        # Save document (embedding will be done by document service later)
        created_doc = await self.doc_repo.create(new_doc)
        
        return ApproveUpdateOutput(
            success=True,
            message=f"Update approved and document created",
            document_id=created_doc.id,
            replaced_doc_id=replaced_doc_id,
        )
