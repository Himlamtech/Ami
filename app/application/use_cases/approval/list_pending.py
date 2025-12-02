"""List pending updates use case."""

from dataclasses import dataclass
from typing import Optional, List

from app.domain.entities.pending_update import PendingUpdate
from app.domain.enums.data_source import PendingStatus, DataCategory, UpdateDetectionType
from app.application.interfaces.repositories.pending_update_repository import IPendingUpdateRepository


@dataclass
class ListPendingUpdatesInput:
    """Input for listing pending updates."""
    skip: int = 0
    limit: int = 50
    status: Optional[PendingStatus] = None
    source_id: Optional[str] = None
    category: Optional[DataCategory] = None
    detection_type: Optional[UpdateDetectionType] = None


@dataclass
class ListPendingUpdatesOutput:
    """Output from listing pending updates."""
    items: List[PendingUpdate]
    total: int
    skip: int
    limit: int


class ListPendingUpdatesUseCase:
    """Use case for listing pending updates."""
    
    def __init__(self, repository: IPendingUpdateRepository):
        self.repository = repository
    
    async def execute(self, input_data: ListPendingUpdatesInput) -> ListPendingUpdatesOutput:
        """List pending updates with pagination and filters."""
        items = await self.repository.list(
            skip=input_data.skip,
            limit=input_data.limit,
            status=input_data.status,
            source_id=input_data.source_id,
            category=input_data.category,
            detection_type=input_data.detection_type,
        )
        
        total = await self.repository.count(
            status=input_data.status,
            source_id=input_data.source_id,
            category=input_data.category,
        )
        
        return ListPendingUpdatesOutput(
            items=items,
            total=total,
            skip=input_data.skip,
            limit=input_data.limit,
        )
