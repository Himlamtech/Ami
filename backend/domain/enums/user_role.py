"""User role enumeration."""

from enum import Enum


class UserRole(str, Enum):
    """User roles for access control."""

    ADMIN = "admin"
    MANAGER = "manager"
    USER = "user"
