"""Log level and action enumerations."""

from enum import Enum


class LogLevel(str, Enum):
    """Log severity levels."""
    
    DEBUG = "debug"
    INFO = "info"
    WARNING = "warning"
    ERROR = "error"
    CRITICAL = "critical"


class LogAction(str, Enum):
    """Types of logged actions."""
    
    # Authentication
    LOGIN = "login"
    LOGOUT = "logout"
    LOGIN_FAILED = "login_failed"
    
    # Chat
    CHAT_MESSAGE = "chat_message"
    CHAT_RESPONSE = "chat_response"
    CHAT_ERROR = "chat_error"
    
    # Document Management
    DOCUMENT_UPLOAD = "document_upload"
    DOCUMENT_DELETE = "document_delete"
    DOCUMENT_VIEW = "document_view"
    
    # Web Crawling
    CRAWL_START = "crawl_start"
    CRAWL_SUCCESS = "crawl_success"
    CRAWL_ERROR = "crawl_error"
    
    # User Management
    USER_CREATE = "user_create"
    USER_UPDATE = "user_update"
    USER_DELETE = "user_delete"
    
    # System
    SYSTEM_START = "system_start"
    SYSTEM_ERROR = "system_error"
    API_ERROR = "api_error"
