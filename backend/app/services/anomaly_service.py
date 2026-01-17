"""
Anomaly Service
Handles anomaly detection, recording, and three-strike policy.
"""
from datetime import datetime
from typing import Optional, List

from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, update, and_

from app.db.models import AnomalyORM, VerificationSessionORM, StudentORM
from app.models.domain import Anomaly
from app.core.config import settings


class AnomalyService:
    """Service for anomaly detection and management."""
    
    MAX_CONSECUTIVE_FAILURES = settings.MAX_CONSECUTIVE_FAILURES  # 3 strikes
    
    async def record_anomaly(
        self,
        db: AsyncSession,
        student_id: Optional[int],
        session_id: Optional[int],
        reason: str,
        anomaly_type: str,
        face_confidence: Optional[float] = None
    ) -> AnomalyORM:
        """
        Record a failed verification attempt or anomaly.
        
        Args:
            db: Database session
            student_id: Student ID (if known)
            session_id: Attendance session ID
            reason: Description of the anomaly
            anomaly_type: Type of anomaly (verification_failed, identity_mismatch, proxy_attempt, session_locked)
            face_confidence: Face recognition confidence score
            
        Returns:
            Created anomaly record
        """
        anomaly = AnomalyORM(
            student_id=student_id,
            session_id=session_id,
            reason=reason,
            anomaly_type=anomaly_type,
            face_confidence=face_confidence,
            timestamp=datetime.utcnow()
        )
        
        db.add(anomaly)
        await db.flush()
        
        return anomaly
    
    async def record_identity_mismatch(
        self,
        db: AsyncSession,
        student_id: int,
        session_id: int,
        face_confidence: float
    ) -> AnomalyORM:
        """
        Record identity mismatch when OTP is correct but face similarity < 0.6.
        
        Args:
            db: Database session
            student_id: Student ID
            session_id: Attendance session ID
            face_confidence: Face recognition confidence score
            
        Returns:
            Created anomaly record
        """
        reason = f"Identity mismatch: OTP verified but face confidence ({face_confidence:.2f}) below threshold"
        
        return await self.record_anomaly(
            db=db,
            student_id=student_id,
            session_id=session_id,
            reason=reason,
            anomaly_type="identity_mismatch",
            face_confidence=face_confidence
        )
    
    async def record_proxy_attempt(
        self,
        db: AsyncSession,
        claimed_student_id: int,
        matched_student_id: Optional[int],
        session_id: int,
        face_confidence: float
    ) -> AnomalyORM:
        """
        Record proxy attempt when face matches different student than claimed ID.
        """
        reason = f"Proxy attempt: Claimed student {claimed_student_id}, face matched student {matched_student_id}"
        
        return await self.record_anomaly(
            db=db,
            student_id=claimed_student_id,
            session_id=session_id,
            reason=reason,
            anomaly_type="proxy_attempt",
            face_confidence=face_confidence
        )
    
    async def get_or_create_verification_session(
        self,
        db: AsyncSession,
        session_key: str,
        student_id: int
    ) -> VerificationSessionORM:
        """Get or create a verification session for tracking strikes."""
        result = await db.execute(
            select(VerificationSessionORM).where(
                VerificationSessionORM.id == session_key
            )
        )
        session = result.scalar_one_or_none()
        
        if session is None:
            session = VerificationSessionORM(
                id=session_key,
                student_id=student_id,
                failure_count=0,
                locked=False
            )
            db.add(session)
            await db.flush()
        
        return session
    
    async def increment_failure_count(
        self,
        db: AsyncSession,
        session_key: str,
        student_id: int
    ) -> int:
        """
        Increment failure count for a session.
        Returns new failure count.
        """
        session = await self.get_or_create_verification_session(db, session_key, student_id)
        session.failure_count += 1
        await db.flush()
        return session.failure_count
    
    async def check_strike_count(
        self,
        db: AsyncSession,
        session_key: str
    ) -> int:
        """Get current failure count for session."""
        result = await db.execute(
            select(VerificationSessionORM).where(
                VerificationSessionORM.id == session_key
            )
        )
        session = result.scalar_one_or_none()
        
        if session is None:
            return 0
        
        return session.failure_count
    
    async def lock_session(
        self,
        db: AsyncSession,
        session_key: str,
        student_id: int,
        attendance_session_id: int
    ) -> None:
        """Lock session after three strikes."""
        result = await db.execute(
            select(VerificationSessionORM).where(
                VerificationSessionORM.id == session_key
            )
        )
        session = result.scalar_one_or_none()
        
        if session:
            session.locked = True
            session.locked_at = datetime.utcnow()
            
            # Record anomaly for session lock
            await self.record_anomaly(
                db=db,
                student_id=student_id,
                session_id=attendance_session_id,
                reason="Session locked due to three consecutive failed verification attempts",
                anomaly_type="session_locked"
            )
            
            await db.flush()
    
    async def is_session_locked(
        self,
        db: AsyncSession,
        session_key: str
    ) -> bool:
        """Check if session is locked."""
        result = await db.execute(
            select(VerificationSessionORM).where(
                VerificationSessionORM.id == session_key
            )
        )
        session = result.scalar_one_or_none()
        
        if session is None:
            return False
        
        return session.locked
    
    async def unlock_session(
        self,
        db: AsyncSession,
        session_key: str,
        faculty_id: int
    ) -> bool:
        """
        Faculty unlock of locked session.
        Returns True if successfully unlocked.
        """
        result = await db.execute(
            select(VerificationSessionORM).where(
                VerificationSessionORM.id == session_key
            )
        )
        session = result.scalar_one_or_none()
        
        if session is None or not session.locked:
            return False
        
        session.locked = False
        session.unlocked_by = faculty_id
        session.unlocked_at = datetime.utcnow()
        session.failure_count = 0  # Reset failure count
        
        await db.flush()
        return True
    
    async def reset_failure_count(
        self,
        db: AsyncSession,
        session_key: str
    ) -> None:
        """Reset failure count after successful verification."""
        result = await db.execute(
            select(VerificationSessionORM).where(
                VerificationSessionORM.id == session_key
            )
        )
        session = result.scalar_one_or_none()
        
        if session:
            session.failure_count = 0
            await db.flush()
    
    async def get_anomalies_by_student(
        self,
        db: AsyncSession,
        student_id: int,
        limit: int = 50
    ) -> List[AnomalyORM]:
        """Get anomalies for a specific student."""
        result = await db.execute(
            select(AnomalyORM)
            .where(AnomalyORM.student_id == student_id)
            .order_by(AnomalyORM.timestamp.desc())
            .limit(limit)
        )
        return list(result.scalars().all())
    
    async def get_anomalies_by_session(
        self,
        db: AsyncSession,
        session_id: int
    ) -> List[AnomalyORM]:
        """Get all anomalies for an attendance session."""
        result = await db.execute(
            select(AnomalyORM)
            .where(AnomalyORM.session_id == session_id)
            .order_by(AnomalyORM.timestamp.desc())
        )
        return list(result.scalars().all())
    
    async def get_unreviewed_anomalies(
        self,
        db: AsyncSession,
        limit: int = 100
    ) -> List[AnomalyORM]:
        """Get all unreviewed anomalies."""
        result = await db.execute(
            select(AnomalyORM)
            .where(AnomalyORM.reviewed == False)
            .order_by(AnomalyORM.timestamp.desc())
            .limit(limit)
        )
        return list(result.scalars().all())
    
    async def mark_anomaly_reviewed(
        self,
        db: AsyncSession,
        anomaly_id: int,
        reviewed_by: int
    ) -> bool:
        """Mark an anomaly as reviewed."""
        result = await db.execute(
            select(AnomalyORM).where(AnomalyORM.id == anomaly_id)
        )
        anomaly = result.scalar_one_or_none()
        
        if anomaly is None:
            return False
        
        anomaly.reviewed = True
        anomaly.reviewed_by = reviewed_by
        anomaly.reviewed_at = datetime.utcnow()
        
        await db.flush()
        return True


# Singleton instance
_anomaly_service: Optional[AnomalyService] = None


def get_anomaly_service() -> AnomalyService:
    """Get or create anomaly service instance."""
    global _anomaly_service
    if _anomaly_service is None:
        _anomaly_service = AnomalyService()
    return _anomaly_service
