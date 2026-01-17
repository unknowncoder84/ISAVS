-- ISAVS Authentication System Migration
-- Run this in Supabase SQL Editor after the main schema

-- ============================================
-- PHASE 1: Create Users and Teachers Tables
-- ============================================

-- Users table (central authentication table)
CREATE TABLE IF NOT EXISTS users (
    id SERIAL PRIMARY KEY,
    supabase_user_id UUID UNIQUE,
    email VARCHAR(255) UNIQUE NOT NULL,
    name VARCHAR(255) NOT NULL,
    role VARCHAR(20) NOT NULL CHECK (role IN ('admin', 'teacher', 'student')),
    created_at TIMESTAMPTZ DEFAULT NOW(),
    updated_at TIMESTAMPTZ DEFAULT NOW()
);

-- Teachers table (extends users)
CREATE TABLE IF NOT EXISTS teachers (
    id SERIAL PRIMARY KEY,
    user_id INTEGER UNIQUE REFERENCES users(id) ON DELETE CASCADE,
    department VARCHAR(255),
    active BOOLEAN DEFAULT TRUE,
    created_at TIMESTAMPTZ DEFAULT NOW(),
    updated_at TIMESTAMPTZ DEFAULT NOW()
);

-- ============================================
-- PHASE 2: Update Students Table
-- ============================================

-- Add authentication and approval columns to students table
ALTER TABLE students 
ADD COLUMN IF NOT EXISTS user_id INTEGER UNIQUE REFERENCES users(id) ON DELETE SET NULL,
ADD COLUMN IF NOT EXISTS approval_status VARCHAR(20) DEFAULT 'pending' 
    CHECK (approval_status IN ('pending', 'approved', 'rejected')),
ADD COLUMN IF NOT EXISTS approved_by INTEGER REFERENCES users(id) ON DELETE SET NULL,
ADD COLUMN IF NOT EXISTS approved_at TIMESTAMPTZ,
ADD COLUMN IF NOT EXISTS rejection_reason TEXT;

-- ============================================
-- PHASE 3: Create Indexes for Performance
-- ============================================

CREATE INDEX IF NOT EXISTS idx_users_supabase_id ON users(supabase_user_id);
CREATE INDEX IF NOT EXISTS idx_users_email ON users(email);
CREATE INDEX IF NOT EXISTS idx_users_role ON users(role);
CREATE INDEX IF NOT EXISTS idx_teachers_user_id ON teachers(user_id);
CREATE INDEX IF NOT EXISTS idx_teachers_active ON teachers(active);
CREATE INDEX IF NOT EXISTS idx_students_user_id ON students(user_id);
CREATE INDEX IF NOT EXISTS idx_students_approval_status ON students(approval_status);

-- ============================================
-- PHASE 4: Update Timestamp Triggers
-- ============================================

-- Trigger for users table
DROP TRIGGER IF EXISTS users_updated_at ON users;
CREATE TRIGGER users_updated_at
    BEFORE UPDATE ON users
    FOR EACH ROW
    EXECUTE FUNCTION update_updated_at();

-- Trigger for teachers table
DROP TRIGGER IF EXISTS teachers_updated_at ON teachers;
CREATE TRIGGER teachers_updated_at
    BEFORE UPDATE ON teachers
    FOR EACH ROW
    EXECUTE FUNCTION update_updated_at();

-- ============================================
-- PHASE 5: Migrate Existing Data
-- ============================================

-- Set all existing students to 'approved' status
-- This ensures existing students can continue using the system
UPDATE students 
SET approval_status = 'approved', 
    approved_at = NOW()
WHERE approval_status IS NULL OR approval_status = 'pending';

-- ============================================
-- PHASE 6: Create First Admin User (MANUAL)
-- ============================================

-- IMPORTANT: Replace 'your-email@gmail.com' with your actual Gmail
-- The supabase_user_id will be updated on first login
-- Run this manually after migration:

-- INSERT INTO users (email, name, role, supabase_user_id)
-- VALUES ('your-email@gmail.com', 'Admin User', 'admin', gen_random_uuid())
-- ON CONFLICT (email) DO NOTHING;

-- ============================================
-- VERIFICATION QUERIES
-- ============================================

-- Verify tables created
SELECT table_name FROM information_schema.tables 
WHERE table_schema = 'public' 
AND table_name IN ('users', 'teachers');

-- Verify columns added to students
SELECT column_name, data_type 
FROM information_schema.columns 
WHERE table_name = 'students' 
AND column_name IN ('user_id', 'approval_status', 'approved_by', 'approved_at', 'rejection_reason');

-- Verify indexes created
SELECT indexname FROM pg_indexes 
WHERE tablename IN ('users', 'teachers', 'students')
AND indexname LIKE 'idx_%';

-- Check existing students are approved
SELECT COUNT(*) as approved_students 
FROM students 
WHERE approval_status = 'approved';

-- ============================================
-- SUCCESS MESSAGE
-- ============================================

DO $$
BEGIN
    RAISE NOTICE '✅ Authentication system migration completed successfully!';
    RAISE NOTICE '📝 Next steps:';
    RAISE NOTICE '1. Create first admin user (uncomment and run the INSERT query above)';
    RAISE NOTICE '2. Install supabase Python client: pip install supabase';
    RAISE NOTICE '3. Update backend/.env with Supabase credentials';
    RAISE NOTICE '4. Start implementing backend auth services';
END $$;
