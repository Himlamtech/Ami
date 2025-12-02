"""Pending update repository interface."""

from abc import ABC, abstractmethod
from typing import Optional, List, Dict, Any

from app.domain.entities.pending_update import PendingUpdate
from app.domain.enums.data_source import PendingStatus, UpdateDetectionType, DataCategory


class IPendingUpdateRepository(ABC):
    """Repository interface for PendingUpdate entity."""
    
    @abstractmethod
    async def create(self, pending: PendingUpdate) -> PendingUpdate:
        """Create new pending update."""
        pass
    
    @abstractmethod
    async def get_by_id(self, pending_id: str) -> Optional[PendingUpdate]:
        """Get pending update by ID."""
        pass
    
    @abstractmethod
    async def update(self, pending: PendingUpdate) -> PendingUpdate:
        """Update pending update."""
        pass
    
    @abstractmethod
    async def delete(self, pending_id: str) -> bool:
        """Delete pending update."""
        pass
    
    @abstractmethod
    async def list(
        self,
        skip: int = 0,
        limit: int = 100,
        status: Optional[PendingStatus] = None,
        source_id: Optional[str] = None,
        category: Optional[DataCategory] = None,
        detection_type: Optional[UpdateDetectionType] = None,
    ) -> List[PendingUpdate]:
        """List pending updates with filters."""
        pass
    
    @abstractmethod
    async def count(
        self,
        status: Optional[PendingStatus] = None,
        source_id: Optional[str] = None,
        category: Optional[DataCategory] = None,
    ) -> int:
        """Count pending updates with filters."""
        pass
    
    @abstractmethod
    async def get_pending_queue(
        self,
        skip: int = 0,
        limit: int = 50,
    ) -> List[PendingUpdate]:
        """Get pending items sorted by priority and date."""
        pass
    
    @abstractmethod
    async def check_duplicate(self, content_hash: str) -> bool:
        """Check if content already exists by hash."""
        pass
    
    @abstractmethod
    async def bulk_approve(self, pending_ids: List[str], reviewer_id: str) -> int:
        """Bulk approve pending updates. Returns count approved."""
        pass
    
    @abstractmethod
    async def bulk_reject(self, pending_ids: List[str], reviewer_id: str) -> int:
        """Bulk reject pending updates. Returns count rejected."""
        pass
    
    @abstractmethod
    async def expire_old(self) -> int:
        """Mark expired items as EXPIRED. Returns count expired."""
        pass
    
    @abstractmethod
    async def get_stats(self) -> Dict[str, Any]:
        """Get approval queue statistics."""
        pass
