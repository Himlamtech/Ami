"""Admin endpoints for monitor targets."""

from fastapi import APIRouter, Depends, HTTPException, status, Query

from app.api.dependencies.auth import verify_admin_api_key
from app.api.schemas.monitor_target_dto import (
    MonitorTargetRequest,
    MonitorTargetUpdateRequest,
    MonitorTargetResponse,
    MonitorTargetListResponse,
)
from app.application.use_cases.monitor_targets import (
    CreateMonitorTargetUseCase,
    CreateMonitorTargetInput,
    ListMonitorTargetsUseCase,
    ListMonitorTargetsInput,
    UpdateMonitorTargetUseCase,
    UpdateMonitorTargetInput,
    DeleteMonitorTargetUseCase,
    DeleteMonitorTargetInput,
)
from app.config.services import ServiceRegistry

router = APIRouter(
    prefix="/admin/monitor-targets",
    tags=["admin-monitor-targets"],
    dependencies=[Depends(verify_admin_api_key)],
)


def _to_response(target) -> MonitorTargetResponse:
    return MonitorTargetResponse(
        id=target.id,
        name=target.name,
        url=target.url,
        collection=target.collection,
        category=target.category,
        interval_hours=target.interval_hours,
        selector=target.selector,
        is_active=target.is_active,
        last_checked_at=target.last_checked_at,
        last_success_at=target.last_success_at,
        last_error=target.last_error,
        consecutive_failures=target.consecutive_failures,
        metadata=target.metadata,
        created_at=target.created_at,
        updated_at=target.updated_at,
    )


@router.post(
    "", response_model=MonitorTargetResponse, status_code=status.HTTP_201_CREATED
)
async def create_monitor_target(request: MonitorTargetRequest):
    repo = ServiceRegistry.get_monitor_target_repository()
    use_case = CreateMonitorTargetUseCase(repo)

    result = await use_case.execute(
        CreateMonitorTargetInput(
            name=request.name,
            url=request.url,
            collection=request.collection,
            category=request.category,
            interval_hours=request.interval_hours,
            selector=request.selector,
            metadata=request.metadata,
        )
    )
    return _to_response(result.target)


@router.get("", response_model=MonitorTargetListResponse)
async def list_monitor_targets(
    skip: int = Query(default=0, ge=0),
    limit: int = Query(default=100, ge=1, le=200),
):
    repo = ServiceRegistry.get_monitor_target_repository()
    use_case = ListMonitorTargetsUseCase(repo)

    result = await use_case.execute(ListMonitorTargetsInput(skip=skip, limit=limit))
    return MonitorTargetListResponse(
        items=[_to_response(t) for t in result.items],
        total=result.total,
        skip=result.skip,
        limit=result.limit,
    )


@router.put("/{target_id}", response_model=MonitorTargetResponse)
async def update_monitor_target(target_id: str, request: MonitorTargetUpdateRequest):
    repo = ServiceRegistry.get_monitor_target_repository()
    use_case = UpdateMonitorTargetUseCase(repo)

    try:
        result = await use_case.execute(
            UpdateMonitorTargetInput(
                target_id=target_id,
                name=request.name,
                url=request.url,
                collection=request.collection,
                category=request.category,
                interval_hours=request.interval_hours,
                selector=request.selector,
                metadata=request.metadata,
                is_active=request.is_active,
            )
        )
        return _to_response(result.target)
    except ValueError as e:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=str(e))


@router.delete("/{target_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_monitor_target(target_id: str):
    repo = ServiceRegistry.get_monitor_target_repository()
    use_case = DeleteMonitorTargetUseCase(repo)

    result = await use_case.execute(DeleteMonitorTargetInput(target_id=target_id))
    if not result.success:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Monitor target {target_id} not found",
        )
    return {"success": True}
