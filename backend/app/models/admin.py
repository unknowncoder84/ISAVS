"""
Admin Models
Pydantic models for admin operations
"""
from pydantic import BaseModel, EmailStr, Field
from typing import Optional
from datetime import datetime


class CreateTeacherRequest(BaseModel):
    """Request model for creating a teacher"""
    email: EmailStr
    name: str = Field(..., min_length=2, max_length=255)
    department: Optional[str] = Field(None, max_length=255)


class UpdateTeacherRequest(BaseModel):
    """Request model for updating a teacher"""
    department: Optional[str] = Field(None, max_length=255)
    active: Optional[bool] = None


class TeacherResponse(BaseModel):
    """Response model for teacher information"""
    id: int
    user_id: int
    email: str
    name: str
    department: Optional[str]
    active: bool
    created_at: datetime
    
    class Config:
        from_attributes = True


class ApproveStudentRequest(BaseModel):
    """Request model for approving a student"""
    student_id: int


class RejectStudentRequest(BaseModel):
    """Request model for rejecting a student"""
    student_id: int
    reason: str = Field(..., min_length=1, max_length=500)


class PendingStudentResponse(BaseModel):
    """Response model for pending student information"""
    id: int
    name: str
    student_id_card_number: str
    email: Optional[str]
    face_image_base64: Optional[str]
    created_at: datetime
    approval_status: str
    
    class Config:
        from_attributes = True


class StudentApprovalResponse(BaseModel):
    """Response model for student approval/rejection"""
    success: bool
    student_id: int
    status: str  # 'approved' or 'rejected'
    message: str
