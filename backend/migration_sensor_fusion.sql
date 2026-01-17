-- ============================================================
-- ISAVS 2026 - Sensor Fusion Migration
-- Adds sensor data columns for 8-factor authentication
-- ============================================================

-- Add sensor columns to attendance table
ALTER TABLE attendance
ADD COLUMN IF NOT EXISTS ble_rssi FLOAT,
ADD COLUMN IF NOT EXISTS ble_beacon_uuid VARCHAR(255),
ADD COLUMN IF NOT EXISTS barometric_pressure FLOAT,
ADD COLUMN IF NOT EXISTS pressure_difference_hpa FLOAT,
ADD COLUMN IF NOT EXISTS motion_correlation FLOAT,
ADD COLUMN IF NOT EXISTS sensor_validation_passed BOOLEAN DEFAULT FALSE,
ADD COLUMN IF NOT EXISTS failed_sensors TEXT[];

-- Add comments for documentation
COMMENT ON COLUMN attendance.ble_rssi IS 'BLE signal strength in dBm (threshold: -70 dBm)';
COMMENT ON COLUMN attendance.ble_beacon_uuid IS 'UUID of detected classroom beacon';
COMMENT ON COLUMN attendance.barometric_pressure IS 'Student barometric pressure in hPa';
COMMENT ON COLUMN attendance.pressure_difference_hpa IS 'Pressure difference from teacher (threshold: 0.5 hPa)';
COMMENT ON COLUMN attendance.motion_correlation IS 'Motion-image correlation coefficient (threshold: 0.7)';
COMMENT ON COLUMN attendance.sensor_validation_passed IS 'Whether all sensor validations passed';
COMMENT ON COLUMN attendance.failed_sensors IS 'Array of sensor names that failed validation';

-- Add sensor columns to attendance_sessions table
ALTER TABLE attendance_sessions
ADD COLUMN IF NOT EXISTS beacon_uuid VARCHAR(255),
ADD COLUMN IF NOT EXISTS teacher_latitude FLOAT,
ADD COLUMN IF NOT EXISTS teacher_longitude FLOAT,
ADD COLUMN IF NOT EXISTS teacher_barometric_pressure FLOAT,
ADD COLUMN IF NOT EXISTS ble_enabled BOOLEAN DEFAULT TRUE,
ADD COLUMN IF NOT EXISTS motion_detection_enabled BOOLEAN DEFAULT TRUE;

-- Add comments
COMMENT ON COLUMN attendance_sessions.beacon_uuid IS 'BLE beacon UUID for this session';
COMMENT ON COLUMN attendance_sessions.teacher_latitude IS 'Classroom GPS latitude';
COMMENT ON COLUMN attendance_sessions.teacher_longitude IS 'Classroom GPS longitude';
COMMENT ON COLUMN attendance_sessions.teacher_barometric_pressure IS 'Classroom barometric pressure in hPa';
COMMENT ON COLUMN attendance_sessions.ble_enabled IS 'Whether BLE proximity check is enabled';
COMMENT ON COLUMN attendance_sessions.motion_detection_enabled IS 'Whether motion-image correlation is enabled';

-- Create sensor_anomalies table for detailed sensor logging
CREATE TABLE IF NOT EXISTS sensor_anomalies (
    id SERIAL PRIMARY KEY,
    student_id INTEGER REFERENCES students(id) ON DELETE CASCADE,
    session_id INTEGER REFERENCES attendance_sessions(id) ON DELETE CASCADE,
    timestamp TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    
    -- Sensor failure details
    failed_sensor VARCHAR(50) NOT NULL,
    failure_reason TEXT NOT NULL,
    
    -- Sensor values
    ble_rssi FLOAT,
    ble_expected_uuid VARCHAR(255),
    ble_detected_uuid VARCHAR(255),
    
    gps_distance_meters FLOAT,
    gps_max_distance_meters FLOAT,
    
    pressure_difference_hpa FLOAT,
    pressure_threshold_hpa FLOAT,
    
    motion_correlation FLOAT,
    motion_threshold FLOAT,
    
    -- Metadata
    device_info JSONB,
    reviewed BOOLEAN DEFAULT FALSE,
    reviewed_by INTEGER,
    reviewed_at TIMESTAMP,
    notes TEXT
);

-- Add comments
COMMENT ON TABLE sensor_anomalies IS 'Detailed logging of sensor validation failures';
COMMENT ON COLUMN sensor_anomalies.failed_sensor IS 'Sensor that failed: BLE, GPS, Barometer, Motion';
COMMENT ON COLUMN sensor_anomalies.failure_reason IS 'Human-readable failure reason';

-- Create indexes for performance
CREATE INDEX IF NOT EXISTS idx_attendance_ble_rssi ON attendance(ble_rssi) WHERE ble_rssi IS NOT NULL;
CREATE INDEX IF NOT EXISTS idx_attendance_motion_correlation ON attendance(motion_correlation) WHERE motion_correlation IS NOT NULL;
CREATE INDEX IF NOT EXISTS idx_attendance_sensor_validation ON attendance(sensor_validation_passed);
CREATE INDEX IF NOT EXISTS idx_sensor_anomalies_student ON sensor_anomalies(student_id);
CREATE INDEX IF NOT EXISTS idx_sensor_anomalies_session ON sensor_anomalies(session_id);
CREATE INDEX IF NOT EXISTS idx_sensor_anomalies_sensor ON sensor_anomalies(failed_sensor);
CREATE INDEX IF NOT EXISTS idx_sensor_anomalies_timestamp ON sensor_anomalies(timestamp DESC);
CREATE INDEX IF NOT EXISTS idx_sensor_anomalies_unreviewed ON sensor_anomalies(reviewed) WHERE reviewed = FALSE;

-- Create view for sensor statistics
CREATE OR REPLACE VIEW sensor_validation_stats AS
SELECT
    COUNT(*) as total_verifications,
    COUNT(*) FILTER (WHERE sensor_validation_passed = TRUE) as sensor_passed_count,
    COUNT(*) FILTER (WHERE sensor_validation_passed = FALSE) as sensor_failed_count,
    ROUND(100.0 * COUNT(*) FILTER (WHERE sensor_validation_passed = TRUE) / NULLIF(COUNT(*), 0), 2) as sensor_pass_rate,
    
    -- BLE statistics
    COUNT(*) FILTER (WHERE ble_rssi IS NOT NULL) as ble_checks,
    COUNT(*) FILTER (WHERE ble_rssi > -70) as ble_passed,
    AVG(ble_rssi) FILTER (WHERE ble_rssi IS NOT NULL) as avg_ble_rssi,
    
    -- Barometer statistics
    COUNT(*) FILTER (WHERE barometric_pressure IS NOT NULL) as barometer_checks,
    AVG(pressure_difference_hpa) FILTER (WHERE pressure_difference_hpa IS NOT NULL) as avg_pressure_diff,
    
    -- Motion correlation statistics
    COUNT(*) FILTER (WHERE motion_correlation IS NOT NULL) as motion_checks,
    COUNT(*) FILTER (WHERE motion_correlation >= 0.7) as motion_passed,
    AVG(motion_correlation) FILTER (WHERE motion_correlation IS NOT NULL) as avg_motion_correlation
FROM attendance
WHERE timestamp >= CURRENT_DATE - INTERVAL '30 days';

COMMENT ON VIEW sensor_validation_stats IS 'Real-time statistics for sensor validation performance';

-- Create view for sensor anomaly summary
CREATE OR REPLACE VIEW sensor_anomaly_summary AS
SELECT
    failed_sensor,
    COUNT(*) as failure_count,
    COUNT(*) FILTER (WHERE reviewed = FALSE) as unreviewed_count,
    ROUND(100.0 * COUNT(*) / SUM(COUNT(*)) OVER (), 2) as failure_percentage
FROM sensor_anomalies
WHERE timestamp >= CURRENT_DATE - INTERVAL '30 days'
GROUP BY failed_sensor
ORDER BY failure_count DESC;

COMMENT ON VIEW sensor_anomaly_summary IS 'Summary of sensor failures by type';

-- ============================================================
-- Migration Complete
-- ============================================================

-- Verify migration
DO $$
BEGIN
    RAISE NOTICE 'Sensor Fusion Migration Complete!';
    RAISE NOTICE 'Added columns to attendance table: ble_rssi, barometric_pressure, motion_correlation';
    RAISE NOTICE 'Added columns to attendance_sessions table: beacon_uuid, teacher_barometric_pressure';
    RAISE NOTICE 'Created sensor_anomalies table for detailed logging';
    RAISE NOTICE 'Created indexes for performance optimization';
    RAISE NOTICE 'Created views: sensor_validation_stats, sensor_anomaly_summary';
END $$;
