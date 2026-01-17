# 🗄️ Database Setup Guide - ISAVS

## Quick Setup (Fresh Start)

### Step 1: Go to Supabase Dashboard
1. Open https://supabase.com/dashboard
2. Select your project: `textjheeqfwmrzjtfdyo`
3. Click **SQL Editor** in the left sidebar
4. Click **New Query**

### Step 2: Run Fresh Database Setup
Copy and paste the entire content of `backend/FRESH_DATABASE_SETUP.sql` into the SQL Editor and click **Run**.

This will:
- ✅ Drop all existing tables (clean slate)
- ✅ Create all tables with correct structure
- ✅ Add indexes for performance
- ✅ Set up triggers and functions
- ✅ Create sample classes

**⚠️ WARNING**: This will delete all existing data!

---

## What Tables Are Created?

### 1. **students**
Stores student information and face data
- `id` - Primary key
- `name` - Student name
- `student_id_card_number` - Unique student ID (e.g., STU001)
- `facial_embedding` - 128-dimensional face features
- `face_image_base64` - Original enrollment photo
- `created_at`, `updated_at` - Timestamps

### 2. **classes**
Stores class information
- `id` - Primary key
- `class_id` - Unique class code (e.g., CS101)
- `name` - Class name
- `created_at` - Timestamp

### 3. **class_enrollments**
Links students to classes (many-to-many)
- `id` - Primary key
- `class_id` - Reference to classes
- `student_id` - Reference to students
- `enrolled_at` - Timestamp

### 4. **attendance_sessions**
Active attendance sessions
- `id` - Primary key
- `session_id` - UUID for session
- `class_id` - Reference to classes
- `started_at`, `expires_at` - Time range
- `status` - active/expired/completed

### 5. **attendance**
Attendance records
- `id` - Primary key
- `student_id` - Reference to students
- `session_id` - Reference to attendance_sessions
- `timestamp` - When attendance was marked
- `verification_status` - verified/failed
- `face_confidence` - Similarity score (0-1)
- `otp_verified` - Boolean

### 6. **anomalies**
Security alerts and issues
- `id` - Primary key
- `student_id` - Reference to students
- `session_id` - Reference to attendance_sessions
- `reason` - Description of issue
- `anomaly_type` - Type of alert
  - `verification_failed` - General failure
  - `identity_mismatch` - Face doesn't match
  - `proxy_attempt` - Someone else trying to mark attendance
  - `session_locked` - Account locked
  - `multiple_faces` - More than one face detected
  - `no_face_detected` - No face in image
- `face_confidence` - Similarity score
- `timestamp` - When it occurred
- `reviewed` - Has admin reviewed it?

### 7. **otp_resend_tracking**
Tracks OTP resend attempts
- Prevents spam
- Max 2 resends per session

### 8. **verification_sessions**
Tracks verification attempts and locks
- Used for three-strike policy
- Stores lock status

---

## After Database Setup

### 1. Restart Backend Server
The backend needs to reconnect to the new database structure.

```bash
# Stop current backend (Ctrl+C in terminal)
# Or use Kiro to stop process

# Start again
cd backend
uvicorn app.main:app --reload --port 8000
```

### 2. Verify Connection
Check backend logs for:
```
✅ Supabase connection successful
✅ Supabase REST API connected
```

### 3. Enroll Students
1. Go to http://localhost:3000
2. Click "Enroll Student"
3. Fill in details:
   - Name: Your name
   - Student ID: STU001 (or any unique ID)
   - Capture face photo (good lighting, centered)
4. Click "Enroll"

### 4. Test Attendance
1. Go to Dashboard
2. Click "Session" tab
3. Enter Class ID (e.g., CS101)
4. Click "Start Session"
5. Copy the full Session ID (UUID format)
6. Go to Kiosk view
7. Enter Session ID
8. Enter Student ID (STU001)
9. Enter OTP (shown in dashboard)
10. Capture face
11. Should verify successfully!

---

## Troubleshooting

### Error: "Could not find column"
- Run the fresh database setup SQL again
- Make sure all tables are created
- Check Supabase logs for errors

### Error: "Student not found"
- Make sure you enrolled the student first
- Check the student ID matches exactly (case-sensitive)

### Error: "Face not recognized"
- Re-enroll with better lighting
- Make sure face is centered and clear
- Try lowering threshold in `.env`: `FACE_SIMILARITY_THRESHOLD=0.2`

### Error: "Account locked"
- This means proxy attempt was detected
- Go to Dashboard → Students tab
- Click "Unlock" button for that student

---

## Database Maintenance

### View All Students
```sql
SELECT id, name, student_id_card_number, created_at 
FROM students 
ORDER BY created_at DESC;
```

### View Recent Attendance
```sql
SELECT 
    s.name,
    s.student_id_card_number,
    a.timestamp,
    a.verification_status,
    a.face_confidence
FROM attendance a
JOIN students s ON a.student_id = s.id
ORDER BY a.timestamp DESC
LIMIT 20;
```

### View Security Alerts
```sql
SELECT 
    s.name,
    an.anomaly_type,
    an.reason,
    an.timestamp
FROM anomalies an
LEFT JOIN students s ON an.student_id = s.id
ORDER BY an.timestamp DESC
LIMIT 20;
```

### Clear All Data (Keep Structure)
```sql
TRUNCATE TABLE attendance CASCADE;
TRUNCATE TABLE anomalies CASCADE;
TRUNCATE TABLE attendance_sessions CASCADE;
TRUNCATE TABLE students CASCADE;
```

---

## Security Notes

### Row Level Security (RLS)
Currently disabled for development. To enable in production:

```sql
ALTER TABLE students ENABLE ROW LEVEL SECURITY;
ALTER TABLE attendance ENABLE ROW LEVEL SECURITY;
ALTER TABLE anomalies ENABLE ROW LEVEL SECURITY;

-- Add policies as needed
```

### API Keys
- Never commit `.env` file
- Use environment variables in production
- Rotate Supabase keys regularly

---

## Need Help?

1. Check backend logs for errors
2. Check Supabase logs in dashboard
3. Verify all tables exist in SQL Editor
4. Make sure `.env` has correct credentials
5. Restart both frontend and backend servers

---

## Files Reference

- `backend/FRESH_DATABASE_SETUP.sql` - Complete fresh setup (drops existing tables)
- `backend/app/db/schema.sql` - Schema with IF NOT EXISTS (safe for updates)
- `backend/migration_add_face_images.sql` - Add face_image_base64 column only
- `backend/.env` - Database credentials and settings
