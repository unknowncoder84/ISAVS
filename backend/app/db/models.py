"""
SQLAlchemy ORM Models for ISAVS
"""
from datetime import datetime
from sqlalchemy import (
    Column, Integer, String, Float, Boolean, DateTime, 
    ForeignKey, ARRAY, CheckConstraint, UniqueConstraint
)
from sqlalchemy.orm import relationship, declarative_base

Base = declarative_base()


class StudentORM(Base):
    """Student ORM model."""
    __tablename__ = "students"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String(255), nullable=False)
    student_id_card_number = Column(String(50), unique=True, nullable=False, index=True)
    facial_embedding = Column(ARRAY(Float), nullable=False)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    # Relationships
    enrollments = relationship("ClassEnrollmentORM", back_populates="student")
    attendance_records = relationship("AttendanceORM", back_populates="student")
    anomalies = relationship("AnomalyORM", back_populates="student")
    verification_sessions = relationship("VerificationSessionORM", back_populates="student")
    otp_tracking = relationship("OTPResendTrackingORM", back_populates="student")


class ClassORM(Base):
    """Class ORM model."""
    __tablename__ = "classes"

    id = Column(Integer, primary_key=True, index=True)
    class_id = Column(String(50), unique=True, nullable=False)
    name = Column(String(255), nullable=False)
    created_at = Column(DateTime, default=datetime.utcnow)

    # Relationships
    enrollments = relationship("ClassEnrollmentORM", back_populates="class_")
    attendance_sessions = relationship("AttendanceSessionORM", back_populates="class_")


class ClassEnrollmentORM(Base):
    """Class enrollment ORM model."""
    __tablename__ = "class_enrollments"

    id = Column(Integer, primary_key=True, index=True)
    class_id = Column(Integer, ForeignKey("classes.id", ondelete="CASCADE"))
    student_id = Column(Integer, ForeignKey("students.id", ondelete="CASCADE"))

    __table_args__ = (
        UniqueConstraint('class_id', 'student_id', name='uq_class_student'),
    )

    # Relationships
    class_ = relationship("ClassORM", back_populates="enrollments")
    student = relationship("StudentORM", back_populates="enrollments")


class AttendanceSessionORM(Base):
    """Attendance session ORM model."""
    __tablename__ = "attendance_sessions"

    id = Column(Integer, primary_key=True, index=True)
    session_id = Column(String(100), unique=True, nullable=False)
    class_id = Column(Integer, ForeignKey("classes.id", ondelete="CASCADE"))
    started_at = Column(DateTime, default=datetime.utcnow)
    expires_at = Column(DateTime, nullable=False)
    status = Column(String(20), default='active')

    __table_args__ = (
        CheckConstraint("status IN ('active', 'expired', 'completed')", name='check_session_status'),
    )

    # Relationships
    class_ = relationship("ClassORM", back_populates="attendance_sessions")
    attendance_records = relationship("AttendanceORM", back_populates="session")
    anomalies = relationship("AnomalyORM", back_populates="session")
    otp_tracking = relationship("OTPResendTrackingORM", back_populates="session")


class AttendanceORM(Base):
    """Attendance ORM model."""
    __tablename__ = "attendance"

    id = Column(Integer, primary_key=True, index=True)
    student_id = Column(Integer, ForeignKey("students.id", ondelete="CASCADE"))
    session_id = Column(Integer, ForeignKey("attendance_sessions.id", ondelete="CASCADE"))
    timestamp = Column(DateTime, default=datetime.utcnow, index=True)
    verification_status = Column(String(20), nullable=False)
    face_confidence = Column(Float)
    otp_verified = Column(Boolean, default=False)

    __table_args__ = (
        CheckConstraint("verification_status IN ('verified', 'failed')", name='check_verification_status'),
    )

    # Relationships
    student = relationship("StudentORM", back_populates="attendance_records")
    session = relationship("AttendanceSessionORM", back_populates="attendance_records")


class AnomalyORM(Base):
    """Anomaly ORM model."""
    __tablename__ = "anomalies"

    id = Column(Integer, primary_key=True, index=True)
    student_id = Column(Integer, ForeignKey("students.id", ondelete="SET NULL"), nullable=True)
    session_id = Column(Integer, ForeignKey("attendance_sessions.id", ondelete="SET NULL"), nullable=True)
    reason = Column(String(500), nullable=False)
    anomaly_type = Column(String(50), nullable=False, index=True)
    face_confidence = Column(Float)
    timestamp = Column(DateTime, default=datetime.utcnow, index=True)
    reviewed = Column(Boolean, default=False)
    reviewed_by = Column(Integer, nullable=True)
    reviewed_at = Column(DateTime, nullable=True)

    __table_args__ = (
        CheckConstraint(
            "anomaly_type IN ('verification_failed', 'identity_mismatch', 'proxy_attempt', 'session_locked')",
            name='check_anomaly_type'
        ),
    )

    # Relationships
    student = relationship("StudentORM", back_populates="anomalies")
    session = relationship("AttendanceSessionORM", back_populates="anomalies")


class OTPResendTrackingORM(Base):
    """OTP resend tracking ORM model."""
    __tablename__ = "otp_resend_tracking"

    id = Column(Integer, primary_key=True, index=True)
    session_id = Column(Integer, ForeignKey("attendance_sessions.id", ondelete="CASCADE"))
    student_id = Column(Integer, ForeignKey("students.id", ondelete="CASCADE"))
    resend_count = Column(Integer, default=0)
    last_resend_at = Column(DateTime, nullable=True)

    __table_args__ = (
        UniqueConstraint('session_id', 'student_id', name='uq_session_student_otp'),
    )

    # Relationships
    session = relationship("AttendanceSessionORM", back_populates="otp_tracking")
    student = relationship("StudentORM", back_populates="otp_tracking")


class VerificationSessionORM(Base):
    """Verification session ORM model for tracking strikes."""
    __tablename__ = "verification_sessions"

    id = Column(String(100), primary_key=True)
    student_id = Column(Integer, ForeignKey("students.id", ondelete="CASCADE"))
    failure_count = Column(Integer, default=0)
    locked = Column(Boolean, default=False)
    locked_at = Column(DateTime, nullable=True)
    unlocked_by = Column(Integer, nullable=True)
    unlocked_at = Column(DateTime, nullable=True)
    created_at = Column(DateTime, default=datetime.utcnow)

    # Relationships
    student = relationship("StudentORM", back_populates="verification_sessions")
