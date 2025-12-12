"""Usage Tracking Middleware - Tracks all API requests for analytics."""

from fastapi import Request
from datetime import datetime
import time
import uuid
from typing import Callable

from app.config.services import ServiceRegistry
from app.domain.entities.usage_metric import UsageMetric, RequestStatus


async def usage_tracking_middleware(request: Request, call_next: Callable):
    """
    Middleware to track API usage metrics.
    
    Logs:
    - Endpoint
    - Method
    - User ID
    - Latency
    - Status code
    - Timestamp
    - Error message (if any)
    """
    start_time = time.time()
    
    # Get user ID from header
    user_id = request.headers.get("X-User-ID")
    
    # Call the endpoint
    response = await call_next(request)
    
    # Calculate latency
    latency_ms = int((time.time() - start_time) * 1000)
    
    # Skip tracking for health check and static files
    if request.url.path in ["/health", "/favicon.ico"] or request.url.path.startswith("/assets"):
        return response
    
    # Log usage metric
    try:
        usage_repo = ServiceRegistry.get_usage_metric_repository()
        
        # Determine if this is an error
        is_error = response.status_code >= 400
        status = RequestStatus.ERROR if is_error else RequestStatus.SUCCESS
        error_message = None
        if is_error:
            error_message = f"HTTP {response.status_code}"
        
        # Create usage metric
        metric = UsageMetric(
            id=str(uuid.uuid4()),
            endpoint=request.url.path,
            method=request.method,
            user_id=user_id,
            latency_ms=latency_ms,
            status=status,
            status_code=response.status_code,
            error_message=error_message,
            timestamp=datetime.now(),
        )
        
        await usage_repo.create(metric)
        
    except Exception as e:
        # Don't fail the request if logging fails
        print(f"[Usage Tracking] Failed to log metric: {e}")
    
    return response

