-- ============================================
-- ISAVS 2026 - Geofencing Fix Migration
-- Fixes: created_at column and GPS verification
-- ============================================

-- Fix attendance_sessions table - ensure created_at exists
DO $$ 
BEGIN
    -- Add created_at if it doesn't exist
    IF NOT EXISTS (SELECT 1 FROM information_schema.columns 
                   WHERE table_name = 'attendance_sessions' AND column_name = 'created_at') THEN
        ALTER TABLE attendance_sessions ADD COLUMN created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP;
        RAISE NOTICE 'Added created_at column to attendance_sessions';
    END IF;
    
    -- Add updated_at if it doesn't exist
    IF NOT EXISTS (SELECT 1 FROM information_schema.columns 
                   WHERE table_name = 'attendance_sessions' AND column_name = 'updated_at') THEN
        ALTER TABLE attendance_sessions ADD COLUMN updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP;
        RAISE NOTICE 'Added updated_at column to attendance_sessions';
    END IF;
END $$;

-- Create index on created_at ONLY after ensuring column exists
DO $$ 
BEGIN
    IF NOT EXISTS (SELECT 1 FROM pg_indexes WHERE indexname = 'idx_sessions_created_at') THEN
        CREATE INDEX idx_sessions_created_at ON attendance_sessions(created_at);
        RAISE NOTICE 'Created index idx_sessions_created_at';
    END IF;
END $$;

-- Add GPS failure tracking columns to attendance table
DO $$ 
BEGIN
    -- Track GPS failure attempts
    IF NOT EXISTS (SELECT 1 FROM information_schema.columns 
                   WHERE table_name = 'attendance' AND column_name = 'gps_failure_count') THEN
        ALTER TABLE attendance ADD COLUMN gps_failure_count INTEGER DEFAULT 0;
        RAISE NOTICE 'Added gps_failure_count column to attendance';
    END IF;
    
    -- Track WiFi SSID for fallback verification
    IF NOT EXISTS (SELECT 1 FROM information_schema.columns 
                   WHERE table_name = 'attendance' AND column_name = 'wifi_ssid') THEN
        ALTER TABLE attendance ADD COLUMN wifi_ssid VARCHAR(255);
        RAISE NOTICE 'Added wifi_ssid column to attendance';
    END IF;
    
    -- Track verification method used
    IF NOT EXISTS (SELECT 1 FROM information_schema.columns 
                   WHERE table_name = 'attendance' AND column_name = 'verification_method') THEN
        ALTER TABLE attendance ADD COLUMN verification_method VARCHAR(50) DEFAULT 'gps' 
            CHECK (verification_method IN ('gps', 'wifi', 'manual'));
        RAISE NOTICE 'Added verification_method column to attendance';
    END IF;
    
    -- Track GPS accuracy
    IF NOT EXISTS (SELECT 1 FROM information_schema.columns 
                   WHERE table_name = 'attendance' AND column_name = 'gps_accuracy') THEN
        ALTER TABLE attendance ADD COLUMN gps_accuracy FLOAT;
        RAISE NOTICE 'Added gps_accuracy column to attendance';
    END IF;
END $$;

-- Add WiFi SSID whitelist table for college networks
CREATE TABLE IF NOT EXISTS wifi_whitelist (
    id SERIAL PRIMARY KEY,
    ssid VARCHAR(255) UNIQUE NOT NULL,
    location_name VARCHAR(255) NOT NULL,
    is_active BOOLEAN DEFAULT TRUE,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Create index on SSID for fast lookup
DO $$ 
BEGIN
    IF NOT EXISTS (SELECT 1 FROM pg_indexes WHERE indexname = 'idx_wifi_ssid') THEN
        CREATE INDEX idx_wifi_ssid ON wifi_whitelist(ssid);
        RAISE NOTICE 'Created index idx_wifi_ssid';
    END IF;
END $$;

-- Insert sample college WiFi networks
INSERT INTO wifi_whitelist (ssid, location_name) VALUES
    ('College-WiFi', 'Main Campus Network'),
    ('College-Staff', 'Staff Network'),
    ('College-Student', 'Student Network'),
    ('Eduroam', 'Education Roaming Network')
ON CONFLICT (ssid) DO NOTHING;

-- Add geofencing configuration table
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

-- Create function to check if WiFi SSID is whitelisted
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

-- Create function to get geofence config value
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

-- Update trigger for geofence_config
DO $$ 
BEGIN
    IF NOT EXISTS (SELECT 1 FROM pg_trigger WHERE tgname = 'update_geofence_config_updated_at') THEN
        CREATE TRIGGER update_geofence_config_updated_at 
        BEFORE UPDATE ON geofence_config
        FOR EACH ROW EXECUTE FUNCTION update_updated_at_column();
        RAISE NOTICE 'Created trigger update_geofence_config_updated_at';
    END IF;
END $$;

-- Add comments for documentation
COMMENT ON COLUMN attendance.gps_failure_count IS 'Number of GPS verification failures before fallback';
COMMENT ON COLUMN attendance.wifi_ssid IS 'WiFi SSID used for fallback verification';
COMMENT ON COLUMN attendance.verification_method IS 'Method used: gps, wifi, or manual';
COMMENT ON COLUMN attendance.gps_accuracy IS 'GPS accuracy in meters from device';
COMMENT ON TABLE wifi_whitelist IS 'Approved college WiFi networks for fallback verification';
COMMENT ON TABLE geofence_config IS 'Geofencing system configuration parameters';

-- Verify migration
SELECT 'Geofencing Fix Migration Complete!' AS status;
SELECT 'Created/Updated Tables: attendance_sessions, attendance, wifi_whitelist, geofence_config' AS tables;
SELECT 'New Functions: is_wifi_whitelisted(), get_geofence_config()' AS functions;
