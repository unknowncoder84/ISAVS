"""
Verification Pipeline Service
Orchestrates the three-factor verification process with geofencing.
"""
from typing import Optional, List
import numpy as np

from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select

from app.db.models import StudentORM, AttendanceORM, AttendanceSessionORM
from app.models.schemas import (
    VerifyRequest, VerifyResponse, FactorResults
)
from app.models.domain import (
    FaceVerificationResult, IDVerificationResult, QualityResult
)
from app.services.face_recognition_service import FaceRecognitionService, get_face_recognition_service
from app.services.liveness_service import LivenessService, get_liveness_service
from app.services.image_quality_service import ImageQualityService, get_image_quality_service
from app.services.otp_service import OTPService, get_otp_service
from app.services.anomaly_service import AnomalyService, get_anomaly_service
from app.services.geofence_service import GeofenceService, get_geofence_service
from app.core.config import settings


class VerificationPipeline:
    """
    Orchestrates the three-factor verification pipeline:
    1. Face Recognition (with liveness check)
    2. ID Validation
    3. OTP Verification
    4. Geofence Validation (50m radius)
    """
    
    FACE_SIMILARITY_THRESHOLD = settings.FACE_SIMILARITY_THRESHOLD  # 0.6
    
    def __init__(
        self,
        face_service: FaceRecognitionService = None,
        liveness_service: LivenessService = None,
        quality_service: ImageQualityService = None,
        otp_service: OTPService = None,
        anomaly_service: AnomalyService = None,
        geofence_service: GeofenceService = None
    ):
        self.face_service = face_service or get_face_recognition_service()
        self.liveness_service = liveness_service or get_liveness_service()
        self.quality_service = quality_service or get_image_quality_service()
        self.otp_service = otp_service or get_otp_service()
        self.anomaly_service = anomaly_service or get_anomaly_service()
        self.geofence_service = geofence_service or get_geofence_service()
    
    async def verify_image_quality(
        self,
        base64_image: str
    ) -> QualityResult:
        """Check image quality before processing."""
        image = self.face_service.decode_base64_image(base64_image)
        if image is None:
            return QualityResult(
                acceptable=False,
                contrast=0.0,
                brightness=0.0,
                issues=["invalid_image"],
                suggestions=["Please capture a valid image"]
            )
        
        return self.quality_service.check_quality_threshold(image)
    
    async def verify_face(
        self,
        base64_image: str,
        student_id: int,
        db: AsyncSession,
        frames_for_liveness: List[str] = None
    ) -> FaceVerificationResult:
        """
        Factor 1: Face recognition with liveness check.
        
        Args:
            base64_image: Base64 encoded face image
            student_id: Database ID of the student to verify against
            db: Database session
            frames_for_liveness: Optional list of frames for liveness detection
            
        Returns:
            FaceVerificationResult with verification status
        """
        # Check image quality first
        quality_result = await self.verify_image_quality(base64_image)
        if not quality_result.acceptable:
            return FaceVerificationResult(
                verified=False,
                confidence=0.0,
                student_id=None,
                liveness_passed=False,
                message=f"Image quality issue: {', '.join(quality_result.suggestions)}"
            )
        
        # Perform liveness check if frames provided
        liveness_passed = True
        if frames_for_liveness:
            decoded_frames = []
            for frame in frames_for_liveness:
                decoded = self.face_service.decode_base64_image(frame)
                if decoded is not None:
                    decoded_frames.append(decoded)
            
            if decoded_frames:
                liveness_result = self.liveness_service.check_liveness(decoded_frames)
                liveness_passed = liveness_result.is_live
                
                if not liveness_passed:
                    return FaceVerificationResult(
                        verified=False,
                        confidence=0.0,
                        student_id=None,
                        liveness_passed=False,
                        message=liveness_result.message
                    )
        
        # Verify face against student
        return await self.face_service.verify_student_face(
            base64_image=base64_image,
            student_id=student_id,
            db=db,
            liveness_passed=liveness_passed
        )
    
    async def verify_id(
        self,
        student_id_card_number: str,
        db: AsyncSession,
        expected_student_id: Optional[int] = None
    ) -> IDVerificationResult:
        """
        Factor 2: College ID validation.
        
        Args:
            student_id_card_number: Student's ID card number
            db: Database session
            expected_student_id: Expected student database ID (from face match)
            
        Returns:
            IDVerificationResult with validation status
        """
        # Validate ID format (basic pattern check)
        if not student_id_card_number or len(student_id_card_number) < 3:
            return IDVerificationResult(
                verified=False,
                student_id=None,
                is_proxy_attempt=False,
                message="Invalid ID format"
            )
        
        # Check if ID exists in database
        result = await db.execute(
            select(StudentORM).where(
                StudentORM.student_id_card_number == student_id_card_number
            )
        )
        student = result.scalar_one_or_none()
        
        if student is None:
            return IDVerificationResult(
                verified=False,
                student_id=None,
                is_proxy_attempt=False,
                message="Student ID not found in database"
            )
        
        # Check for proxy attempt (ID doesn't match face)
        is_proxy = False
        if expected_student_id is not None and student.id != expected_student_id:
            is_proxy = True
        
        return IDVerificationResult(
            verified=True,
            student_id=student.id,
            is_proxy_attempt=is_proxy,
            message="ID verified" if not is_proxy else "Potential proxy attempt detected"
        )
    
    async def verify_otp(
        self,
        session_id: str,
        student_id_card_number: str,
        entered_otp: str
    ) -> tuple[bool, str]:
        """
        Factor 3: OTP verification.
        
        Args:
            session_id: Attendance session ID
            student_id_card_number: Student's ID card number
            entered_otp: OTP entered by student
            
        Returns:
            Tuple of (verified, message)
        """
        result = await self.otp_service.verify_otp(
            session_id=session_id,
            student_id=student_id_card_number,
            entered_otp=entered_otp
        )
        
        return result.valid, result.message
    
    async def verify_geofence(
        self,
        student_lat: Optional[float],
        student_lon: Optional[float],
        classroom_lat: float,
        classroom_lon: float,
        radius_meters: float = 50
    ) -> tuple[bool, float, str]:
        """
        Factor 4: Geofence verification (50m radius).
        
        Args:
            student_lat: Student's GPS latitude
            student_lon: Student's GPS longitude
            classroom_lat: Classroom's latitude
            classroom_lon: Classroom's longitude
            radius_meters: Geofence radius (default 50m)
            
        Returns:
            Tuple of (verified, distance_meters, message)
        """
        # If no GPS provided, skip geofence check (backward compatibility)
        if student_lat is None or student_lon is None:
            return True, 0.0, "Geofence check skipped (no GPS data)"
        
        # Validate coordinates
        if not self.geofence_service.validate_coordinates(student_lat, student_lon):
            return False, 0.0, "Invalid GPS coordinates"
        
        if not self.geofence_service.validate_coordinates(classroom_lat, classroom_lon):
            return False, 0.0, "Invalid classroom coordinates"
        
        # Check if within geofence
        is_within, distance = self.geofence_service.is_within_geofence(
            student_lat, student_lon,
            classroom_lat, classroom_lon,
            radius_meters
        )
        
        if is_within:
            return True, distance, f"Within geofence ({distance:.1f}m from classroom)"
        else:
            return False, distance, f"Outside geofence ({distance:.1f}m from classroom, max {radius_meters}m)"
    
    async def run_full_verification(
        self,
        request: VerifyRequest,
        db: AsyncSession,
        frames_for_liveness: List[str] = None
    ) -> VerifyResponse:
        """
        Execute complete three-factor verification pipeline.
        
        Args:
            request: Verification request with all factors
            db: Database session
            frames_for_liveness: Optional frames for liveness detection
            
        Returns:
            VerifyResponse with complete verification results
        """
        # Initialize results
        face_verified = False
        face_confidence = 0.0
        liveness_passed = False
        id_verified = False
        otp_verified = False
        geofence_verified = True  # Default true for backward compatibility
        distance_meters = None
        messages = []
        
        # Get student from ID
        id_result = await self.verify_id(request.student_id, db)
        id_verified = id_result.verified
        student_db_id = id_result.student_id
        
        if not id_verified:
            messages.append(f"ID verification failed: {id_result.message}")
        
        # Get attendance session
        session_result = await db.execute(
            select(AttendanceSessionORM).where(
                AttendanceSessionORM.session_id == request.session_id
            )
        )
        attendance_session = session_result.scalar_one_or_none()
        attendance_session_id = attendance_session.id if attendance_session else None
        
        # Verify Geofence (if GPS coordinates provided)
        if request.latitude is not None and request.longitude is not None:
            # TODO: Get classroom coordinates from session/class data
            # For now, using example coordinates (replace with actual classroom location)
            classroom_lat = 28.6139  # Example: Delhi
            classroom_lon = 77.2090
            
            geofence_verified, distance_meters, geofence_message = await self.verify_geofence(
                student_lat=request.latitude,
                student_lon=request.longitude,
                classroom_lat=classroom_lat,
                classroom_lon=classroom_lon,
                radius_meters=50
            )
            
            if not geofence_verified:
                messages.append(f"Geofence verification failed: {geofence_message}")
        
        # Check if session is locked (three-strike policy)
        if student_db_id:
            session_key = f"{request.session_id}:{student_db_id}"
            is_locked = await self.anomaly_service.is_session_locked(db, session_key)
            
            if is_locked:
                return VerifyResponse(
                    success=False,
                    factors=FactorResults(
                        face_verified=False,
                        face_confidence=0.0,
                        liveness_passed=False,
                        id_verified=id_verified,
                        otp_verified=False
                    ),
                    message="Session is locked due to multiple failed attempts. Please contact faculty.",
                    attendance_id=None
                )
        
        # Verify OTP
        otp_verified, otp_message = await self.verify_otp(
            session_id=request.session_id,
            student_id_card_number=request.student_id,
            entered_otp=request.otp
        )
        
        if not otp_verified:
            messages.append(f"OTP verification failed: {otp_message}")
        
        # Verify face (only if ID verified)
        if id_verified and student_db_id:
            face_result = await self.verify_face(
                base64_image=request.face_image,
                student_id=student_db_id,
                db=db,
                frames_for_liveness=frames_for_liveness
            )
            
            face_verified = face_result.verified
            face_confidence = face_result.confidence
            liveness_passed = face_result.liveness_passed
            
            if not face_verified:
                messages.append(f"Face verification failed: {face_result.message}")
            
            # Check for identity mismatch (OTP correct but face < 0.6)
            if otp_verified and not face_verified and face_confidence < self.FACE_SIMILARITY_THRESHOLD:
                await self.anomaly_service.record_identity_mismatch(
                    db=db,
                    student_id=student_db_id,
                    session_id=attendance_session_id,
                    face_confidence=face_confidence
                )
                messages.append("Identity mismatch detected")
            
            # Check for proxy attempt
            if id_result.is_proxy_attempt:
                await self.anomaly_service.record_proxy_attempt(
                    db=db,
                    claimed_student_id=student_db_id,
                    matched_student_id=face_result.student_id,
                    session_id=attendance_session_id,
                    face_confidence=face_confidence
                )
        
        # Determine overall success (including geofence)
        all_factors_passed = face_verified and id_verified and otp_verified and liveness_passed and geofence_verified
        
        # Handle failure - increment strike count
        attendance_id = None
        if not all_factors_passed and student_db_id:
            session_key = f"{request.session_id}:{student_db_id}"
            failure_count = await self.anomaly_service.increment_failure_count(
                db, session_key, student_db_id
            )
            
            # Check for three-strike lockout
            if failure_count >= self.anomaly_service.MAX_CONSECUTIVE_FAILURES:
                await self.anomaly_service.lock_session(
                    db, session_key, student_db_id, attendance_session_id
                )
                messages.append("Session locked after 3 failed attempts")
            
            # Record general verification failure
            if not any(m.startswith("Identity mismatch") or m.startswith("Proxy") for m in messages):
                await self.anomaly_service.record_anomaly(
                    db=db,
                    student_id=student_db_id,
                    session_id=attendance_session_id,
                    reason="; ".join(messages) if messages else "Verification failed",
                    anomaly_type="verification_failed",
                    face_confidence=face_confidence
                )
        
        # Record successful attendance
        if all_factors_passed and student_db_id and attendance_session_id:
            # Reset failure count on success
            session_key = f"{request.session_id}:{student_db_id}"
            await self.anomaly_service.reset_failure_count(db, session_key)
            
            # Invalidate OTP after successful use
            await self.otp_service.invalidate_otp(request.session_id, request.student_id)
            
            # Create attendance record
            attendance = AttendanceORM(
                student_id=student_db_id,
                session_id=attendance_session_id,
                verification_status="verified",
                face_confidence=face_confidence,
                otp_verified=True
            )
            db.add(attendance)
            await db.flush()
            attendance_id = attendance.id
        
        return VerifyResponse(
            success=all_factors_passed,
            factors=FactorResults(
                face_verified=face_verified,
                face_confidence=face_confidence,
                liveness_passed=liveness_passed,
                id_verified=id_verified,
                otp_verified=otp_verified,
                geofence_verified=geofence_verified,
                distance_meters=distance_meters
            ),
            message="Verification successful" if all_factors_passed else "; ".join(messages),
            attendance_id=attendance_id
        )


# Singleton instance
_verification_pipeline: Optional[VerificationPipeline] = None


def get_verification_pipeline() -> VerificationPipeline:
    """Get or create verification pipeline instance."""
    global _verification_pipeline
    if _verification_pipeline is None:
        _verification_pipeline = VerificationPipeline()
    return _verification_pipeline
