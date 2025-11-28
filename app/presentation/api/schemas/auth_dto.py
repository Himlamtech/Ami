"""Authentication DTOs (Data Transfer Objects)."""

from pydantic import BaseModel, EmailStr
from typing import Optional


class RegisterRequest(BaseModel):
    """User registration request."""
    username: str
    email: EmailStr
    password: str
    full_name: Optional[str] = None


class LoginRequest(BaseModel):
    """Login request."""
    username: str
    password: str


class TokenResponse(BaseModel):
    """JWT token response."""
    access_token: str
    token_type: str = "bearer"


class UserResponse(BaseModel):
    """User information response."""
    id: str
    username: str
    email: str
    full_name: Optional[str]
    is_active: bool
    role_ids: list = []
    
    class Config:
        from_attributes = True
