from pydantic import BaseModel, EmailStr, Field
from typing import Optional


class LoginRequest(BaseModel):
    email: EmailStr
    password: str


class RegisterRequest(BaseModel):
    email: EmailStr
    password: str
    password_confirmation: str
    full_name: str


class AuthResponse(BaseModel):
    user_id: str
    token: str  # This will be either the admin_api_key or just user_id for students
    role: str
    full_name: str
    email: str
