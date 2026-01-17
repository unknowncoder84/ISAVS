"""
Pydantic Models for API Request/Response
"""
from datetime import datetime
from typing import Optional, List, Literal
from pydantic import BaseModel, Field


# ============== Enrollment Models ==============

class EnrollRequest(BaseModel):
    """Request model for student enrollment."""
    name: str = Field(..., min_length=1, max_length=255)
    student_id_card_number: str = Field(..., min_length=1, max_length=50)
    face_image: str = Field(..., description="Base64 encoded facial image")


class EnrollResponse(BaseModel):
    """Response model for student enrollment."""
    success: bool
    student_id: Optional[int] = None
    message: str


# ============== Session Models ==============

class StartSessionRequest(BaseModel):
    """Request model for starting an attendance session."""
    class_id: str = Field(..., min_length=1, max_length=50)


class StartSessionResponse(BaseModel):
    """Response model for starting an attendance session."""
    success: bool
    session_id: str
    otp_count: int
    expires_at: datetime
    message: str


# ============== Verification Models ==============

class VerifyRequest(BaseModel):
    """Request model for multi-factor verification with sensor fusion."""
    student_id: str = Field(..., description="Student ID card number")
    otp: str = Field(..., min_length=4, max_length=4, description="4-digit OTP")
    face_image: str = Field(..., description="Base64 encoded frame")
    session_id: str = Field(..., description="Active session ID")
    
    # GPS data
    latitude: Optional[float] = Field(None, ge=-90, le=90, description="Student's GPS latitude")
    longitude: Optional[float] = Field(None, ge=-180, le=180, description="Student's GPS longitude")
    
    # BLE proximity data
    ble_rssi: Optional[float] = Field(None, description="BLE signal strength in dBm")
    ble_beacon_uuid: Optional[str] = Field(None, description="Detected beacon UUID")
    
    # Barometer data
    barometric_pressure: Optional[float] = Field(None, ge=900, le=1100, description="Barometric pressure in hPa")
    
    # Motion sensor data (for motion-image correlation)
    motion_timestamps: Optional[List[float]] = Field(None, description="Motion sensor timestamps (Unix seconds)")
    accelerometer_x: Optional[List[float]] = Field(None, description="Accelerometer X-axis (m/s²)")
    accelerometer_y: Optional[List[float]] = Field(None, description="Accelerometer Y-axis (m/s²)")
    accelerometer_z: Optional[List[float]] = Field(None, description="Accelerometer Z-axis (m/s²)")
    gyroscope_x: Optional[List[float]] = Field(None, description="Gyroscope X-axis (rad/s)")
    gyroscope_y: Optional[List[float]] = Field(None, description="Gyroscope Y-axis (rad/s)")
    gyroscope_z: Optional[List[float]] = Field(None, description="Gyroscope Z-axis (rad/s)")
    
    # Camera frame data (for motion-image correlation)
    frame_timestamps: Optional[List[float]] = Field(None, description="Frame timestamps (Unix seconds)")
    frames_base64: Optional[List[str]] = Field(None, description="Base64 encoded frames for optical flow")


class FactorResults(BaseModel):
    """Results for each verification factor (8-factor authentication)."""
    face_verified: bool
    face_confidence: float = Field(..., ge=0.0, le=1.0)
    liveness_passed: bool
    id_verified: bool
    otp_verified: bool
    geofence_verified: bool = True  # Default True for backward compatibility
    distance_meters: Optional[float] = None
    
    # Sensor fusion factors
    ble_verified: Optional[bool] = None
    ble_rssi: Optional[float] = None
    barometer_verified: Optional[bool] = None
    pressure_difference_hpa: Optional[float] = None
    motion_correlation_verified: Optional[bool] = None
    motion_correlation: Optional[float] = None


class VerifyResponse(BaseModel):
    """Response model for verification."""
    success: bool
    factors: FactorResults
    message: str
    attendance_id: Optional[int] = None


# ============== OTP Models ==============

class ResendOTPRequest(BaseModel):
    """Request model for OTP resend."""
    student_id: str
    session_id: str


class ResendOTPResponse(BaseModel):
    """Response model for OTP resend."""
    success: bool
    attempts_remaining: int
    expires_at: Optional[datetime] = None
    message: str


class OTPVerificationResult(BaseModel):
    """Result of OTP verification."""
    valid: bool
    expired: bool = False
    message: str


# ============== Report Models ==============

class AttendanceRecord(BaseModel):
    """Attendance record for reports."""
    id: int
    student_id: int
    student_name: str
    student_id_card_number: str
    timestamp: datetime
    verification_status: Literal['verified', 'failed']
    face_confidence: Optional[float] = None
    otp_verified: bool


class ProxyAlert(BaseModel):
    """Proxy attempt alert."""
    id: int
    student_id: Optional[int]
    student_name: Optional[str]
    reason: str
    timestamp: datetime


class IdentityMismatchAlert(BaseModel):
    """Identity mismatch alert (OTP correct but face < 0.6)."""
    id: int
    student_id: int
    student_name: str
    face_confidence: float
    timestamp: datetime


class AttendanceStatistics(BaseModel):
    """Attendance statistics for a class."""
    total_students: int
    verified_count: int
    failed_count: int
    attendance_percentage: float


class ReportResponse(BaseModel):
    """Response model for reports."""
    attendance_records: List[AttendanceRecord]
    proxy_alerts: List[ProxyAlert]
    identity_mismatch_alerts: List[IdentityMismatchAlert]
    statistics: AttendanceStatistics
