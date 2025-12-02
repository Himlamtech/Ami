"""Update data source use case."""

from dataclasses import dataclass
from typing import Optional, Dict, Any, List
from datetime import datetime

from app.domain.entities.data_source import DataSource, SourceAuth, CrawlConfig
from app.domain.enums.data_source import DataCategory, DataType, SourceType
from app.application.interfaces.repositories.data_source_repository import IDataSourceRepository


@dataclass
class UpdateDataSourceInput:
    """Input for updating a data source."""
    source_id: str
    name: Optional[str] = None
    base_url: Optional[str] = None
    source_type: Optional[SourceType] = None
    category: Optional[DataCategory] = None
    data_type: Optional[DataType] = None
    collection: Optional[str] = None
    schedule_cron: Optional[str] = None
    is_active: Optional[bool] = None
    priority: Optional[int] = None
    description: Optional[str] = None
    tags: Optional[List[str]] = None
    
    # Auth config
    auth_type: Optional[str] = None
    auth_username: Optional[str] = None
    auth_password: Optional[str] = None
    auth_token: Optional[str] = None
    auth_headers: Optional[Dict[str, str]] = None
    
    # Crawl config
    list_selector: Optional[str] = None
    detail_selector: Optional[str] = None
    title_selector: Optional[str] = None
    date_selector: Optional[str] = None
    max_depth: Optional[int] = None
    max_pages: Optional[int] = None
    rate_limit: Optional[int] = None


@dataclass
class UpdateDataSourceOutput:
    """Output from updating a data source."""
    source: DataSource
    message: str


class UpdateDataSourceUseCase:
    """Use case for updating an existing data source."""
    
    def __init__(self, repository: IDataSourceRepository):
        self.repository = repository
    
    async def execute(self, input_data: UpdateDataSourceInput) -> UpdateDataSourceOutput:
        """
        Update an existing data source.
        
        Only updates fields that are provided (not None).
        """
        # Get existing
        source = await self.repository.get_by_id(input_data.source_id)
        if not source:
            raise ValueError(f"Data source '{input_data.source_id}' not found")
        
        # Check URL duplicate if changing
        if input_data.base_url and input_data.base_url != source.base_url:
            existing = await self.repository.get_by_url(input_data.base_url)
            if existing and existing.id != source.id:
                raise ValueError(f"Data source with URL '{input_data.base_url}' already exists")
        
        # Update basic fields
        if input_data.name is not None:
            source.name = input_data.name
        if input_data.base_url is not None:
            source.base_url = input_data.base_url
        if input_data.source_type is not None:
            source.source_type = input_data.source_type
        if input_data.category is not None:
            source.category = input_data.category
        if input_data.data_type is not None:
            source.data_type = input_data.data_type
        if input_data.collection is not None:
            source.collection = input_data.collection
        if input_data.schedule_cron is not None:
            source.schedule_cron = input_data.schedule_cron
        if input_data.is_active is not None:
            source.is_active = input_data.is_active
        if input_data.priority is not None:
            source.priority = input_data.priority
        if input_data.description is not None:
            source.description = input_data.description
        if input_data.tags is not None:
            source.tags = input_data.tags
        
        # Update auth config
        if input_data.auth_type is not None:
            if input_data.auth_type == "none":
                source.auth = None
            else:
                source.auth = SourceAuth(
                    auth_type=input_data.auth_type,
                    username=input_data.auth_username,
                    password=input_data.auth_password,
                    token=input_data.auth_token,
                    headers=input_data.auth_headers,
                )
        
        # Update crawl config
        if source.crawl_config is None:
            source.crawl_config = CrawlConfig()
        
        if input_data.list_selector is not None:
            source.crawl_config.list_selector = input_data.list_selector
        if input_data.detail_selector is not None:
            source.crawl_config.detail_selector = input_data.detail_selector
        if input_data.title_selector is not None:
            source.crawl_config.title_selector = input_data.title_selector
        if input_data.date_selector is not None:
            source.crawl_config.date_selector = input_data.date_selector
        if input_data.max_depth is not None:
            source.crawl_config.max_depth = input_data.max_depth
        if input_data.max_pages is not None:
            source.crawl_config.max_pages = input_data.max_pages
        if input_data.rate_limit is not None:
            source.crawl_config.rate_limit = input_data.rate_limit
        
        source.updated_at = datetime.now()
        
        # Persist
        updated = await self.repository.update(source)
        
        return UpdateDataSourceOutput(
            source=updated,
            message=f"Data source '{updated.name}' updated successfully",
        )
