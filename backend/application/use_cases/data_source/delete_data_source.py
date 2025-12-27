"""Delete data source use case."""

from dataclasses import dataclass

from application.interfaces.repositories.data_source_repository import (
    IDataSourceRepository,
)


@dataclass
class DeleteDataSourceInput:
    """Input for deleting a data source."""

    source_id: str


@dataclass
class DeleteDataSourceOutput:
    """Output from deleting a data source."""

    success: bool
    message: str


class DeleteDataSourceUseCase:
    """Use case for deleting a data source."""

    def __init__(self, repository: IDataSourceRepository):
        self.repository = repository

    async def execute(
        self, input_data: DeleteDataSourceInput
    ) -> DeleteDataSourceOutput:
        """Delete a data source by ID."""
        # Check exists
        source = await self.repository.get_by_id(input_data.source_id)
        if not source:
            raise ValueError(f"Data source '{input_data.source_id}' not found")

        # Delete
        deleted = await self.repository.delete(input_data.source_id)

        if deleted:
            return DeleteDataSourceOutput(
                success=True,
                message=f"Data source '{source.name}' deleted successfully",
            )
        else:
            return DeleteDataSourceOutput(
                success=False,
                message=f"Failed to delete data source '{source.name}'",
            )
