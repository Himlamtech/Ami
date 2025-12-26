"""List monitor targets use case."""

from dataclasses import dataclass
from typing import List

from app.domain.entities.monitor_target import MonitorTarget
from app.application.interfaces.repositories.monitor_target_repository import (
    IMonitorTargetRepository,
)


@dataclass
class ListMonitorTargetsInput:
    skip: int = 0
    limit: int = 100


@dataclass
class ListMonitorTargetsOutput:
    items: List[MonitorTarget]
    total: int
    skip: int
    limit: int


class ListMonitorTargetsUseCase:
    """List monitor targets."""

    def __init__(self, repository: IMonitorTargetRepository):
        self.repository = repository

    async def execute(
        self, input_data: ListMonitorTargetsInput
    ) -> ListMonitorTargetsOutput:
        items = await self.repository.list(skip=input_data.skip, limit=input_data.limit)
        total = len(items)
        return ListMonitorTargetsOutput(
            items=items,
            total=total,
            skip=input_data.skip,
            limit=input_data.limit,
        )
