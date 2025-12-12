"""Crawler routes - Protected by Admin API Key."""

from fastapi import APIRouter, Depends, HTTPException, status
from typing import List

from app.api.schemas.crawler_dto import (
    CreateCrawlJobRequest,
    CrawlJobResponse,
)
from app.api.dependencies.auth import verify_admin_api_key
from app.domain.enums.crawl_status import CrawlJobType
from app.domain.entities.crawl_job import CrawlJob
from datetime import datetime
from app.infrastructure.factory import get_factory


router = APIRouter(
    prefix="/admin/crawler",
    tags=["admin-crawler"],
    dependencies=[Depends(verify_admin_api_key)],
)


@router.post("/jobs", response_model=CrawlJobResponse)
async def create_crawl_job(
    request: CreateCrawlJobRequest,
):
    """Create new crawl job (admin only)."""
    factory = get_factory()
    crawler_repo = factory.get_crawler_repository()

    # Create job entity
    job = CrawlJob(
        id="",
        created_by="admin",
        job_type=CrawlJobType.SCRAPE,
        url=request.url,
        collection=request.collection,
        max_depth=request.max_depth,
        limit=request.limit,
        auto_ingest=request.auto_ingest,
        created_at=datetime.now(),
    )

    # Save job
    created_job = await crawler_repo.create_job(job)

    return CrawlJobResponse(
        id=created_job.id,
        url=created_job.url,
        status=created_job.status.value,
        total_pages=created_job.total_pages,
        successful_pages=created_job.successful_pages,
        failed_pages=created_job.failed_pages,
        created_at=created_job.created_at,
    )


@router.get("/jobs", response_model=List[CrawlJobResponse])
async def list_crawl_jobs(skip: int = 0, limit: int = 100):
    """List crawl jobs."""
    factory = get_factory()
    crawler_repo = factory.get_crawler_repository()

    jobs = await crawler_repo.list_jobs(skip=skip, limit=limit)

    return [
        CrawlJobResponse(
            id=job.id,
            url=job.url or "",
            status=job.status.value,
            total_pages=job.total_pages,
            successful_pages=job.successful_pages,
            failed_pages=job.failed_pages,
            created_at=job.created_at,
        )
        for job in jobs
    ]


@router.get("/jobs/{job_id}", response_model=CrawlJobResponse)
async def get_crawl_job(job_id: str):
    """Get crawl job details."""
    factory = get_factory()
    crawler_repo = factory.get_crawler_repository()

    job = await crawler_repo.get_job_by_id(job_id)

    if not job:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="Job not found"
        )

    return CrawlJobResponse(
        id=job.id,
        url=job.url or "",
        status=job.status.value,
        total_pages=job.total_pages,
        successful_pages=job.successful_pages,
        failed_pages=job.failed_pages,
        created_at=job.created_at,
    )
