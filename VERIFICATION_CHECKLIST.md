# ✅ ISAVS 2026 - Verification Checklist

Use this checklist to verify that all components of the upgraded system are working correctly.

---

## 📦 Pre-Flight Checks

### Dependencies Installed
- [ ] Backend: `pip install -r requirements.txt` completed successfully
- [ ] Frontend: `npm install` completed successfully
- [ ] No error messages during installation

### MediaPipe Model Downloaded
- [ ] File `backend/face_landmarker.task` exists
- [ ] File size: ~10MB
- [ ] Downloaded from: https://storage.googleapis.com/mediapipe-models/face_landmarker/face_landmarker/float16/1/face_landmarker.task

### Environment Configuration
- [ ] `backend/.env` file exists
- [ ] `DATABASE_URL` is set (Supabase connection string)
- [ ] `SUPABASE_URL` is set
- [ ] `SUPABASE_ANON_KEY` is set
- [ ] `SUPABASE_SERVICE_KEY` is set
- [ ] `CLASSROOM_LATITUDE` is set (your classroom coordinates)
- [ ] `CLASSROOM_LONGITUDE` is set (your classroom coordinates)
- [ ] `OTP_TTL_SECONDS=60`
- [ ] `FACE_SIMILARITY_THRESHOLD=0.6`
- [ ] `GEOFENCE_RADIUS_METERS=50.0`

---

## 🚀 System Startup

### Backend
- [ ] Run: `cd backend && uvicorn app.main:app --reload --port 8000`
- [ ] No error messages in console
- [ ] See: "✓ FacePreprocessor initialized with MediaPipe Tasks API + CLAHE"
- [ ] API accessible at: http://localhost:8000
- [ ] Health check: http://localhost:8000/health returns `{"status":"healthy"}`
- [ ] API docs: http://localhost:8000/docs loads successfully

### Frontend
- [ ] Run: `cd frontend && npm run dev`
- [ ] No error messages in console
- [ ] App accessible at: http://localhost:5173
- [ ] Home page loads correctly

---

## 🧪 Functional Testing

### 1. Enrollment Test

#### Navigate to Enrollment
- [ ] Go to: http://localhost:5173/enroll
- [ ] Page loads without errors
- [ ] Camera permission requested
- [ ] Camera feed visible

#### Enroll Test Student
- [ ] Enter name: "Test Student"
- [ ] Enter student ID: "TEST001"
- [ ] Take clear photo (good lighting, face centered)
- [ ] Click "Enroll Student"
- [ ] Success message appears
- [ ] Check console: "✓ Added student X to FAISS index"

#### Verify Enrollment in Database
- [ ] Open Supabase dashboard
- [ ] Go to Table Editor > students
- [ ] Find "Test Student" with ID "TEST001"
- [ ] Check `facial_embedding` column has 128 values
- [ ] Check `face_image_base64` column has image data (if column exists)

#### Test Deduplication
- [ ] Try enrolling same person again with different ID
- [ ] Should see error: "Identity already exists"
- [ ] Similarity score should be > 0.90

---

### 2. Session Management Test

#### Start Session
- [ ] Go to: http://localhost:5173/faculty
- [ ] Click "Start Session" tab
- [ ] Enter class ID: "TEST_CLASS"
- [ ] Click "Start Session & Generate OTPs"
- [ ] Success message appears
- [ ] Session ID displayed (UUID format)
- [ ] OTP count shown (number of enrolled students)
- [ ] Copy session ID button works

#### Verify Session in Database
- [ ] Open Supabase dashboard
- [ ] Go to Table Editor > attendance_sessions
- [ ] Find session with matching session_id
- [ ] Check status = 'active'
- [ ] Check expires_at is ~60 seconds in future

---

### 3. OTP Generation Test

#### Get Student OTP
- [ ] Open: http://localhost:8000/api/v1/session/{session_id}/otp/TEST001
- [ ] Replace {session_id} with actual session ID
- [ ] Response shows:
  - [ ] `otp`: 4-digit number
  - [ ] `remaining_seconds`: ~60
  - [ ] `student_id`: "TEST001"
  - [ ] `student_name`: "Test Student"

#### Verify OTP in Redis/Cache
- [ ] Check backend console for OTP generation logs
- [ ] OTP should be unique per student
- [ ] OTP should expire after 60 seconds

---

### 4. Verification Test (Full Flow)

#### Navigate to Kiosk
- [ ] Go to: http://localhost:5173/kiosk/{session_id}
- [ ] Replace {session_id} with actual session ID
- [ ] Page loads without errors

#### Step 1: Enter Student ID
- [ ] Enter: "TEST001"
- [ ] Click "Continue"
- [ ] OTP displayed on screen (4 digits)
- [ ] Student name shown: "Test Student"
- [ ] 60-second countdown timer starts
- [ ] Timer color: Green (>20s), Amber (11-20s), Red (≤10s)

#### Step 2: Enter OTP
- [ ] Enter the 4-digit OTP shown
- [ ] Countdown timer continues
- [ ] Geolocation permission requested
- [ ] Allow geolocation access
- [ ] See: "✓ Location verified" (or warning if denied)
- [ ] Automatically proceeds to face scan

#### Step 3: Face Scan
- [ ] Camera feed visible
- [ ] Green bounding box appears when face detected
- [ ] Smiley face icon turns green when face detected
- [ ] "Face Detected - Ready to Verify" message shown
- [ ] Click "Verify Attendance"

#### Step 4: Verification Result
- [ ] Success screen appears
- [ ] Green checkmark icon
- [ ] "Attendance Marked!" message
- [ ] Face confidence percentage shown (should be ≥ 60%)
- [ ] Distance from classroom shown (if geolocation enabled)

#### Verify Attendance in Database
- [ ] Open Supabase dashboard
- [ ] Go to Table Editor > attendance
- [ ] Find record for TEST001
- [ ] Check `verification_status` = 'verified'
- [ ] Check `face_confidence` ≥ 0.6
- [ ] Check `otp_verified` = true
- [ ] Check `timestamp` is recent

---

### 5. Geofencing Test

#### Test Within Geofence
- [ ] Set `CLASSROOM_LATITUDE` and `CLASSROOM_LONGITUDE` to your current location
- [ ] Restart backend
- [ ] Complete verification flow
- [ ] Should succeed with distance shown

#### Test Outside Geofence
- [ ] Set `CLASSROOM_LATITUDE` and `CLASSROOM_LONGITUDE` to distant location
- [ ] Restart backend
- [ ] Complete verification flow
- [ ] Should fail with: "Location verification failed. You are Xm from classroom (max 50m)"

---

### 6. Security Tests

#### Test Proxy Attempt
- [ ] Enroll two different students (STUDENT_A and STUDENT_B)
- [ ] Start new session
- [ ] Get OTP for STUDENT_A
- [ ] Try to verify with STUDENT_A's OTP but STUDENT_B's face
- [ ] Should see: "SECURITY ALERT: Proxy attempt detected. Account locked for 60 minutes."
- [ ] Try to verify STUDENT_A again
- [ ] Should see: "Account locked due to security violation. Try again in X minutes."

#### Verify Proxy Attempt in Database
- [ ] Open Supabase dashboard
- [ ] Go to Table Editor > anomalies
- [ ] Find record with `anomaly_type` = 'proxy_attempt'
- [ ] Check `reason` contains "PROXY ATTEMPT DETECTED"
- [ ] Check `face_confidence` < 0.6

#### Test Account Unlock
- [ ] Wait 60 minutes (or clear Redis cache)
- [ ] Try to verify STUDENT_A again
- [ ] Should work normally

---

### 7. OTP Expiry Test

#### Test OTP Timeout
- [ ] Start new session
- [ ] Get OTP for student
- [ ] Enter student ID in kiosk
- [ ] Wait for 60-second countdown to reach 0
- [ ] Timer should turn red
- [ ] "⚠️ OTP Expired" message shown
- [ ] Try to proceed to face scan
- [ ] Should fail with "OTP has expired"

#### Test OTP Resend
- [ ] After OTP expires, click "Resend OTP"
- [ ] New OTP generated
- [ ] Countdown timer resets to 60 seconds
- [ ] "X resend(s) remaining" shown
- [ ] After 2 resends, "No resend attempts remaining" shown

---

### 8. Face Recognition Accuracy Test

#### Test with Same Person
- [ ] Enroll student with clear photo
- [ ] Verify with same person
- [ ] Face confidence should be ≥ 0.70 (high confidence)

#### Test with Different Lighting
- [ ] Enroll in good lighting
- [ ] Verify in dim lighting
- [ ] CLAHE preprocessing should handle it
- [ ] Face confidence should still be ≥ 0.60

#### Test with Different Angle
- [ ] Enroll with frontal face
- [ ] Verify with slight angle (±15°)
- [ ] Face alignment should handle it
- [ ] Face confidence should be ≥ 0.60

#### Test with Different Person
- [ ] Enroll STUDENT_A
- [ ] Try to verify with STUDENT_B's face
- [ ] Face confidence should be < 0.60
- [ ] Verification should fail

---

### 9. Performance Test

#### Measure Verification Time
- [ ] Open browser DevTools > Network tab
- [ ] Complete verification flow
- [ ] Check `/api/v1/verify` request time
- [ ] Should be < 500ms

#### Check Console Logs
- [ ] Backend console shows timing logs
- [ ] Preprocessing: ~50ms
- [ ] Embedding extraction: ~200ms
- [ ] Cosine similarity: <1ms
- [ ] Total: ~250ms

---

### 10. Dashboard Test

#### Faculty Dashboard
- [ ] Go to: http://localhost:5173/faculty
- [ ] "Overview" tab shows:
  - [ ] Total Students count
  - [ ] Attendance Rate percentage
  - [ ] Verified Today count
  - [ ] Alerts count
- [ ] Weekly attendance graph displays
- [ ] Recent activity list shows verified students
- [ ] Calendar view shows session markers

#### Real-time Updates
- [ ] Keep dashboard open
- [ ] Verify attendance in another tab
- [ ] Dashboard updates within 10 seconds
- [ ] New attendance record appears in "Recent Activity"
- [ ] Statistics update automatically

---

## 🔍 Edge Cases

### Empty Database
- [ ] Start with no enrolled students
- [ ] Try to start session
- [ ] Should succeed with 0 OTPs generated
- [ ] Try to verify
- [ ] Should fail with "Student not found"

### Invalid Image Format
- [ ] Try to enroll with corrupted image
- [ ] Should fail with "Invalid image format"

### No Face in Image
- [ ] Try to enroll with image of object (not face)
- [ ] Should fail with "No face detected"

### Poor Image Quality
- [ ] Try to enroll with blurry image
- [ ] Should fail with "Image too blurry"
- [ ] Try with very dark image
- [ ] Should fail with "Image too dark"

### Invalid Session ID
- [ ] Try to access kiosk with fake session ID
- [ ] Should fail gracefully

### Expired Session
- [ ] Start session
- [ ] Wait for session to expire (check `expires_at`)
- [ ] Try to verify
- [ ] Should handle gracefully

---

## 📊 Final Verification

### All Systems Green
- [ ] Backend running without errors
- [ ] Frontend running without errors
- [ ] Database connected
- [ ] Redis/Cache working (if enabled)
- [ ] MediaPipe model loaded
- [ ] CLAHE preprocessing working
- [ ] Face recognition working (128-d embeddings)
- [ ] Cosine similarity working (0.6 threshold)
- [ ] OTP generation working (60s validity)
- [ ] Geofencing working (50m radius)
- [ ] Proxy detection working
- [ ] Account locking working
- [ ] Dashboard updates working

### Performance Metrics
- [ ] Verification time < 500ms
- [ ] Face confidence ≥ 0.60 for same person
- [ ] Face confidence < 0.60 for different person
- [ ] Deduplication threshold = 0.90
- [ ] OTP expires after 60 seconds
- [ ] Geofence radius = 50 meters

### Security Checks
- [ ] Proxy attempts detected and logged
- [ ] Accounts locked for 60 minutes after proxy attempt
- [ ] Only embeddings stored (no raw images)
- [ ] Anomalies logged in database
- [ ] Deduplication prevents duplicate enrollments

---

## 🎉 Completion

If all items are checked, your ISAVS 2026 system is **fully operational** and ready for production deployment!

### Next Steps
1. **Deploy to Production**
   - Follow deployment checklist in `ISAVS_2026_UPGRADE_GUIDE.md`
   - Set up monitoring and backups

2. **Train Users**
   - Show faculty how to start sessions
   - Show students how to verify attendance
   - Explain geofencing requirements

3. **Monitor System**
   - Track attendance rates
   - Monitor proxy attempts
   - Review anomaly logs
   - Check performance metrics

---

**Congratulations! Your system is ready! 🚀**
