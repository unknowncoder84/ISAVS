"""
OTP Service
Handles generation, storage, and verification of one-time passwords.
"""
import random
import string
from datetime import datetime, timedelta
from typing import Dict, List, Optional, Tuple
import asyncio

from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, update

from app.db.cache import CacheBackend, get_cache
from app.db.models import OTPResendTrackingORM, AttendanceSessionORM
from app.models.schemas import OTPVerificationResult, ResendOTPResponse
from app.core.config import settings


class OTPService:
    """Service for OTP generation and verification."""
    
    OTP_TTL_SECONDS = 60  # 60 seconds (2026 spec)
    MAX_RESEND_ATTEMPTS = 2  # 2 resend attempts
    
    def __init__(self, cache: CacheBackend = None):
        self.cache = cache or get_cache()
        self._lock = asyncio.Lock()
    
    def generate_otp(self) -> str:
        """Generate a random 4-digit OTP."""
        return ''.join(random.choices(string.digits, k=4))
    
    def _get_otp_key(self, session_id: str, student_id: str) -> str:
        """Generate cache key for OTP storage."""
        return f"otp:{session_id}:{student_id}"
    
    def _get_resend_key(self, session_id: str, student_id: str) -> str:
        """Generate cache key for resend tracking."""
        return f"otp_resend:{session_id}:{student_id}"
    
    async def generate_class_otps(
        self,
        session_id: str,
        student_ids: List[str]
    ) -> Dict[str, str]:
        """
        Generate unique 4-digit OTPs for all students in a class.
        Ensures no duplicate OTPs within the same session.
        
        Args:
            session_id: Attendance session ID
            student_ids: List of student ID card numbers
            
        Returns:
            Dictionary mapping student_id to OTP
        """
        async with self._lock:
            otps: Dict[str, str] = {}
            used_otps: set = set()
            
            for student_id in student_ids:
                # Generate unique OTP
                otp = self.generate_otp()
                attempts = 0
                while otp in used_otps and attempts < 100:
                    otp = self.generate_otp()
                    attempts += 1
                
                used_otps.add(otp)
                otps[student_id] = otp
                
                # Store in cache with TTL
                key = self._get_otp_key(session_id, student_id)
                await self.cache.set(key, otp, self.OTP_TTL_SECONDS)
                
                # Initialize resend counter
                resend_key = self._get_resend_key(session_id, student_id)
                await self.cache.set(resend_key, 0, self.OTP_TTL_SECONDS * 10)
            
            return otps
    
    async def store_otp(
        self,
        session_id: str,
        student_id: str,
        otp: str,
        ttl: int = None
    ) -> None:
        """Store OTP in cache with TTL."""
        ttl = ttl or self.OTP_TTL_SECONDS
        key = self._get_otp_key(session_id, student_id)
        await self.cache.set(key, otp, ttl)
    
    async def verify_otp(
        self,
        session_id: str,
        student_id: str,
        entered_otp: str
    ) -> OTPVerificationResult:
        """
        Verify if entered OTP matches stored OTP for student.
        
        Args:
            session_id: Attendance session ID
            student_id: Student ID card number
            entered_otp: OTP entered by student
            
        Returns:
            OTPVerificationResult with validation status
        """
        key = self._get_otp_key(session_id, student_id)
        stored_otp = await self.cache.get(key)
        
        if stored_otp is None:
            # Check if key ever existed (expired vs never created)
            return OTPVerificationResult(
                valid=False,
                expired=True,
                message="OTP has expired or was not generated"
            )
        
        if str(stored_otp) == str(entered_otp):
            return OTPVerificationResult(
                valid=True,
                expired=False,
                message="OTP verified successfully"
            )
        
        return OTPVerificationResult(
            valid=False,
            expired=False,
            message="Invalid OTP"
        )
    
    async def resend_otp(
        self,
        session_id: str,
        student_id: str,
        db: AsyncSession = None
    ) -> Tuple[bool, str, int, Optional[datetime]]:
        """
        Generate new OTP if resend attempts remain.
        
        Returns:
            Tuple of (success, message, attempts_remaining, expires_at)
        """
        resend_key = self._get_resend_key(session_id, student_id)
        
        # Get current resend count
        resend_count = await self.cache.get(resend_key)
        if resend_count is None:
            resend_count = 0
        else:
            resend_count = int(resend_count)
        
        if resend_count >= self.MAX_RESEND_ATTEMPTS:
            return (
                False,
                "Maximum resend attempts reached",
                0,
                None
            )
        
        # Generate new OTP
        new_otp = self.generate_otp()
        otp_key = self._get_otp_key(session_id, student_id)
        
        # Store new OTP
        await self.cache.set(otp_key, new_otp, self.OTP_TTL_SECONDS)
        
        # Increment resend counter
        await self.cache.set(resend_key, resend_count + 1, self.OTP_TTL_SECONDS * 10)
        
        # Update database tracking if session provided
        if db:
            await self._update_resend_tracking(db, session_id, student_id)
        
        expires_at = datetime.utcnow() + timedelta(seconds=self.OTP_TTL_SECONDS)
        attempts_remaining = self.MAX_RESEND_ATTEMPTS - resend_count - 1
        
        return (
            True,
            f"New OTP generated. {attempts_remaining} resend(s) remaining.",
            attempts_remaining,
            expires_at
        )
    
    async def _update_resend_tracking(
        self,
        db: AsyncSession,
        session_id: str,
        student_id: str
    ) -> None:
        """Update resend tracking in database."""
        # This would update the OTPResendTrackingORM table
        # Implementation depends on how session_id maps to database
        pass
    
    async def get_remaining_ttl(self, session_id: str, student_id: str) -> int:
        """Get remaining seconds until OTP expires."""
        key = self._get_otp_key(session_id, student_id)
        ttl = await self.cache.ttl(key)
        return max(0, ttl)
    
    async def invalidate_otp(self, session_id: str, student_id: str) -> None:
        """Invalidate OTP after successful verification."""
        key = self._get_otp_key(session_id, student_id)
        await self.cache.delete(key)
    
    async def get_resend_attempts_remaining(
        self,
        session_id: str,
        student_id: str
    ) -> int:
        """Get number of resend attempts remaining."""
        resend_key = self._get_resend_key(session_id, student_id)
        resend_count = await self.cache.get(resend_key)
        
        if resend_count is None:
            return self.MAX_RESEND_ATTEMPTS
        
        return max(0, self.MAX_RESEND_ATTEMPTS - int(resend_count))


# Singleton instance
_otp_service: Optional[OTPService] = None


def get_otp_service() -> OTPService:
    """Get or create OTP service instance."""
    global _otp_service
    if _otp_service is None:
        _otp_service = OTPService()
    return _otp_service
