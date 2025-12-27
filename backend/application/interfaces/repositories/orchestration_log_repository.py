"""Orchestration Log Repository interface."""

from abc import ABC, abstractmethod
from typing import Optional, List
from datetime import datetime

from app.domain.entities.orchestration_result import OrchestrationResult


class IOrchestrationLogRepository(ABC):
    """
    Repository interface for OrchestrationResult entity.

    Stores orchestration decisions for analytics and debugging.
    """

    # ===== CRUD Operations =====

    @abstractmethod
    async def create(self, result: OrchestrationResult) -> OrchestrationResult:
        """Save orchestration result."""
        pass

    @abstractmethod
    async def get_by_id(self, log_id: str) -> Optional[OrchestrationResult]:
        """Get log by ID."""
        pass

    # ===== Query Operations =====

    @abstractmethod
    async def list_by_user(
        self,
        user_id: str,
        skip: int = 0,
        limit: int = 100,
        date_from: Optional[datetime] = None,
        date_to: Optional[datetime] = None,
    ) -> List[OrchestrationResult]:
        """List orchestration logs by user."""
        pass

    @abstractmethod
    async def list_by_session(
        self,
        session_id: str,
        skip: int = 0,
        limit: int = 100,
    ) -> List[OrchestrationResult]:
        """List orchestration logs by session."""
        pass

    @abstractmethod
    async def list_by_tool_type(
        self,
        tool_type: str,
        skip: int = 0,
        limit: int = 100,
        date_from: Optional[datetime] = None,
        date_to: Optional[datetime] = None,
    ) -> List[OrchestrationResult]:
        """List logs by primary tool used."""
        pass

    # ===== Analytics Operations =====

    @abstractmethod
    async def count_by_tool_type(
        self,
        date_from: Optional[datetime] = None,
        date_to: Optional[datetime] = None,
    ) -> dict:
        """Count orchestrations by tool type."""
        pass

    @abstractmethod
    async def get_average_latency(
        self,
        date_from: Optional[datetime] = None,
        date_to: Optional[datetime] = None,
    ) -> dict:
        """Get average latency metrics."""
        pass

    @abstractmethod
    async def list_failed(
        self,
        skip: int = 0,
        limit: int = 100,
        date_from: Optional[datetime] = None,
        date_to: Optional[datetime] = None,
    ) -> List[OrchestrationResult]:
        """List failed orchestration attempts."""
        pass
