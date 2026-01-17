-- Migration: Add Emotion Detection Support
-- Date: 2026-01-17
-- Description: Add emotion tracking columns for smile-to-verify liveness detection

-- Add embedding metadata to students table
ALTER TABLE students 
ADD COLUMN IF NOT EXISTS embedding_dimension INTEGER DEFAULT 128,
ADD COLUMN IF NOT EXISTS embedding_model VARCHAR(50) DEFAULT 'deepface_facenet';

-- Add emotion tracking to attendance table
ALTER TABLE attendance
ADD COLUMN IF NOT EXISTS emotion_detected VARCHAR(20),
ADD COLUMN IF NOT EXISTS emotion_confidence FLOAT;

-- Create index for emotion queries
CREATE INDEX IF NOT EXISTS idx_attendance_emotion ON attendance(emotion_detected);

-- Update existing records to set default values
UPDATE students 
SET embedding_dimension = 128, 
    embedding_model = 'deepface_facenet'
WHERE embedding_dimension IS NULL;

-- Add comment for documentation
COMMENT ON COLUMN attendance.emotion_detected IS 'Detected emotion during verification (happy, sad, angry, surprise, fear, disgust, neutral)';
COMMENT ON COLUMN attendance.emotion_confidence IS 'Confidence score for detected emotion (0.0 to 1.0)';
COMMENT ON COLUMN students.embedding_dimension IS 'Dimension of facial embedding (128 or 512)';
COMMENT ON COLUMN students.embedding_model IS 'AI model used for embedding (deepface_facenet, insightface_buffalo_l, etc.)';
