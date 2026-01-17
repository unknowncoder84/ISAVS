"""
Authentication Models
Pydantic models for authentication requests and responses
"""
from pydantic import BaseModel, EmailStr, Field
from typing import Optional
from datetime import datetime


class LoginRequest(BaseModel):
    """Request model for login endpoint"""
    token: str = Field(..., description="Supabase JWT token from OAuth")


class RegisterRequest(BaseModel):
    """Request model for student registration"""
    name: str = Field(..., min_length=2, max_length=255)
    student_id_card_number: str = Field(..., min_length=1, max_length=50)
    face_image: str = Field(..., description="Base64 encoded face image")
    # Email comes from Supabase token, not from request


class UserResponse(BaseModel):
    """Response model for user information"""
    id: int
    email: str
    name: str
    role: str  # 'admin', 'teacher', 'student'
    created_at: datetime
    
    class Config:
        from_attributes = True


class LoginResponse(BaseModel):
    """Response model for login endpoint"""
    success: bool
    user: UserResponse
    message: str


class RegisterResponse(BaseModel):
    """Response model for registration endpoint"""
    success: bool
    student_id: int
    message: str


class LogoutResponse(BaseModel):
    """Response model for logout endpoint"""
    success: bool
    message: str
