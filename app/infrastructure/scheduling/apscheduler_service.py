"""APScheduler implementation with MongoDB JobStore."""

import logging
from typing import Callable, Optional, Dict, Any, List
from datetime import datetime

from apscheduler.schedulers.asyncio import AsyncIOScheduler
from apscheduler.jobstores.mongodb import MongoDBJobStore
from apscheduler.executors.asyncio import AsyncIOExecutor
from apscheduler.triggers.cron import CronTrigger
from apscheduler.triggers.interval import IntervalTrigger
from apscheduler.triggers.date import DateTrigger

from app.application.interfaces.services.scheduler_service import ISchedulerService, JobStatus
from app.config import mongodb_config

logger = logging.getLogger(__name__)


class APSchedulerService(ISchedulerService):
    """
    APScheduler implementation with MongoDB persistence.
    
    Jobs are persisted to MongoDB so they survive restarts.
    """
    
    def __init__(self, mongo_uri: Optional[str] = None):
        """
        Initialize APScheduler.
        
        Args:
            mongo_uri: MongoDB connection URI (defaults from mongodb_config)
        """
        self._mongo_uri = mongo_uri or mongodb_config.get_connection_url()
        self._scheduler: Optional[AsyncIOScheduler] = None
        self._initialized = False
    
    def _ensure_initialized(self) -> None:
        """Lazy initialization of scheduler."""
        if self._initialized:
            return
        
        # Configure job stores
        jobstores = {
            'default': MongoDBJobStore(
                database='ami_scheduler',
                collection='jobs',
                client=None,  # Will use mongo_uri
                host=self._mongo_uri,
            )
        }
        
        # Configure executors
        executors = {
            'default': AsyncIOExecutor(),
        }
        
        # Job defaults
        job_defaults = {
            'coalesce': True,  # Combine missed runs into one
            'max_instances': 1,  # Only one instance at a time
            'misfire_grace_time': 60 * 60,  # 1 hour grace time
        }
        
        self._scheduler = AsyncIOScheduler(
            jobstores=jobstores,
            executors=executors,
            job_defaults=job_defaults,
            timezone='Asia/Ho_Chi_Minh',
        )
        
        self._initialized = True
        logger.info("APScheduler initialized with MongoDB JobStore")
    
    async def start(self) -> None:
        """Start the scheduler."""
        self._ensure_initialized()
        if not self._scheduler.running:
            self._scheduler.start()
            logger.info("APScheduler started")
    
    async def shutdown(self, wait: bool = True) -> None:
        """Shutdown the scheduler."""
        if self._scheduler and self._scheduler.running:
            self._scheduler.shutdown(wait=wait)
            logger.info("APScheduler shutdown")
    
    def _create_trigger(self, trigger_type: str, **trigger_args):
        """Create trigger from type and args."""
        if trigger_type == "cron":
            return CronTrigger(**trigger_args)
        elif trigger_type == "interval":
            return IntervalTrigger(**trigger_args)
        elif trigger_type == "date":
            return DateTrigger(**trigger_args)
        else:
            raise ValueError(f"Unknown trigger type: {trigger_type}")
    
    def add_job(
        self,
        job_id: str,
        func: Callable,
        trigger: str,
        **trigger_args,
    ) -> bool:
        """Add a scheduled job."""
        self._ensure_initialized()
        
        try:
            # Check if job exists
            if self.job_exists(job_id):
                logger.warning(f"Job {job_id} already exists, removing first")
                self.remove_job(job_id)
            
            trigger_obj = self._create_trigger(trigger, **trigger_args)
            
            self._scheduler.add_job(
                func=func,
                trigger=trigger_obj,
                id=job_id,
                replace_existing=True,
            )
            
            logger.info(f"Added job: {job_id} with trigger: {trigger}")
            return True
            
        except Exception as e:
            logger.error(f"Failed to add job {job_id}: {e}")
            return False
    
    def remove_job(self, job_id: str) -> bool:
        """Remove a scheduled job."""
        self._ensure_initialized()
        
        try:
            self._scheduler.remove_job(job_id)
            logger.info(f"Removed job: {job_id}")
            return True
        except Exception as e:
            logger.error(f"Failed to remove job {job_id}: {e}")
            return False
    
    def pause_job(self, job_id: str) -> bool:
        """Pause a scheduled job."""
        self._ensure_initialized()
        
        try:
            self._scheduler.pause_job(job_id)
            logger.info(f"Paused job: {job_id}")
            return True
        except Exception as e:
            logger.error(f"Failed to pause job {job_id}: {e}")
            return False
    
    def resume_job(self, job_id: str) -> bool:
        """Resume a paused job."""
        self._ensure_initialized()
        
        try:
            self._scheduler.resume_job(job_id)
            logger.info(f"Resumed job: {job_id}")
            return True
        except Exception as e:
            logger.error(f"Failed to resume job {job_id}: {e}")
            return False
    
    def get_job(self, job_id: str) -> Optional[Dict[str, Any]]:
        """Get job details."""
        self._ensure_initialized()
        
        try:
            job = self._scheduler.get_job(job_id)
            if not job:
                return None
            
            return {
                "id": job.id,
                "name": job.name,
                "next_run_time": job.next_run_time.isoformat() if job.next_run_time else None,
                "trigger": str(job.trigger),
                "pending": job.pending,
            }
        except Exception as e:
            logger.error(f"Failed to get job {job_id}: {e}")
            return None
    
    def list_jobs(self) -> List[Dict[str, Any]]:
        """List all scheduled jobs."""
        self._ensure_initialized()
        
        try:
            jobs = self._scheduler.get_jobs()
            return [
                {
                    "id": job.id,
                    "name": job.name,
                    "next_run_time": job.next_run_time.isoformat() if job.next_run_time else None,
                    "trigger": str(job.trigger),
                    "pending": job.pending,
                }
                for job in jobs
            ]
        except Exception as e:
            logger.error(f"Failed to list jobs: {e}")
            return []
    
    def job_exists(self, job_id: str) -> bool:
        """Check if job exists."""
        self._ensure_initialized()
        return self._scheduler.get_job(job_id) is not None
    
    def update_job(
        self,
        job_id: str,
        trigger: Optional[str] = None,
        **trigger_args,
    ) -> bool:
        """Update job schedule."""
        self._ensure_initialized()
        
        try:
            if trigger:
                trigger_obj = self._create_trigger(trigger, **trigger_args)
                self._scheduler.reschedule_job(job_id, trigger=trigger_obj)
            else:
                self._scheduler.modify_job(job_id, **trigger_args)
            
            logger.info(f"Updated job: {job_id}")
            return True
        except Exception as e:
            logger.error(f"Failed to update job {job_id}: {e}")
            return False
