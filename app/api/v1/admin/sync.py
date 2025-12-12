"""Admin sync management routes."""

from fastapi import APIRouter, HTTPException, status, BackgroundTasks
from pydantic import BaseModel, Field
from typing import Optional, List, Dict, Any
from datetime import datetime

from app.infrastructure.factory import get_factory

router = APIRouter(prefix="/admin/sync", tags=["admin-sync"])


# ========== DTOs ==========


class ScheduleSyncRequest(BaseModel):
    """Request to schedule sync for a data source."""

    data_source_id: str
    schedule_type: str = Field("interval", pattern="^(interval|cron)$")
    interval_hours: int = Field(24, ge=1, le=168)  # 1 hour to 1 week
    cron_hour: Optional[int] = Field(None, ge=0, le=23)
    cron_minute: int = Field(0, ge=0, le=59)
    cron_day_of_week: Optional[str] = None  # "mon,wed,fri" etc


class SyncJobResponse(BaseModel):
    """Response with sync job info."""

    job_id: str
    data_source_id: str
    next_run_time: Optional[datetime] = None
    trigger: str
    status: str


class ValidationRequest(BaseModel):
    """Request to validate content."""

    content: str
    metadata: dict = Field(default_factory=dict)
    check_links: bool = False


class ValidationIssueResponse(BaseModel):
    """Single validation issue."""

    code: str
    message: str
    severity: str
    field: Optional[str] = None
    suggestion: Optional[str] = None


class ValidationResponse(BaseModel):
    """Validation result response."""

    is_valid: bool
    score: float
    issues: List[ValidationIssueResponse]


class SyncResultResponse(BaseModel):
    """Sync execution result."""

    data_source_id: str
    status: str
    documents_processed: int
    documents_added: int
    documents_updated: int
    documents_deleted: int
    errors: List[str]
    duration_seconds: float


# ========== Scheduler Endpoints ==========


@router.post("/schedule", response_model=SyncJobResponse)
async def schedule_sync(request: ScheduleSyncRequest):
    """
    Schedule automatic sync for a data source.

    Sync will run automatically based on schedule.
    """
    try:
        factory = get_factory()

        # Get scheduler service
        scheduler = factory.get_scheduler_service()
        if not scheduler:
            raise HTTPException(
                status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
                detail="Scheduler service not available",
            )

        # Get data source repo
        data_source_repo = factory.data_source_repository

        # Validate data source exists
        data_source = await data_source_repo.get_by_id(request.data_source_id)
        if not data_source:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Data source {request.data_source_id} not found",
            )

        # Build job ID
        job_id = f"sync_{request.data_source_id}"

        # Configure trigger args
        trigger_args: Dict[str, Any] = {}
        if request.schedule_type == "interval":
            trigger_args["hours"] = request.interval_hours
        else:
            trigger_args["hour"] = request.cron_hour or 2
            trigger_args["minute"] = request.cron_minute
            if request.cron_day_of_week:
                trigger_args["day_of_week"] = request.cron_day_of_week

        # Create sync job function (placeholder - will be replaced with actual sync)
        async def sync_job():
            # This would call the actual sync executor
            pass

        # Add job
        success = scheduler.add_job(
            job_id=job_id,
            func=sync_job,
            trigger=request.schedule_type,
            **trigger_args,
        )

        if not success:
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail="Failed to schedule sync job",
            )

        # Get job info
        job_info = scheduler.get_job(job_id)

        return SyncJobResponse(
            job_id=job_id,
            data_source_id=request.data_source_id,
            next_run_time=(
                datetime.fromisoformat(job_info["next_run_time"])
                if job_info and job_info.get("next_run_time")
                else None
            ),
            trigger=request.schedule_type,
            status="scheduled",
        )

    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to schedule sync: {str(e)}",
        )


@router.delete("/schedule/{data_source_id}")
async def cancel_sync(data_source_id: str):
    """Cancel scheduled sync for a data source."""
    try:
        factory = get_factory()
        scheduler = factory.get_scheduler_service()

        if not scheduler:
            raise HTTPException(
                status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
                detail="Scheduler service not available",
            )

        job_id = f"sync_{data_source_id}"

        if scheduler.job_exists(job_id):
            scheduler.remove_job(job_id)

        return {"message": f"Sync cancelled for {data_source_id}"}

    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to cancel sync: {str(e)}",
        )


@router.post("/schedule/{data_source_id}/pause")
async def pause_sync(data_source_id: str):
    """Pause scheduled sync."""
    try:
        factory = get_factory()
        scheduler = factory.get_scheduler_service()

        if not scheduler:
            raise HTTPException(
                status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
                detail="Scheduler service not available",
            )

        job_id = f"sync_{data_source_id}"
        success = scheduler.pause_job(job_id)

        if not success:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Sync job not found for {data_source_id}",
            )

        return {"message": f"Sync paused for {data_source_id}"}

    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to pause sync: {str(e)}",
        )


@router.post("/schedule/{data_source_id}/resume")
async def resume_sync(data_source_id: str):
    """Resume paused sync."""
    try:
        factory = get_factory()
        scheduler = factory.get_scheduler_service()

        if not scheduler:
            raise HTTPException(
                status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
                detail="Scheduler service not available",
            )

        job_id = f"sync_{data_source_id}"
        success = scheduler.resume_job(job_id)

        if not success:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Sync job not found for {data_source_id}",
            )

        return {"message": f"Sync resumed for {data_source_id}"}

    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to resume sync: {str(e)}",
        )


@router.get("/jobs", response_model=List[SyncJobResponse])
async def list_sync_jobs():
    """List all scheduled sync jobs."""
    try:
        factory = get_factory()
        scheduler = factory.get_scheduler_service()

        if not scheduler:
            raise HTTPException(
                status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
                detail="Scheduler service not available",
            )

        all_jobs = scheduler.list_jobs()
        sync_jobs = [job for job in all_jobs if job["id"].startswith("sync_")]

        return [
            SyncJobResponse(
                job_id=job["id"],
                data_source_id=job["id"].replace("sync_", ""),
                next_run_time=(
                    datetime.fromisoformat(job["next_run_time"])
                    if job.get("next_run_time")
                    else None
                ),
                trigger=job.get("trigger", ""),
                status="paused" if job.get("pending") else "active",
            )
            for job in sync_jobs
        ]

    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to list jobs: {str(e)}",
        )


# ========== Manual Sync Endpoints ==========


@router.post("/trigger/{data_source_id}", response_model=SyncResultResponse)
async def trigger_immediate_sync(
    data_source_id: str,
    background_tasks: BackgroundTasks,
):
    """
    Trigger immediate sync for a data source.

    Sync runs in background, returns immediately.
    """
    try:
        factory = get_factory()
        data_source_repo = factory.data_source_repository

        # Validate data source exists
        data_source = await data_source_repo.get_by_id(data_source_id)
        if not data_source:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Data source {data_source_id} not found",
            )

        # For now, return placeholder result
        # TODO: Implement actual sync in background task
        return SyncResultResponse(
            data_source_id=data_source_id,
            status="started",
            documents_processed=0,
            documents_added=0,
            documents_updated=0,
            documents_deleted=0,
            errors=[],
            duration_seconds=0,
        )

    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to trigger sync: {str(e)}",
        )


# ========== Validation Endpoints ==========


@router.post("/validate", response_model=ValidationResponse)
async def validate_content(request: ValidationRequest):
    """
    Validate content quality.

    Checks:
    - Content length
    - Metadata completeness
    - Outdated markers
    - Broken links (optional)
    """
    from app.application.use_cases.validation import QualityValidatorUseCase

    try:
        validator = QualityValidatorUseCase()

        result = await validator.validate(
            content=request.content,
            metadata=request.metadata,
            check_links=request.check_links,
        )

        return ValidationResponse(
            is_valid=result.is_valid,
            score=result.score,
            issues=[
                ValidationIssueResponse(
                    code=issue.code,
                    message=issue.message,
                    severity=issue.severity.value,
                    field=issue.field,
                    suggestion=issue.suggestion,
                )
                for issue in result.issues
            ],
        )

    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Validation failed: {str(e)}",
        )


@router.post("/validate/batch")
async def batch_validate_content(documents: List[ValidationRequest]):
    """Batch validate multiple documents."""
    from app.application.use_cases.validation import QualityValidatorUseCase

    try:
        validator = QualityValidatorUseCase()

        results = []
        for doc in documents:
            result = await validator.validate(
                content=doc.content,
                metadata=doc.metadata,
                check_links=doc.check_links,
            )
            results.append(
                {
                    "is_valid": result.is_valid,
                    "score": result.score,
                    "issues_count": len(result.issues),
                }
            )

        return {
            "total": len(results),
            "valid_count": sum(1 for r in results if r["is_valid"]),
            "average_score": (
                sum(r["score"] for r in results) / len(results) if results else 0
            ),
            "results": results,
        }

    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Batch validation failed: {str(e)}",
        )
