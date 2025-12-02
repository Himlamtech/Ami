"""Scheduler service interface."""

from abc import ABC, abstractmethod
from typing import Callable, Optional, Dict, Any, List
from datetime import datetime
from enum import Enum


class JobStatus(Enum):
    """Job execution status."""
    PENDING = "pending"
    RUNNING = "running"
    COMPLETED = "completed"
    FAILED = "failed"
    PAUSED = "paused"


class ISchedulerService(ABC):
    """
    Interface for job scheduling service.
    
    Supports:
    - Cron-based scheduling
    - Interval-based scheduling
    - One-time scheduled jobs
    - Job management (pause, resume, remove)
    """
    
    @abstractmethod
    async def start(self) -> None:
        """Start the scheduler."""
        pass
    
    @abstractmethod
    async def shutdown(self, wait: bool = True) -> None:
        """Shutdown the scheduler."""
        pass
    
    @abstractmethod
    def add_job(
        self,
        job_id: str,
        func: Callable,
        trigger: str,  # "cron", "interval", "date"
        **trigger_args,
    ) -> bool:
        """
        Add a scheduled job.
        
        Args:
            job_id: Unique job identifier
            func: Async function to execute
            trigger: Trigger type (cron, interval, date)
            **trigger_args: Trigger-specific arguments
                - cron: hour, minute, day_of_week, etc.
                - interval: hours, minutes, seconds
                - date: run_date
                
        Returns:
            True if job added successfully
        """
        pass
    
    @abstractmethod
    def remove_job(self, job_id: str) -> bool:
        """Remove a scheduled job."""
        pass
    
    @abstractmethod
    def pause_job(self, job_id: str) -> bool:
        """Pause a scheduled job."""
        pass
    
    @abstractmethod
    def resume_job(self, job_id: str) -> bool:
        """Resume a paused job."""
        pass
    
    @abstractmethod
    def get_job(self, job_id: str) -> Optional[Dict[str, Any]]:
        """Get job details."""
        pass
    
    @abstractmethod
    def list_jobs(self) -> List[Dict[str, Any]]:
        """List all scheduled jobs."""
        pass
    
    @abstractmethod
    def job_exists(self, job_id: str) -> bool:
        """Check if job exists."""
        pass
    
    @abstractmethod
    def update_job(
        self,
        job_id: str,
        trigger: Optional[str] = None,
        **trigger_args,
    ) -> bool:
        """Update job schedule."""
        pass
