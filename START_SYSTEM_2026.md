# 🚀 ISAVS 2026 - Quick Start Guide

## Prerequisites Check

Before starting, ensure you have:

- [ ] Python 3.8+ installed
- [ ] Node.js 16+ installed
- [ ] PostgreSQL/Supabase database configured
- [ ] Redis (optional, for caching)

---

## Step 1: Download MediaPipe Model

**CRITICAL**: The system requires the MediaPipe face landmarker model.

### Option A: Using wget (Linux/Mac)
```bash
cd backend
wget https://storage.googleapis.com/mediapipe-models/face_landmarker/face_landmarker/float16/1/face_landmarker.task
```

### Option B: Using curl (Linux/Mac)
```bash
cd backend
curl -o face_landmarker.task https://storage.googleapis.com/mediapipe-models/face_landmarker/face_landmarker/float16/1/face_landmarker.task
```

### Option C: Using PowerShell (Windows)
```powershell
cd backend
Invoke-WebRequest -Uri "https://storage.googleapis.com/mediapipe-models/face_landmarker/face_landmarker/float16/1/face_landmarker.task" -OutFile "face_landmarker.task"
```

### Option D: Manual Download
1. Open: https://storage.googleapis.com/mediapipe-models/face_landmarker/face_landmarker/float16/1/face_landmarker.task
2. Save file to `backend/face_landmarker.task`

**Verify**: File should be ~10MB

---

## Step 2: Install Dependencies

### Backend
```bash
cd backend
pip install -r requirements.txt
```

**Note**: If `dlib` installation fails on Windows, install Visual C++ Build Tools first:
- Download: https://visualstudio.microsoft.com/visual-cpp-build-tools/
- Or use pre-built wheel: `pip install dlib-binary`

### Frontend
```bash
cd frontend
npm install
```

---

## Step 3: Configure Environment

### Backend Configuration

1. Copy example environment file:
```bash
cd backend
cp .env.example .env
```

2. Edit `backend/.env` and set:

```env
# Database (Supabase)
DATABASE_URL=postgresql://postgres.[project-ref]:[password]@aws-0-[region].pooler.supabase.com:6543/postgres
SUPABASE_URL=https://[project-ref].supabase.co
SUPABASE_ANON_KEY=your_anon_key_here
SUPABASE_SERVICE_KEY=your_service_key_here

# OTP Settings (2026 Standard)
OTP_TTL_SECONDS=60
OTP_MAX_RESEND_ATTEMPTS=2

# Face Recognition (Cosine Similarity)
FACE_SIMILARITY_THRESHOLD=0.6

# Geofencing (IMPORTANT: Set your classroom coordinates!)
GEOFENCE_RADIUS_METERS=50.0
CLASSROOM_LATITUDE=14.5995    # Replace with your classroom latitude
CLASSROOM_LONGITUDE=120.9842  # Replace with your classroom longitude

# Redis Cache (optional)
REDIS_URL=redis://localhost:6379/0
USE_REDIS=false

# CORS
CORS_ORIGINS=http://localhost:3000,http://localhost:5173
```

**Get your classroom coordinates**: https://www.latlong.net/

### Frontend Configuration

1. Copy example environment file:
```bash
cd frontend
cp .env.example .env
```

2. Edit `frontend/.env`:
```env
VITE_API_URL=http://localhost:8000
```

---

## Step 4: Test the System

Run the test script to verify everything is working:

```bash
cd backend
python test_2026_upgrade.py
```

**Expected output:**
```
🧪 Testing imports...
✅ ai_service imported successfully
✅ preprocess imported successfully
✅ geofence_service imported successfully
✅ otp_service imported successfully
✅ endpoints imported successfully

🧪 Testing AI service...
✅ AI service initialized
✅ Cosine similarity test: 0.xxxx
✅ Identical embeddings similarity: 1.0000

🧪 Testing geofence service...
✅ Geofence service initialized
✅ Distance calculation: 10000m (~10km expected)
✅ Same location geofence: within=True, distance=0.00m
✅ Different location geofence: within=False, distance=10000m

🧪 Testing configuration...
✅ OTP_TTL_SECONDS: 60
✅ FACE_SIMILARITY_THRESHOLD: 0.6
✅ GEOFENCE_RADIUS_METERS: 50.0
✅ OTP TTL is 60 seconds (2026 standard)
✅ Face threshold is 0.6 (2026 standard)
✅ Geofence radius is 50m (2026 standard)

🧪 Testing preprocessor...
✅ MediaPipe model found at: backend/face_landmarker.task
✅ Preprocessor initialized with MediaPipe Tasks API + CLAHE

Results: 5/5 tests passed
🎉 All tests passed! System is ready.
```

---

## Step 5: Start the System

### Terminal 1: Start Backend
```bash
cd backend
uvicorn app.main:app --reload --port 8000
```

**Expected output:**
```
INFO:     Uvicorn running on http://127.0.0.1:8000
INFO:     Application startup complete.
✓ FacePreprocessor initialized with MediaPipe Tasks API + CLAHE
```

**Verify**: Open http://localhost:8000/health
Should return: `{"status":"healthy","service":"ISAVS"}`

**API Docs**: http://localhost:8000/docs

### Terminal 2: Start Frontend
```bash
cd frontend
npm run dev
```

**Expected output:**
```
VITE v4.x.x  ready in xxx ms

➜  Local:   http://localhost:5173/
➜  Network: use --host to expose
```

**Verify**: Open http://localhost:5173
Should show the ISAVS home page

---

## Step 6: Test the Full Flow

### 1. Enroll a Student

1. Go to: http://localhost:5173/enroll
2. Enter name: "Test Student"
3. Enter student ID: "TEST001"
4. Allow camera access
5. Take a clear photo (good lighting, face centered)
6. Click "Enroll Student"
7. ✅ Success message should appear

**Verify in Database**:
- Open Supabase dashboard
- Go to Table Editor > students
- Find "Test Student" with ID "TEST001"
- Check `facial_embedding` has 128 values

### 2. Start a Session

1. Go to: http://localhost:5173/faculty
2. Click "Start Session" tab
3. Enter class ID: "TEST_CLASS"
4. Click "Start Session & Generate OTPs"
5. ✅ Session ID displayed
6. Copy the session ID

### 3. Verify Attendance

1. Go to: http://localhost:5173/kiosk/{session_id}
   (Replace {session_id} with the copied session ID)
2. Enter student ID: "TEST001"
3. Click "Continue"
4. ✅ OTP displayed (4 digits)
5. ✅ 60-second countdown starts
6. Enter the OTP
7. Allow geolocation access
8. ✅ "Location verified" message
9. Scan face (align with green bounding box)
10. ✅ "Face Detected - Ready to Verify"
11. Click "Verify Attendance"
12. ✅ Success screen with green checkmark!

**Verify in Database**:
- Open Supabase dashboard
- Go to Table Editor > attendance
- Find record for TEST001
- Check `verification_status` = 'verified'
- Check `face_confidence` >= 0.6

---

## Troubleshooting

### Issue: "face_landmarker.task not found"
**Solution**: Download the model file (see Step 1)

### Issue: "ModuleNotFoundError: No module named 'dlib'"
**Solution**: 
```bash
# Windows
pip install dlib-binary

# Linux/Mac
pip install dlib
```

### Issue: "ModuleNotFoundError: No module named 'face_recognition'"
**Solution**:
```bash
pip install face-recognition
```

### Issue: "Geolocation not working"
**Solution**:
- Use HTTPS (geolocation requires secure context)
- Check browser permissions
- Set `CLASSROOM_LATITUDE` and `CLASSROOM_LONGITUDE` in `.env`

### Issue: "Face not detected"
**Solution**:
- Ensure good lighting
- Face should be centered and clearly visible
- Minimum 100x100 pixels
- Try different angle

### Issue: "Invalid embedding dimension: 2622"
**Solution**: The system is using old DeepFace code. Restart the backend to load the new AI service.

### Issue: "Connection refused" when accessing API
**Solution**: Ensure backend is running on port 8000

### Issue: "CORS error" in browser console
**Solution**: Check `CORS_ORIGINS` in `backend/.env` includes your frontend URL

---

## System Status Check

### Backend Health
```bash
curl http://localhost:8000/health
```
Should return: `{"status":"healthy","service":"ISAVS"}`

### API Documentation
Open: http://localhost:8000/docs

### Frontend
Open: http://localhost:5173

---

## Production Deployment

For production deployment, see:
- **[ISAVS_2026_UPGRADE_GUIDE.md](./ISAVS_2026_UPGRADE_GUIDE.md)** - Complete deployment guide
- **[VERIFICATION_CHECKLIST.md](./VERIFICATION_CHECKLIST.md)** - Full testing checklist

---

## Quick Commands Reference

### Backend
```bash
# Install dependencies
cd backend && pip install -r requirements.txt

# Run tests
python test_2026_upgrade.py

# Start server
uvicorn app.main:app --reload --port 8000

# Check health
curl http://localhost:8000/health
```

### Frontend
```bash
# Install dependencies
cd frontend && npm install

# Start dev server
npm run dev

# Build for production
npm run build
```

---

## System Features (2026 Standard)

✅ **Modern AI**: face_recognition library (128-d embeddings)  
✅ **CLAHE Preprocessing**: Works in uneven lighting  
✅ **MediaPipe Tasks API**: 2026-compatible landmark detection  
✅ **Cosine Similarity**: 0.6 threshold for accurate matching  
✅ **Individual OTPs**: Unique 4-digit codes per student (60s validity)  
✅ **Geofencing**: 50-meter radius validation  
✅ **Proxy Detection**: Account locking on suspicious activity  
✅ **Smooth UI**: 60-second countdown, live camera, geolocation  
✅ **Privacy-First**: Only embeddings stored, no raw images  

---

## Need Help?

- **Setup Guide**: [ISAVS_2026_UPGRADE_GUIDE.md](./ISAVS_2026_UPGRADE_GUIDE.md)
- **Quick Reference**: [QUICK_REFERENCE_2026.md](./QUICK_REFERENCE_2026.md)
- **Testing Checklist**: [VERIFICATION_CHECKLIST.md](./VERIFICATION_CHECKLIST.md)

---

**Happy Deploying! 🚀**
