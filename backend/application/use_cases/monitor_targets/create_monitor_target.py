"""Create monitor target use case."""

from dataclasses import dataclass
from typing import Optional, Dict
from datetime import datetime

from app.domain.entities.monitor_target import MonitorTarget
from app.application.interfaces.repositories.monitor_target_repository import (
    IMonitorTargetRepository,
)


@dataclass
class CreateMonitorTargetInput:
    name: str
    url: str
    collection: str = "default"
    category: str = "general"
    interval_hours: int = 6
    selector: Optional[str] = None
    metadata: Optional[Dict[str, str]] = None


@dataclass
class CreateMonitorTargetOutput:
    target: MonitorTarget
    message: str


class CreateMonitorTargetUseCase:
    """Create monitor target entry."""

    def __init__(self, repository: IMonitorTargetRepository):
        self.repository = repository

    async def execute(
        self, input_data: CreateMonitorTargetInput
    ) -> CreateMonitorTargetOutput:
        target = MonitorTarget(
            id="",
            name=input_data.name,
            url=input_data.url,
            collection=input_data.collection,
            category=input_data.category,
            interval_hours=input_data.interval_hours,
            selector=input_data.selector,
            metadata=input_data.metadata or {},
            created_at=datetime.now(),
            updated_at=datetime.now(),
        )

        created = await self.repository.create(target)
        return CreateMonitorTargetOutput(
            target=created,
            message="Monitor target created",
        )
