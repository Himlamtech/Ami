"""API routes package."""

from .auth_routes import router as auth_router
from .chat_history_routes import router as chat_router
from .generate_routes import router as generate_router
from .vectordb_routes import router as vectordb_router
from .image_routes import router as image_router
from .admin_routes import router as admin_router
from .crawler_routes import router as crawler_router
from .config_routes import router as config_router

__all__ = [
    "auth_router",
    "chat_router",
    "generate_router",
    "vectordb_router",
    "image_router",
    "admin_router",
    "crawler_router",
    "config_router",
]
