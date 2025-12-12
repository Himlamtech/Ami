"""Admin Knowledge Routes - UC-A-004: Knowledge Quality & Gap Detection."""

from fastapi import APIRouter, Depends, HTTPException, status, Query
from typing import Optional
from datetime import datetime, timedelta

from app.api.dependencies.auth import verify_admin_api_key
from app.api.schemas.admin_dto import (
    KnowledgeGapResponse,
    GapDetailResponse,
    LowConfidenceQueryResponse,
    CoverageAnalysisResponse,
)
from app.domain.entities.search_log import GapStatus
from app.config.services import ServiceRegistry


router = APIRouter(prefix="/admin/knowledge", tags=["Admin - Knowledge Quality"])


@router.get("/health")
async def get_knowledge_health(
    is_admin: bool = Depends(verify_admin_api_key),
):
    """
    Get overall knowledge base health metrics.

    - Total documents and chunks
    - Coverage percentage
    - Average confidence scores
    - Recent query success rate
    """
    search_log_repo = ServiceRegistry.get_search_log_repository()
    gap_repo = ServiceRegistry.get_knowledge_gap_repository()

    # Get stats from recent searches
    now = datetime.now()
    date_from = now - timedelta(days=30)

    # Get low confidence count as proxy for quality
    low_conf_logs = await search_log_repo.find_low_confidence(
        threshold=0.5,
        date_from=date_from,
        limit=1000,
    )

    # Get all gaps
    all_gaps = await gap_repo.find_all(limit=1000)
    open_gaps = len([g for g in all_gaps if g.status not in [GapStatus.RESOLVED]])
    resolved_gaps = len([g for g in all_gaps if g.status == GapStatus.RESOLVED])

    # Calculate average confidence from logs
    avg_confidence = 0.5  # Default
    if low_conf_logs:
        avg_confidence = sum(log.top_score for log in low_conf_logs) / len(
            low_conf_logs
        )

    return {
        "open_gaps": open_gaps,
        "resolved_gaps": resolved_gaps,
        "low_confidence_queries": len(low_conf_logs),
        "avg_confidence": round(avg_confidence, 3),
    }


@router.get("/gaps", response_model=list[KnowledgeGapResponse])
async def get_knowledge_gaps(
    status: Optional[str] = Query(
        default=None, pattern="^(identified|confirmed|in_progress|resolved|won_t_fix)$"
    ),
    category: Optional[str] = None,
    priority: Optional[str] = Query(
        default=None, pattern="^(critical|high|medium|low)$"
    ),
    page: int = Query(default=1, ge=1),
    limit: int = Query(default=20, ge=1, le=100),
    is_admin: bool = Depends(verify_admin_api_key),
):
    """
    List identified knowledge gaps.

    Knowledge gaps are queries that consistently return low-confidence results.
    """
    gap_repo = ServiceRegistry.get_knowledge_gap_repository()

    skip = (page - 1) * limit

    # Get all gaps and filter in-memory (simpler approach)
    all_gaps = await gap_repo.find_all(limit=1000)

    # Apply filters
    filtered = all_gaps
    if status:
        filtered = [g for g in filtered if g.status.value == status]
    if category:
        filtered = [g for g in filtered if getattr(g, "category", None) == category]
    if priority:
        # Convert string priority to int range check
        filtered = [g for g in filtered if g.priority >= 5]  # Simple filter

    # Paginate
    paged = filtered[skip : skip + limit]

    return [
        KnowledgeGapResponse(
            id=str(gap.id),
            topic=gap.topic,
            description=gap.description,
            example_queries=gap.sample_queries[:5],
            query_count=gap.query_count,
            avg_confidence=round(gap.avg_score, 3),
            category=getattr(gap, "category", None),
            priority=str(gap.priority),
            status=gap.status.value,
            suggested_action=getattr(gap, "suggested_action", None),
            created_at=gap.first_detected_at,
            updated_at=gap.updated_at,
        )
        for gap in paged
    ]


@router.get("/gaps/{gap_id}", response_model=GapDetailResponse)
async def get_gap_detail(
    gap_id: str,
    is_admin: bool = Depends(verify_admin_api_key),
):
    """
    Get detailed information about a specific knowledge gap.
    """
    gap_repo = ServiceRegistry.get_knowledge_gap_repository()
    search_log_repo = ServiceRegistry.get_search_log_repository()

    gap = await gap_repo.find_by_id(gap_id)
    if not gap:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Knowledge gap not found",
        )

    # Get related search logs for this topic
    related_logs = await search_log_repo.find_low_confidence(
        threshold=0.5,
        limit=20,
    )

    # Filter logs that match this gap's sample queries (simplified)
    matching_logs = [
        log
        for log in related_logs
        if any(
            eq.lower() in log.query.lower() or log.query.lower() in eq.lower()
            for eq in gap.sample_queries
        )
    ][:10]

    return GapDetailResponse(
        id=str(gap.id),
        topic=gap.topic,
        description=gap.description,
        example_queries=gap.sample_queries,
        query_count=gap.query_count,
        avg_confidence=round(gap.avg_score, 3),
        category=getattr(gap, "category", None),
        priority=str(gap.priority),
        status=gap.status.value,
        suggested_action=getattr(gap, "suggested_action", None),
        notes=gap.resolution_notes,
        related_queries=[
            {
                "query": log.query,
                "confidence": round(log.top_score, 3),
                "timestamp": log.timestamp.isoformat(),
            }
            for log in matching_logs
        ],
        created_at=gap.first_detected_at,
        updated_at=gap.updated_at,
    )


@router.patch("/gaps/{gap_id}/status")
async def update_gap_status(
    gap_id: str,
    new_status: str = Query(
        ..., pattern="^(detected|todo|in_progress|resolved|dismissed)$"
    ),
    notes: Optional[str] = None,
    is_admin: bool = Depends(verify_admin_api_key),
):
    """
    Update the status of a knowledge gap.

    Status flow: detected → todo → in_progress → resolved/dismissed
    """
    gap_repo = ServiceRegistry.get_knowledge_gap_repository()

    gap = await gap_repo.find_by_id(gap_id)
    if not gap:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Knowledge gap not found",
        )

    gap.status = GapStatus(new_status)
    gap.updated_at = datetime.now()
    if notes:
        gap.resolution_notes = notes

    if new_status == "resolved":
        gap.resolved_at = datetime.now()

    await gap_repo.update(gap)

    return {
        "status": "ok",
        "gap_id": gap_id,
        "new_status": new_status,
    }


@router.get("/low-confidence", response_model=list[LowConfidenceQueryResponse])
async def get_low_confidence_queries(
    threshold: float = Query(default=0.5, ge=0, le=1),
    period: str = Query(default="week", pattern="^(day|week|month)$"),
    page: int = Query(default=1, ge=1),
    limit: int = Query(default=20, ge=1, le=100),
    is_admin: bool = Depends(verify_admin_api_key),
):
    """
    Get queries with low confidence scores.

    These queries may indicate gaps in the knowledge base.
    """
    search_log_repo = ServiceRegistry.get_search_log_repository()

    # Calculate date range
    now = datetime.now()
    days = {"day": 1, "week": 7, "month": 30}[period]
    date_from = now - timedelta(days=days)

    skip = (page - 1) * limit

    logs = await search_log_repo.find_low_confidence(
        threshold=threshold,
        date_from=date_from,
        limit=limit,
        skip=skip,
    )

    return [
        LowConfidenceQueryResponse(
            id=str(log.id),
            query=log.query,
            max_score=round(log.top_score, 3),
            results_count=log.result_count,
            timestamp=log.timestamp,
            user_id=log.user_id,
        )
        for log in logs
    ]


@router.get("/coverage", response_model=CoverageAnalysisResponse)
async def get_coverage_analysis(
    is_admin: bool = Depends(verify_admin_api_key),
):
    """
    Get knowledge base coverage analysis.

    Analyzes which topics are well-covered vs under-represented.
    """
    search_log_repo = ServiceRegistry.get_search_log_repository()
    gap_repo = ServiceRegistry.get_knowledge_gap_repository()

    now = datetime.now()
    date_from = now - timedelta(days=30)

    # Get topic distribution from searches
    topic_stats = await search_log_repo.get_topic_stats(
        date_from=date_from,
        date_to=now,
    )

    # Get all gaps grouped by category
    all_gaps = await gap_repo.find_all(limit=1000)
    gap_by_category = {}
    for gap in all_gaps:
        cat = getattr(gap, "category", None) or "uncategorized"
        gap_by_category[cat] = gap_by_category.get(cat, 0) + 1

    # Calculate coverage (simplified)
    well_covered = [topic for topic in topic_stats if topic.get("avg_score", 0) >= 0.7]

    needs_improvement = [
        topic for topic in topic_stats if 0.4 <= topic.get("avg_score", 0) < 0.7
    ]

    poor_coverage = [topic for topic in topic_stats if topic.get("avg_score", 0) < 0.4]

    return CoverageAnalysisResponse(
        total_topics=len(topic_stats),
        well_covered=[t.get("topic", "unknown") for t in well_covered[:20]],
        needs_improvement=[t.get("topic", "unknown") for t in needs_improvement[:20]],
        poor_coverage=[t.get("topic", "unknown") for t in poor_coverage[:20]],
        gaps_by_category=gap_by_category,
    )


@router.post("/gaps/detect")
async def trigger_gap_detection(
    days: int = Query(default=7, ge=1, le=30),
    threshold: float = Query(default=0.4, ge=0, le=1),
    is_admin: bool = Depends(verify_admin_api_key),
):
    """
    Trigger gap detection analysis.

    Analyzes recent queries to identify new knowledge gaps.
    """
    search_log_repo = ServiceRegistry.get_search_log_repository()
    gap_repo = ServiceRegistry.get_knowledge_gap_repository()

    now = datetime.now()
    date_from = now - timedelta(days=days)

    # Get low confidence queries
    low_conf_logs = await search_log_repo.find_low_confidence(
        threshold=threshold,
        date_from=date_from,
        limit=500,
    )

    # Group by similar queries (simplified - just exact match for now)
    query_groups = {}
    for log in low_conf_logs:
        query_lower = log.query.lower().strip()
        if query_lower not in query_groups:
            query_groups[query_lower] = {
                "queries": [],
                "scores": [],
            }
        query_groups[query_lower]["queries"].append(log.query)
        query_groups[query_lower]["scores"].append(log.top_score)

    # Create gaps for queries that appear multiple times
    new_gaps_created = 0
    for query_key, data in query_groups.items():
        if len(data["queries"]) >= 3:  # Appears 3+ times
            # Check if gap already exists
            existing = await gap_repo.find_by_topic(query_key)
            if not existing:
                from app.domain.entities.search_log import KnowledgeGap, GapStatus
                import uuid

                gap = KnowledgeGap(
                    id=str(uuid.uuid4()),
                    topic=query_key,
                    description=f"Query '{query_key}' consistently returns low confidence results",
                    sample_queries=list(set(data["queries"]))[:5],
                    query_count=len(data["queries"]),
                    avg_score=sum(data["scores"]) / len(data["scores"]),
                    status=GapStatus.DETECTED,
                    priority=5 if len(data["queries"]) < 10 else 8,
                )
                await gap_repo.save(gap)
                new_gaps_created += 1

    return {
        "status": "ok",
        "analyzed_queries": len(low_conf_logs),
        "query_groups_found": len(query_groups),
        "new_gaps_created": new_gaps_created,
    }
