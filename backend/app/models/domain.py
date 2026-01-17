"""
Domain Models for ISAVS
"""
from datetime import datetime
from typing import Optional, List, Literal
from pydantic import BaseModel, Field


class Student(BaseModel):
    """Student domain model."""
    id: int
    name: str
    student_id_card_number: str
    facial_embedding: List[float] = Field(..., min_length=128, max_length=128)
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True


class Class(BaseModel):
    """Class domain model."""
    id: int
    class_id: str
    name: str
    created_at: datetime

    class Config:
        from_attributes = True


class ClassEnrollment(BaseModel):
    """Class enrollment domain model."""
    id: int
    class_id: int
    student_id: int

    class Config:
        from_attributes = True


class AttendanceSession(BaseModel):
    """Attendance session domain model."""
    id: int
    session_id: str
    class_id: int
    started_at: datetime
    expires_at: datetime
    status: Literal['active', 'expired', 'completed']

    class Config:
        from_attributes = True


class Attendance(BaseModel):
    """Attendance domain model."""
    id: int
    student_id: int
    session_id: int
    timestamp: datetime
    verification_status: Literal['verified', 'failed']
    face_confidence: Optional[float] = None
    otp_verified: bool = False

    class Config:
        from_attributes = True


class Anomaly(BaseModel):
    """Anomaly domain model."""
    id: int
    student_id: Optional[int] = None
    session_id: Optional[int] = None
    reason: str
    anomaly_type: Literal['verification_failed', 'identity_mismatch', 'proxy_attempt', 'session_locked']
    face_confidence: Optional[float] = None
    timestamp: datetime
    reviewed: bool = False
    reviewed_by: Optional[int] = None
    reviewed_at: Optional[datetime] = None

    class Config:
        from_attributes = True


class OTPResendTracking(BaseModel):
    """OTP resend tracking domain model."""
    id: int
    session_id: int
    student_id: int
    resend_count: int = 0
    last_resend_at: Optional[datetime] = None

    class Config:
        from_attributes = True


class VerificationSession(BaseModel):
    """Verification session for tracking strikes."""
    id: str
    student_id: int
    failure_count: int = 0
    locked: bool = False
    locked_at: Optional[datetime] = None
    unlocked_by: Optional[int] = None
    unlocked_at: Optional[datetime] = None
    created_at: datetime

    class Config:
        from_attributes = True


# ============== Service Result Models ==============

class FaceVerificationResult(BaseModel):
    """Result of face verification."""
    verified: bool
    confidence: float
    student_id: Optional[int] = None
    liveness_passed: bool
    message: str


class IDVerificationResult(BaseModel):
    """Result of ID verification."""
    verified: bool
    student_id: Optional[int] = None
    is_proxy_attempt: bool = False
    message: str


class LivenessResult(BaseModel):
    """Result of liveness detection."""
    is_live: bool
    blink_detected: bool
    confidence: float
    message: str


class QualityResult(BaseModel):
    """Result of image quality analysis."""
    acceptable: bool
    contrast: float
    brightness: float
    issues: List[str]
    suggestions: List[str]


class StudentMatch(BaseModel):
    """Result of student matching."""
    student_id: int
    student_name: str
    student_id_card_number: str
    similarity: float
