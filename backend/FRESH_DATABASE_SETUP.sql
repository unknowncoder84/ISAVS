-- ============================================
-- ISAVS - COMPLETE FRESH DATABASE SETUP
-- ============================================
-- Run this in Supabase SQL Editor to create a fresh database
-- This will DROP all existing tables and create new ones
-- ⚠️ WARNING: This will DELETE ALL existing data!
-- ============================================

-- Enable required extensions
CREATE EXTENSION IF NOT EXISTS "uuid-ossp";

-- ============================================
-- DROP ALL EXISTING TABLES (Clean Slate)
-- ============================================
DROP TABLE IF EXISTS otp_resend_tracking CASCADE;
DROP TABLE IF EXISTS verification_sessions CASCADE;
DROP TABLE IF EXISTS anomalies CASCADE;
DROP TABLE IF EXISTS attendance CASCADE;
DROP TABLE IF EXISTS attendance_sessions CASCADE;
DROP TABLE IF EXISTS class_enrollments CASCADE;
DROP TABLE IF EXISTS classes CASCADE;
DROP TABLE IF EXISTS students CASCADE;

-- ============================================
-- CREATE TABLES
-- ============================================

-- Students table (with face image storage)
CREATE TABLE students (
    id SERIAL PRIMARY KEY,
    name VARCHAR(255) NOT NULL,
    student_id_card_number VARCHAR(50) UNIQUE NOT NULL,
    facial_embedding FLOAT8[] NOT NULL,
    face_image_base64 TEXT,  -- Store original enrollment photo
    created_at TIMESTAMPTZ DEFAULT NOW(),
    updated_at TIMESTAMPTZ DEFAULT NOW()
);

-- Classes table
CREATE TABLE classes (
    id SERIAL PRIMARY KEY,
    class_id VARCHAR(50) UNIQUE NOT NULL,
    name VARCHAR(255) NOT NULL,
    created_at TIMESTAMPTZ DEFAULT NOW()
);

-- Class enrollments (many-to-many relationship)
CREATE TABLE class_enrollments (
    id SERIAL PRIMARY KEY,
    class_id INTEGER REFERENCES classes(id) ON DELETE CASCADE,
    student_id INTEGER REFERENCES students(id) ON DELETE CASCADE,
    enrolled_at TIMESTAMPTZ DEFAULT NOW(),
    UNIQUE(class_id, student_id)
);

-- Attendance sessions
CREATE TABLE attendance_sessions (
    id SERIAL PRIMARY KEY,
    session_id VARCHAR(100) UNIQUE NOT NULL,
    class_id INTEGER REFERENCES classes(id) ON DELETE CASCADE,
    started_at TIMESTAMPTZ DEFAULT NOW(),
    expires_at TIMESTAMPTZ NOT NULL,
    status VARCHAR(20) DEFAULT 'active' CHECK (status IN ('active', 'expired', 'completed'))
);

-- Attendance records
CREATE TABLE attendance (
    id SERIAL PRIMARY KEY,
    student_id INTEGER REFERENCES students(id) ON DELETE CASCADE,
    session_id INTEGER REFERENCES attendance_sessions(id) ON DELETE CASCADE,
    timestamp TIMESTAMPTZ DEFAULT NOW(),
    verification_status VARCHAR(20) NOT NULL CHECK (verification_status IN ('verified', 'failed')),
    face_confidence FLOAT,
    otp_verified BOOLEAN DEFAULT FALSE,
    UNIQUE(student_id, session_id)  -- Prevent duplicate attendance in same session
);

-- Anomalies table (security alerts)
CREATE TABLE anomalies (
    id SERIAL PRIMARY KEY,
    student_id INTEGER REFERENCES students(id) ON DELETE SET NULL,
    session_id INTEGER REFERENCES attendance_sessions(id) ON DELETE SET NULL,
    reason VARCHAR(500) NOT NULL,
    anomaly_type VARCHAR(50) NOT NULL CHECK (anomaly_type IN (
        'verification_failed', 
        'identity_mismatch', 
        'proxy_attempt', 
        'session_locked',
        'multiple_faces',
        'no_face_detected'
    )),
    face_confidence FLOAT,
    timestamp TIMESTAMPTZ DEFAULT NOW(),
    reviewed BOOLEAN DEFAULT FALSE,
    reviewed_by INTEGER,
    reviewed_at TIMESTAMPTZ
);

-- OTP resend tracking
CREATE TABLE otp_resend_tracking (
    id SERIAL PRIMARY KEY,
    session_id INTEGER REFERENCES attendance_sessions(id) ON DELETE CASCADE,
    student_id INTEGER REFERENCES students(id) ON DELETE CASCADE,
    resend_count INTEGER DEFAULT 0,
    last_resend_at TIMESTAMPTZ,
    UNIQUE(session_id, student_id)
);

-- Verification sessions (for three-strike tracking)
CREATE TABLE verification_sessions (
    id VARCHAR(100) PRIMARY KEY,
    student_id INTEGER REFERENCES students(id) ON DELETE CASCADE,
    failure_count INTEGER DEFAULT 0,
    locked BOOLEAN DEFAULT FALSE,
    locked_at TIMESTAMPTZ,
    unlocked_by INTEGER,
    unlocked_at TIMESTAMPTZ,
    created_at TIMESTAMPTZ DEFAULT NOW()
);

-- ============================================
-- CREATE INDEXES FOR PERFORMANCE
-- ============================================
CREATE INDEX idx_students_card ON students(student_id_card_number);
CREATE INDEX idx_students_created ON students(created_at);

CREATE INDEX idx_attendance_student ON attendance(student_id);
CREATE INDEX idx_attendance_session ON attendance(session_id);
CREATE INDEX idx_attendance_timestamp ON attendance(timestamp);
CREATE INDEX idx_attendance_status ON attendance(verification_status);

CREATE INDEX idx_anomalies_student ON anomalies(student_id);
CREATE INDEX idx_anomalies_session ON anomalies(session_id);
CREATE INDEX idx_anomalies_timestamp ON anomalies(timestamp);
CREATE INDEX idx_anomalies_type ON anomalies(anomaly_type);
CREATE INDEX idx_anomalies_reviewed ON anomalies(reviewed);

CREATE INDEX idx_sessions_status ON attendance_sessions(status);
CREATE INDEX idx_sessions_expires ON attendance_sessions(expires_at);

-- ============================================
-- CREATE FUNCTIONS AND TRIGGERS
-- ============================================

-- Auto-update timestamp function
CREATE OR REPLACE FUNCTION update_updated_at()
RETURNS TRIGGER AS $$
BEGIN
    NEW.updated_at = NOW();
    RETURN NEW;
END;
$$ LANGUAGE plpgsql;

-- Trigger for students table
CREATE TRIGGER students_updated_at
    BEFORE UPDATE ON students
    FOR EACH ROW
    EXECUTE FUNCTION update_updated_at();

-- ============================================
-- INSERT SAMPLE DATA (Optional - for testing)
-- ============================================

-- Sample class
INSERT INTO classes (class_id, name) VALUES 
    ('CS101', 'Computer Science 101'),
    ('MATH201', 'Advanced Mathematics');

-- ============================================
-- ENABLE ROW LEVEL SECURITY (Optional - for production)
-- ============================================
-- Uncomment these lines if you want to enable RLS
-- ALTER TABLE students ENABLE ROW LEVEL SECURITY;
-- ALTER TABLE attendance ENABLE ROW LEVEL SECURITY;
-- ALTER TABLE anomalies ENABLE ROW LEVEL SECURITY;
-- ALTER TABLE classes ENABLE ROW LEVEL SECURITY;
-- ALTER TABLE attendance_sessions ENABLE ROW LEVEL SECURITY;

-- ============================================
-- GRANT PERMISSIONS
-- ============================================
-- Grant permissions to authenticated users (adjust as needed)
-- GRANT ALL ON ALL TABLES IN SCHEMA public TO authenticated;
-- GRANT ALL ON ALL SEQUENCES IN SCHEMA public TO authenticated;

-- ============================================
-- VERIFICATION QUERIES
-- ============================================
-- Run these to verify the setup:

-- Check all tables exist
SELECT table_name 
FROM information_schema.tables 
WHERE table_schema = 'public' 
ORDER BY table_name;

-- Check students table structure
SELECT column_name, data_type, is_nullable
FROM information_schema.columns
WHERE table_name = 'students'
ORDER BY ordinal_position;

-- ============================================
-- SETUP COMPLETE!
-- ============================================
-- Your database is now ready to use.
-- Next steps:
-- 1. Restart your backend server
-- 2. Enroll students via the enrollment page
-- 3. Start attendance sessions from the dashboard
-- ============================================
