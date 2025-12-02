"""Data source repository interface."""

from abc import ABC, abstractmethod
from typing import Optional, List

from app.domain.entities.data_source import DataSource
from app.domain.enums.data_source import SourceStatus, DataCategory


class IDataSourceRepository(ABC):
    """Repository interface for DataSource entity."""
    
    @abstractmethod
    async def create(self, source: DataSource) -> DataSource:
        """Create new data source."""
        pass
    
    @abstractmethod
    async def get_by_id(self, source_id: str) -> Optional[DataSource]:
        """Get data source by ID."""
        pass
    
    @abstractmethod
    async def update(self, source: DataSource) -> DataSource:
        """Update data source."""
        pass
    
    @abstractmethod
    async def delete(self, source_id: str) -> bool:
        """Delete data source."""
        pass
    
    @abstractmethod
    async def list(
        self,
        skip: int = 0,
        limit: int = 100,
        status: Optional[SourceStatus] = None,
        category: Optional[DataCategory] = None,
        is_active: Optional[bool] = None,
    ) -> List[DataSource]:
        """List data sources with filters."""
        pass
    
    @abstractmethod
    async def count(
        self,
        status: Optional[SourceStatus] = None,
        category: Optional[DataCategory] = None,
        is_active: Optional[bool] = None,
    ) -> int:
        """Count data sources with filters."""
        pass
    
    @abstractmethod
    async def get_active_sources(self) -> List[DataSource]:
        """Get all active data sources for scheduling."""
        pass
    
    @abstractmethod
    async def get_by_url(self, base_url: str) -> Optional[DataSource]:
        """Get data source by base URL (for duplicate check)."""
        pass
    
    @abstractmethod
    async def update_crawl_stats(
        self,
        source_id: str,
        success: bool,
        docs_count: int = 0,
        error: Optional[str] = None,
    ) -> bool:
        """Update crawl statistics after job completion."""
        pass
