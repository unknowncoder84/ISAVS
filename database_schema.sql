-- ============================================
-- ISAVS 2026 - Complete Database Schema
-- Intelligent Student Attendance Verification System
-- Dual Portal Architecture (Teacher Port 2001, Student Port 2002)
-- ============================================

-- Enable UUID extension
CREATE EXTENSION IF NOT EXISTS "uuid-ossp";

-- ============================================
-- 1. USERS TABLE (Authentication)
-- ============================================
CREATE TABLE IF NOT EXISTS users (
    id SERIAL PRIMARY KEY,
    email VARCHAR(255) UNIQUE NOT NULL,
    name VARCHAR(255) NOT NULL,
    role VARCHAR(20) NOT NULL CHECK (role IN ('admin', 'teacher', 'student')),
    supabase_user_id UUID UNIQUE,
    created_at TIMESTAMP DEFAULT NOW(),
    updated_at TIMESTAMP DEFAULT NOW()
);

CREATE INDEX idx_users_email ON users(email);
CREATE INDEX idx_users_supabase_id ON users(supabase_user_id);
CREATE INDEX idx_users_role ON users(role);

-- ============================================
-- 2. CLASSES TABLE
-- ============================================
CREATE TABLE IF NOT EXISTS classes (
    id SERIAL PRIMARY KEY,
    class_id VARCHAR(50) UNIQUE NOT NULL,
    name VARCHAR(255) NOT NULL,
    teacher_id INTEGER REFERENCES users(id) ON DELETE SET NULL,
    created_at TIMESTAMP DEFAULT NOW(),
    updated_at TIMESTAMP DEFAULT NOW()
);

CREATE INDEX idx_classes_class_id ON classes(class_id);
CREATE INDEX idx_classes_teacher_id ON classes(teacher_id);

-- ============================================
-- 3. STUDENTS TABLE (Core Entity)
-- ============================================
CREATE TABLE IF NOT EXISTS students (
    id SERIAL PRIMARY KEY,
    name VARCHAR(255) NOT NULL,
    student_id_card_number VARCHAR(50) UNIQUE NOT NULL,
    facial_embedding FLOAT8[] NOT NULL,  -- 128-dimensional face embedding
    face_image_base64 TEXT,              -- Base64 encoded face image
    user_id INTEGER REFERENCES users(id) ON DELETE CASCADE,
    approval_status VARCHAR(20) DEFAULT 'approved' CHECK (approval_status IN ('pending', 'approved', 'rejected')),
    rejection_reason TEXT,
    approved_by INTEGER REFERENCES users(id) ON DELETE SET NULL,
    approved_at TIMESTAMP,
    created_at TIMESTAMP DEFAULT NOW(),
    updated_at TIMESTAMP DEFAULT NOW()
);

CREATE INDEX idx_students_student_id ON students(student_id_card_number);
CREATE INDEX idx_students_user_id ON students(user_id);
CREATE INDEX idx_students_approval_status ON students(approval_status);

-- ============================================
-- 4. ATTENDANCE SESSIONS TABLE
-- ============================================
CREATE TABLE IF NOT EXISTS attendance_sessions (
    id SERIAL PRIMARY KEY,
    session_id UUID UNIQUE NOT NULL DEFAULT uuid_generate_v4(),
    class_id INTEGER REFERENCES classes(id) ON DELETE CASCADE,
    teacher_id INTEGER REFERENCES users(id) ON DELETE SET NULL,
    status VARCHAR(20) DEFAULT 'active' CHECK (status IN ('active', 'completed', 'cancelled')),
    expires_at TIMESTAMP NOT NULL,
    created_at TIMESTAMP DEFAULT NOW(),
    updated_at TIMESTAMP DEFAULT NOW()
);

CREATE INDEX idx_sessions_session_id ON attendance_sessions(session_id);
CREATE INDEX idx_sessions_class_id ON attendance_sessions(class_id);
CREATE INDEX idx_sessions_teacher_id ON attendance_sessions(teacher_id);
CREATE INDEX idx_sessions_status ON attendance_sessions(status);
CREATE INDEX idx_sessions_created_at ON attendance_sessions(created_at);

-- ============================================
-- 5. ATTENDANCE TABLE (Verification Records)
-- ============================================
CREATE TABLE IF NOT EXISTS attendance (
    id SERIAL PRIMARY KEY,
    student_id INTEGER NOT NULL REFERENCES students(id) ON DELETE CASCADE,
    session_id INTEGER NOT NULL REFERENCES attendance_sessions(id) ON DELETE CASCADE,
    verification_status VARCHAR(20) NOT NULL CHECK (verification_status IN ('verified', 'failed', 'pending')),
    face_confidence FLOAT,
    otp_verified BOOLEAN DEFAULT FALSE,
    geofence_verified BOOLEAN DEFAULT FALSE,
    distance_meters FLOAT,
    emotion_detected VARCHAR(50),
    emotion_confidence FLOAT,
    timestamp TIMESTAMP DEFAULT NOW(),
    UNIQUE(student_id, session_id)  -- Prevent duplicate attendance for same session
);

CREATE INDEX idx_attendance_student_id ON attendance(student_id);
CREATE INDEX idx_attendance_session_id ON attendance(session_id);
CREATE INDEX idx_attendance_status ON attendance(verification_status);
CREATE INDEX idx_attendance_timestamp ON attendance(timestamp);

-- ============================================
-- 6. ANOMALIES TABLE (Security Alerts)
-- ============================================
CREATE TABLE IF NOT EXISTS anomalies (
    id SERIAL PRIMARY KEY,
    student_id INTEGER REFERENCES students(id) ON DELETE CASCADE,
    session_id INTEGER REFERENCES attendance_sessions(id) ON DELETE CASCADE,
    reason TEXT NOT NULL,
    anomaly_type VARCHAR(50) NOT NULL CHECK (anomaly_type IN ('proxy_attempt', 'verification_failed', 'geofence_violation', 'otp_expired', 'face_mismatch', 'liveness_failed')),
    face_confidence FLOAT,
    reviewed BOOLEAN DEFAULT FALSE,
    reviewed_by INTEGER REFERENCES users(id) ON DELETE SET NULL,
    reviewed_at TIMESTAMP,
    timestamp TIMESTAMP DEFAULT NOW()
);

CREATE INDEX idx_anomalies_student_id ON anomalies(student_id);
CREATE INDEX idx_anomalies_session_id ON anomalies(session_id);
CREATE INDEX idx_anomalies_type ON anomalies(anomaly_type);
CREATE INDEX idx_anomalies_reviewed ON anomalies(reviewed);
CREATE INDEX idx_anomalies_timestamp ON anomalies(timestamp);

-- ============================================
-- 7. OTP CACHE TABLE (For OTP Management)
-- Note: In production, use Redis. This is for SQL-only deployments
-- ============================================
CREATE TABLE IF NOT EXISTS otp_cache (
    id SERIAL PRIMARY KEY,
    session_id UUID NOT NULL,
    student_id_card_number VARCHAR(50) NOT NULL,
    otp VARCHAR(4) NOT NULL,
    resend_attempts INTEGER DEFAULT 0,
    expires_at TIMESTAMP NOT NULL,
    created_at TIMESTAMP DEFAULT NOW(),
    UNIQUE(session_id, student_id_card_number)
);

CREATE INDEX idx_otp_session_student ON otp_cache(session_id, student_id_card_number);
CREATE INDEX idx_otp_expires_at ON otp_cache(expires_at);

-- ============================================
-- 8. ACCOUNT LOCKS TABLE (Security)
-- ============================================
CREATE TABLE IF NOT EXISTS account_locks (
    id SERIAL PRIMARY KEY,
    student_id_card_number VARCHAR(50) UNIQUE NOT NULL,
    reason VARCHAR(255) NOT NULL,
    locked_at TIMESTAMP DEFAULT NOW(),
    expires_at TIMESTAMP NOT NULL,
    unlocked_by INTEGER REFERENCES users(id) ON DELETE SET NULL,
    unlocked_at TIMESTAMP
);

CREATE INDEX idx_locks_student_id ON account_locks(student_id_card_number);
CREATE INDEX idx_locks_expires_at ON account_locks(expires_at);

-- ============================================
-- 9. CLASS ENROLLMENTS TABLE (Student-Class Mapping)
-- ============================================
CREATE TABLE IF NOT EXISTS class_enrollments (
    id SERIAL PRIMARY KEY,
    class_id INTEGER NOT NULL REFERENCES classes(id) ON DELETE CASCADE,
    student_id INTEGER NOT NULL REFERENCES students(id) ON DELETE CASCADE,
    enrolled_at TIMESTAMP DEFAULT NOW(),
    UNIQUE(class_id, student_id)
);

CREATE INDEX idx_enrollments_class_id ON class_enrollments(class_id);
CREATE INDEX idx_enrollments_student_id ON class_enrollments(student_id);

-- ============================================
-- 10. AUDIT LOG TABLE (System Activity Tracking)
-- ============================================
CREATE TABLE IF NOT EXISTS audit_log (
    id SERIAL PRIMARY KEY,
    user_id INTEGER REFERENCES users(id) ON DELETE SET NULL,
    action VARCHAR(100) NOT NULL,
    entity_type VARCHAR(50) NOT NULL,
    entity_id INTEGER,
    details JSONB,
    ip_address INET,
    user_agent TEXT,
    timestamp TIMESTAMP DEFAULT NOW()
);

CREATE INDEX idx_audit_user_id ON audit_log(user_id);
CREATE INDEX idx_audit_action ON audit_log(action);
CREATE INDEX idx_audit_entity ON audit_log(entity_type, entity_id);
CREATE INDEX idx_audit_timestamp ON audit_log(timestamp);

-- ============================================
-- VIEWS FOR REPORTING
-- ============================================

-- View: Student Attendance Summary
CREATE OR REPLACE VIEW student_attendance_summary AS
SELECT 
    s.id AS student_id,
    s.name AS student_name,
    s.student_id_card_number,
    COUNT(a.id) AS total_sessions,
    COUNT(CASE WHEN a.verification_status = 'verified' THEN 1 END) AS verified_sessions,
    COUNT(CASE WHEN a.verification_status = 'failed' THEN 1 END) AS failed_sessions,
    ROUND(
        (COUNT(CASE WHEN a.verification_status = 'verified' THEN 1 END)::FLOAT / 
        NULLIF(COUNT(a.id), 0) * 100), 2
    ) AS attendance_percentage,
    MAX(a.timestamp) AS last_attendance
FROM students s
LEFT JOIN attendance a ON s.id = a.student_id
GROUP BY s.id, s.name, s.student_id_card_number;

-- View: Session Statistics
CREATE OR REPLACE VIEW session_statistics AS
SELECT 
    ats.id AS session_id,
    ats.session_id AS session_uuid,
    c.name AS class_name,
    c.class_id,
    COUNT(a.id) AS total_verifications,
    COUNT(CASE WHEN a.verification_status = 'verified' THEN 1 END) AS verified_count,
    COUNT(CASE WHEN a.verification_status = 'failed' THEN 1 END) AS failed_count,
    ROUND(AVG(a.face_confidence), 2) AS avg_face_confidence,
    ats.created_at AS session_start,
    ats.status
FROM attendance_sessions ats
LEFT JOIN classes c ON ats.class_id = c.id
LEFT JOIN attendance a ON ats.id = a.session_id
GROUP BY ats.id, ats.session_id, c.name, c.class_id, ats.created_at, ats.status;

-- View: Anomaly Summary
CREATE OR REPLACE VIEW anomaly_summary AS
SELECT 
    anomaly_type,
    COUNT(*) AS count,
    COUNT(CASE WHEN reviewed = FALSE THEN 1 END) AS unreviewed_count,
    MAX(timestamp) AS last_occurrence
FROM anomalies
GROUP BY anomaly_type
ORDER BY count DESC;

-- ============================================
-- FUNCTIONS
-- ============================================

-- Function: Clean expired OTPs
CREATE OR REPLACE FUNCTION clean_expired_otps()
RETURNS INTEGER AS $$
DECLARE
    deleted_count INTEGER;
BEGIN
    DELETE FROM otp_cache WHERE expires_at < NOW();
    GET DIAGNOSTICS deleted_count = ROW_COUNT;
    RETURN deleted_count;
END;
$$ LANGUAGE plpgsql;

-- Function: Clean expired account locks
CREATE OR REPLACE FUNCTION clean_expired_locks()
RETURNS INTEGER AS $$
DECLARE
    deleted_count INTEGER;
BEGIN
    DELETE FROM account_locks WHERE expires_at < NOW() AND unlocked_at IS NULL;
    GET DIAGNOSTICS deleted_count = ROW_COUNT;
    RETURN deleted_count;
END;
$$ LANGUAGE plpgsql;

-- Function: Get student attendance rate
CREATE OR REPLACE FUNCTION get_student_attendance_rate(p_student_id INTEGER)
RETURNS FLOAT AS $$
DECLARE
    attendance_rate FLOAT;
BEGIN
    SELECT 
        ROUND(
            (COUNT(CASE WHEN verification_status = 'verified' THEN 1 END)::FLOAT / 
            NULLIF(COUNT(*), 0) * 100), 2
        )
    INTO attendance_rate
    FROM attendance
    WHERE student_id = p_student_id;
    
    RETURN COALESCE(attendance_rate, 0);
END;
$$ LANGUAGE plpgsql;

-- ============================================
-- TRIGGERS
-- ============================================

-- Trigger: Update updated_at timestamp
CREATE OR REPLACE FUNCTION update_updated_at_column()
RETURNS TRIGGER AS $$
BEGIN
    NEW.updated_at = NOW();
    RETURN NEW;
END;
$$ LANGUAGE plpgsql;

CREATE TRIGGER update_users_updated_at BEFORE UPDATE ON users
    FOR EACH ROW EXECUTE FUNCTION update_updated_at_column();

CREATE TRIGGER update_students_updated_at BEFORE UPDATE ON students
    FOR EACH ROW EXECUTE FUNCTION update_updated_at_column();

CREATE TRIGGER update_classes_updated_at BEFORE UPDATE ON classes
    FOR EACH ROW EXECUTE FUNCTION update_updated_at_column();

CREATE TRIGGER update_sessions_updated_at BEFORE UPDATE ON attendance_sessions
    FOR EACH ROW EXECUTE FUNCTION update_updated_at_column();

-- ============================================
-- SAMPLE DATA (For Testing)
-- ============================================

-- Insert sample admin user
INSERT INTO users (email, name, role) VALUES
    ('admin@isavs.com', 'System Administrator', 'admin'),
    ('teacher@isavs.com', 'John Teacher', 'teacher')
ON CONFLICT (email) DO NOTHING;

-- Insert sample class
INSERT INTO classes (class_id, name, teacher_id) VALUES
    ('CS101', 'Computer Science 101', 2),
    ('MATH201', 'Advanced Mathematics', 2)
ON CONFLICT (class_id) DO NOTHING;

-- ============================================
-- CLEANUP JOBS (Run periodically)
-- ============================================

-- Clean expired OTPs (run every 5 minutes)
-- SELECT clean_expired_otps();

-- Clean expired locks (run every hour)
-- SELECT clean_expired_locks();

-- ============================================
-- PERMISSIONS (Adjust based on your setup)
-- ============================================

-- Grant permissions to application user
-- GRANT SELECT, INSERT, UPDATE, DELETE ON ALL TABLES IN SCHEMA public TO isavs_app;
-- GRANT USAGE, SELECT ON ALL SEQUENCES IN SCHEMA public TO isavs_app;

-- ============================================
-- COMMENTS
-- ============================================

COMMENT ON TABLE students IS 'Core student entity with 128-d facial embeddings';
COMMENT ON TABLE attendance_sessions IS 'Teacher-initiated attendance sessions with OTP generation';
COMMENT ON TABLE attendance IS 'Individual attendance verification records';
COMMENT ON TABLE anomalies IS 'Security alerts including proxy attempts and verification failures';
COMMENT ON TABLE otp_cache IS 'Temporary OTP storage (use Redis in production)';
COMMENT ON TABLE account_locks IS 'Temporary account locks for security violations';

COMMENT ON COLUMN students.facial_embedding IS '128-dimensional face embedding from face_recognition library';
COMMENT ON COLUMN attendance.face_confidence IS 'Cosine similarity score (0.0-1.0), threshold 0.6';
COMMENT ON COLUMN attendance.distance_meters IS 'Distance from classroom in meters (geofencing)';

-- ============================================
-- END OF SCHEMA
-- ============================================

-- Verify schema
SELECT 'ISAVS 2026 Database Schema Created Successfully!' AS status;
