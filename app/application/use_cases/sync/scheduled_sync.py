"""Scheduled sync use case for automatic data source synchronization."""

from dataclasses import dataclass, field
from typing import List, Optional, Dict, Any
from datetime import datetime
import logging

from app.domain.entities.data_source import DataSource
from app.domain.enums.data_source import SourceStatus
from app.application.interfaces.repositories.data_source_repository import (
    IDataSourceRepository,
)
from app.application.interfaces.services.scheduler_service import ISchedulerService
from app.application.use_cases.sync.change_detector import ChangeDetectorUseCase

logger = logging.getLogger(__name__)


@dataclass
class ScheduledSyncInput:
    """Input for scheduled sync configuration."""

    data_source_id: str
    schedule_type: str = "interval"  # "interval" or "cron"
    # Interval settings
    interval_hours: int = 24
    # Cron settings (for advanced scheduling)
    cron_hour: Optional[int] = None
    cron_minute: int = 0
    cron_day_of_week: Optional[str] = None  # "mon,wed,fri" etc.


@dataclass
class ScheduledSyncOutput:
    """Output from scheduled sync setup."""

    success: bool
    job_id: Optional[str] = None
    next_run_time: Optional[datetime] = None
    message: str = ""


@dataclass
class SyncJobResult:
    """Result from a sync job execution."""

    data_source_id: str
    status: str  # "success", "partial", "failed"
    documents_processed: int = 0
    documents_added: int = 0
    documents_updated: int = 0
    documents_deleted: int = 0
    errors: List[str] = field(default_factory=list)
    duration_seconds: float = 0.0
    started_at: datetime = field(default_factory=datetime.now)
    completed_at: Optional[datetime] = None


class ScheduledSyncUseCase:
    """
    Use Case: Schedule automatic data source synchronization.

    Business Rules:
    1. Only active data sources can be scheduled
    2. Each data source has at most one active sync job
    3. Sync jobs persist across restarts (MongoDB JobStore)
    4. Failed syncs are logged but don't disable the schedule

    Single Responsibility: Managing sync schedules
    """

    def __init__(
        self,
        data_source_repository: IDataSourceRepository,
        scheduler_service: ISchedulerService,
        sync_executor: "SyncExecutor",  # Forward reference
    ):
        self.data_source_repo = data_source_repository
        self.scheduler = scheduler_service
        self.sync_executor = sync_executor

    async def schedule_sync(
        self, input_data: ScheduledSyncInput
    ) -> ScheduledSyncOutput:
        """
        Schedule a sync job for a data source.

        Args:
            input_data: Sync configuration

        Returns:
            ScheduledSyncOutput with job details
        """
        # 1. Validate data source exists and is active
        data_source = await self.data_source_repo.get_by_id(input_data.data_source_id)
        if not data_source:
            return ScheduledSyncOutput(
                success=False,
                message=f"Data source {input_data.data_source_id} not found",
            )

        if data_source.status != SourceStatus.ACTIVE:
            return ScheduledSyncOutput(
                success=False,
                message=f"Data source is not active (status: {data_source.status.value})",
            )

        # 2. Build job ID
        job_id = f"sync_{input_data.data_source_id}"

        # 3. Create sync function
        async def sync_job():
            await self._execute_sync(input_data.data_source_id)

        # 4. Configure trigger
        trigger_args: Dict[str, Any] = {}
        if input_data.schedule_type == "interval":
            trigger_args["hours"] = input_data.interval_hours
        else:  # cron
            trigger_args["hour"] = input_data.cron_hour or 2  # Default 2 AM
            trigger_args["minute"] = input_data.cron_minute
            if input_data.cron_day_of_week:
                trigger_args["day_of_week"] = input_data.cron_day_of_week

        # 5. Add job to scheduler
        success = self.scheduler.add_job(
            job_id=job_id,
            func=sync_job,
            trigger=input_data.schedule_type,
            **trigger_args,
        )

        if not success:
            return ScheduledSyncOutput(
                success=False, message="Failed to schedule sync job"
            )

        # 6. Get next run time
        job_info = self.scheduler.get_job(job_id)
        next_run = None
        if job_info and job_info.get("next_run_time"):
            next_run = datetime.fromisoformat(job_info["next_run_time"])

        # 7. Update data source with sync schedule
        data_source.sync_schedule = {
            "type": input_data.schedule_type,
            "interval_hours": (
                input_data.interval_hours
                if input_data.schedule_type == "interval"
                else None
            ),
            "cron_hour": input_data.cron_hour,
            "cron_minute": input_data.cron_minute,
            "cron_day_of_week": input_data.cron_day_of_week,
            "job_id": job_id,
            "next_run_time": next_run.isoformat() if next_run else None,
        }
        await self.data_source_repo.update(data_source)

        logger.info(
            f"Scheduled sync for {input_data.data_source_id}, next run: {next_run}"
        )

        return ScheduledSyncOutput(
            success=True,
            job_id=job_id,
            next_run_time=next_run,
            message="Sync scheduled successfully",
        )

    async def cancel_sync(self, data_source_id: str) -> bool:
        """Cancel scheduled sync for a data source."""
        job_id = f"sync_{data_source_id}"

        if self.scheduler.job_exists(job_id):
            success = self.scheduler.remove_job(job_id)

            # Update data source
            data_source = await self.data_source_repo.get_by_id(data_source_id)
            if data_source:
                data_source.sync_schedule = None
                await self.data_source_repo.update(data_source)

            logger.info(f"Cancelled sync for {data_source_id}")
            return success

        return True  # Already not scheduled

    async def pause_sync(self, data_source_id: str) -> bool:
        """Pause sync without removing schedule."""
        job_id = f"sync_{data_source_id}"
        return self.scheduler.pause_job(job_id)

    async def resume_sync(self, data_source_id: str) -> bool:
        """Resume paused sync."""
        job_id = f"sync_{data_source_id}"
        return self.scheduler.resume_job(job_id)

    async def trigger_immediate_sync(self, data_source_id: str) -> SyncJobResult:
        """Trigger an immediate sync outside of schedule."""
        return await self._execute_sync(data_source_id)

    async def _execute_sync(self, data_source_id: str) -> SyncJobResult:
        """Execute the actual sync process."""
        import time

        start_time = time.time()

        result = SyncJobResult(
            data_source_id=data_source_id,
            status="pending",
        )

        try:
            # Delegate to sync executor
            sync_result = await self.sync_executor.sync_data_source(data_source_id)

            result.status = sync_result.get("status", "success")
            result.documents_processed = sync_result.get("documents_processed", 0)
            result.documents_added = sync_result.get("documents_added", 0)
            result.documents_updated = sync_result.get("documents_updated", 0)
            result.documents_deleted = sync_result.get("documents_deleted", 0)
            result.errors = sync_result.get("errors", [])

        except Exception as e:
            logger.error(f"Sync failed for {data_source_id}: {e}")
            result.status = "failed"
            result.errors.append(str(e))

        result.duration_seconds = time.time() - start_time
        result.completed_at = datetime.now()

        # Update data source last_synced_at
        data_source = await self.data_source_repo.get_by_id(data_source_id)
        if data_source:
            data_source.last_synced_at = result.completed_at
            await self.data_source_repo.update(data_source)

        return result

    def list_scheduled_syncs(self) -> List[Dict[str, Any]]:
        """List all scheduled sync jobs."""
        all_jobs = self.scheduler.list_jobs()
        return [job for job in all_jobs if job["id"].startswith("sync_")]


class SyncExecutor:
    """
    Executor for data source synchronization.

    Handles the actual crawling/fetching of data from sources.
    """

    def __init__(
        self,
        data_source_repository: IDataSourceRepository,
        document_repository,  # IDocumentRepository
        change_detector: ChangeDetectorUseCase,
    ):
        self.data_source_repo = data_source_repository
        self.document_repo = document_repository
        self.change_detector = change_detector

    async def sync_data_source(self, data_source_id: str) -> Dict[str, Any]:
        """
        Sync a data source - fetch new/updated content.

        Returns:
            Dict with sync results
        """
        data_source = await self.data_source_repo.get_by_id(data_source_id)
        if not data_source:
            return {"status": "failed", "errors": ["Data source not found"]}

        result: Dict[str, Any] = {
            "status": "success",
            "documents_processed": 0,
            "documents_added": 0,
            "documents_updated": 0,
            "documents_deleted": 0,
            "errors": [],
        }

        try:
            # 1. Fetch content from source based on type
            if data_source.source_type.value == "web":
                content_items = await self._fetch_web_content(data_source)
            elif data_source.source_type.value == "file":
                content_items = await self._fetch_file_content(data_source)
            elif data_source.source_type.value == "api":
                content_items = await self._fetch_api_content(data_source)
            else:
                content_items = []

            # 2. Process each content item
            for item in content_items:
                result["documents_processed"] += 1

                # Check for changes using content hash
                change_result = await self.change_detector.detect_change(
                    content=item["content"],
                    source_url=item.get("url", ""),
                    data_source_id=data_source_id,
                )

                if change_result.is_new:
                    # Create new document
                    result["documents_added"] += 1
                elif change_result.is_modified:
                    # Update existing document
                    result["documents_updated"] += 1
                # else: unchanged, skip

            # 3. Check for deleted content (items that exist in DB but not in source)
            # This would require tracking source URLs

        except Exception as e:
            logger.error(f"Sync error: {e}")
            result["status"] = (
                "partial" if result["documents_processed"] > 0 else "failed"
            )
            result["errors"].append(str(e))

        return result

    async def _fetch_web_content(self, data_source: DataSource) -> List[Dict[str, Any]]:
        """Fetch content from web source."""
        # TODO: Integrate with crawler service
        logger.info(f"Fetching web content from {data_source.base_url}")
        return []

    async def _fetch_file_content(
        self, data_source: DataSource
    ) -> List[Dict[str, Any]]:
        """Fetch content from file source (Google Drive, etc.)."""
        # TODO: Integrate with file storage service
        logger.info(f"Fetching file content from {data_source.base_url}")
        return []

    async def _fetch_api_content(self, data_source: DataSource) -> List[Dict[str, Any]]:
        """Fetch content from API source."""
        # TODO: Integrate with API client
        logger.info(f"Fetching API content from {data_source.base_url}")
        return []
