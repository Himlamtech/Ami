"""API versioned packages."""

from .chat.router import router as chat_api_router  # noqa: F401
from .admin.router import router as admin_api_router  # noqa: F401

__all__ = ["chat_api_router", "admin_api_router"]
