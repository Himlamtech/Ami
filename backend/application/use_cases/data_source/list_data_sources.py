"""List data sources use case."""

from dataclasses import dataclass
from typing import Optional, List

from domain.entities.data_source import DataSource
from domain.enums.data_source import SourceStatus, DataCategory
from application.interfaces.repositories.data_source_repository import (
    IDataSourceRepository,
)


@dataclass
class ListDataSourcesInput:
    """Input for listing data sources."""

    skip: int = 0
    limit: int = 50
    status: Optional[SourceStatus] = None
    category: Optional[DataCategory] = None
    is_active: Optional[bool] = None


@dataclass
class ListDataSourcesOutput:
    """Output from listing data sources."""

    sources: List[DataSource]
    total: int
    skip: int
    limit: int


class ListDataSourcesUseCase:
    """Use case for listing data sources."""

    def __init__(self, repository: IDataSourceRepository):
        self.repository = repository

    async def execute(self, input_data: ListDataSourcesInput) -> ListDataSourcesOutput:
        """List data sources with pagination and filters."""
        sources = await self.repository.list(
            skip=input_data.skip,
            limit=input_data.limit,
            status=input_data.status,
            category=input_data.category,
            is_active=input_data.is_active,
        )

        total = await self.repository.count(
            status=input_data.status,
            category=input_data.category,
            is_active=input_data.is_active,
        )

        return ListDataSourcesOutput(
            sources=sources,
            total=total,
            skip=input_data.skip,
            limit=input_data.limit,
        )
