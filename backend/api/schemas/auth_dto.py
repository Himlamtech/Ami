from pydantic import BaseModel, EmailStr, Field
from typing import Optional


class LoginRequest(BaseModel):
    email: str
    password: str


class RegisterRequest(BaseModel):
    email: EmailStr
    password: str
    password_confirmation: str
    full_name: str
    username: Optional[str] = None
    role: Optional[str] = None


class AuthResponse(BaseModel):
    user_id: str
    token: str
    role: str
    full_name: str
    email: str
