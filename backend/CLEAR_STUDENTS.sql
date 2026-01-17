-- Clear all student data (keeps table structure)
-- Run this in Supabase SQL Editor if you want to start fresh with enrollments

-- Delete all students (cascades to attendance, anomalies, etc.)
DELETE FROM students;

-- Reset the ID sequence to start from 1
ALTER SEQUENCE students_id_seq RESTART WITH 1;

-- Also clear attendance sessions if you want
DELETE FROM attendance_sessions;
ALTER SEQUENCE attendance_sessions_id_seq RESTART WITH 1;

-- Clear classes if needed
DELETE FROM classes;
ALTER SEQUENCE classes_id_seq RESTART WITH 1;

-- Verify everything is cleared
SELECT 'Students count:' as info, COUNT(*) as count FROM students
UNION ALL
SELECT 'Attendance count:', COUNT(*) FROM attendance
UNION ALL
SELECT 'Sessions count:', COUNT(*) FROM attendance_sessions
UNION ALL
SELECT 'Anomalies count:', COUNT(*) FROM anomalies;
