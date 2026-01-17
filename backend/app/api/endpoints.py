"""
API Endpoints for ISAVS
Complete REST API for attendance verification system.
Uses Supabase REST API for database operations.
PRODUCTION-GRADE: Robust preprocessing, multi-shot enrollment, dynamic matching, FAISS search
"""
from datetime import datetime, timedelta
from typing import Optional, List
import uuid
import traceback
import numpy as np

from fastapi import APIRouter, HTTPException, status, Query

from app.db.supabase_client import get_supabase
from app.models.schemas import (
    EnrollRequest, EnrollResponse,
    StartSessionResponse,
    VerifyRequest, VerifyResponse,
    ResendOTPRequest, ResendOTPResponse,
    ReportResponse, AttendanceRecord, AttendanceStatistics
)
from app.services.face_recognition_service import get_face_recognition_service
from app.services.otp_service import get_otp_service
from app.services.preprocess import get_preprocessor
from app.services.enrollment_engine import get_enrollment_engine
from app.services.matcher import get_matcher
from app.services.vector_search import get_vector_search
from app.services.geofence_service import get_geofence_service
from app.services.emotion_service import get_emotion_service
from app.core.config import settings

router = APIRouter(prefix="/api/v1", tags=["ISAVS"])


# ============== Enrollment Endpoints ==============

@router.post("/enroll", response_model=EnrollResponse)
async def enroll_student(request: EnrollRequest):
    """
    PRODUCTION-GRADE ENROLLMENT (2026 Standard)
    - Modern AI: face_recognition library (128-d embeddings)
    - CLAHE preprocessing for lighting normalization
    - Quality validation
    - Deduplication check (prevents duplicate enrollments)
    - Centroid embedding support (for multi-shot enrollment)
    """
    try:
        supabase = get_supabase()
        
        # Import modern AI service
        from app.services.ai_service import get_ai_service
        ai_service = get_ai_service()
        
        # Step 1: Check for duplicate student ID
        existing = supabase.table('students').select('id').eq(
            'student_id_card_number', request.student_id_card_number
        ).execute()
        
        if existing.data and len(existing.data) > 0:
            raise HTTPException(
                status_code=status.HTTP_409_CONFLICT,
                detail="Student ID already exists"
            )
        
        # Step 2: Decode and validate image
        image = ai_service.decode_base64_image(request.face_image)
        if image is None:
            raise HTTPException(
                status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
                detail="Invalid image format"
            )
        
        # Quality check
        preprocessor = get_preprocessor()
        is_good_quality, quality_reason = preprocessor.quality_check(image)
        if not is_good_quality:
            raise HTTPException(
                status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
                detail=f"Image quality check failed: {quality_reason}"
            )
        
        # Step 3: Extract 128-dimensional embedding with CLAHE preprocessing
        embedding = ai_service.extract_128d_embedding(image)
        
        if embedding is None:
            raise HTTPException(
                status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
                detail="Face enrollment failed: No face detected"
            )
        
        # Verify embedding dimension
        if len(embedding) != 128:
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail=f"Invalid embedding dimension: {len(embedding)} (expected 128)"
            )
        
        # Step 4: Check for duplicate face (prevents fraud)
        all_students = supabase.table('students').select('id, name, facial_embedding').execute()
        
        for s in (all_students.data or []):
            if s.get('facial_embedding'):
                stored_emb = np.array(s['facial_embedding'])
                similarity = ai_service.cosine_similarity(embedding, stored_emb)
                
                # Duplicate threshold: 0.90
                if similarity >= 0.90:
                    raise HTTPException(
                        status_code=status.HTTP_409_CONFLICT,
                        detail=f"Identity already exists: {s['name']} (similarity: {similarity:.2f})"
                    )
        
        # Step 5: Store in database
        student_data = {
            'name': request.name,
            'student_id_card_number': request.student_id_card_number,
            'facial_embedding': embedding.tolist()
        }
        
        # Try to store image if column exists
        try:
            student_data['face_image_base64'] = request.face_image
            result = supabase.table('students').insert(student_data).execute()
        except Exception as img_error:
            if 'face_image_base64' in str(img_error):
                print("⚠️ face_image_base64 column not found, storing without image")
                del student_data['face_image_base64']
                result = supabase.table('students').insert(student_data).execute()
            else:
                raise
        
        if not result.data or len(result.data) == 0:
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail="Failed to create student record"
            )
        
        student_id = result.data[0]['id']
        
        # Step 6: Add to FAISS vector index for fast search (optional)
        try:
            vector_search = get_vector_search()
            vector_search.add_embedding(student_id, request.name, embedding)
            vector_search.save()
            print(f"✓ Added student {student_id} to FAISS index")
        except Exception as e:
            print(f"⚠️ Failed to add to FAISS index: {e}")
            # Don't fail enrollment if FAISS fails
        
        return EnrollResponse(
            success=True,
            student_id=student_id,
            message=f"Student enrolled successfully with 128-d embedding. Quality: {quality_reason}"
        )
            
    except HTTPException:
        raise
    except Exception as e:
        print(f"Enrollment error: {traceback.format_exc()}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Enrollment failed: {str(e)}"
        )


# ============== Session Management Endpoints ==============

@router.post("/session/start/{class_id}", response_model=StartSessionResponse)
async def start_attendance_session(class_id: str):
    """
    Start an attendance session for a class.
    """
    try:
        supabase = get_supabase()
        otp_service = get_otp_service()
        
        # Get or create class
        class_result = supabase.table('classes').select('id').eq('class_id', class_id).execute()
        
        if not class_result.data or len(class_result.data) == 0:
            # Create class if doesn't exist
            new_class = supabase.table('classes').insert({
                'class_id': class_id,
                'name': f"Class {class_id}"
            }).execute()
            class_db_id = new_class.data[0]['id']
        else:
            class_db_id = class_result.data[0]['id']
        
        # Get all students (for demo - in production, filter by class enrollment)
        students_result = supabase.table('students').select('student_id_card_number').execute()
        student_ids = [s['student_id_card_number'] for s in (students_result.data or [])]
        
        # Generate session ID
        session_id = str(uuid.uuid4())
        expires_at = datetime.utcnow() + timedelta(seconds=settings.OTP_TTL_SECONDS)
        
        # Create attendance session record
        supabase.table('attendance_sessions').insert({
            'session_id': session_id,
            'class_id': class_db_id,
            'expires_at': expires_at.isoformat(),
            'status': 'active'
        }).execute()
        
        # Generate OTPs for all students
        if student_ids:
            await otp_service.generate_class_otps(session_id, student_ids)
        
        return StartSessionResponse(
            success=True,
            session_id=session_id,
            otp_count=len(student_ids),
            expires_at=expires_at,
            message=f"Session started with {len(student_ids)} OTPs generated"
        )
        
    except Exception as e:
        print(f"Session start error: {traceback.format_exc()}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to start session: {str(e)}"
        )


@router.get("/session/{session_id}/otp/{student_id}")
async def get_student_otp(session_id: str, student_id: str):
    """
    Get OTP for a specific student. If no OTP exists, generate one.
    """
    supabase = get_supabase()
    otp_service = get_otp_service()
    
    # First check if student exists
    student_result = supabase.table('students').select('id, name, student_id_card_number').eq(
        'student_id_card_number', student_id
    ).execute()
    
    if not student_result.data or len(student_result.data) == 0:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Student not found. Please check your Student ID."
        )
    
    student = student_result.data[0]
    
    # Check if session exists
    session_result = supabase.table('attendance_sessions').select('id, status').eq(
        'session_id', session_id
    ).execute()
    
    if not session_result.data or len(session_result.data) == 0:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Session not found. Please check the Session ID."
        )
    
    # Get OTP from cache
    key = f"otp:{session_id}:{student_id}"
    otp = await otp_service.cache.get(key)
    
    # If no OTP exists, generate one for this student
    if otp is None:
        otp = otp_service.generate_otp()
        await otp_service.cache.set(key, otp, settings.OTP_TTL_SECONDS)
        # Initialize resend counter
        resend_key = f"otp_resend:{session_id}:{student_id}"
        await otp_service.cache.set(resend_key, 0, settings.OTP_TTL_SECONDS * 10)
    
    ttl = await otp_service.get_remaining_ttl(session_id, student_id)
    
    return {
        "otp": otp,
        "remaining_seconds": ttl if ttl > 0 else settings.OTP_TTL_SECONDS,
        "student_id": student_id,
        "student_name": student['name']
    }


# ============== Verification Endpoints ==============

@router.post("/verify", response_model=VerifyResponse)
async def verify_attendance(request: VerifyRequest):
    """
    PRODUCTION-GRADE VERIFICATION (2026 Standard)
    - Modern AI: face_recognition library (128-d embeddings)
    - CLAHE preprocessing for lighting normalization
    - Cosine similarity with 0.6 threshold
    - Geofencing (50-meter radius)
    - Proxy detection with account locking
    """
    try:
        supabase = get_supabase()
        otp_service = get_otp_service()
        geofence_service = get_geofence_service()
        cache = otp_service.cache
        
        # Import modern AI service
        from app.services.ai_service import get_ai_service
        ai_service = get_ai_service()
        
        # Step 1: Verify student exists
        student_result = supabase.table('students').select('*').eq(
            'student_id_card_number', request.student_id
        ).execute()
        
        if not student_result.data or len(student_result.data) == 0:
            return VerifyResponse(
                success=False,
                factors={
                    'face_verified': False,
                    'face_confidence': 0.0,
                    'liveness_passed': False,
                    'id_verified': False,
                    'otp_verified': False,
                    'geofence_verified': False
                },
                message="Student not found"
            )
        
        student = student_result.data[0]
        student_id = student['id']
        student_name = student['name']
        
        # Step 1.5: Check if student is approved
        approval_status = student.get('approval_status', 'approved')  # Default to approved for existing students
        if approval_status != 'approved':
            if approval_status == 'rejected':
                rejection_reason = student.get('rejection_reason', 'No reason provided')
                return VerifyResponse(
                    success=False,
                    factors={
                        'face_verified': False,
                        'face_confidence': 0.0,
                        'liveness_passed': False,
                        'id_verified': False,
                        'otp_verified': False,
                        'geofence_verified': False
                    },
                    message=f"Registration rejected: {rejection_reason}"
                )
            else:  # pending
                return VerifyResponse(
                    success=False,
                    factors={
                        'face_verified': False,
                        'face_confidence': 0.0,
                        'liveness_passed': False,
                        'id_verified': False,
                        'otp_verified': False,
                        'geofence_verified': False
                    },
                    message="Registration pending admin approval. Please wait for approval before verifying attendance."
                )
        
        # Step 2: Check if account is locked
        lock_key = f"account_locked:{request.student_id}"
        is_locked = await cache.get(lock_key)
        
        if is_locked:
            lock_ttl = await cache.ttl(lock_key)
            minutes_remaining = max(1, lock_ttl // 60)
            return VerifyResponse(
                success=False,
                factors={
                    'face_verified': False,
                    'face_confidence': 0.0,
                    'liveness_passed': False,
                    'id_verified': False,
                    'otp_verified': False,
                    'geofence_verified': False
                },
                message=f"Account locked due to security violation. Try again in {minutes_remaining} minutes."
            )
        
        id_verified = True
        
        # Step 3: Verify OTP
        otp_result = await otp_service.verify_otp(
            request.session_id, 
            request.student_id, 
            request.otp
        )
        otp_verified = otp_result.valid
        
        # Step 4: Verify Geofence (if coordinates provided)
        geofence_verified = True
        distance_meters = None
        
        if request.latitude is not None and request.longitude is not None:
            # Get classroom coordinates from settings
            from app.core.config import settings
            
            if settings.CLASSROOM_LATITUDE and settings.CLASSROOM_LONGITUDE:
                is_within, distance = geofence_service.is_within_geofence(
                    request.latitude,
                    request.longitude,
                    settings.CLASSROOM_LATITUDE,
                    settings.CLASSROOM_LONGITUDE,
                    settings.GEOFENCE_RADIUS_METERS
                )
                geofence_verified = is_within
                distance_meters = distance
                
                if not is_within:
                    return VerifyResponse(
                        success=False,
                        factors={
                            'face_verified': False,
                            'face_confidence': 0.0,
                            'liveness_passed': False,
                            'id_verified': id_verified,
                            'otp_verified': otp_verified,
                            'geofence_verified': False,
                            'distance_meters': distance_meters
                        },
                        message=f"Location verification failed. You are {distance:.0f}m from classroom (max 50m)."
                    )
        
        # Step 5: Emotion-based Liveness Check (Smile-to-Verify)
        emotion_detected = None
        emotion_confidence = None
        liveness_passed = True  # Default to true if emotion check disabled
        
        if settings.REQUIRE_SMILE:
            emotion_service = get_emotion_service()
            
            if emotion_service.is_available():
                # Decode image for emotion check
                image = ai_service.decode_base64_image(request.face_image)
                
                if image is not None:
                    is_smiling, smile_conf, emotions = emotion_service.check_smile(image)
                    dominant_emotion, emotion_conf = emotion_service.get_dominant_emotion(emotions)
                    
                    emotion_detected = dominant_emotion
                    emotion_confidence = emotion_conf
                    liveness_passed = is_smiling
                    
                    if not is_smiling:
                        feedback = emotion_service.format_emotion_feedback(emotions)
                        return VerifyResponse(
                            success=False,
                            factors={
                                'face_verified': False,
                                'face_confidence': 0.0,
                                'liveness_passed': False,
                                'id_verified': id_verified,
                                'otp_verified': otp_verified,
                                'geofence_verified': geofence_verified,
                                'distance_meters': distance_meters
                            },
                            message=f"Liveness check failed: {feedback}"
                        )
        
        # Step 6: Extract face embedding using modern AI (128-d)
        image = ai_service.decode_base64_image(request.face_image)
        if image is None:
            return VerifyResponse(
                success=False,
                factors={
                    'face_verified': False,
                    'face_confidence': 0.0,
                    'liveness_passed': liveness_passed,
                    'id_verified': id_verified,
                    'otp_verified': otp_verified,
                    'geofence_verified': geofence_verified,
                    'distance_meters': distance_meters
                },
                message="Invalid image format"
            )
        
        # Extract 128-dimensional embedding with CLAHE preprocessing
        current_embedding = ai_service.extract_128d_embedding(image)
        
        if current_embedding is None:
            return VerifyResponse(
                success=False,
                factors={
                    'face_verified': False,
                    'face_confidence': 0.0,
                    'liveness_passed': liveness_passed,
                    'id_verified': id_verified,
                    'otp_verified': otp_verified,
                    'geofence_verified': geofence_verified,
                    'distance_meters': distance_meters
                },
                message="Face extraction failed - no face detected"
            )
        
        # Step 7: Verify face using cosine similarity (threshold: 0.6)
        stored_embedding = np.array(student['facial_embedding'])
        
        # Verify dimensions match
        if len(stored_embedding) != 128:
            return VerifyResponse(
                success=False,
                factors={
                    'face_verified': False,
                    'face_confidence': 0.0,
                    'liveness_passed': liveness_passed,
                    'id_verified': id_verified,
                    'otp_verified': otp_verified,
                    'geofence_verified': geofence_verified,
                    'distance_meters': distance_meters
                },
                message=f"Invalid stored embedding dimension: {len(stored_embedding)}"
            )
        
        # Use cosine similarity with 0.6 threshold
        face_verified, face_confidence = ai_service.verify_face(
            current_embedding,
            stored_embedding,
            threshold=0.6
        )
        
        # Step 8: Detect proxy attempt (OTP valid but face doesn't match)
        if otp_verified and not face_verified:
            # This is a proxy attempt - someone else is trying to mark attendance
            # Lock the account for 60 minutes
            await cache.set(lock_key, "locked", 3600)  # 3600 seconds = 60 minutes
            
            # Get session ID from database
            session_result = supabase.table('attendance_sessions').select('id').eq(
                'session_id', request.session_id
            ).execute()
            session_db_id = session_result.data[0]['id'] if session_result.data else None
            
            # Log critical security anomaly
            if session_db_id:
                supabase.table('anomalies').insert({
                    'student_id': student_id,
                    'session_id': session_db_id,
                    'reason': f"PROXY ATTEMPT DETECTED: OTP verified but face mismatch (confidence: {face_confidence:.2f}). Account locked for 60 minutes.",
                    'anomaly_type': 'proxy_attempt',
                    'face_confidence': face_confidence
                }).execute()
                
                # Record failed attendance
                supabase.table('attendance').insert({
                    'student_id': student_id,
                    'session_id': session_db_id,
                    'verification_status': 'failed',
                    'face_confidence': max(0.0, face_confidence),
                    'otp_verified': otp_verified
                }).execute()
            
            return VerifyResponse(
                success=False,
                factors={
                    'face_verified': False,
                    'face_confidence': face_confidence,
                    'liveness_passed': liveness_passed,
                    'id_verified': id_verified,
                    'otp_verified': otp_verified,
                    'geofence_verified': geofence_verified,
                    'distance_meters': distance_meters
                },
                message="SECURITY ALERT: Proxy attempt detected. Account locked for 60 minutes. Contact administrator."
            )
        
        # Step 9: Determine overall success (now includes liveness)
        success = id_verified and otp_verified and face_verified and geofence_verified and liveness_passed
        
        # Step 10: Get session ID from database
        session_result = supabase.table('attendance_sessions').select('id').eq(
            'session_id', request.session_id
        ).execute()
        session_db_id = session_result.data[0]['id'] if session_result.data else None
        
        # Step 11: Record attendance with emotion data
        if session_db_id:
            # Check if attendance already exists for this student+session
            existing_attendance = supabase.table('attendance').select('id, verification_status').eq(
                'student_id', student_id
            ).eq('session_id', session_db_id).execute()
            
            if existing_attendance.data:
                # Attendance already recorded
                existing_status = existing_attendance.data[0]['verification_status']
                if existing_status == 'verified':
                    return VerifyResponse(
                        success=False,
                        factors={
                            'face_verified': face_verified,
                            'face_confidence': face_confidence,
                            'liveness_passed': liveness_passed,
                            'id_verified': id_verified,
                            'otp_verified': otp_verified,
                            'geofence_verified': geofence_verified,
                            'distance_meters': distance_meters
                        },
                        message="Attendance already recorded for this session. You cannot verify twice."
                    )
                else:
                    # Previous attempt failed, allow retry by updating the record
                    attendance_record = {
                        'verification_status': 'verified' if success else 'failed',
                        'face_confidence': max(0.0, face_confidence),
                        'otp_verified': otp_verified,
                        'timestamp': 'NOW()'
                    }
                    
                    # Add emotion data if available
                    if emotion_detected is not None:
                        attendance_record['emotion_detected'] = emotion_detected
                    if emotion_confidence is not None:
                        attendance_record['emotion_confidence'] = emotion_confidence
                    
                    supabase.table('attendance').update(attendance_record).eq(
                        'id', existing_attendance.data[0]['id']
                    ).execute()
            else:
                # First attempt - insert new record
                attendance_record = {
                    'student_id': student_id,
                    'session_id': session_db_id,
                    'verification_status': 'verified' if success else 'failed',
                    'face_confidence': max(0.0, face_confidence),
                    'otp_verified': otp_verified
                }
                
                # Add emotion data if available
                if emotion_detected is not None:
                    attendance_record['emotion_detected'] = emotion_detected
                if emotion_confidence is not None:
                    attendance_record['emotion_confidence'] = emotion_confidence
                
                supabase.table('attendance').insert(attendance_record).execute()
            
            # Log anomaly if failed (but not proxy - that's handled above)
            if not success and not (otp_verified and not face_verified):
                anomaly_type = 'verification_failed'
                
                supabase.table('anomalies').insert({
                    'student_id': student_id,
                    'session_id': session_db_id,
                    'reason': f"Face: {face_verified}, OTP: {otp_verified}, ID: {id_verified}, Geofence: {geofence_verified}, Confidence: {face_confidence:.2f}",
                    'anomaly_type': anomaly_type,
                    'face_confidence': face_confidence
                }).execute()
        
        # Build success message
        if success:
            message = f"Attendance verified successfully! Face confidence: {face_confidence:.2f}"
            if distance_meters is not None:
                message += f" | Distance: {distance_meters:.0f}m"
        else:
            reasons = []
            if not face_verified:
                reasons.append(f"Face mismatch ({face_confidence:.2f} < 0.60)")
            if not otp_verified:
                reasons.append("Invalid OTP")
            if not geofence_verified:
                reasons.append("Outside geofence")
            message = "Verification failed: " + ", ".join(reasons)
        
        return VerifyResponse(
            success=success,
            factors={
                'face_verified': face_verified,
                'face_confidence': face_confidence,
                'liveness_passed': liveness_passed,
                'id_verified': id_verified,
                'otp_verified': otp_verified,
                'geofence_verified': geofence_verified,
                'distance_meters': distance_meters
            },
            message=message
        )
        
    except Exception as e:
        print(f"Verification error: {traceback.format_exc()}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Verification failed: {str(e)}"
        )


# ============== OTP Endpoints ==============

@router.post("/otp/resend", response_model=ResendOTPResponse)
async def resend_otp(request: ResendOTPRequest):
    """
    Resend OTP for a student (max 2 resends per session).
    """
    otp_service = get_otp_service()
    
    success, message, attempts_remaining, expires_at = await otp_service.resend_otp(
        session_id=request.session_id,
        student_id=request.student_id,
        db=None  # Not using SQLAlchemy
    )
    
    if not success:
        raise HTTPException(
            status_code=status.HTTP_429_TOO_MANY_REQUESTS,
            detail=message
        )
    
    return ResendOTPResponse(
        success=success,
        attempts_remaining=attempts_remaining,
        expires_at=expires_at,
        message=message
    )


# ============== Report Endpoints ==============

@router.get("/reports", response_model=ReportResponse)
async def get_reports(
    session_id: Optional[int] = Query(None),
    date: Optional[str] = Query(None)
):
    """
    Get attendance reports with statistics.
    """
    try:
        supabase = get_supabase()
        
        # Get attendance records with student info
        query = supabase.table('attendance').select(
            '*, students(id, name, student_id_card_number)'
        ).order('timestamp', desc=True).limit(100)
        
        if session_id:
            query = query.eq('session_id', session_id)
        
        result = query.execute()
        
        records = []
        for row in (result.data or []):
            student = row.get('students', {})
            records.append(AttendanceRecord(
                id=row['id'],
                student_id=student.get('id', 0),
                student_name=student.get('name', 'Unknown'),
                student_id_card_number=student.get('student_id_card_number', ''),
                timestamp=row['timestamp'],
                verification_status=row['verification_status'],
                face_confidence=row.get('face_confidence'),
                otp_verified=row.get('otp_verified', False)
            ))
        
        # Get statistics
        total_students = len(supabase.table('students').select('id').execute().data or [])
        verified_count = len([r for r in records if r.verification_status == 'verified'])
        failed_count = len([r for r in records if r.verification_status == 'failed'])
        
        stats = AttendanceStatistics(
            total_students=total_students,
            verified_count=verified_count,
            failed_count=failed_count,
            attendance_percentage=round((verified_count / total_students * 100) if total_students > 0 else 0, 2)
        )
        
        return ReportResponse(
            attendance_records=records,
            proxy_alerts=[],
            identity_mismatch_alerts=[],
            statistics=stats
        )
        
    except Exception as e:
        print(f"Reports error: {traceback.format_exc()}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to get reports: {str(e)}"
        )


@router.get("/reports/anomalies")
async def get_anomalies(
    session_id: Optional[int] = None,
    anomaly_type: Optional[str] = None,
    unreviewed_only: bool = False,
    limit: int = Query(100, le=500)
):
    """
    Get anomaly records.
    """
    try:
        supabase = get_supabase()
        
        query = supabase.table('anomalies').select(
            '*, students(id, name)'
        ).order('timestamp', desc=True).limit(limit)
        
        if session_id:
            query = query.eq('session_id', session_id)
        if anomaly_type:
            query = query.eq('anomaly_type', anomaly_type)
        if unreviewed_only:
            query = query.eq('reviewed', False)
        
        result = query.execute()
        
        anomalies = []
        for row in (result.data or []):
            student = row.get('students', {})
            anomalies.append({
                "id": row['id'],
                "student_id": row.get('student_id'),
                "student_name": student.get('name') if student else None,
                "session_id": row.get('session_id'),
                "reason": row['reason'],
                "anomaly_type": row['anomaly_type'],
                "face_confidence": row.get('face_confidence'),
                "timestamp": row['timestamp'],
                "reviewed": row.get('reviewed', False)
            })
        
        return {"anomalies": anomalies, "count": len(anomalies)}
        
    except Exception as e:
        print(f"Anomalies error: {traceback.format_exc()}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to get anomalies: {str(e)}"
        )


# ============== Student Management Endpoints ==============

@router.get("/students")
async def list_students(
    limit: int = Query(100, le=500),
    include_images: bool = Query(False, description="Include face images in response")
):
    """
    List all enrolled students.
    Set include_images=true to get face photos (larger response).
    """
    try:
        supabase = get_supabase()
        
        # Select fields based on whether images are requested
        if include_images:
            fields = 'id, name, student_id_card_number, face_image_base64, created_at'
        else:
            fields = 'id, name, student_id_card_number, created_at'
        
        result = supabase.table('students').select(fields).order('name').limit(limit).execute()
        
        students = []
        for s in (result.data or []):
            student_data = {
                "id": s['id'],
                "name": s['name'],
                "student_id_card_number": s['student_id_card_number'],
                "created_at": s['created_at']
            }
            if include_images and 'face_image_base64' in s:
                student_data['face_image'] = s['face_image_base64']
            students.append(student_data)
        
        return {"students": students, "count": len(students)}
        
    except Exception as e:
        print(f"Students list error: {traceback.format_exc()}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to list students: {str(e)}"
        )


@router.get("/students/{student_id}")
async def get_student(
    student_id: int,
    include_image: bool = Query(False, description="Include face image in response")
):
    """
    Get student details by ID.
    Set include_image=true to get face photo.
    """
    try:
        supabase = get_supabase()
        
        # Select fields based on whether image is requested
        if include_image:
            fields = '*'
        else:
            fields = 'id, name, student_id_card_number, created_at, updated_at'
        
        result = supabase.table('students').select(fields).eq('id', student_id).execute()
        
        if not result.data or len(result.data) == 0:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Student not found"
            )
        
        student = result.data[0]
        response = {
            "id": student['id'],
            "name": student['name'],
            "student_id_card_number": student['student_id_card_number'],
            "created_at": student['created_at'],
            "updated_at": student.get('updated_at')
        }
        
        if include_image and 'face_image_base64' in student:
            response['face_image'] = student['face_image_base64']
        
        return response
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to get student: {str(e)}"
        )


@router.delete("/students/{student_id}")
async def delete_student(student_id: int):
    """
    Delete a student record.
    """
    try:
        supabase = get_supabase()
        
        # Check if exists
        existing = supabase.table('students').select('id').eq('id', student_id).execute()
        if not existing.data:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Student not found"
            )
        
        supabase.table('students').delete().eq('id', student_id).execute()
        
        return {"message": "Student deleted successfully"}
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to delete student: {str(e)}"
        )


# ============== Class Management Endpoints ==============

@router.post("/classes")
async def create_class(class_id: str, name: str):
    """
    Create a new class.
    """
    try:
        supabase = get_supabase()
        
        # Check for duplicate
        existing = supabase.table('classes').select('id').eq('class_id', class_id).execute()
        if existing.data and len(existing.data) > 0:
            raise HTTPException(
                status_code=status.HTTP_409_CONFLICT,
                detail="Class ID already exists"
            )
        
        result = supabase.table('classes').insert({
            'class_id': class_id,
            'name': name
        }).execute()
        
        if result.data:
            return {
                "id": result.data[0]['id'],
                "class_id": class_id,
                "name": name
            }
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to create class: {str(e)}"
        )


# ============== Session Lock Management ==============

@router.post("/sessions/{session_key}/unlock")
async def unlock_session(session_key: str, faculty_id: int):
    """
    Unlock a locked verification session (faculty action).
    """
    try:
        supabase = get_supabase()
        
        result = supabase.table('verification_sessions').update({
            'locked': False,
            'unlocked_by': faculty_id,
            'unlocked_at': datetime.utcnow().isoformat()
        }).eq('id', session_key).eq('locked', True).execute()
        
        if not result.data:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Session not found or not locked"
            )
        
        return {"message": "Session unlocked successfully"}
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to unlock session: {str(e)}"
        )


@router.post("/students/{student_id}/unlock")
async def unlock_student_account(student_id: str):
    """
    Unlock a student account that was locked due to proxy attempt.
    Faculty/Admin action.
    """
    try:
        otp_service = get_otp_service()
        cache = otp_service.cache
        
        lock_key = f"account_locked:{student_id}"
        
        # Check if account is locked
        is_locked = await cache.get(lock_key)
        
        if not is_locked:
            return {
                "success": False,
                "message": "Account is not locked"
            }
        
        # Unlock the account
        await cache.delete(lock_key)
        
        return {
            "success": True,
            "message": f"Account {student_id} unlocked successfully"
        }
        
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to unlock account: {str(e)}"
        )


# ============== Authentication Endpoints ==============

from app.models.auth import (
    LoginRequest, LoginResponse, RegisterRequest, RegisterResponse, 
    LogoutResponse, UserResponse
)
from app.services.auth_service import get_auth_service
from app.middleware.auth_middleware import get_current_user, require_admin, require_teacher_or_admin, require_student, require_approved_student
from fastapi import Depends

@router.post("/auth/login", response_model=LoginResponse)
async def login(request: LoginRequest):
    """
    Login with Supabase JWT token
    Verifies token and returns user info with role
    """
    try:
        auth_service = get_auth_service()
        
        # Verify token with Supabase
        token_data = await auth_service.verify_token(request.token)
        supabase_id = token_data["supabase_user_id"]
        email = token_data["email"]
        
        # Get user from database
        user = await auth_service.get_user_by_supabase_id(supabase_id)
        
        if not user:
            # Check if user exists by email (for existing users before migration)
            user = await auth_service.get_user_by_email(email)
            
            if user:
                # Update supabase_user_id for existing user
                user = await auth_service.update_user_supabase_id(user["id"], supabase_id)
            else:
                # New user - needs registration
                return LoginResponse(
                    success=False,
                    user=None,
                    message="User not registered. Please complete registration."
                )
        
        # Return user info
        user_response = UserResponse(
            id=user["id"],
            email=user["email"],
            name=user["name"],
            role=user["role"],
            created_at=user["created_at"]
        )
        
        return LoginResponse(
            success=True,
            user=user_response,
            message="Login successful"
        )
        
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail=f"Login failed: {str(e)}"
        )


@router.post("/auth/register", response_model=RegisterResponse)
async def register_student(request: RegisterRequest, current_user: dict = Depends(get_current_user)):
    """
    Register new student
    Requires valid Supabase token
    Creates student with pending approval status
    """
    try:
        supabase = get_supabase()
        auth_service = get_auth_service()
        
        # Check if user needs registration
        if not current_user.get("needs_registration"):
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="User already registered"
            )
        
        email = current_user["email"]
        supabase_id = current_user["supabase_user_id"]
        
        # Check for duplicate student ID
        existing = supabase.table('students').select('id').eq(
            'student_id_card_number', request.student_id_card_number
        ).execute()
        
        if existing.data and len(existing.data) > 0:
            raise HTTPException(
                status_code=status.HTTP_409_CONFLICT,
                detail="Student ID already exists"
            )
        
        # Extract face embedding
        from app.services.ai_service import get_ai_service
        ai_service = get_ai_service()
        
        image = ai_service.decode_base64_image(request.face_image)
        if image is None:
            raise HTTPException(
                status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
                detail="Invalid image format"
            )
        
        embedding = ai_service.extract_128d_embedding(image)
        if embedding is None:
            raise HTTPException(
                status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
                detail="Face enrollment failed: No face detected"
            )
        
        # Create user record
        user = await auth_service.create_user(
            email=email,
            name=request.name,
            role="student",
            supabase_id=supabase_id
        )
        
        # Create student record with pending status
        student_data = {
            "name": request.name,
            "student_id_card_number": request.student_id_card_number,
            "facial_embedding": embedding.tolist(),
            "face_image_base64": request.face_image,
            "user_id": user["id"],
            "approval_status": "pending"
        }
        
        student_response = supabase.table('students').insert(student_data).execute()
        
        if not student_response.data or len(student_response.data) == 0:
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail="Failed to create student record"
            )
        
        student_id = student_response.data[0]["id"]
        
        return RegisterResponse(
            success=True,
            student_id=student_id,
            message="Registration submitted. Awaiting admin approval."
        )
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Registration failed: {str(e)}"
        )


@router.get("/auth/me", response_model=UserResponse)
async def get_current_user_info(current_user: dict = Depends(get_current_user)):
    """
    Get current authenticated user info
    """
    if current_user.get("needs_registration"):
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="User not registered"
        )
    
    return UserResponse(
        id=current_user["id"],
        email=current_user["email"],
        name=current_user["name"],
        role=current_user["role"],
        created_at=current_user["created_at"]
    )


@router.post("/auth/logout", response_model=LogoutResponse)
async def logout():
    """
    Logout (client-side token clearing)
    """
    return LogoutResponse(
        success=True,
        message="Logged out successfully"
    )


# ============== Admin Endpoints ==============

from app.models.admin import (
    CreateTeacherRequest, UpdateTeacherRequest, TeacherResponse,
    ApproveStudentRequest, RejectStudentRequest, PendingStudentResponse,
    StudentApprovalResponse
)
from app.services.admin_service import get_admin_service

@router.get("/admin/teachers", response_model=List[TeacherResponse])
async def list_teachers(current_user: dict = Depends(require_admin)):
    """
    List all teachers (admin only)
    """
    try:
        admin_service = get_admin_service()
        teachers = await admin_service.list_teachers()
        
        return [TeacherResponse(**teacher) for teacher in teachers]
        
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to list teachers: {str(e)}"
        )


@router.post("/admin/teachers", response_model=TeacherResponse)
async def create_teacher(request: CreateTeacherRequest, current_user: dict = Depends(require_admin)):
    """
    Create new teacher (admin only)
    """
    try:
        admin_service = get_admin_service()
        teacher = await admin_service.create_teacher(
            email=request.email,
            name=request.name,
            department=request.department
        )
        
        return TeacherResponse(**teacher)
        
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to create teacher: {str(e)}"
        )


@router.put("/admin/teachers/{teacher_id}", response_model=TeacherResponse)
async def update_teacher(teacher_id: int, request: UpdateTeacherRequest, current_user: dict = Depends(require_admin)):
    """
    Update teacher (admin only)
    """
    try:
        admin_service = get_admin_service()
        teacher = await admin_service.update_teacher(
            teacher_id=teacher_id,
            department=request.department,
            active=request.active
        )
        
        return TeacherResponse(**teacher)
        
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to update teacher: {str(e)}"
        )


@router.get("/admin/students/pending", response_model=List[PendingStudentResponse])
async def list_pending_students(current_user: dict = Depends(require_admin)):
    """
    List pending student registrations (admin only)
    """
    try:
        admin_service = get_admin_service()
        students = await admin_service.list_pending_students()
        
        return [PendingStudentResponse(**student) for student in students]
        
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to list pending students: {str(e)}"
        )


@router.put("/admin/students/{student_id}/approve", response_model=StudentApprovalResponse)
async def approve_student(student_id: int, current_user: dict = Depends(require_admin)):
    """
    Approve student registration (admin only)
    """
    try:
        admin_service = get_admin_service()
        student = await admin_service.approve_student(
            student_id=student_id,
            admin_id=current_user["id"]
        )
        
        return StudentApprovalResponse(
            success=True,
            student_id=student_id,
            status="approved",
            message="Student approved successfully"
        )
        
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to approve student: {str(e)}"
        )


@router.put("/admin/students/{student_id}/reject", response_model=StudentApprovalResponse)
async def reject_student(student_id: int, request: RejectStudentRequest, current_user: dict = Depends(require_admin)):
    """
    Reject student registration (admin only)
    """
    try:
        admin_service = get_admin_service()
        student = await admin_service.reject_student(
            student_id=request.student_id,
            admin_id=current_user["id"],
            reason=request.reason
        )
        
        return StudentApprovalResponse(
            success=True,
            student_id=student_id,
            status="rejected",
            message="Student rejected"
        )
        
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to reject student: {str(e)}"
        )


# ============== Student Endpoints ==============

from app.models.student import (
    StudentProfileResponse, UpdateStudentProfileRequest,
    AttendanceRecordResponse, AttendanceStatsResponse
)
from app.services.student_service import get_student_service

@router.get("/student/profile", response_model=StudentProfileResponse)
async def get_student_profile(current_user: dict = Depends(require_student)):
    """
    Get own profile (student only)
    """
    try:
        student_service = get_student_service()
        student = await student_service.get_student_by_user_id(current_user["id"])
        
        if not student:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Student profile not found"
            )
        
        return StudentProfileResponse(**student)
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to get profile: {str(e)}"
        )


@router.get("/student/attendance", response_model=List[AttendanceRecordResponse])
async def get_student_attendance(
    start_date: Optional[str] = Query(None),
    end_date: Optional[str] = Query(None),
    current_user: dict = Depends(require_student)
):
    """
    Get own attendance history (student only)
    """
    try:
        student_service = get_student_service()
        student = await student_service.get_student_by_user_id(current_user["id"])
        
        if not student:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Student profile not found"
            )
        
        records = await student_service.get_attendance_history(
            student_id=student["id"],
            start_date=start_date,
            end_date=end_date
        )
        
        return [AttendanceRecordResponse(**record) for record in records]
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to get attendance: {str(e)}"
        )


@router.get("/student/attendance/stats", response_model=AttendanceStatsResponse)
async def get_student_attendance_stats(current_user: dict = Depends(require_student)):
    """
    Get own attendance statistics (student only)
    """
    try:
        student_service = get_student_service()
        student = await student_service.get_student_by_user_id(current_user["id"])
        
        if not student:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Student profile not found"
            )
        
        stats = await student_service.get_attendance_stats(student_id=student["id"])
        
        return AttendanceStatsResponse(**stats)
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to get stats: {str(e)}"
        )


@router.put("/student/profile", response_model=StudentProfileResponse)
async def update_student_profile(request: UpdateStudentProfileRequest, current_user: dict = Depends(require_student)):
    """
    Update own profile (student only, limited fields)
    """
    try:
        student_service = get_student_service()
        student = await student_service.get_student_by_user_id(current_user["id"])
        
        if not student:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Student profile not found"
            )
        
        updated_student = await student_service.update_profile(
            student_id=student["id"],
            name=request.name
        )
        
        # Get full profile
        student = await student_service.get_student_by_user_id(current_user["id"])
        
        return StudentProfileResponse(**student)
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to update profile: {str(e)}"
        )
