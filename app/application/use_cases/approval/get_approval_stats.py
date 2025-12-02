"""Get approval stats use case."""

from dataclasses import dataclass
from typing import Dict, Any

from app.application.interfaces.repositories.pending_update_repository import IPendingUpdateRepository


@dataclass
class GetApprovalStatsOutput:
    """Output from getting approval stats."""
    total_pending: int
    total_approved: int
    total_rejected: int
    by_category: Dict[str, int]
    by_detection_type: Dict[str, int]
    by_source: Dict[str, int]


class GetApprovalStatsUseCase:
    """Use case for getting approval queue statistics."""
    
    def __init__(self, repository: IPendingUpdateRepository):
        self.repository = repository
    
    async def execute(self) -> GetApprovalStatsOutput:
        """Get approval queue statistics."""
        stats = await self.repository.get_stats()
        
        return GetApprovalStatsOutput(
            total_pending=stats.get("total_pending", 0),
            total_approved=stats.get("total_approved", 0),
            total_rejected=stats.get("total_rejected", 0),
            by_category=stats.get("by_category", {}),
            by_detection_type=stats.get("by_detection_type", {}),
            by_source=stats.get("by_source", {}),
        )
