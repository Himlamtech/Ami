"""
Crawler Management API routes.
Provides endpoints for managing crawl jobs, history, and statistics.
Protected by JWT authentication - requires ADMIN role.
"""

import logging
from typing import List, Optional

from fastapi import APIRouter, Depends, HTTPException, Query, status

from app.api.auth_dependencies import get_current_admin_user
from app.application.crawler_management_service import CrawlerManagementService
from app.application.factory import ProviderFactory
from app.core.mongodb_models import (
    CrawlHistoryResponse,
    CrawlJobCreate,
    CrawlJobResponse,
    CrawlJobStatus,
    CrawlJobType,
    CrawlerStatsResponse,
    UserInDB,
    WebsiteInfoResponse,
)

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/crawler", tags=["crawler"])


async def get_crawler_service() -> CrawlerManagementService:
    """Get crawler management service instance."""
    mongodb = await ProviderFactory.get_mongodb_client()
    return CrawlerManagementService(mongodb)


@router.post("/jobs", response_model=CrawlJobResponse, status_code=status.HTTP_201_CREATED)
async def create_crawl_job(
    job_data: CrawlJobCreate,
    current_admin: UserInDB = Depends(get_current_admin_user),
    service: CrawlerManagementService = Depends(get_crawler_service),
):
    """
    Create a new crawl job.
    Admin only.
    
    - Creates a job for scraping, crawling, or batch processing
    - Job can be scheduled with cron expression
    - Returns created job with ID
    """
    try:
        job = await service.create_job(job_data, current_admin.id)
        logger.info(f"Created crawl job {job.id} by {current_admin.username}")
        return job
    except Exception as e:
        logger.error(f"Failed to create crawl job: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to create job: {str(e)}",
        )


@router.get("/jobs", response_model=List[CrawlJobResponse])
async def list_crawl_jobs(
    skip: int = Query(0, ge=0),
    limit: int = Query(50, ge=1, le=100),
    status_filter: Optional[CrawlJobStatus] = Query(None, alias="status"),
    job_type: Optional[CrawlJobType] = Query(None, alias="type"),
    current_admin: UserInDB = Depends(get_current_admin_user),
    service: CrawlerManagementService = Depends(get_crawler_service),
):
    """
    List crawl jobs with optional filtering.
    Admin only.
    
    - Returns paginated list of jobs
    - Can filter by status and job type
    - Sorted by creation date (newest first)
    """
    try:
        jobs = await service.list_jobs(
            skip=skip, limit=limit, status=status_filter, job_type=job_type
        )
        return jobs
    except Exception as e:
        logger.error(f"Failed to list jobs: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to list jobs: {str(e)}",
        )


@router.get("/jobs/{job_id}", response_model=CrawlJobResponse)
async def get_crawl_job(
    job_id: str,
    current_admin: UserInDB = Depends(get_current_admin_user),
    service: CrawlerManagementService = Depends(get_crawler_service),
):
    """
    Get a specific crawl job by ID.
    Admin only.
    
    - Returns job details including status and results
    """
    try:
        job = await service.get_job(job_id)
        if not job:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Job {job_id} not found",
            )
        return job
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Failed to get job {job_id}: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to get job: {str(e)}",
        )


@router.get("/history", response_model=List[CrawlHistoryResponse])
async def get_crawl_history(
    skip: int = Query(0, ge=0),
    limit: int = Query(100, ge=1, le=500),
    job_id: Optional[str] = Query(None),
    status_filter: Optional[str] = Query(None, alias="status"),
    current_admin: UserInDB = Depends(get_current_admin_user),
    service: CrawlerManagementService = Depends(get_crawler_service),
):
    """
    Get crawl history with optional filtering.
    Admin only.
    
    - Returns paginated list of crawl history entries
    - Can filter by job ID and status
    - Sorted by crawl date (newest first)
    """
    try:
        history = await service.get_history(
            skip=skip, limit=limit, job_id=job_id, status=status_filter
        )
        return history
    except Exception as e:
        logger.error(f"Failed to get history: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to get history: {str(e)}",
        )


@router.get("/stats", response_model=CrawlerStatsResponse)
async def get_crawler_stats(
    current_admin: UserInDB = Depends(get_current_admin_user),
    service: CrawlerManagementService = Depends(get_crawler_service),
):
    """
    Get crawler statistics.
    Admin only.
    
    - Returns overall crawler statistics
    - Includes job counts, page counts, recent activity
    - Useful for dashboard overview
    """
    try:
        stats = await service.get_stats()
        return stats
    except Exception as e:
        logger.error(f"Failed to get stats: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to get stats: {str(e)}",
        )


@router.get("/website-info", response_model=WebsiteInfoResponse)
async def get_website_info(
    csv_path: str = Query("assets/data_sheet.csv"),
    current_admin: UserInDB = Depends(get_current_admin_user),
    service: CrawlerManagementService = Depends(get_crawler_service),
):
    """
    Get website structure information from CSV.
    Admin only.
    
    - Analyzes CSV file to get website structure
    - Returns URL counts by category
    - Shows crawl status (crawled, pending, failed)
    - Provides hierarchical URL tree
    """
    try:
        info = await service.get_website_info(csv_path)
        return info
    except Exception as e:
        logger.error(f"Failed to get website info: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to get website info: {str(e)}",
        )

