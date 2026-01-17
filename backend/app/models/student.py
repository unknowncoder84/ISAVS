"""
Student Models
Pydantic models for student operations
"""
from pydantic import BaseModel, Field
from typing import Optional
from datetime import datetime


class StudentProfileResponse(BaseModel):
    """Response model for student profile"""
    id: int
    name: str
    student_id_card_number: str
    email: Optional[str]
    approval_status: str
    created_at: datetime
    approved_at: Optional[datetime]
    
    class Config:
        from_attributes = True


class UpdateStudentProfileRequest(BaseModel):
    """Request model for updating student profile"""
    name: Optional[str] = Field(None, min_length=2, max_length=255)


class AttendanceRecordResponse(BaseModel):
    """Response model for attendance record"""
    id: int
    session_id: int
    class_id: Optional[str]
    timestamp: datetime
    verification_status: str
    face_confidence: Optional[float]
    otp_verified: bool
    
    class Config:
        from_attributes = True


class AttendanceStatsResponse(BaseModel):
    """Response model for attendance statistics"""
    total_sessions: int
    attended_sessions: int
    attendance_rate: float
    last_attendance: Optional[datetime]
