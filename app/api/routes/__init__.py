"""API routes package."""

from .chat_history_routes import router as chat_router
from .generate_routes import router as generate_router
from .vectordb_routes import router as vectordb_router
from .image_routes import router as image_router
from .admin_routes import router as admin_router
from .crawler_routes import router as crawler_router
from .config_routes import router as config_router
from .admin_vectordb_routes import router as admin_vectordb_router
from .admin_data_source_routes import router as admin_data_source_router
from .admin_approval_routes import router as admin_approval_router
from .smart_query_routes import router as smart_query_router
from .admin_sync_routes import router as admin_sync_router
from .profile_routes import router as profile_router
from .feedback_routes import router as feedback_router
from .multimodal_routes import router as multimodal_router

__all__ = [
    "chat_router",
    "generate_router",
    "vectordb_router",
    "image_router",
    "admin_router",
    "crawler_router",
    "config_router",
    "admin_vectordb_router",
    "admin_data_source_router",
    "admin_approval_router",
    "smart_query_router",
    "admin_sync_router",
    "profile_router",
    "feedback_router",
    "multimodal_router",
]
