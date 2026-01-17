-- ISAVS Database Schema for Supabase
-- Run this in Supabase SQL Editor: Dashboard > SQL Editor > New Query

-- Enable required extensions
CREATE EXTENSION IF NOT EXISTS "uuid-ossp";

-- Students table
CREATE TABLE IF NOT EXISTS students (
    id SERIAL PRIMARY KEY,
    name VARCHAR(255) NOT NULL,
    student_id_card_number VARCHAR(50) UNIQUE NOT NULL,
    facial_embedding FLOAT8[] NOT NULL,
    face_image_base64 TEXT,
    created_at TIMESTAMPTZ DEFAULT NOW(),
    updated_at TIMESTAMPTZ DEFAULT NOW()
);

-- Classes table
CREATE TABLE IF NOT EXISTS classes (
    id SERIAL PRIMARY KEY,
    class_id VARCHAR(50) UNIQUE NOT NULL,
    name VARCHAR(255) NOT NULL,
    created_at TIMESTAMPTZ DEFAULT NOW()
);

-- Class enrollments
CREATE TABLE IF NOT EXISTS class_enrollments (
    id SERIAL PRIMARY KEY,
    class_id INTEGER REFERENCES classes(id) ON DELETE CASCADE,
    student_id INTEGER REFERENCES students(id) ON DELETE CASCADE,
    enrolled_at TIMESTAMPTZ DEFAULT NOW(),
    UNIQUE(class_id, student_id)
);

-- Attendance sessions
CREATE TABLE IF NOT EXISTS attendance_sessions (
    id SERIAL PRIMARY KEY,
    session_id VARCHAR(100) UNIQUE NOT NULL,
    class_id INTEGER REFERENCES classes(id) ON DELETE CASCADE,
    started_at TIMESTAMPTZ DEFAULT NOW(),
    expires_at TIMESTAMPTZ NOT NULL,
    status VARCHAR(20) DEFAULT 'active' CHECK (status IN ('active', 'expired', 'completed'))
);

-- Attendance records
CREATE TABLE IF NOT EXISTS attendance (
    id SERIAL PRIMARY KEY,
    student_id INTEGER REFERENCES students(id) ON DELETE CASCADE,
    session_id INTEGER REFERENCES attendance_sessions(id) ON DELETE CASCADE,
    timestamp TIMESTAMPTZ DEFAULT NOW(),
    verification_status VARCHAR(20) NOT NULL CHECK (verification_status IN ('verified', 'failed')),
    face_confidence FLOAT,
    otp_verified BOOLEAN DEFAULT FALSE,
    UNIQUE(student_id, session_id)
);

-- Anomalies table
CREATE TABLE IF NOT EXISTS anomalies (
    id SERIAL PRIMARY KEY,
    student_id INTEGER REFERENCES students(id) ON DELETE SET NULL,
    session_id INTEGER REFERENCES attendance_sessions(id) ON DELETE SET NULL,
    reason VARCHAR(500) NOT NULL,
    anomaly_type VARCHAR(50) NOT NULL CHECK (anomaly_type IN ('verification_failed', 'identity_mismatch', 'proxy_attempt', 'session_locked', 'multiple_faces', 'no_face_detected')),
    face_confidence FLOAT,
    timestamp TIMESTAMPTZ DEFAULT NOW(),
    reviewed BOOLEAN DEFAULT FALSE,
    reviewed_by INTEGER,
    reviewed_at TIMESTAMPTZ
);

-- OTP resend tracking
CREATE TABLE IF NOT EXISTS otp_resend_tracking (
    id SERIAL PRIMARY KEY,
    session_id INTEGER REFERENCES attendance_sessions(id) ON DELETE CASCADE,
    student_id INTEGER REFERENCES students(id) ON DELETE CASCADE,
    resend_count INTEGER DEFAULT 0,
    last_resend_at TIMESTAMPTZ,
    UNIQUE(session_id, student_id)
);

-- Verification sessions
CREATE TABLE IF NOT EXISTS verification_sessions (
    id VARCHAR(100) PRIMARY KEY,
    student_id INTEGER REFERENCES students(id) ON DELETE CASCADE,
    failure_count INTEGER DEFAULT 0,
    locked BOOLEAN DEFAULT FALSE,
    locked_at TIMESTAMPTZ,
    unlocked_by INTEGER,
    unlocked_at TIMESTAMPTZ,
    created_at TIMESTAMPTZ DEFAULT NOW()
);

-- Performance indexes
CREATE INDEX IF NOT EXISTS idx_attendance_student ON attendance(student_id);
CREATE INDEX IF NOT EXISTS idx_attendance_session ON attendance(session_id);
CREATE INDEX IF NOT EXISTS idx_attendance_timestamp ON attendance(timestamp);
CREATE INDEX IF NOT EXISTS idx_anomalies_student ON anomalies(student_id);
CREATE INDEX IF NOT EXISTS idx_anomalies_timestamp ON anomalies(timestamp);
CREATE INDEX IF NOT EXISTS idx_anomalies_type ON anomalies(anomaly_type);
CREATE INDEX IF NOT EXISTS idx_students_card ON students(student_id_card_number);

-- Auto-update timestamp function
CREATE OR REPLACE FUNCTION update_updated_at()
RETURNS TRIGGER AS $$
BEGIN
    NEW.updated_at = NOW();
    RETURN NEW;
END;
$$ LANGUAGE plpgsql;

-- Trigger for students table
DROP TRIGGER IF EXISTS students_updated_at ON students;
CREATE TRIGGER students_updated_at
    BEFORE UPDATE ON students
    FOR EACH ROW
    EXECUTE FUNCTION update_updated_at();
