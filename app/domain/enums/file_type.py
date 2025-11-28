"""File type enumeration."""

from enum import Enum


class FileType(str, Enum):
    """Type of file."""
    
    UPLOADED = "uploaded"
    GENERATED = "generated"
    AVATAR = "avatar"
    THUMBNAIL = "thumbnail"
