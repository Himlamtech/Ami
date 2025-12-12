"""Aggregated Admin API routes (RBAC-protected)."""

from fastapi import APIRouter

from .analytics import router as analytics_router
from .approvals import router as approvals_router
from .conversations import router as conversations_router
from .data_sources import router as data_sources_router
from .feedback import router as feedback_router
from .knowledge import router as knowledge_router
from .dashboard import router as dashboard_router
from .sync import router as sync_router
from .users import router as users_router
from .vector_admin import router as vector_admin_router
from .vector_store import router as vector_store_router
from .crawler import router as crawler_router
from .config import router as admin_config_router

router = APIRouter()

# Core admin resources
router.include_router(dashboard_router)
router.include_router(users_router)
router.include_router(admin_config_router)
router.include_router(vector_admin_router)
router.include_router(vector_store_router)
router.include_router(data_sources_router)
router.include_router(approvals_router)

# Ops & sync
router.include_router(sync_router)
router.include_router(crawler_router)

# Observability
router.include_router(conversations_router)
router.include_router(feedback_router)
router.include_router(analytics_router)
router.include_router(knowledge_router)

__all__ = ["router"]
