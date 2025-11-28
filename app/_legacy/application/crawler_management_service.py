"""
Crawler Management Service for tracking and managing crawl jobs.
Provides job creation, tracking, history, and statistics.
"""

import logging
from datetime import datetime
from pathlib import Path
from typing import Dict, List, Optional

from app.core.mongodb_models import (
    CrawlHistoryInDB,
    CrawlHistoryResponse,
    CrawlJobCreate,
    CrawlJobInDB,
    CrawlJobResponse,
    CrawlJobStatus,
    CrawlJobType,
    CrawlerStatsResponse,
    WebsiteInfoResponse,
)
from app.infrastructure.databases.mongodb_client import MongoDBClient
from app.infrastructure.tools.csv_parser import DataSheetParser

logger = logging.getLogger(__name__)


class CrawlerManagementService:
    """Service for managing crawler jobs and history."""

    def __init__(self, mongodb: MongoDBClient):
        """
        Initialize the crawler management service.

        Args:
            mongodb: MongoDB client
        """
        self.mongodb = mongodb
        self.db = mongodb.db
        self.jobs_collection = self.db.get_collection("crawl_jobs")
        self.history_collection = self.db.get_collection("crawl_history")

    async def create_job(
        self, job_data: CrawlJobCreate, user_id: str
    ) -> CrawlJobResponse:
        """
        Create a new crawl job.

        Args:
            job_data: Job creation data
            user_id: User creating the job

        Returns:
            Created job
        """
        # Create job document
        job_dict = job_data.model_dump()
        job_dict["created_by"] = user_id
        job_dict["status"] = CrawlJobStatus.PENDING
        job_dict["created_at"] = datetime.now()
        job_dict["total_pages"] = 0
        job_dict["successful_pages"] = 0
        job_dict["failed_pages"] = 0
        job_dict["ingested_pages"] = 0
        job_dict["duration_seconds"] = 0.0

        # Insert into database
        result = await self.jobs_collection.insert_one(job_dict)
        job_dict["_id"] = str(result.inserted_id)

        logger.info(f"Created crawl job {job_dict['_id']} by user {user_id}")

        return CrawlJobResponse(**self._convert_job_doc(job_dict))

    async def get_job(self, job_id: str) -> Optional[CrawlJobResponse]:
        """Get a crawl job by ID."""
        job = await self.jobs_collection.find_one({"_id": job_id})
        if not job:
            return None
        return CrawlJobResponse(**self._convert_job_doc(job))

    async def list_jobs(
        self,
        skip: int = 0,
        limit: int = 50,
        status: Optional[CrawlJobStatus] = None,
        job_type: Optional[CrawlJobType] = None,
    ) -> List[CrawlJobResponse]:
        """
        List crawl jobs with optional filtering.

        Args:
            skip: Number of jobs to skip
            limit: Maximum number of jobs to return
            status: Filter by status
            job_type: Filter by job type

        Returns:
            List of jobs
        """
        query = {}
        if status:
            query["status"] = status
        if job_type:
            query["job_type"] = job_type

        cursor = (
            self.jobs_collection.find(query)
            .sort("created_at", -1)
            .skip(skip)
            .limit(limit)
        )

        jobs = []
        async for job in cursor:
            jobs.append(CrawlJobResponse(**self._convert_job_doc(job)))

        return jobs

    async def update_job_status(
        self,
        job_id: str,
        status: CrawlJobStatus,
        error: Optional[str] = None,
        results: Optional[Dict] = None,
    ) -> Optional[CrawlJobResponse]:
        """
        Update job status and results.

        Args:
            job_id: Job ID
            status: New status
            error: Error message if failed
            results: Job results (total_pages, successful_pages, etc.)

        Returns:
            Updated job
        """
        update_data = {"status": status}

        if status == CrawlJobStatus.RUNNING and not await self._get_job_field(
            job_id, "started_at"
        ):
            update_data["started_at"] = datetime.now()

        if status in [CrawlJobStatus.COMPLETED, CrawlJobStatus.FAILED]:
            update_data["completed_at"] = datetime.now()

        if error:
            update_data["error"] = error

        if results:
            update_data.update(results)

        await self.jobs_collection.update_one({"_id": job_id}, {"$set": update_data})

        return await self.get_job(job_id)

    async def add_history(
        self,
        url: str,
        status: str,
        user_id: str,
        job_id: Optional[str] = None,
        content_length: int = 0,
        error: Optional[str] = None,
        duration_seconds: float = 0.0,
        saved_path: Optional[str] = None,
        ingested: bool = False,
        doc_id: Optional[str] = None,
        chunk_count: int = 0,
        metadata: Optional[Dict] = None,
    ) -> CrawlHistoryResponse:
        """
        Add a crawl history entry.

        Args:
            url: Crawled URL
            status: Crawl status (success, failed, skipped)
            user_id: User who performed the crawl
            job_id: Associated job ID
            content_length: Length of crawled content
            error: Error message if failed
            duration_seconds: Crawl duration
            saved_path: Path where content was saved
            ingested: Whether content was ingested to RAG
            doc_id: MongoDB document ID if ingested
            chunk_count: Number of chunks created
            metadata: Additional metadata

        Returns:
            Created history entry
        """
        history_dict = {
            "job_id": job_id,
            "url": url,
            "status": status,
            "content_length": content_length,
            "error": error,
            "metadata": metadata or {},
            "crawled_by": user_id,
            "crawled_at": datetime.now(),
            "duration_seconds": duration_seconds,
            "saved_path": saved_path,
            "ingested": ingested,
            "doc_id": doc_id,
            "chunk_count": chunk_count,
        }

        result = await self.history_collection.insert_one(history_dict)
        history_dict["_id"] = str(result.inserted_id)

        return CrawlHistoryResponse(**self._convert_history_doc(history_dict))

    async def get_history(
        self,
        skip: int = 0,
        limit: int = 100,
        job_id: Optional[str] = None,
        status: Optional[str] = None,
    ) -> List[CrawlHistoryResponse]:
        """
        Get crawl history with optional filtering.

        Args:
            skip: Number of entries to skip
            limit: Maximum number of entries to return
            job_id: Filter by job ID
            status: Filter by status

        Returns:
            List of history entries
        """
        query = {}
        if job_id:
            query["job_id"] = job_id
        if status:
            query["status"] = status

        cursor = (
            self.history_collection.find(query)
            .sort("crawled_at", -1)
            .skip(skip)
            .limit(limit)
        )

        history = []
        async for entry in cursor:
            history.append(CrawlHistoryResponse(**self._convert_history_doc(entry)))

        return history

    async def get_stats(self) -> CrawlerStatsResponse:
        """
        Get crawler statistics.

        Returns:
            Crawler statistics
        """
        # Count jobs by status
        jobs_pipeline = [{"$group": {"_id": "$status", "count": {"$sum": 1}}}]
        jobs_by_status = {}
        async for result in self.jobs_collection.aggregate(jobs_pipeline):
            jobs_by_status[result["_id"]] = result["count"]

        total_jobs = sum(jobs_by_status.values())

        # Count crawled pages
        total_crawled = await self.history_collection.count_documents({})
        total_ingested = await self.history_collection.count_documents(
            {"ingested": True}
        )
        total_failed = await self.history_collection.count_documents(
            {"status": "failed"}
        )

        # Get recent jobs
        recent_jobs = await self.list_jobs(skip=0, limit=5)

        # Get recent history
        recent_history = await self.get_history(skip=0, limit=10)

        # Calculate average duration
        avg_pipeline = [{"$group": {"_id": None, "avg": {"$avg": "$duration_seconds"}}}]
        avg_result = await self.history_collection.aggregate(avg_pipeline).to_list(1)
        avg_duration = avg_result[0]["avg"] if avg_result else 0.0

        return CrawlerStatsResponse(
            total_jobs=total_jobs,
            jobs_by_status=jobs_by_status,
            total_crawled_pages=total_crawled,
            total_ingested_pages=total_ingested,
            total_failed_pages=total_failed,
            recent_jobs=recent_jobs,
            recent_history=recent_history,
            crawled_urls_count=total_crawled,
            avg_duration_seconds=avg_duration,
        )

    async def get_website_info(
        self, csv_path: str = "assets/data_sheet.csv"
    ) -> WebsiteInfoResponse:
        """
        Get website structure information from CSV.

        Args:
            csv_path: Path to CSV file

        Returns:
            Website structure information
        """
        parser = DataSheetParser(csv_path)
        tasks = parser.parse()

        # Count by category
        urls_by_category = {}
        for task in tasks:
            category = task.metadata.get("category", "Unknown")
            urls_by_category[category] = urls_by_category.get(category, 0) + 1

        # Check crawl status
        urls_by_status = {"crawled": 0, "pending": 0, "failed": 0}
        output_dir = Path("assets/raw")

        for task in tasks:
            if task.output_filename and (output_dir / task.output_filename).exists():
                urls_by_status["crawled"] += 1
            else:
                urls_by_status["pending"] += 1

        # Build URL tree (simplified)
        url_tree = []
        for category, count in urls_by_category.items():
            url_tree.append({"category": category, "count": count, "urls": []})

        return WebsiteInfoResponse(
            total_urls=len(tasks),
            urls_by_category=urls_by_category,
            urls_by_status=urls_by_status,
            categories=list(urls_by_category.keys()),
            url_tree=url_tree,
        )

    def _convert_job_doc(self, doc: Dict) -> Dict:
        """Convert MongoDB document to response format."""
        doc["id"] = str(doc.pop("_id"))
        return doc

    def _convert_history_doc(self, doc: Dict) -> Dict:
        """Convert MongoDB history document to response format."""
        doc["id"] = str(doc.pop("_id"))
        return doc

    async def _get_job_field(self, job_id: str, field: str):
        """Get a specific field from a job."""
        job = await self.jobs_collection.find_one({"_id": job_id}, {field: 1})
        return job.get(field) if job else None

