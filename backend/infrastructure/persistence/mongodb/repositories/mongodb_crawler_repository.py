"""MongoDB Crawler Repository implementation."""

from typing import Optional, List, Dict, Any
from motor.motor_asyncio import AsyncIOMotorDatabase
from bson import ObjectId

from domain.entities.crawl_job import CrawlJob
from domain.enums.crawl_status import CrawlJobStatus
from application.interfaces.repositories.crawler_repository import (
    ICrawlerRepository,
)


class MongoDBCrawlerRepository(ICrawlerRepository):
    """MongoDB implementation of Crawler Repository."""

    def __init__(self, db: AsyncIOMotorDatabase):
        self.db = db
        self.collection = db["crawl_jobs"]

    async def create_job(self, job: CrawlJob) -> CrawlJob:
        """Create crawl job."""
        job_dict = {
            "created_by": job.created_by,
            "job_type": job.job_type.value,
            "url": job.url,
            "collection": job.collection,
            "status": job.status.value,
            "total_pages": job.total_pages,
            "successful_pages": job.successful_pages,
            "failed_pages": job.failed_pages,
            "created_at": job.created_at,
        }

        result = await self.collection.insert_one(job_dict)
        job.id = str(result.inserted_id)
        return job

    async def get_job_by_id(self, job_id: str) -> Optional[CrawlJob]:
        """Get job by ID."""
        try:
            doc = await self.collection.find_one({"_id": ObjectId(job_id)})
        except:
            return None

        if not doc:
            return None

        return self._doc_to_entity(doc)

    async def update_job(self, job: CrawlJob) -> CrawlJob:
        """Update job."""
        job_dict = {
            "status": job.status.value,
            "total_pages": job.total_pages,
            "successful_pages": job.successful_pages,
            "failed_pages": job.failed_pages,
            "completed_at": job.completed_at,
        }

        await self.collection.update_one({"_id": ObjectId(job.id)}, {"$set": job_dict})

        return job

    async def delete_job(self, job_id: str) -> bool:
        """Delete job."""
        result = await self.collection.delete_one({"_id": ObjectId(job_id)})
        return result.deleted_count > 0

    async def list_jobs(
        self,
        skip: int = 0,
        limit: int = 100,
        status: Optional[CrawlJobStatus] = None,
        created_by: Optional[str] = None,
    ) -> List[CrawlJob]:
        """List jobs."""
        query = {}
        if status:
            query["status"] = status.value
        if created_by:
            query["created_by"] = created_by

        cursor = (
            self.collection.find(query).sort("created_at", -1).skip(skip).limit(limit)
        )
        jobs = []

        async for doc in cursor:
            jobs.append(self._doc_to_entity(doc))

        return jobs

    async def count_jobs(
        self,
        status: Optional[CrawlJobStatus] = None,
        created_by: Optional[str] = None,
    ) -> int:
        """Count jobs."""
        query = {}
        if status:
            query["status"] = status.value
        if created_by:
            query["created_by"] = created_by

        return await self.collection.count_documents(query)

    async def get_running_jobs(self) -> List[CrawlJob]:
        """Get running jobs."""
        return await self.list_jobs(status=CrawlJobStatus.RUNNING, limit=1000)

    async def get_scheduled_jobs(self) -> List[CrawlJob]:
        """Get scheduled jobs."""
        cursor = self.collection.find({"schedule_cron": {"$ne": None}})
        jobs = []

        async for doc in cursor:
            jobs.append(self._doc_to_entity(doc))

        return jobs

    async def get_crawler_stats(self) -> Dict[str, Any]:
        """Get crawler statistics."""
        # Simple stats - can be enhanced
        total_jobs = await self.collection.count_documents({})

        pipeline = [{"$group": {"_id": "$status", "count": {"$sum": 1}}}]

        status_counts = {}
        async for doc in self.collection.aggregate(pipeline):
            status_counts[doc["_id"]] = doc["count"]

        return {
            "total_jobs": total_jobs,
            "jobs_by_status": status_counts,
        }

    def _doc_to_entity(self, doc: dict) -> CrawlJob:
        """Convert MongoDB doc to entity."""
        from datetime import datetime

        return CrawlJob(
            id=str(doc["_id"]),
            created_by=doc["created_by"],
            job_type=doc["job_type"],
            url=doc.get("url"),
            collection=doc.get("collection", "web_content"),
            status=CrawlJobStatus(doc.get("status", "pending")),
            total_pages=doc.get("total_pages", 0),
            successful_pages=doc.get("successful_pages", 0),
            failed_pages=doc.get("failed_pages", 0),
            created_at=doc.get("created_at", datetime.now()),
        )
