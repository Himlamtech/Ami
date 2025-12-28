"""API versioned packages."""

from .chat.router import router as chat_api_router  # noqa: F401
from .admin.router import router as admin_api_router  # noqa: F401
from .auth.router import router as auth_api_router  # noqa: F401
from .logs.router import router as logs_api_router  # noqa: F401

__all__ = ["chat_api_router", "admin_api_router", "auth_api_router", "logs_api_router"]
