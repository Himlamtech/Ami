"""Admin routes for Data Source management."""

from fastapi import APIRouter, Depends, HTTPException, status, Query
from typing import Optional

from api.dependencies.auth import verify_admin_api_key
from api.schemas.data_source_dto import (
    CreateDataSourceRequest,
    UpdateDataSourceRequest,
    TestDataSourceRequest,
    DataSourceResponse,
    DataSourceListResponse,
    TestDataSourceResponse,
    CrawlConfigResponse,
    AuthConfigResponse,
)
from domain.enums.data_source import (
    DataCategory,
    SourceType,
    SourceStatus,
)
from domain.entities.data_source import DataSource
from application.use_cases.data_source import (
    CreateDataSourceUseCase,
    ListDataSourcesUseCase,
    UpdateDataSourceUseCase,
    DeleteDataSourceUseCase,
    TestDataSourceUseCase,
)
from application.use_cases.data_source.create_data_source import (
    CreateDataSourceInput,
)
from application.use_cases.data_source.list_data_sources import ListDataSourcesInput
from application.use_cases.data_source.update_data_source import (
    UpdateDataSourceInput,
)
from application.use_cases.data_source.delete_data_source import (
    DeleteDataSourceInput,
)
from application.use_cases.data_source.test_data_source import TestDataSourceInput
from config.services import ServiceRegistry


router = APIRouter(prefix="/admin/data-sources", tags=["admin-data-sources"])


# ===== Helper Functions =====


def _to_response(source: DataSource) -> DataSourceResponse:
    """Convert DataSource entity to response DTO."""
    crawl_config = None
    if source.crawl_config:
        crawl_config = CrawlConfigResponse(
            selectors=source.crawl_config.selectors,
            exclude_selectors=source.crawl_config.exclude_selectors,
            max_depth=source.crawl_config.max_depth,
            max_pages=source.crawl_config.max_pages,
            follow_links=source.crawl_config.follow_links,
            allowed_domains=source.crawl_config.allowed_domains,
            rate_limit_delay=source.crawl_config.rate_limit_delay,
            timeout=source.crawl_config.timeout,
            user_agent=source.crawl_config.user_agent,
        )

    auth_config = None
    if source.auth and source.auth.auth_type != "none":
        auth_config = AuthConfigResponse(
            auth_type=source.auth.auth_type,
            has_credentials=bool(
                source.auth.username or source.auth.token or source.auth.cookies
            ),
        )

    return DataSourceResponse(
        id=source.id,
        name=source.name,
        description=source.description,
        base_url=source.base_url,
        source_type=(
            source.source_type.value
            if isinstance(source.source_type, SourceType)
            else source.source_type
        ),
        category=(
            source.category.value
            if isinstance(source.category, DataCategory)
            else source.category
        ),
        data_type=(
            source.data_type.value
            if hasattr(source.data_type, "value")
            else source.data_type
        ),
        schedule_cron=source.schedule_cron,
        crawl_config=crawl_config,
        auth_config=auth_config,
        status=(
            source.status.value
            if isinstance(source.status, SourceStatus)
            else source.status
        ),
        last_crawl_at=source.last_crawl_at,
        next_crawl_at=source.next_crawl_at,
        crawl_count=source.crawl_count,
        success_count=source.success_count,
        error_count=source.error_count,
        last_error=source.last_error,
        created_at=source.created_at,
        updated_at=source.updated_at,
    )


# ===== Routes =====


@router.post("", response_model=DataSourceResponse, status_code=status.HTTP_201_CREATED)
async def create_data_source(
    request: CreateDataSourceRequest,
    is_admin: bool = Depends(verify_admin_api_key),
):
    """Create a new data source."""
    repo = ServiceRegistry.get_data_source_repository()

    use_case = CreateDataSourceUseCase(repo)

    input_data = CreateDataSourceInput(
        name=request.name,
        base_url=request.base_url,
        source_type=SourceType(request.source_type),
        category=DataCategory(request.category),
        description=request.description,
        schedule_cron=request.schedule_cron or "0 */6 * * *",
        priority=request.priority or 5,
        auth_type=request.auth_type or "none",
        auth_username=request.auth_username,
        auth_password=request.auth_password,
        auth_token=request.auth_token,
        auth_headers=request.auth_headers,
        list_selector=request.crawl_selectors[0] if request.crawl_selectors else None,
        max_depth=request.crawl_max_depth or 2,
        max_pages=request.crawl_max_pages or 50,
        rate_limit=int(request.crawl_rate_limit_delay or 1),
    )

    try:
        result = await use_case.execute(input_data)
        return _to_response(result.source)
    except ValueError as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e),
        )


@router.get("", response_model=DataSourceListResponse)
async def list_data_sources(
    skip: int = Query(default=0, ge=0),
    limit: int = Query(default=50, ge=1, le=100),
    status_filter: Optional[str] = Query(default=None, alias="status"),
    category: Optional[str] = None,
    is_admin: bool = Depends(verify_admin_api_key),
):
    """List all data sources."""
    repo = ServiceRegistry.get_data_source_repository()

    use_case = ListDataSourcesUseCase(repo)

    # Convert string filters to enums if provided
    status_enum = SourceStatus(status_filter) if status_filter else None
    category_enum = DataCategory(category) if category else None

    input_data = ListDataSourcesInput(
        skip=skip,
        limit=limit,
        status=status_enum,
        category=category_enum,
    )

    result = await use_case.execute(input_data)

    return DataSourceListResponse(
        items=[_to_response(s) for s in result.sources],
        total=result.total,
        skip=result.skip,
        limit=result.limit,
    )


@router.get("/{source_id}", response_model=DataSourceResponse)
async def get_data_source(
    source_id: str,
    is_admin: bool = Depends(verify_admin_api_key),
):
    """Get a single data source by ID."""
    repo = ServiceRegistry.get_data_source_repository()

    source = await repo.get_by_id(source_id)
    if not source:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Data source with id '{source_id}' not found",
        )

    return _to_response(source)


@router.put("/{source_id}", response_model=DataSourceResponse)
async def update_data_source(
    source_id: str,
    request: UpdateDataSourceRequest,
    is_admin: bool = Depends(verify_admin_api_key),
):
    """Update a data source."""
    repo = ServiceRegistry.get_data_source_repository()

    use_case = UpdateDataSourceUseCase(repo)

    # Convert to enum types if provided
    source_type = SourceType(request.source_type) if request.source_type else None
    category = DataCategory(request.category) if request.category else None

    input_data = UpdateDataSourceInput(
        source_id=source_id,
        name=request.name,
        base_url=request.base_url,
        source_type=source_type,
        category=category,
        schedule_cron=request.schedule_cron,
        priority=request.priority,
        description=request.description,
        auth_type=request.auth_type,
        auth_username=request.auth_username,
        auth_password=request.auth_password,
        auth_token=request.auth_token,
        auth_headers=request.auth_headers,
        list_selector=request.crawl_selectors[0] if request.crawl_selectors else None,
        max_depth=request.crawl_max_depth,
        max_pages=request.crawl_max_pages,
        rate_limit=(
            int(request.crawl_rate_limit_delay)
            if request.crawl_rate_limit_delay
            else None
        ),
    )

    try:
        result = await use_case.execute(input_data)
        return _to_response(result.source)
    except ValueError as e:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=str(e),
        )


@router.delete("/{source_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_data_source(
    source_id: str,
    is_admin: bool = Depends(verify_admin_api_key),
):
    """Delete a data source."""
    repo = ServiceRegistry.get_data_source_repository()

    use_case = DeleteDataSourceUseCase(repo)

    input_data = DeleteDataSourceInput(source_id=source_id)

    try:
        await use_case.execute(input_data)
    except ValueError as e:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=str(e),
        )

    return None


@router.post("/{source_id}/activate", response_model=DataSourceResponse)
async def activate_data_source(
    source_id: str,
    is_admin: bool = Depends(verify_admin_api_key),
):
    """Activate a data source."""
    repo = ServiceRegistry.get_data_source_repository()

    source = await repo.get_by_id(source_id)
    if not source:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Data source with id '{source_id}' not found",
        )

    source.activate()
    await repo.update(source)

    return _to_response(source)


@router.post("/{source_id}/pause", response_model=DataSourceResponse)
async def pause_data_source(
    source_id: str,
    is_admin: bool = Depends(verify_admin_api_key),
):
    """Pause a data source."""
    repo = ServiceRegistry.get_data_source_repository()

    source = await repo.get_by_id(source_id)
    if not source:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Data source with id '{source_id}' not found",
        )

    source.pause()
    await repo.update(source)

    return _to_response(source)


@router.post("/test", response_model=TestDataSourceResponse)
async def test_data_source(
    request: TestDataSourceRequest,
    is_admin: bool = Depends(verify_admin_api_key),
):
    """Test crawling a URL before saving."""
    # Get crawler from factory
    crawler = factory.get_firecrawl_crawler()

    use_case = TestDataSourceUseCase(crawler)

    input_data = TestDataSourceInput(
        url=request.url,
        source_type=(
            SourceType(request.source_type)
            if request.source_type
            else SourceType.WEB_CRAWL
        ),
        detail_selector=request.crawl_selectors[0] if request.crawl_selectors else None,
        auth_type=request.auth_type or "none",
        auth_token=request.auth_token,
        auth_headers=request.auth_headers,
    )

    result = await use_case.execute(input_data)

    return TestDataSourceResponse(
        success=result.success,
        message=result.error if not result.success else "Successfully crawled URL",
        content_preview=result.content_preview,
        content_length=result.content_length,
        response_time_ms=int(result.duration_seconds * 1000),
        detected_encoding=None,  # Not available from firecrawl
    )
