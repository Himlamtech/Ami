"""Search log and knowledge gap domain entities."""

from dataclasses import dataclass, field
from datetime import datetime
from typing import List, Optional, Dict, Any
from enum import Enum


class SearchResultQuality(Enum):
    """Quality of search results."""

    HIGH = "high"  # score >= 0.7
    MEDIUM = "medium"  # 0.5 <= score < 0.7
    LOW = "low"  # 0.3 <= score < 0.5
    NONE = "none"  # score < 0.3 or no results


class GapStatus(Enum):
    """Status of knowledge gap."""

    DETECTED = "detected"
    TODO = "todo"
    IN_PROGRESS = "in_progress"
    RESOLVED = "resolved"
    DISMISSED = "dismissed"


@dataclass
class SearchResult:
    """Individual search result."""

    document_id: str
    chunk_id: Optional[str] = None
    title: Optional[str] = None
    score: float = 0.0

    def to_dict(self) -> Dict[str, Any]:
        return {
            "document_id": self.document_id,
            "chunk_id": self.chunk_id,
            "title": self.title,
            "score": self.score,
        }


@dataclass
class SearchLog:
    """
    Search log entity for tracking RAG queries.

    Tracks each search/RAG query for knowledge gap detection.
    """

    # Identity
    id: str

    # Query info
    query: str
    user_id: Optional[str] = None
    session_id: Optional[str] = None
    message_id: Optional[str] = None

    # Search results
    results: List[SearchResult] = field(default_factory=list)
    top_score: float = 0.0
    result_count: int = 0
    result_quality: SearchResultQuality = SearchResultQuality.NONE

    # Fallback tracking
    used_web_fallback: bool = False
    web_search_query: Optional[str] = None

    # Collection info
    collection: Optional[str] = None

    # Performance
    search_latency_ms: int = 0

    # Timestamp
    timestamp: datetime = field(default_factory=datetime.now)

    def calculate_quality(self) -> None:
        """Calculate result quality based on top score."""
        if self.result_count == 0 or self.top_score < 0.3:
            self.result_quality = SearchResultQuality.NONE
        elif self.top_score >= 0.7:
            self.result_quality = SearchResultQuality.HIGH
        elif self.top_score >= 0.5:
            self.result_quality = SearchResultQuality.MEDIUM
        else:
            self.result_quality = SearchResultQuality.LOW

    def is_gap_candidate(self) -> bool:
        """Check if this search indicates a knowledge gap."""
        return (
            self.result_quality in [SearchResultQuality.LOW, SearchResultQuality.NONE]
            or self.used_web_fallback
        )

    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary."""
        return {
            "id": self.id,
            "query": self.query,
            "user_id": self.user_id,
            "session_id": self.session_id,
            "message_id": self.message_id,
            "results": [r.to_dict() for r in self.results],
            "top_score": self.top_score,
            "result_count": self.result_count,
            "result_quality": self.result_quality.value,
            "used_web_fallback": self.used_web_fallback,
            "web_search_query": self.web_search_query,
            "collection": self.collection,
            "search_latency_ms": self.search_latency_ms,
            "timestamp": self.timestamp.isoformat(),
        }


@dataclass
class KnowledgeGap:
    """
    Knowledge gap entity for tracking missing knowledge.

    Aggregates low-score queries to identify knowledge gaps.
    """

    # Identity
    id: str

    # Gap info
    topic: str  # Extracted/clustered topic
    description: Optional[str] = None

    # Statistics
    query_count: int = 0
    avg_score: float = 0.0
    sample_queries: List[str] = field(default_factory=list)

    # Status
    status: GapStatus = GapStatus.DETECTED
    priority: int = 0  # Higher = more important

    # Resolution
    resolved_by_document_id: Optional[str] = None
    resolved_by: Optional[str] = None  # Admin user ID
    resolved_at: Optional[datetime] = None
    resolution_notes: Optional[str] = None

    # Timestamps
    first_detected_at: datetime = field(default_factory=datetime.now)
    last_query_at: datetime = field(default_factory=datetime.now)
    updated_at: datetime = field(default_factory=datetime.now)

    def add_query(self, query: str, score: float) -> None:
        """Add a query to this gap."""
        self.query_count += 1
        # Update average score
        self.avg_score = (
            self.avg_score * (self.query_count - 1) + score
        ) / self.query_count
        # Keep sample queries (max 10)
        if query not in self.sample_queries and len(self.sample_queries) < 10:
            self.sample_queries.append(query)
        self.last_query_at = datetime.now()
        self.updated_at = datetime.now()
        # Update priority based on query count
        self._update_priority()

    def _update_priority(self) -> None:
        """Update priority based on query count and recency."""
        # Base priority on query count
        if self.query_count >= 50:
            self.priority = 3
        elif self.query_count >= 20:
            self.priority = 2
        elif self.query_count >= 5:
            self.priority = 1
        else:
            self.priority = 0

    def mark_todo(self) -> None:
        """Mark gap as todo."""
        self.status = GapStatus.TODO
        self.updated_at = datetime.now()

    def mark_in_progress(self) -> None:
        """Mark gap as in progress."""
        self.status = GapStatus.IN_PROGRESS
        self.updated_at = datetime.now()

    def resolve(
        self,
        document_id: str,
        resolved_by: str,
        notes: Optional[str] = None,
    ) -> None:
        """Mark gap as resolved."""
        self.status = GapStatus.RESOLVED
        self.resolved_by_document_id = document_id
        self.resolved_by = resolved_by
        self.resolved_at = datetime.now()
        self.resolution_notes = notes
        self.updated_at = datetime.now()

    def dismiss(self, notes: Optional[str] = None) -> None:
        """Dismiss gap."""
        self.status = GapStatus.DISMISSED
        self.resolution_notes = notes
        self.updated_at = datetime.now()

    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary."""
        return {
            "id": self.id,
            "topic": self.topic,
            "description": self.description,
            "query_count": self.query_count,
            "avg_score": self.avg_score,
            "sample_queries": self.sample_queries,
            "status": self.status.value,
            "priority": self.priority,
            "resolved_by_document_id": self.resolved_by_document_id,
            "resolved_by": self.resolved_by,
            "resolved_at": self.resolved_at.isoformat() if self.resolved_at else None,
            "resolution_notes": self.resolution_notes,
            "first_detected_at": self.first_detected_at.isoformat(),
            "last_query_at": self.last_query_at.isoformat(),
            "updated_at": self.updated_at.isoformat(),
        }

    def __repr__(self) -> str:
        return f"KnowledgeGap(topic={self.topic}, queries={self.query_count}, status={self.status.value})"
