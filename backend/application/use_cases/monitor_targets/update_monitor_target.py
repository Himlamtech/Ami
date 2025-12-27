"""Update monitor target use case."""

from dataclasses import dataclass
from typing import Optional, Dict
from datetime import datetime

from domain.entities.monitor_target import MonitorTarget
from application.interfaces.repositories.monitor_target_repository import (
    IMonitorTargetRepository,
)


@dataclass
class UpdateMonitorTargetInput:
    target_id: str
    name: Optional[str] = None
    url: Optional[str] = None
    collection: Optional[str] = None
    category: Optional[str] = None
    interval_hours: Optional[int] = None
    selector: Optional[str] = None
    metadata: Optional[Dict[str, str]] = None
    is_active: Optional[bool] = None


@dataclass
class UpdateMonitorTargetOutput:
    target: MonitorTarget
    message: str


class UpdateMonitorTargetUseCase:
    """Update monitor target information."""

    def __init__(self, repository: IMonitorTargetRepository):
        self.repository = repository

    async def execute(
        self, input_data: UpdateMonitorTargetInput
    ) -> UpdateMonitorTargetOutput:
        target = await self.repository.get_by_id(input_data.target_id)
        if not target:
            raise ValueError(f"Monitor target {input_data.target_id} not found")

        if input_data.name:
            target.name = input_data.name
        if input_data.url:
            target.url = input_data.url
        if input_data.collection:
            target.collection = input_data.collection
        if input_data.category:
            target.category = input_data.category
        if input_data.interval_hours:
            target.interval_hours = input_data.interval_hours
        if input_data.selector is not None:
            target.selector = input_data.selector
        if input_data.metadata is not None:
            target.metadata = input_data.metadata
        if input_data.is_active is not None:
            target.is_active = input_data.is_active

        target.updated_at = datetime.now()
        updated = await self.repository.update(target)
        return UpdateMonitorTargetOutput(
            target=updated,
            message="Monitor target updated",
        )
