"""Crawler repository interface."""

from abc import ABC, abstractmethod
from typing import Optional, List, Dict, Any
from domain.entities.crawl_job import CrawlJob
from domain.enums.crawl_status import CrawlJobStatus


class ICrawlerRepository(ABC):
    """
    Repository interface for CrawlJob entity.

    Handles crawler job and history persistence.
    """

    @abstractmethod
    async def create_job(self, job: CrawlJob) -> CrawlJob:
        """Create new crawl job."""
        pass

    @abstractmethod
    async def get_job_by_id(self, job_id: str) -> Optional[CrawlJob]:
        """Get crawl job by ID."""
        pass

    @abstractmethod
    async def update_job(self, job: CrawlJob) -> CrawlJob:
        """Update existing crawl job."""
        pass

    @abstractmethod
    async def delete_job(self, job_id: str) -> bool:
        """Delete crawl job."""
        pass

    @abstractmethod
    async def list_jobs(
        self,
        skip: int = 0,
        limit: int = 100,
        status: Optional[CrawlJobStatus] = None,
        created_by: Optional[str] = None,
    ) -> List[CrawlJob]:
        """
        List crawl jobs with filters.

        Args:
            skip: Number to skip
            limit: Maximum to return
            status: Filter by job status
            created_by: Filter by creator user ID

        Returns:
            List of crawl jobs
        """
        pass

    @abstractmethod
    async def count_jobs(
        self,
        status: Optional[CrawlJobStatus] = None,
        created_by: Optional[str] = None,
    ) -> int:
        """Count crawl jobs with filters."""
        pass

    @abstractmethod
    async def get_running_jobs(self) -> List[CrawlJob]:
        """Get all currently running jobs."""
        pass

    @abstractmethod
    async def get_scheduled_jobs(self) -> List[CrawlJob]:
        """Get all scheduled jobs (with cron schedule)."""
        pass

    @abstractmethod
    async def get_crawler_stats(self) -> Dict[str, Any]:
        """
        Get crawler statistics.

        Returns:
            Dictionary with stats:
            - total_jobs: Total number of jobs
            - jobs_by_status: Count by status
            - total_pages_crawled: Sum of all pages
            - total_successful: Sum of successful pages
            - total_failed: Sum of failed pages
            - avg_success_rate: Average success rate
        """
        pass
