"""Search log and knowledge gap repository interfaces."""

from abc import ABC, abstractmethod
from typing import Optional, List
from datetime import datetime

from domain.entities.search_log import (
    SearchLog,
    KnowledgeGap,
    SearchResultQuality,
    GapStatus,
)


class ISearchLogRepository(ABC):
    """
    Repository interface for SearchLog entity.

    Handles search/RAG query logging for knowledge gap detection.
    """

    # ===== CRUD Operations =====

    @abstractmethod
    async def create(self, log: SearchLog) -> SearchLog:
        """Create new search log."""
        pass

    @abstractmethod
    async def get_by_id(self, log_id: str) -> Optional[SearchLog]:
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
    ) -> List[SearchLog]:
        """List logs by user."""
        pass

    @abstractmethod
    async def list_by_session(
        self,
        session_id: str,
        skip: int = 0,
        limit: int = 100,
    ) -> List[SearchLog]:
        """List logs by session."""
        pass

    @abstractmethod
    async def list_low_quality(
        self,
        quality: SearchResultQuality = SearchResultQuality.LOW,
        skip: int = 0,
        limit: int = 100,
        date_from: Optional[datetime] = None,
        date_to: Optional[datetime] = None,
    ) -> List[SearchLog]:
        """List logs with low quality results."""
        pass

    @abstractmethod
    async def list_with_fallback(
        self,
        skip: int = 0,
        limit: int = 100,
        date_from: Optional[datetime] = None,
        date_to: Optional[datetime] = None,
    ) -> List[SearchLog]:
        """List logs that used web fallback."""
        pass

    # ===== Analytics Operations =====

    @abstractmethod
    async def get_quality_distribution(
        self,
        date_from: Optional[datetime] = None,
        date_to: Optional[datetime] = None,
    ) -> dict:
        """
        Get distribution of result quality.

        Returns:
            {
                "high": int,
                "medium": int,
                "low": int,
                "none": int,
                "total": int,
            }
        """
        pass

    @abstractmethod
    async def get_fallback_rate(
        self,
        date_from: Optional[datetime] = None,
        date_to: Optional[datetime] = None,
    ) -> float:
        """Get percentage of queries using web fallback."""
        pass

    @abstractmethod
    async def get_avg_score_by_collection(
        self,
        date_from: Optional[datetime] = None,
        date_to: Optional[datetime] = None,
    ) -> List[dict]:
        """
        Get average score by collection.

        Returns list of {collection, avg_score, query_count}
        """
        pass

    @abstractmethod
    async def get_gap_candidates(
        self,
        min_queries: int = 3,
        max_score: float = 0.5,
        days: int = 30,
    ) -> List[dict]:
        """
        Get queries that might indicate knowledge gaps.

        Returns list of {query_pattern, count, avg_score, samples}
        """
        pass


class IKnowledgeGapRepository(ABC):
    """
    Repository interface for KnowledgeGap entity.

    Handles tracking and management of knowledge gaps.
    """

    # ===== CRUD Operations =====

    @abstractmethod
    async def create(self, gap: KnowledgeGap) -> KnowledgeGap:
        """Create new knowledge gap."""
        pass

    @abstractmethod
    async def get_by_id(self, gap_id: str) -> Optional[KnowledgeGap]:
        """Get gap by ID."""
        pass

    @abstractmethod
    async def update(self, gap: KnowledgeGap) -> KnowledgeGap:
        """Update existing gap."""
        pass

    @abstractmethod
    async def delete(self, gap_id: str) -> bool:
        """Delete gap."""
        pass

    # ===== Query Operations =====

    @abstractmethod
    async def find_by_topic(self, topic: str) -> Optional[KnowledgeGap]:
        """Find gap by topic (for deduplication)."""
        pass

    @abstractmethod
    async def list_all(
        self,
        skip: int = 0,
        limit: int = 100,
        status: Optional[GapStatus] = None,
        min_priority: int = 0,
    ) -> List[KnowledgeGap]:
        """List all gaps with filters."""
        pass

    @abstractmethod
    async def count_by_status(self) -> dict:
        """
        Count gaps by status.

        Returns:
            {
                "detected": int,
                "todo": int,
                "in_progress": int,
                "resolved": int,
                "dismissed": int,
            }
        """
        pass

    @abstractmethod
    async def get_top_gaps(
        self,
        limit: int = 10,
        status: Optional[GapStatus] = None,
    ) -> List[KnowledgeGap]:
        """Get top gaps by priority and query count."""
        pass

    # ===== Update Operations =====

    @abstractmethod
    async def add_query_to_gap(
        self,
        gap_id: str,
        query: str,
        score: float,
    ) -> KnowledgeGap:
        """Add a query to an existing gap."""
        pass

    @abstractmethod
    async def find_or_create_gap(
        self,
        topic: str,
        query: str,
        score: float,
    ) -> KnowledgeGap:
        """Find existing gap or create new one."""
        pass
