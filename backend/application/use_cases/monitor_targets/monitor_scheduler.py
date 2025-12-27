"""Scheduler utilities for monitor targets."""

import logging

from app.config.services import ServiceRegistry
from app.application.use_cases.monitor_targets import RunMonitorTargetsUseCase

logger = logging.getLogger(__name__)


async def run_monitor_targets_job() -> None:
    """Run the monitor targets use case."""
    monitor_repo = ServiceRegistry.get_monitor_target_repository()
    web_crawler = ServiceRegistry.get_web_crawler()
    ingest_service = ServiceRegistry.get_document_ingest_service()
    use_case = RunMonitorTargetsUseCase(
        monitor_repository=monitor_repo,
        web_crawler=web_crawler,
        ingest_service=ingest_service,
    )
    await use_case.execute()


async def register_monitor_targets_job() -> None:
    """Ensure the monitor targets job is scheduled every 6 hours."""
    scheduler = ServiceRegistry.get_scheduler()
    await scheduler.start()

    job_id = "monitor_targets_job"

    scheduler.add_job(
        job_id=job_id,
        func=run_monitor_targets_job,
        trigger="interval",
        hours=6,
    )
    logger.info("Monitor targets job scheduled every 6 hours")
