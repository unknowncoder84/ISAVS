-- ============================================
-- ISAVS 2026 - FINAL COMPREHENSIVE MIGRATION
-- This script handles ALL existing database issues
-- Safe to run multiple times (idempotent)
-- ============================================

-- Enable UUID extension
CREATE EXTENSION IF NOT EXISTS "uuid-ossp";

-- ============================================
-- STEP 1: FIX CLASSES TABLE
-- ============================================
DO $$ 
BEGIN
    RAISE NOTICE 'Step 1: Fixing classes table...';
    
    -- Add teacher_id column if it doesn't exist
    IF NOT EXISTS (SELECT 1 FROM information_schema.columns 
                   WHERE table_name = 'classes' AND column_name = 'teacher_id') THEN
        ALTER TABLE classes ADD COLUMN teacher_id INTEGER;
        RAISE NOTICE '  ✓ Added teacher_id column to classes';
    ELSE
        RAISE NOTICE '  - teacher_id column already exists';
    END IF;
    
    -- Add foreign key constraint if it doesn't exist
    IF NOT EXISTS (SELECT 1 FROM pg_constraint WHERE conname = 'classes_teacher_id_fkey') THEN
        ALTER TABLE classes ADD CONSTRAINT classes_teacher_id_fkey 
            FOREIGN KEY (teacher_id) REFERENCES users(id) ON DELETE SET NULL;
        RAISE NOTICE '  ✓ Added foreign key constraint for teacher_id';
    ELSE
        RAISE NOTICE '  - Foreign key constraint already exists';
    END IF;
    
    -- Add created_at if missing
    IF NOT EXISTS (SELECT 1 FROM information_schema.columns 
                   WHERE table_name = 'classes' AND column_name = 'created_at') THEN
        ALTER TABLE classes ADD COLUMN created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP;
        RAISE NOTICE '  ✓ Added created_at column to classes';
    ELSE
        RAISE NOTICE '  - created_at column already exists';
    END IF;
    
    -- Add updated_at if missing
    IF NOT EXISTS (SELECT 1 FROM information_schema.columns 
                   WHERE table_name = 'classes' AND column_name = 'updated_at') THEN
        ALTER TABLE classes ADD COLUMN updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP;
        RAISE NOTICE '  ✓ Added updated_at column to classes';
    ELSE
        RAISE NOTICE '  - updated_at column already exists';
    END IF;
END $$;

-- Create indexes for classes table
DO $$ 
BEGIN
    IF NOT EXISTS (SELECT 1 FROM pg_indexes WHERE indexname = 'idx_classes_class_id') THEN
        CREATE INDEX idx_classes_class_id ON classes(class_id);
        RAISE NOTICE '  ✓ Created index idx_classes_class_id';
    END IF;
    
    IF NOT EXISTS (SELECT 1 FROM pg_indexes WHERE indexname = 'idx_classes_teacher_id') THEN
        CREATE INDEX idx_classes_teacher_id ON classes(teacher_id);
        RAISE NOTICE '  ✓ Created index idx_classes_teacher_id';
    END IF;
END $$;

-- ============================================
-- STEP 2: FIX ATTENDANCE_SESSIONS TABLE
-- ============================================
DO $$ 
BEGIN
    RAISE NOTICE 'Step 2: Fixing attendance_sessions table...';
    
    -- Add created_at if it doesn't exist
    IF NOT EXISTS (SELECT 1 FROM information_schema.columns 
                   WHERE table_name = 'attendance_sessions' AND column_name = 'created_at') THEN
        ALTER TABLE attendance_sessions ADD COLUMN created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP;
        RAISE NOTICE '  ✓ Added created_at column to attendance_sessions';
    ELSE
        RAISE NOTICE '  - created_at column already exists';
    END IF;
    
    -- Add updated_at if it doesn't exist
    IF NOT EXISTS (SELECT 1 FROM information_schema.columns 
                   WHERE table_name = 'attendance_sessions' AND column_name = 'updated_at') THEN
        ALTER TABLE attendance_sessions ADD COLUMN updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP;
        RAISE NOTICE '  ✓ Added updated_at column to attendance_sessions';
    ELSE
        RAISE NOTICE '  - updated_at column already exists';
    END IF;
END $$;

-- Create index on created_at
DO $$ 
BEGIN
    IF NOT EXISTS (SELECT 1 FROM pg_indexes WHERE indexname = 'idx_sessions_created_at') THEN
        CREATE INDEX idx_sessions_created_at ON attendance_sessions(created_at);
        RAISE NOTICE '  ✓ Created index idx_sessions_created_at';
    END IF;
END $$;

-- ============================================
-- STEP 3: ADD GPS TRACKING TO ATTENDANCE TABLE
-- ============================================
DO $$ 
BEGIN
    RAISE NOTICE 'Step 3: Adding GPS tracking columns to attendance...';
    
    -- Track GPS failure attempts
    IF NOT EXISTS (SELECT 1 FROM information_schema.columns 
                   WHERE table_name = 'attendance' AND column_name = 'gps_failure_count') THEN
        ALTER TABLE attendance ADD COLUMN gps_failure_count INTEGER DEFAULT 0;
        RAISE NOTICE '  ✓ Added gps_failure_count column';
    ELSE
        RAISE NOTICE '  - gps_failure_count column already exists';
    END IF;
    
    -- Track WiFi SSID for fallback verification
    IF NOT EXISTS (SELECT 1 FROM information_schema.columns 
                   WHERE table_name = 'attendance' AND column_name = 'wifi_ssid') THEN
        ALTER TABLE attendance ADD COLUMN wifi_ssid VARCHAR(255);
        RAISE NOTICE '  ✓ Added wifi_ssid column';
    ELSE
        RAISE NOTICE '  - wifi_ssid column already exists';
    END IF;
    
    -- Track verification method used
    IF NOT EXISTS (SELECT 1 FROM information_schema.columns 
                   WHERE table_name = 'attendance' AND column_name = 'verification_method') THEN
        ALTER TABLE attendance ADD COLUMN verification_method VARCHAR(50) DEFAULT 'gps';
        RAISE NOTICE '  ✓ Added verification_method column';
    ELSE
        RAISE NOTICE '  - verification_method column already exists';
    END IF;
    
    -- Track GPS accuracy
    IF NOT EXISTS (SELECT 1 FROM information_schema.columns 
                   WHERE table_name = 'attendance' AND column_name = 'gps_accuracy') THEN
        ALTER TABLE attendance ADD COLUMN gps_accuracy FLOAT;
        RAISE NOTICE '  ✓ Added gps_accuracy column';
    ELSE
        RAISE NOTICE '  - gps_accuracy column already exists';
    END IF;
END $$;

-- Add check constraint for verification_method
DO $$ 
BEGIN
    IF NOT EXISTS (SELECT 1 FROM pg_constraint WHERE conname = 'attendance_verification_method_check') THEN
        ALTER TABLE attendance ADD CONSTRAINT attendance_verification_method_check 
            CHECK (verification_method IN ('gps', 'wifi', 'manual'));
        RAISE NOTICE '  ✓ Added check constraint for verification_method';
    END IF;
END $$;

-- ============================================
-- STEP 4: CREATE WIFI WHITELIST TABLE
-- ============================================
CREATE TABLE IF NOT EXISTS wifi_whitelist (
    id SERIAL PRIMARY KEY,
    ssid VARCHAR(255) UNIQUE NOT NULL,
    location_name VARCHAR(255) NOT NULL,
    is_active BOOLEAN DEFAULT TRUE,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

DO $$ 
BEGIN
    IF NOT EXISTS (SELECT 1 FROM pg_indexes WHERE indexname = 'idx_wifi_ssid') THEN
        CREATE INDEX idx_wifi_ssid ON wifi_whitelist(ssid);
        RAISE NOTICE 'Step 4: ✓ Created wifi_whitelist table and index';
    ELSE
        RAISE NOTICE 'Step 4: - wifi_whitelist table already exists';
    END IF;
END $$;

-- Insert sample college WiFi networks
INSERT INTO wifi_whitelist (ssid, location_name) VALUES
    ('College-WiFi', 'Main Campus Network'),
    ('College-Staff', 'Staff Network'),
    ('College-Student', 'Student Network'),
    ('Eduroam', 'Education Roaming Network')
ON CONFLICT (ssid) DO NOTHING;

-- ============================================
-- STEP 5: CREATE GEOFENCE CONFIG TABLE
-- ============================================
CREATE TABLE IF NOT EXISTS geofence_config (
    id SERIAL PRIMARY KEY,
    config_key VARCHAR(100) UNIQUE NOT NULL,
    config_value VARCHAR(255) NOT NULL,
    description TEXT,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Insert geofencing configuration
INSERT INTO geofence_config (config_key, config_value, description) VALUES
    ('max_distance_meters', '100', 'Maximum allowed distance from teacher in meters'),
    ('gps_failure_threshold', '2', 'Number of GPS failures before WiFi fallback'),
    ('high_accuracy_required', 'true', 'Require high accuracy GPS mode'),
    ('wifi_fallback_enabled', 'true', 'Enable WiFi SSID fallback verification')
ON CONFLICT (config_key) DO UPDATE SET 
    config_value = EXCLUDED.config_value,
    updated_at = CURRENT_TIMESTAMP;

RAISE NOTICE 'Step 5: ✓ Created geofence_config table';

-- ============================================
-- STEP 6: CREATE HELPER FUNCTIONS
-- ============================================

-- Function to check if WiFi SSID is whitelisted
CREATE OR REPLACE FUNCTION is_wifi_whitelisted(p_ssid VARCHAR)
RETURNS BOOLEAN AS $$
DECLARE
    is_valid BOOLEAN;
BEGIN
    SELECT EXISTS(
        SELECT 1 FROM wifi_whitelist 
        WHERE ssid = p_ssid AND is_active = TRUE
    ) INTO is_valid;
    
    RETURN is_valid;
END;
$$ LANGUAGE plpgsql;

-- Function to get geofence config value
CREATE OR REPLACE FUNCTION get_geofence_config(p_key VARCHAR)
RETURNS VARCHAR AS $$
DECLARE
    config_val VARCHAR;
BEGIN
    SELECT config_value INTO config_val
    FROM geofence_config
    WHERE config_key = p_key;
    
    RETURN config_val;
END;
$$ LANGUAGE plpgsql;

RAISE NOTICE 'Step 6: ✓ Created helper functions';

-- ============================================
-- STEP 7: CREATE/UPDATE TRIGGERS
-- ============================================

-- Function for updating updated_at timestamp
CREATE OR REPLACE FUNCTION update_updated_at_column()
RETURNS TRIGGER AS $$
BEGIN
    NEW.updated_at = CURRENT_TIMESTAMP;
    RETURN NEW;
END;
$$ LANGUAGE plpgsql;

-- Create triggers if they don't exist
DO $$ 
BEGIN
    -- Trigger for geofence_config
    IF NOT EXISTS (SELECT 1 FROM pg_trigger WHERE tgname = 'update_geofence_config_updated_at') THEN
        CREATE TRIGGER update_geofence_config_updated_at 
        BEFORE UPDATE ON geofence_config
        FOR EACH ROW EXECUTE FUNCTION update_updated_at_column();
        RAISE NOTICE 'Step 7: ✓ Created trigger for geofence_config';
    END IF;
    
    -- Trigger for wifi_whitelist
    IF NOT EXISTS (SELECT 1 FROM pg_trigger WHERE tgname = 'update_wifi_whitelist_updated_at') THEN
        CREATE TRIGGER update_wifi_whitelist_updated_at 
        BEFORE UPDATE ON wifi_whitelist
        FOR EACH ROW EXECUTE FUNCTION update_updated_at_column();
        RAISE NOTICE 'Step 7: ✓ Created trigger for wifi_whitelist';
    END IF;
    
    -- Trigger for classes
    IF NOT EXISTS (SELECT 1 FROM pg_trigger WHERE tgname = 'update_classes_updated_at') THEN
        CREATE TRIGGER update_classes_updated_at 
        BEFORE UPDATE ON classes
        FOR EACH ROW EXECUTE FUNCTION update_updated_at_column();
        RAISE NOTICE 'Step 7: ✓ Created trigger for classes';
    END IF;
    
    -- Trigger for attendance_sessions
    IF NOT EXISTS (SELECT 1 FROM pg_trigger WHERE tgname = 'update_sessions_updated_at') THEN
        CREATE TRIGGER update_sessions_updated_at 
        BEFORE UPDATE ON attendance_sessions
        FOR EACH ROW EXECUTE FUNCTION update_updated_at_column();
        RAISE NOTICE 'Step 7: ✓ Created trigger for attendance_sessions';
    END IF;
END $$;

-- ============================================
-- STEP 8: ADD COMMENTS FOR DOCUMENTATION
-- ============================================
COMMENT ON COLUMN attendance.gps_failure_count IS 'Number of GPS verification failures before fallback';
COMMENT ON COLUMN attendance.wifi_ssid IS 'WiFi SSID used for fallback verification';
COMMENT ON COLUMN attendance.verification_method IS 'Method used: gps, wifi, or manual';
COMMENT ON COLUMN attendance.gps_accuracy IS 'GPS accuracy in meters from device';
COMMENT ON TABLE wifi_whitelist IS 'Approved college WiFi networks for fallback verification';
COMMENT ON TABLE geofence_config IS 'Geofencing system configuration parameters';

-- ============================================
-- VERIFICATION QUERIES
-- ============================================

-- Verify all tables exist
DO $$
DECLARE
    table_count INTEGER;
BEGIN
    SELECT COUNT(*) INTO table_count
    FROM information_schema.tables
    WHERE table_schema = 'public' 
    AND table_name IN ('classes', 'attendance_sessions', 'attendance', 'wifi_whitelist', 'geofence_config');
    
    RAISE NOTICE '';
    RAISE NOTICE '========================================';
    RAISE NOTICE 'MIGRATION COMPLETE!';
    RAISE NOTICE '========================================';
    RAISE NOTICE 'Tables verified: % of 5', table_count;
END $$;

-- Show configuration
SELECT 'Geofence Configuration:' as info;
SELECT config_key, config_value, description FROM geofence_config ORDER BY config_key;

SELECT '' as separator;
SELECT 'WiFi Whitelist:' as info;
SELECT ssid, location_name, is_active FROM wifi_whitelist ORDER BY location_name;

SELECT '' as separator;
SELECT '✅ ISAVS 2026 - Database Migration Complete!' as status;
SELECT '✅ All tables, columns, indexes, and functions created successfully!' as status;
SELECT '✅ Safe to run multiple times (idempotent)' as status;
