"""
MongoDB Pydantic models for documents and users.
Clean data models following domain-driven design.
"""

from datetime import datetime
from enum import Enum
from typing import Any, Dict, List, Optional

from pydantic import BaseModel, EmailStr, Field


class UserRole(str, Enum):
    """User roles for access control."""
    
    ADMIN = "admin"
    USER = "user"


class UserBase(BaseModel):
    """Base user model."""
    
    username: str = Field(..., min_length=3, max_length=50)
    email: EmailStr
    full_name: Optional[str] = None
    role: UserRole = UserRole.USER
    is_active: bool = True


class UserCreate(UserBase):
    """Model for creating a new user."""
    
    password: str = Field(..., min_length=8)


class UserUpdate(BaseModel):
    """Model for updating user information."""
    
    email: Optional[EmailStr] = None
    full_name: Optional[str] = None
    role: Optional[UserRole] = None
    is_active: Optional[bool] = None
    password: Optional[str] = Field(None, min_length=8)


class UserInDB(UserBase):
    """User model as stored in database."""
    
    id: str = Field(alias="_id")
    hashed_password: str
    created_at: datetime = Field(default_factory=datetime.now)
    updated_at: datetime = Field(default_factory=datetime.now)
    last_login: Optional[datetime] = None

    class Config:
        populate_by_name = True


class UserResponse(UserBase):
    """User model for API responses (without sensitive data)."""
    
    id: str
    created_at: datetime
    last_login: Optional[datetime] = None


class DocumentBase(BaseModel):
    """Base document model."""
    
    title: str = Field(..., min_length=1, max_length=500)
    file_name: str = Field(..., min_length=1, max_length=255)
    content: Optional[str] = None
    metadata: Dict[str, Any] = Field(default_factory=dict)
    tags: List[str] = Field(default_factory=list)
    is_active: bool = True


class DocumentCreate(DocumentBase):
    """Model for creating a new document."""
    
    collection: str = "default"


class DocumentUpdate(BaseModel):
    """Model for updating document metadata."""
    
    title: Optional[str] = Field(None, min_length=1, max_length=500)
    file_name: Optional[str] = Field(None, min_length=1, max_length=255)
    content: Optional[str] = None
    metadata: Optional[Dict[str, Any]] = None
    tags: Optional[List[str]] = None
    is_active: Optional[bool] = None


class DocumentInDB(DocumentBase):
    """Document model as stored in database."""
    
    id: str = Field(alias="_id")
    collection: str = "default"
    chunk_count: int = 0
    created_at: datetime = Field(default_factory=datetime.now)
    updated_at: datetime = Field(default_factory=datetime.now)
    created_by: Optional[str] = None  # User ID
    
    class Config:
        populate_by_name = True


class DocumentResponse(DocumentBase):
    """Document model for API responses."""
    
    id: str
    collection: str
    chunk_count: int
    created_at: datetime
    updated_at: datetime


class VectorMapping(BaseModel):
    """Mapping between MongoDB document and Qdrant vector point."""
    
    document_id: str
    qdrant_point_id: str
    chunk_index: int
    metadata: Dict[str, Any] = Field(default_factory=dict)


class LoginRequest(BaseModel):
    """Login request model."""
    
    username: str
    password: str


class LoginResponse(BaseModel):
    """Login response model."""
    
    access_token: str
    token_type: str = "bearer"
    user: UserResponse


class Token(BaseModel):
    """JWT token model."""
    
    access_token: str
    token_type: str = "bearer"


class TokenData(BaseModel):
    """Token payload data."""
    
    username: Optional[str] = None
    role: Optional[str] = None


class DocumentListResponse(BaseModel):
    """Paginated document list response."""
    
    documents: List[DocumentResponse]
    total: int
    skip: int
    limit: int


class UserListResponse(BaseModel):
    """Paginated user list response."""
    
    users: List[UserResponse]
    total: int
    skip: int
    limit: int

