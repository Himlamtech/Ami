"""Admin Analytics Routes - UC-A-003: Analytics & Cost Monitoring."""

from fastapi import APIRouter, Depends, Query
from datetime import datetime, timedelta

from app.api.dependencies.auth import verify_admin_api_key
from app.api.schemas.admin_dto import (
    AnalyticsOverview,
    UsageAnalyticsResponse,
    UsageTrend,
    CostBreakdown,
    CostAnalyticsResponse,
    LatencyPercentiles,
    ErrorBreakdown,
    SlowQuery,
    PerformanceAnalyticsResponse,
    BudgetAlertRequest,
)
from app.infrastructure.factory import get_factory


router = APIRouter(prefix="/admin/analytics", tags=["Admin - Analytics"])


def _parse_period(period: str) -> tuple[datetime, datetime]:
    """Parse period string to date range."""
    now = datetime.now()

    if period == "today":
        date_from = now.replace(hour=0, minute=0, second=0, microsecond=0)
    elif period == "week":
        date_from = now - timedelta(days=7)
    elif period == "month":
        date_from = now - timedelta(days=30)
    elif period == "quarter":
        date_from = now - timedelta(days=90)
    else:
        date_from = now - timedelta(days=30)

    return date_from, now


@router.get("/overview", response_model=AnalyticsOverview)
async def get_analytics_overview(
    period: str = Query(default="today", pattern="^(today|week|month)$"),
    is_admin: bool = Depends(verify_admin_api_key),
):
    """
    Get real-time analytics overview.

    Period options: today, week, month
    """
    factory = get_factory()
    usage_repo = factory.get_usage_metric_repository()

    date_from, date_to = _parse_period(period)

    stats = await usage_repo.get_overview_stats(
        date_from=date_from,
        date_to=date_to,
    )

    return AnalyticsOverview(
        requests=stats.get("total_requests", 0),
        active_users=stats.get("unique_users", 0),
        avg_latency_ms=stats.get("avg_latency_ms", 0.0),
        error_rate=stats.get("error_rate", 0.0),
    )


@router.get("/usage", response_model=UsageAnalyticsResponse)
async def get_usage_analytics(
    period: str = Query(default="month", pattern="^(week|month|quarter)$"),
    group_by: str = Query(default="day", pattern="^(day|hour|endpoint)$"),
    is_admin: bool = Depends(verify_admin_api_key),
):
    """
    Get detailed usage analytics.

    - DAU/WAU/MAU trends
    - Requests by endpoint
    - Peak hours heatmap
    """
    factory = get_factory()
    usage_repo = factory.get_usage_metric_repository()
    daily_repo = factory.get_daily_stats_repository()

    date_from, date_to = _parse_period(period)

    # Get daily stats
    daily_stats = await daily_repo.get_range(date_from, date_to)

    # Get by endpoint
    by_endpoint_data = await usage_repo.get_requests_by_endpoint(
        date_from=date_from,
        date_to=date_to,
    )

    # Get peak hours
    hourly_data = await usage_repo.get_hourly_distribution(
        date_from=date_from,
        date_to=date_to,
    )

    return UsageAnalyticsResponse(
        data=[
            UsageTrend(
                date=stat.date.strftime("%Y-%m-%d"),
                requests=stat.total_requests,
                users=stat.unique_users,
            )
            for stat in daily_stats
        ],
        by_endpoint={item["endpoint"]: item["count"] for item in by_endpoint_data},
        peak_hours=hourly_data,
    )


@router.get("/costs", response_model=CostAnalyticsResponse)
async def get_cost_analytics(
    period: str = Query(default="month", pattern="^(week|month|quarter)$"),
    breakdown: str = Query(default="provider", pattern="^(provider|model|use_case)$"),
    is_admin: bool = Depends(verify_admin_api_key),
):
    """
    Get cost analytics and breakdown.

    Breakdown options: provider, model, use_case
    """
    factory = get_factory()
    llm_repo = factory.get_llm_usage_repository()

    date_from, date_to = _parse_period(period)

    # Get summary
    summary = await llm_repo.get_cost_summary(date_from=date_from, date_to=date_to)

    # Get breakdowns
    by_provider = await llm_repo.get_cost_by_provider(
        date_from=date_from, date_to=date_to
    )
    by_model = await llm_repo.get_cost_by_model(date_from=date_from, date_to=date_to)
    by_use_case = await llm_repo.get_cost_by_use_case(
        date_from=date_from, date_to=date_to
    )

    # Get daily costs
    days = {"week": 7, "month": 30, "quarter": 90}[period]
    daily_costs = await llm_repo.get_daily_costs(days=days)

    return CostAnalyticsResponse(
        total=summary.get("total_cost", 0.0),
        by_provider=[
            CostBreakdown(
                name=item["provider"],
                cost=item["cost"],
                tokens=item["tokens"],
                percentage=item["percentage"],
            )
            for item in by_provider
        ],
        by_model=[
            CostBreakdown(
                name=item["model"],
                cost=item["cost"],
                tokens=item["tokens"],
                percentage=item["percentage"],
            )
            for item in by_model
        ],
        by_use_case=[
            CostBreakdown(
                name=item["use_case"],
                cost=item["cost"],
                tokens=item["tokens"],
                percentage=item["percentage"],
            )
            for item in by_use_case
        ],
        daily=daily_costs,
    )


@router.get("/performance", response_model=PerformanceAnalyticsResponse)
async def get_performance_analytics(
    period: str = Query(default="week", pattern="^(today|week|month)$"),
    is_admin: bool = Depends(verify_admin_api_key),
):
    """
    Get performance metrics.

    - Response time percentiles (P50, P95, P99)
    - Error breakdown by type
    - Slow queries list
    """
    factory = get_factory()
    usage_repo = factory.get_usage_metric_repository()

    date_from, date_to = _parse_period(period)

    # Get latency percentiles
    percentiles = await usage_repo.get_latency_percentiles(
        date_from=date_from,
        date_to=date_to,
    )

    # Get error requests
    errors = await usage_repo.get_error_requests(
        limit=100,
        date_from=date_from,
        date_to=date_to,
    )

    # Group errors by type
    error_counts = {}
    for err in errors:
        err_type = err.error_message or "Unknown"
        error_counts[err_type] = error_counts.get(err_type, 0) + 1

    total_errors = len(errors)
    error_breakdown = [
        ErrorBreakdown(
            error_type=err_type,
            count=count,
            percentage=round(count / total_errors * 100, 2) if total_errors > 0 else 0,
        )
        for err_type, count in sorted(error_counts.items(), key=lambda x: -x[1])[:10]
    ]

    # Get slow queries
    slow = await usage_repo.get_slow_requests(
        threshold_ms=3000,
        limit=20,
        date_from=date_from,
        date_to=date_to,
    )

    return PerformanceAnalyticsResponse(
        latency_percentiles=LatencyPercentiles(
            p50=percentiles.get("p50", 0),
            p75=percentiles.get("p75", 0),
            p90=percentiles.get("p90", 0),
            p95=percentiles.get("p95", 0),
            p99=percentiles.get("p99", 0),
        ),
        error_breakdown=error_breakdown,
        slow_queries=[
            SlowQuery(
                endpoint=q.endpoint,
                latency_ms=q.latency_ms,
                timestamp=q.timestamp,
                user_id=q.user_id,
            )
            for q in slow
        ],
    )


@router.post("/budget-alert")
async def set_budget_alert(
    request: BudgetAlertRequest,
    is_admin: bool = Depends(verify_admin_api_key),
):
    """
    Set budget alert threshold.

    Will notify when monthly cost exceeds threshold.
    """
    # TODO: Implement budget alert storage and notification
    return {
        "status": "ok",
        "threshold_usd": request.threshold_usd,
        "notify_email": request.notify_email,
        "notify_slack": request.notify_slack,
    }


@router.get("/export")
async def export_analytics(
    type: str = Query(..., pattern="^(usage|costs|performance)$"),
    format: str = Query(default="json", pattern="^(json|csv)$"),
    period: str = Query(default="month", pattern="^(week|month|quarter)$"),
    is_admin: bool = Depends(verify_admin_api_key),
):
    """
    Export analytics data.

    Types: usage, costs, performance
    Formats: json, csv
    """
    factory = get_factory()
    date_from, date_to = _parse_period(period)

    if type == "usage":
        usage_repo = factory.get_usage_metric_repository()
        stats = await usage_repo.get_overview_stats(
            date_from=date_from, date_to=date_to
        )
        by_endpoint = await usage_repo.get_requests_by_endpoint(
            date_from=date_from, date_to=date_to
        )

        return {
            "type": "usage",
            "period": period,
            "data": {
                "overview": stats,
                "by_endpoint": by_endpoint,
            },
        }

    elif type == "costs":
        llm_repo = factory.get_llm_usage_repository()
        summary = await llm_repo.get_cost_summary(date_from=date_from, date_to=date_to)
        by_provider = await llm_repo.get_cost_by_provider(
            date_from=date_from, date_to=date_to
        )

        return {
            "type": "costs",
            "period": period,
            "data": {
                "summary": summary,
                "by_provider": by_provider,
            },
        }

    else:  # performance
        usage_repo = factory.get_usage_metric_repository()
        percentiles = await usage_repo.get_latency_percentiles(
            date_from=date_from, date_to=date_to
        )

        return {
            "type": "performance",
            "period": period,
            "data": {
                "latency_percentiles": percentiles,
            },
        }
