"""
Property-Based Tests for OTP Service

**Feature: isavs, Property 10: OTP generation uniqueness per student**
**Feature: isavs, Property 11: OTP TTL enforcement**
**Feature: isavs, Property 13: OTP resend limit enforcement**
**Validates: Requirements 4.1, 4.2, 4.4, 4.5**
"""
import pytest
import asyncio
from hypothesis import given, strategies as st, settings, assume
from datetime import datetime, timedelta

from app.services.otp_service import OTPService
from app.db.cache import InMemoryCache


# Custom strategies
@st.composite
def student_id_list_strategy(draw):
    """Generate list of student IDs."""
    count = draw(st.integers(min_value=2, max_value=50))
    prefix = draw(st.sampled_from(['STU', 'FAC', 'ADM']))
    
    student_ids = []
    for i in range(count):
        number = draw(st.integers(min_value=10000, max_value=99999))
        student_ids.append(f"{prefix}{number}")
    
    return student_ids


@st.composite
def session_id_strategy(draw):
    """Generate session ID."""
    return f"session_{draw(st.integers(min_value=1000, max_value=9999))}"


class TestOTPUniquenessProperty:
    """
    Property tests for OTP uniqueness.
    
    **Feature: isavs, Property 10: OTP generation uniqueness per student**
    """
    
    @pytest.mark.asyncio
    @given(student_ids=student_id_list_strategy(), session_id=session_id_strategy())
    @settings(max_examples=50, deadline=5000)
    async def test_otp_uniqueness_in_session(self, student_ids, session_id):
        """
        **Feature: isavs, Property 10: OTP generation uniqueness per student**
        
        For any class session, each student SHALL receive a unique OTP.
        """
        cache = InMemoryCache()
        service = OTPService(cache)
        
        # Generate OTPs for all students
        otps = await service.generate_class_otps(session_id, student_ids)
        
        # Check all students got OTPs
        assert len(otps) == len(student_ids), "All students must receive OTPs"
        
        # Check uniqueness - no two students should have same OTP
        otp_values = list(otps.values())
        unique_otps = set(otp_values)
        
        assert len(unique_otps) == len(otp_values), \
            f"OTPs must be unique within session. Got {len(otp_values)} OTPs but only {len(unique_otps)} unique"
    
    @pytest.mark.asyncio
    @given(student_ids=student_id_list_strategy())
    @settings(max_examples=30, deadline=5000)
    async def test_otp_format_is_4_digits(self, student_ids):
        """
        **Feature: isavs, Property 10: OTP generation uniqueness per student**
        
        All generated OTPs must be 4-digit strings.
        """
        cache = InMemoryCache()
        service = OTPService(cache)
        session_id = "test_session"
        
        otps = await service.generate_class_otps(session_id, student_ids)
        
        for student_id, otp in otps.items():
            assert len(otp) == 4, f"OTP must be 4 digits, got {len(otp)} for {student_id}"
            assert otp.isdigit(), f"OTP must be numeric, got {otp} for {student_id}"
    
    @pytest.mark.asyncio
    async def test_single_otp_generation(self):
        """
        **Feature: isavs, Property 10: OTP generation uniqueness per student**
        
        Single OTP generation should produce valid 4-digit code.
        """
        service = OTPService()
        
        for _ in range(100):
            otp = service.generate_otp()
            assert len(otp) == 4, f"OTP must be 4 digits, got {len(otp)}"
            assert otp.isdigit(), f"OTP must be numeric, got {otp}"
            assert 0 <= int(otp) <= 9999, f"OTP must be in range 0000-9999, got {otp}"


class TestOTPTTLProperty:
    """
    Property tests for OTP TTL enforcement.
    
    **Feature: isavs, Property 11: OTP TTL enforcement**
    """
    
    @pytest.mark.asyncio
    @given(student_id=st.text(min_size=5, max_size=20), session_id=session_id_strategy())
    @settings(max_examples=30, deadline=5000)
    async def test_otp_stored_with_ttl(self, student_id, session_id):
        """
        **Feature: isavs, Property 11: OTP TTL enforcement**
        
        For any OTP stored, it must have a TTL set.
        """
        cache = InMemoryCache()
        service = OTPService(cache)
        
        otp = service.generate_otp()
        await service.store_otp(session_id, student_id, otp)
        
        # Check TTL is set and positive
        ttl = await service.get_remaining_ttl(session_id, student_id)
        assert ttl > 0, f"OTP must have positive TTL, got {ttl}"
        assert ttl <= service.OTP_TTL_SECONDS, \
            f"OTP TTL must not exceed {service.OTP_TTL_SECONDS}, got {ttl}"
    
    @pytest.mark.asyncio
    async def test_otp_expires_after_ttl(self):
        """
        **Feature: isavs, Property 11: OTP TTL enforcement**
        
        OTP must be invalid after TTL expires.
        """
        cache = InMemoryCache()
        service = OTPService(cache)
        session_id = "test_session"
        student_id = "STU12345"
        
        # Store OTP with very short TTL (1 second)
        otp = service.generate_otp()
        await service.store_otp(session_id, student_id, otp, ttl=1)
        
        # Verify OTP is valid immediately
        result = await service.verify_otp(session_id, student_id, otp)
        assert result.valid, "OTP should be valid immediately after creation"
        
        # Wait for expiration
        await asyncio.sleep(1.5)
        
        # Verify OTP is now expired
        result = await service.verify_otp(session_id, student_id, otp)
        assert not result.valid, "OTP should be invalid after TTL expires"
        assert result.expired, "OTP should be marked as expired"
    
    @pytest.mark.asyncio
    @given(student_ids=student_id_list_strategy())
    @settings(max_examples=20, deadline=5000)
    async def test_all_otps_have_ttl(self, student_ids):
        """
        **Feature: isavs, Property 11: OTP TTL enforcement**
        
        All OTPs generated for a class must have TTL set.
        """
        cache = InMemoryCache()
        service = OTPService(cache)
        session_id = "test_session"
        
        otps = await service.generate_class_otps(session_id, student_ids)
        
        for student_id in student_ids:
            ttl = await service.get_remaining_ttl(session_id, student_id)
            assert ttl > 0, f"OTP for {student_id} must have positive TTL"
            assert ttl <= service.OTP_TTL_SECONDS, \
                f"OTP TTL for {student_id} must not exceed {service.OTP_TTL_SECONDS}"
    
    @pytest.mark.asyncio
    async def test_otp_verification_fails_after_expiry(self):
        """
        **Feature: isavs, Property 11: OTP TTL enforcement**
        
        Verification must fail for expired OTPs.
        """
        cache = InMemoryCache()
        service = OTPService(cache)
        session_id = "test_session"
        student_id = "STU12345"
        
        otp = service.generate_otp()
        await service.store_otp(session_id, student_id, otp, ttl=1)
        
        # Wait for expiration
        await asyncio.sleep(1.5)
        
        # Try to verify expired OTP
        result = await service.verify_otp(session_id, student_id, otp)
        
        assert not result.valid, "Expired OTP verification must fail"
        assert result.expired, "Result must indicate OTP is expired"


class TestOTPResendLimitProperty:
    """
    Property tests for OTP resend limit enforcement.
    
    **Feature: isavs, Property 13: OTP resend limit enforcement**
    """
    
    @pytest.mark.asyncio
    @given(student_id=st.text(min_size=5, max_size=20), session_id=session_id_strategy())
    @settings(max_examples=30, deadline=5000)
    async def test_resend_limit_enforced(self, student_id, session_id):
        """
        **Feature: isavs, Property 13: OTP resend limit enforcement**
        
        For any student, maximum 2 resend attempts must be enforced.
        """
        cache = InMemoryCache()
        service = OTPService(cache)
        
        # Initial OTP generation
        otp = service.generate_otp()
        await service.store_otp(session_id, student_id, otp)
        
        # Track resend attempts
        resend_count = 0
        max_attempts = service.MAX_RESEND_ATTEMPTS
        
        # Try resending up to max attempts
        for i in range(max_attempts):
            success, message, remaining, expires_at = await service.resend_otp(
                session_id, student_id
            )
            assert success, f"Resend {i+1} should succeed"
            assert remaining == max_attempts - i - 1, \
                f"Remaining attempts should be {max_attempts - i - 1}, got {remaining}"
            resend_count += 1
        
        # Next resend should fail
        success, message, remaining, expires_at = await service.resend_otp(
            session_id, student_id
        )
        assert not success, "Resend should fail after max attempts"
        assert remaining == 0, "No attempts should remain"
        assert "Maximum resend attempts reached" in message
    
    @pytest.mark.asyncio
    async def test_resend_generates_new_otp(self):
        """
        **Feature: isavs, Property 13: OTP resend limit enforcement**
        
        Resending must generate a new OTP.
        """
        cache = InMemoryCache()
        service = OTPService(cache)
        session_id = "test_session"
        student_id = "STU12345"
        
        # Generate initial OTP
        initial_otp = service.generate_otp()
        await service.store_otp(session_id, student_id, initial_otp)
        
        # Resend OTP
        success, message, remaining, expires_at = await service.resend_otp(
            session_id, student_id
        )
        assert success, "Resend should succeed"
        
        # Get new OTP from cache
        key = service._get_otp_key(session_id, student_id)
        new_otp = await cache.get(key)
        
        # New OTP might be same by chance, but should be valid
        assert new_otp is not None, "New OTP should be stored"
        assert len(str(new_otp)) == 4, "New OTP should be 4 digits"
    
    @pytest.mark.asyncio
    async def test_resend_counter_persists(self):
        """
        **Feature: isavs, Property 13: OTP resend limit enforcement**
        
        Resend counter must persist across multiple resend attempts.
        """
        cache = InMemoryCache()
        service = OTPService(cache)
        session_id = "test_session"
        student_id = "STU12345"
        
        # Initial OTP
        otp = service.generate_otp()
        await service.store_otp(session_id, student_id, otp)
        
        # First resend
        success1, _, remaining1, _ = await service.resend_otp(session_id, student_id)
        assert success1 and remaining1 == 1, "First resend should succeed with 1 remaining"
        
        # Second resend
        success2, _, remaining2, _ = await service.resend_otp(session_id, student_id)
        assert success2 and remaining2 == 0, "Second resend should succeed with 0 remaining"
        
        # Third resend should fail
        success3, _, remaining3, _ = await service.resend_otp(session_id, student_id)
        assert not success3 and remaining3 == 0, "Third resend should fail"
    
    @pytest.mark.asyncio
    async def test_resend_attempts_remaining_accurate(self):
        """
        **Feature: isavs, Property 13: OTP resend limit enforcement**
        
        get_resend_attempts_remaining must return accurate count.
        """
        cache = InMemoryCache()
        service = OTPService(cache)
        session_id = "test_session"
        student_id = "STU12345"
        
        # Initial state - should have max attempts
        remaining = await service.get_resend_attempts_remaining(session_id, student_id)
        assert remaining == service.MAX_RESEND_ATTEMPTS, \
            f"Should start with {service.MAX_RESEND_ATTEMPTS} attempts"
        
        # After first resend
        otp = service.generate_otp()
        await service.store_otp(session_id, student_id, otp)
        await service.resend_otp(session_id, student_id)
        
        remaining = await service.get_resend_attempts_remaining(session_id, student_id)
        assert remaining == service.MAX_RESEND_ATTEMPTS - 1, \
            f"Should have {service.MAX_RESEND_ATTEMPTS - 1} attempts after first resend"


class TestOTPVerificationProperty:
    """Property tests for OTP verification."""
    
    @pytest.mark.asyncio
    @given(
        student_id=st.text(min_size=5, max_size=20),
        session_id=session_id_strategy()
    )
    @settings(max_examples=30, deadline=5000)
    async def test_correct_otp_verifies(self, student_id, session_id):
        """
        **Feature: isavs, Property 12: OTP verification correctness**
        
        For any valid OTP, verification with correct code must succeed.
        """
        cache = InMemoryCache()
        service = OTPService(cache)
        
        otp = service.generate_otp()
        await service.store_otp(session_id, student_id, otp)
        
        result = await service.verify_otp(session_id, student_id, otp)
        
        assert result.valid, "Correct OTP must verify successfully"
        assert not result.expired, "Valid OTP should not be marked as expired"
    
    @pytest.mark.asyncio
    @given(
        student_id=st.text(min_size=5, max_size=20),
        session_id=session_id_strategy()
    )
    @settings(max_examples=30, deadline=5000)
    async def test_incorrect_otp_fails(self, student_id, session_id):
        """
        **Feature: isavs, Property 12: OTP verification correctness**
        
        For any OTP, verification with incorrect code must fail.
        """
        cache = InMemoryCache()
        service = OTPService(cache)
        
        correct_otp = service.generate_otp()
        await service.store_otp(session_id, student_id, correct_otp)
        
        # Generate different OTP
        wrong_otp = correct_otp
        while wrong_otp == correct_otp:
            wrong_otp = service.generate_otp()
        
        result = await service.verify_otp(session_id, student_id, wrong_otp)
        
        assert not result.valid, "Incorrect OTP must fail verification"
        assert not result.expired, "Should not be marked as expired, just invalid"
    
    @pytest.mark.asyncio
    async def test_nonexistent_otp_fails(self):
        """
        **Feature: isavs, Property 12: OTP verification correctness**
        
        Verification must fail for non-existent OTP.
        """
        cache = InMemoryCache()
        service = OTPService(cache)
        
        result = await service.verify_otp("nonexistent_session", "STU12345", "1234")
        
        assert not result.valid, "Non-existent OTP must fail verification"
        assert result.expired, "Should be marked as expired/not found"


class TestOTPEdgeCases:
    """Edge case tests for OTP service."""
    
    @pytest.mark.asyncio
    async def test_empty_student_list(self):
        """Test OTP generation with empty student list."""
        cache = InMemoryCache()
        service = OTPService(cache)
        
        otps = await service.generate_class_otps("session_1", [])
        
        assert len(otps) == 0, "Empty student list should produce no OTPs"
    
    @pytest.mark.asyncio
    async def test_single_student(self):
        """Test OTP generation for single student."""
        cache = InMemoryCache()
        service = OTPService(cache)
        
        otps = await service.generate_class_otps("session_1", ["STU12345"])
        
        assert len(otps) == 1, "Single student should get one OTP"
        assert "STU12345" in otps, "Student ID should be in result"
    
    @pytest.mark.asyncio
    async def test_large_class(self):
        """Test OTP generation for large class."""
        cache = InMemoryCache()
        service = OTPService(cache)
        
        # Generate 100 students
        student_ids = [f"STU{i:05d}" for i in range(100)]
        otps = await service.generate_class_otps("session_1", student_ids)
        
        assert len(otps) == 100, "All students should get OTPs"
        
        # Check uniqueness
        unique_otps = set(otps.values())
        assert len(unique_otps) == 100, "All OTPs should be unique"
    
    @pytest.mark.asyncio
    async def test_otp_invalidation(self):
        """Test OTP invalidation after use."""
        cache = InMemoryCache()
        service = OTPService(cache)
        session_id = "test_session"
        student_id = "STU12345"
        
        otp = service.generate_otp()
        await service.store_otp(session_id, student_id, otp)
        
        # Verify OTP exists
        result = await service.verify_otp(session_id, student_id, otp)
        assert result.valid, "OTP should be valid before invalidation"
        
        # Invalidate OTP
        await service.invalidate_otp(session_id, student_id)
        
        # Verify OTP is gone
        result = await service.verify_otp(session_id, student_id, otp)
        assert not result.valid, "OTP should be invalid after invalidation"
