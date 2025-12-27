"""Delete monitor target use case."""

from dataclasses import dataclass

from application.interfaces.repositories.monitor_target_repository import (
    IMonitorTargetRepository,
)


@dataclass
class DeleteMonitorTargetInput:
    target_id: str


@dataclass
class DeleteMonitorTargetOutput:
    success: bool


class DeleteMonitorTargetUseCase:
    """Delete a monitor target."""

    def __init__(self, repository: IMonitorTargetRepository):
        self.repository = repository

    async def execute(
        self, input_data: DeleteMonitorTargetInput
    ) -> DeleteMonitorTargetOutput:
        success = await self.repository.delete(input_data.target_id)
        return DeleteMonitorTargetOutput(success=success)
