-- Migration: Add face_image_base64 column to students table
-- Run this in Supabase SQL Editor

-- Add the column if it doesn't exist
ALTER TABLE students 
ADD COLUMN IF NOT EXISTS face_image_base64 TEXT;

-- Add a comment to document the column
COMMENT ON COLUMN students.face_image_base64 IS 'Base64 encoded enrollment photo for visual verification and re-training';
