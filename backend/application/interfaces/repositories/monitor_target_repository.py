"""Repository interface for monitor targets."""

from abc import ABC, abstractmethod
from typing import List, Optional
from datetime import datetime

from domain.entities.monitor_target import MonitorTarget


class IMonitorTargetRepository(ABC):
    """Repository contract for monitor targets."""

    @abstractmethod
    async def create(self, target: MonitorTarget) -> MonitorTarget:
        pass

    @abstractmethod
    async def update(self, target: MonitorTarget) -> MonitorTarget:
        pass

    @abstractmethod
    async def delete(self, target_id: str) -> bool:
        pass

    @abstractmethod
    async def get_by_id(self, target_id: str) -> Optional[MonitorTarget]:
        pass

    @abstractmethod
    async def list(self, skip: int = 0, limit: int = 100) -> List[MonitorTarget]:
        pass

    @abstractmethod
    async def get_due_targets(
        self, now: Optional[datetime] = None
    ) -> List[MonitorTarget]:
        pass
