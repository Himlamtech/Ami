"""Usage metrics repository interface."""

from abc import ABC, abstractmethod
from typing import Optional, List
from datetime import datetime

from domain.entities.usage_metric import (
    UsageMetric,
    LLMUsage,
    DailyUsageStats,
    LLMProvider,
)


class IUsageMetricRepository(ABC):
    """
    Repository interface for UsageMetric entity.

    Handles request tracking and performance analytics.
    """

    # ===== CRUD Operations =====

    @abstractmethod
    async def create(self, metric: UsageMetric) -> UsageMetric:
        """Create new usage metric."""
        pass

    @abstractmethod
    async def get_by_id(self, metric_id: str) -> Optional[UsageMetric]:
        """Get metric by ID."""
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
    ) -> List[UsageMetric]:
        """List metrics by user."""
        pass

    @abstractmethod
    async def list_by_endpoint(
        self,
        endpoint: str,
        skip: int = 0,
        limit: int = 100,
        date_from: Optional[datetime] = None,
        date_to: Optional[datetime] = None,
    ) -> List[UsageMetric]:
        """List metrics by endpoint."""
        pass

    @abstractmethod
    async def get_slow_requests(
        self,
        threshold_ms: int = 3000,
        limit: int = 100,
        date_from: Optional[datetime] = None,
        date_to: Optional[datetime] = None,
    ) -> List[UsageMetric]:
        """Get slow requests above threshold."""
        pass

    @abstractmethod
    async def get_error_requests(
        self,
        limit: int = 100,
        date_from: Optional[datetime] = None,
        date_to: Optional[datetime] = None,
    ) -> List[UsageMetric]:
        """Get requests with errors."""
        pass

    # ===== Analytics Operations =====

    @abstractmethod
    async def get_overview_stats(
        self,
        date_from: Optional[datetime] = None,
        date_to: Optional[datetime] = None,
    ) -> dict:
        """
        Get overview statistics.

        Returns:
            {
                "total_requests": int,
                "unique_users": int,
                "unique_sessions": int,
                "avg_latency_ms": float,
                "error_count": int,
                "error_rate": float,
            }
        """
        pass

    @abstractmethod
    async def get_latency_percentiles(
        self,
        date_from: Optional[datetime] = None,
        date_to: Optional[datetime] = None,
    ) -> dict:
        """
        Get latency percentiles.

        Returns:
            {
                "p50": float,
                "p75": float,
                "p90": float,
                "p95": float,
                "p99": float,
            }
        """
        pass

    @abstractmethod
    async def get_requests_by_endpoint(
        self,
        date_from: Optional[datetime] = None,
        date_to: Optional[datetime] = None,
    ) -> List[dict]:
        """
        Get request counts by endpoint.

        Returns list of {endpoint, count, avg_latency}
        """
        pass

    @abstractmethod
    async def get_hourly_distribution(
        self,
        date_from: Optional[datetime] = None,
        date_to: Optional[datetime] = None,
    ) -> List[dict]:
        """
        Get requests by hour of day.

        Returns list of {hour, count}
        """
        pass


class ILLMUsageRepository(ABC):
    """
    Repository interface for LLMUsage entity.

    Handles LLM token usage and cost tracking.
    """

    # ===== CRUD Operations =====

    @abstractmethod
    async def create(self, usage: LLMUsage) -> LLMUsage:
        """Create new LLM usage record."""
        pass

    @abstractmethod
    async def get_by_id(self, usage_id: str) -> Optional[LLMUsage]:
        """Get usage by ID."""
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
    ) -> List[LLMUsage]:
        """List usage by user."""
        pass

    @abstractmethod
    async def list_by_provider(
        self,
        provider: LLMProvider,
        skip: int = 0,
        limit: int = 100,
        date_from: Optional[datetime] = None,
        date_to: Optional[datetime] = None,
    ) -> List[LLMUsage]:
        """List usage by provider."""
        pass

    # ===== Analytics Operations =====

    @abstractmethod
    async def get_cost_summary(
        self,
        date_from: Optional[datetime] = None,
        date_to: Optional[datetime] = None,
    ) -> dict:
        """
        Get cost summary.

        Returns:
            {
                "total_cost": float,
                "total_tokens": int,
                "total_input_tokens": int,
                "total_output_tokens": int,
            }
        """
        pass

    @abstractmethod
    async def get_cost_by_provider(
        self,
        date_from: Optional[datetime] = None,
        date_to: Optional[datetime] = None,
    ) -> List[dict]:
        """
        Get cost breakdown by provider.

        Returns list of {provider, cost, tokens, percentage}
        """
        pass

    @abstractmethod
    async def get_cost_by_model(
        self,
        date_from: Optional[datetime] = None,
        date_to: Optional[datetime] = None,
    ) -> List[dict]:
        """
        Get cost breakdown by model.

        Returns list of {model, cost, tokens, percentage}
        """
        pass

    @abstractmethod
    async def get_cost_by_use_case(
        self,
        date_from: Optional[datetime] = None,
        date_to: Optional[datetime] = None,
    ) -> List[dict]:
        """
        Get cost breakdown by use case.

        Returns list of {use_case, cost, tokens, percentage}
        """
        pass

    @abstractmethod
    async def get_daily_costs(
        self,
        days: int = 30,
    ) -> List[dict]:
        """
        Get daily cost trends.

        Returns list of {date, cost, tokens}
        """
        pass


class IDailyStatsRepository(ABC):
    """
    Repository interface for DailyUsageStats.

    Handles pre-aggregated daily statistics.
    """

    @abstractmethod
    async def upsert(self, stats: DailyUsageStats) -> DailyUsageStats:
        """Create or update daily stats."""
        pass

    @abstractmethod
    async def get_by_date(self, date: datetime) -> Optional[DailyUsageStats]:
        """Get stats for a specific date."""
        pass

    @abstractmethod
    async def get_range(
        self,
        date_from: datetime,
        date_to: datetime,
    ) -> List[DailyUsageStats]:
        """Get stats for a date range."""
        pass

    @abstractmethod
    async def get_summary(
        self,
        days: int = 30,
    ) -> dict:
        """
        Get summary for last N days.

        Returns aggregated stats.
        """
        pass
