"""Admin routes for Approval Queue management."""

from fastapi import APIRouter, Depends, HTTPException, status, Query
from typing import Optional

from app.api.dependencies.auth import verify_admin_api_key
from app.api.schemas.pending_update_dto import (
    ApproveUpdateRequest,
    RejectUpdateRequest,
    BulkActionRequest,
    IngestUpdateRequest,
    PendingUpdateResponse,
    PendingUpdateDetailResponse,
    PendingUpdateListResponse,
    ApprovalActionResponse,
    BulkActionResponse,
    ApprovalStatsResponse,
)
from app.domain.enums.data_source import (
    PendingStatus,
    DataCategory,
    UpdateDetectionType,
)
from app.application.use_cases.approval import (
    ListPendingUpdatesUseCase,
    ApproveUpdateUseCase,
    RejectUpdateUseCase,
    GetApprovalStatsUseCase,
    IngestPendingUpdateUseCase,
    IngestPendingUpdateInput,
)
from app.application.use_cases.approval.list_pending import ListPendingUpdatesInput
from app.application.use_cases.approval.approve_update import ApproveUpdateInput
from app.application.use_cases.approval.reject_update import RejectUpdateInput
from app.config.services import ServiceRegistry


router = APIRouter(prefix="/admin/approvals", tags=["admin-approvals"])


# ===== Helper Functions =====


def _to_response(pending) -> PendingUpdateResponse:
    """Convert PendingUpdate entity to response DTO."""
    content_preview = (
        pending.content[:500] + "..." if len(pending.content) > 500 else pending.content
    )

    return PendingUpdateResponse(
        id=pending.id,
        source_id=pending.source_id,
        title=pending.title,
        content_preview=content_preview,
        content_hash=pending.content_hash,
        source_url=pending.source_url,
        category=(
            pending.category.value
            if hasattr(pending.category, "value")
            else pending.category
        ),
        detection_type=(
            pending.detection_type.value
            if hasattr(pending.detection_type, "value")
            else pending.detection_type
        ),
        similarity_score=pending.similarity_score,
        matched_doc_id=pending.matched_doc_id,
        llm_analysis=pending.llm_analysis,
        llm_summary=pending.llm_summary,
        diff_summary=pending.diff_summary,
        status=(
            pending.status.value if hasattr(pending.status, "value") else pending.status
        ),
        priority=pending.priority,
        auto_approve_score=pending.auto_approve_score,
        reviewed_by=pending.reviewed_by,
        reviewed_at=pending.reviewed_at,
        review_note=pending.review_note,
        created_at=pending.created_at,
        expires_at=pending.expires_at,
    )


def _to_detail_response(pending) -> PendingUpdateDetailResponse:
    """Convert PendingUpdate entity to detailed response DTO."""
    content_preview = (
        pending.content[:500] + "..." if len(pending.content) > 500 else pending.content
    )

    return PendingUpdateDetailResponse(
        id=pending.id,
        source_id=pending.source_id,
        title=pending.title,
        content_preview=content_preview,
        content=pending.content,  # Full content
        content_hash=pending.content_hash,
        source_url=pending.source_url,
        category=(
            pending.category.value
            if hasattr(pending.category, "value")
            else pending.category
        ),
        detection_type=(
            pending.detection_type.value
            if hasattr(pending.detection_type, "value")
            else pending.detection_type
        ),
        similarity_score=pending.similarity_score,
        matched_doc_id=pending.matched_doc_id,
        matched_doc_ids=pending.matched_doc_ids or [],
        llm_analysis=pending.llm_analysis,
        llm_summary=pending.llm_summary,
        diff_summary=pending.diff_summary,
        status=(
            pending.status.value if hasattr(pending.status, "value") else pending.status
        ),
        priority=pending.priority,
        auto_approve_score=pending.auto_approve_score,
        reviewed_by=pending.reviewed_by,
        reviewed_at=pending.reviewed_at,
        review_note=pending.review_note,
        created_at=pending.created_at,
        expires_at=pending.expires_at,
        metadata=pending.metadata or {},
        raw_file_path=pending.raw_file_path,
    )


# ===== Routes =====


@router.get("", response_model=PendingUpdateListResponse)
async def list_pending_updates(
    skip: int = Query(default=0, ge=0),
    limit: int = Query(default=50, ge=1, le=100),
    status_filter: Optional[str] = Query(default="pending", alias="status"),
    category: Optional[str] = None,
    detection_type: Optional[str] = None,
    source_id: Optional[str] = None,
    is_admin: bool = Depends(verify_admin_api_key),
):
    """List pending updates in the approval queue."""
    repo = ServiceRegistry.get_pending_update_repository()

    use_case = ListPendingUpdatesUseCase(repo)

    # Convert string filters to enums if provided
    status_enum = PendingStatus(status_filter) if status_filter else None
    category_enum = DataCategory(category) if category else None
    detection_enum = UpdateDetectionType(detection_type) if detection_type else None

    # Create input dataclass
    input_data = ListPendingUpdatesInput(
        skip=skip,
        limit=limit,
        status=status_enum,
        category=category_enum,
        detection_type=detection_enum,
        source_id=source_id,
    )

    result = await use_case.execute(input_data)

    return PendingUpdateListResponse(
        items=[_to_response(p) for p in result.items],
        total=result.total,
        skip=result.skip,
        limit=result.limit,
    )


@router.get("/stats", response_model=ApprovalStatsResponse)
async def get_approval_stats(
    is_admin: bool = Depends(verify_admin_api_key),
):
    """Get statistics about the approval queue."""
    repo = ServiceRegistry.get_pending_update_repository()

    use_case = GetApprovalStatsUseCase(repo)
    stats = await use_case.execute()

    return ApprovalStatsResponse(
        total_pending=stats.total_pending,
        total_approved=stats.total_approved,
        total_rejected=stats.total_rejected,
        by_category=stats.by_category,
        by_detection_type=stats.by_detection_type,
        by_source=stats.by_source,
    )


@router.get("/{pending_id}", response_model=PendingUpdateDetailResponse)
async def get_pending_update(
    pending_id: str,
    is_admin: bool = Depends(verify_admin_api_key),
):
    """Get a single pending update by ID with full content."""
    repo = ServiceRegistry.get_pending_update_repository()

    pending = await repo.get_by_id(pending_id)
    if not pending:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Pending update with id '{pending_id}' not found",
        )

    return _to_detail_response(pending)


@router.post("/ingest", response_model=PendingUpdateDetailResponse)
async def ingest_pending_update(
    request: IngestUpdateRequest,
    is_admin: bool = Depends(verify_admin_api_key),
):
    """Ingest crawled content into the approval queue with LLM triage."""
    use_case = _build_ingest_use_case()

    category_enum = (
        DataCategory(request.category) if request.category else DataCategory.GENERAL
    )

    input_data = IngestPendingUpdateInput(
        source_id=request.source_id,
        title=request.title,
        content=request.content,
        source_url=request.source_url,
        collection=request.collection or "default",
        category=category_enum,
        metadata=request.metadata,
        priority=request.priority,
    )

    result = await use_case.execute(input_data)
    return _to_detail_response(result.pending)


@router.post("/{pending_id}/approve", response_model=ApprovalActionResponse)
async def approve_update(
    pending_id: str,
    request: Optional[ApproveUpdateRequest] = None,
    is_admin: bool = Depends(verify_admin_api_key),
):
    """Approve a pending update."""
    pending_repo = ServiceRegistry.get_pending_update_repository()
    doc_repo = ServiceRegistry.get_document_repository()
    embedding = ServiceRegistry.get_embedding()
    vector_store = ServiceRegistry.get_vector_store()
    from app.infrastructure.processing import TextChunker

    use_case = ApproveUpdateUseCase(
        pending_repository=pending_repo,
        document_repository=doc_repo,
        embedding_service=embedding,
        vector_store_service=vector_store,
        text_chunker=TextChunker(),
    )

    input_data = ApproveUpdateInput(
        pending_id=pending_id,
        reviewer_id="admin",  # TODO: Get from auth
        note=request.note if request else None,
    )

    try:
        result = await use_case.execute(input_data)
        return ApprovalActionResponse(
            success=result.success,
            message=result.message,
            document_id=result.document_id,
            replaced_doc_id=result.replaced_doc_id,
        )
    except ValueError as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e),
        )


@router.post("/{pending_id}/reject", response_model=ApprovalActionResponse)
async def reject_update(
    pending_id: str,
    request: Optional[RejectUpdateRequest] = None,
    is_admin: bool = Depends(verify_admin_api_key),
):
    """Reject a pending update."""
    repo = ServiceRegistry.get_pending_update_repository()

    use_case = RejectUpdateUseCase(repo)

    input_data = RejectUpdateInput(
        pending_id=pending_id,
        reviewer_id="admin",  # TODO: Get from auth
        note=request.note if request else None,
    )

    try:
        result = await use_case.execute(input_data)
        return ApprovalActionResponse(
            success=result.success,
            message=result.message,
        )
    except ValueError as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e),
        )


@router.post("/bulk/approve", response_model=BulkActionResponse)
async def bulk_approve(
    request: BulkActionRequest,
    is_admin: bool = Depends(verify_admin_api_key),
):
    """Bulk approve multiple pending updates."""
    repo = ServiceRegistry.get_pending_update_repository()

    count = await repo.bulk_approve(
        pending_ids=request.pending_ids,
        reviewer_id="admin",  # TODO: Get from auth
    )

    return BulkActionResponse(
        success=True,
        processed_count=count,
        message=f"Approved {count} pending updates",
    )


@router.post("/bulk/reject", response_model=BulkActionResponse)
async def bulk_reject(
    request: BulkActionRequest,
    is_admin: bool = Depends(verify_admin_api_key),
):
    """Bulk reject multiple pending updates."""
    repo = ServiceRegistry.get_pending_update_repository()

    count = await repo.bulk_reject(
        pending_ids=request.pending_ids,
        reviewer_id="admin",  # TODO: Get from auth
    )

    return BulkActionResponse(
        success=True,
        processed_count=count,
        message=f"Rejected {count} pending updates",
    )


def _build_ingest_use_case() -> IngestPendingUpdateUseCase:
    ingest_service = ServiceRegistry.get_document_ingest_service()
    return IngestPendingUpdateUseCase(ingest_service)
