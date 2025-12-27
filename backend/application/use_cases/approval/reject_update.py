"""Reject update use case."""

from dataclasses import dataclass
from typing import Optional

from application.interfaces.repositories.pending_update_repository import (
    IPendingUpdateRepository,
)


@dataclass
class RejectUpdateInput:
    """Input for rejecting an update."""

    pending_id: str
    reviewer_id: str
    note: Optional[str] = None


@dataclass
class RejectUpdateOutput:
    """Output from rejecting an update."""

    success: bool
    message: str


class RejectUpdateUseCase:
    """Use case for rejecting a pending update."""

    def __init__(self, repository: IPendingUpdateRepository):
        self.repository = repository

    async def execute(self, input_data: RejectUpdateInput) -> RejectUpdateOutput:
        """Reject a pending update."""
        # Get pending item
        pending = await self.repository.get_by_id(input_data.pending_id)
        if not pending:
            raise ValueError(f"Pending update '{input_data.pending_id}' not found")

        if not pending.is_pending():
            raise ValueError(
                f"Update already processed with status: {pending.status.value}"
            )

        # Mark as rejected
        pending.reject(input_data.reviewer_id, input_data.note)
        await self.repository.update(pending)

        return RejectUpdateOutput(
            success=True,
            message="Update rejected",
        )
