"""Create data source use case."""

import uuid
from dataclasses import dataclass
from typing import Optional, Dict, List
from datetime import datetime

from domain.entities.data_source import DataSource, SourceAuth, CrawlConfig
from domain.enums.data_source import DataCategory, DataType, SourceType
from application.interfaces.repositories.data_source_repository import (
    IDataSourceRepository,
)


@dataclass
class CreateDataSourceInput:
    """Input for creating a data source."""

    name: str
    base_url: str
    source_type: SourceType = SourceType.WEB_CRAWL
    category: DataCategory = DataCategory.GENERAL
    data_type: DataType = DataType.REALTIME
    collection: str = "default"
    schedule_cron: str = "0 */6 * * *"
    priority: int = 5
    description: Optional[str] = None
    tags: Optional[List[str]] = None

    # Auth config
    auth_type: str = "none"
    auth_username: Optional[str] = None
    auth_password: Optional[str] = None
    auth_token: Optional[str] = None
    auth_headers: Optional[Dict[str, str]] = None

    # Crawl config
    list_selector: Optional[str] = None
    detail_selector: Optional[str] = None
    title_selector: Optional[str] = None
    date_selector: Optional[str] = None
    max_depth: int = 2
    max_pages: int = 50
    rate_limit: int = 10

    created_by: Optional[str] = None


@dataclass
class CreateDataSourceOutput:
    """Output from creating a data source."""

    source: DataSource
    message: str


class CreateDataSourceUseCase:
    """Use case for creating a new data source."""

    def __init__(self, repository: IDataSourceRepository):
        self.repository = repository

    async def execute(
        self, input_data: CreateDataSourceInput
    ) -> CreateDataSourceOutput:
        """
        Create a new data source.

        Validation:
        - Check URL not duplicate
        - Validate cron expression format
        """
        # Check duplicate URL
        existing = await self.repository.get_by_url(input_data.base_url)
        if existing:
            raise ValueError(
                f"Data source with URL '{input_data.base_url}' already exists"
            )

        # Build auth config
        auth = None
        if input_data.auth_type != "none":
            auth = SourceAuth(
                auth_type=input_data.auth_type,
                username=input_data.auth_username,
                password=input_data.auth_password,
                token=input_data.auth_token,
                headers=input_data.auth_headers,
            )

        # Build crawl config
        crawl_config = CrawlConfig(
            list_selector=input_data.list_selector,
            detail_selector=input_data.detail_selector,
            title_selector=input_data.title_selector,
            date_selector=input_data.date_selector,
            max_depth=input_data.max_depth,
            max_pages=input_data.max_pages,
            rate_limit=input_data.rate_limit,
        )

        # Create entity
        source = DataSource(
            id=str(uuid.uuid4()),
            name=input_data.name,
            base_url=input_data.base_url,
            source_type=input_data.source_type,
            category=input_data.category,
            data_type=input_data.data_type,
            collection=input_data.collection,
            schedule_cron=input_data.schedule_cron,
            priority=input_data.priority,
            description=input_data.description,
            tags=input_data.tags or [],
            auth=auth,
            crawl_config=crawl_config,
            created_by=input_data.created_by,
            created_at=datetime.now(),
            updated_at=datetime.now(),
        )

        # Persist
        created = await self.repository.create(source)

        return CreateDataSourceOutput(
            source=created,
            message=f"Data source '{created.name}' created successfully",
        )
