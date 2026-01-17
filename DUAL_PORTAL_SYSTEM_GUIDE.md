# ISAVS 2026 - Dual Portal System Guide

## 🎯 System Architecture

The ISAVS 2026 system now features a **Dual Portal Architecture** with separate interfaces for teachers and students:

### Port Configuration
- **Port 2000**: Teacher Dashboard (Session Management & Monitoring)
- **Port 2001**: Student Kiosk (Verification Interface)
- **Port 6000**: Backend API (FastAPI)

---

## 🎓 Teacher Dashboard (Port 2000)

### Features
1. **Professional Sidebar Navigation**
   - Overview: Real-time stats and recent activity
   - Start Session: Generate OTPs for entire class
   - Student List: View all enrolled students
   - Anomaly Reports: Security alerts and proxy attempts

2. **Start Session Flow**
   - Enter Class ID (e.g., CS101, MATH201)
   - Click "Start Session & Generate OTPs"
   - System generates unique 4-digit OTPs for all students
   - Share Session ID with students
   - OTPs valid for 60 seconds

3. **Real-time Monitoring**
   - WebSocket connection for live updates
   - See students check in as they verify
   - Identity mismatches flagged in RED
   - Proxy attempts trigger account locks

4. **Statistics Dashboard**
   - Total Students
   - Verified Today
   - Attendance Rate
   - Proxy Alerts

### How to Start
```bash
cd frontend
npm run dev:teacher
# Opens on http://localhost:2000
```

---

## 🎒 Student Kiosk (Port 2001)

### Features
1. **Mobile-First Design**
   - Clean, large buttons for easy interaction
   - Touch-friendly interface
   - Progress indicator showing current step

2. **4-Step Verification Flow**

   **Step 1: Session & Student ID**
   - Enter Session ID (provided by teacher)
   - Enter Student ID (e.g., STU001)
   - Click Continue

   **Step 2: GPS Check**
   - Automatic location verification
   - Must be within 50 meters of classroom
   - UI locks if distance > 50m
   - Shows exact distance from classroom

   **Step 3: OTP Input**
   - Enter 4-digit OTP code
   - OTP displayed on screen (demo mode)
   - 60-second countdown timer
   - 2 resend attempts allowed

   **Step 4: Face Scan**
   - Camera opens automatically
   - CLAHE preprocessing applied
   - 128-dimensional embedding extraction
   - Cosine similarity matching (0.6 threshold)
   - Real-time face detection indicator

3. **Verification Result**
   - Success: Green checkmark with confidence score
   - Failure: Red X with detailed reason
   - Shows face match percentage
   - Displays distance from classroom

### How to Start
```bash
cd frontend
npm run dev:student
# Opens on http://localhost:2001
```

---

## 🔧 Backend Updates

### CORS Configuration
Updated to support both portals:
```python
CORS_ORIGINS: str = "http://localhost:2000,http://localhost:2001,http://localhost:3000,http://localhost:5173"
```

### WebSocket Endpoint
```
ws://localhost:6000/ws/dashboard
```

**Message Types:**
- `attendance_update`: Student checked in
- `anomaly_alert`: Security violation detected

### POST /api/v1/verify Endpoint

**Single Transaction Verification:**
- OTP validation
- Face matching (128-d embeddings, cosine similarity)
- GPS geofencing (50m radius)
- Liveness detection (optional smile-to-verify)
- Proxy detection with account locking

**Request:**
```json
{
  "student_id": "STU001",
  "otp": "1234",
  "face_image": "base64_encoded_image",
  "session_id": "uuid",
  "latitude": 37.7749,
  "longitude": -122.4194
}
```

**Response:**
```json
{
  "success": true,
  "factors": {
    "face_verified": true,
    "face_confidence": 0.87,
    "liveness_passed": true,
    "id_verified": true,
    "otp_verified": true,
    "geofence_verified": true,
    "distance_meters": 23.5
  },
  "message": "Attendance verified successfully!"
}
```

---

## 🚀 Quick Start Guide

### 1. Start Backend
```bash
cd backend
python -m uvicorn app.main:app --reload --port 6000
```

### 2. Start Teacher Dashboard
```bash
cd frontend
npm run dev:teacher
# Open http://localhost:2000
```

### 3. Start Student Kiosk
```bash
cd frontend
npm run dev:student
# Open http://localhost:2001
```

### 4. Test the Flow

**Teacher Side (Port 2000):**
1. Navigate to "Start Session" tab
2. Enter Class ID: `CS101`
3. Click "Start Session & Generate OTPs"
4. Copy the Session ID
5. Watch the "Overview" tab for real-time check-ins

**Student Side (Port 2001):**
1. Enter the Session ID from teacher
2. Enter Student ID: `STU001`
3. Allow GPS access (will auto-check)
4. Enter the 4-digit OTP shown on screen
5. Align face with camera
6. Click "Verify Attendance"
7. See result screen

---

## 🔐 Security Features

### Three-Strike Policy
- 3 consecutive failures → Account locked for 60 minutes
- Proxy attempts → Immediate lock + anomaly report

### Proxy Detection
- OTP valid + Face mismatch = PROXY ATTEMPT
- Account locked automatically
- Red alert in Teacher Dashboard
- Requires admin unlock

### Geofencing
- 50-meter radius enforcement
- Haversine distance calculation
- Real-time distance display
- UI locks if out of range

### Face Recognition
- Modern AI: face_recognition library
- 128-dimensional embeddings
- CLAHE preprocessing for lighting
- Cosine similarity (0.6 threshold)
- Quality validation before enrollment

---

## 📊 Real-time Features

### WebSocket Updates
Teacher Dashboard receives:
- Live attendance check-ins
- Anomaly alerts
- Student verification status
- Face confidence scores

### Auto-refresh
- Dashboard refreshes every 10 seconds
- WebSocket provides instant updates
- No manual refresh needed

---

## 🎨 UI/UX Highlights

### Teacher Dashboard
- Professional sidebar layout
- Dark theme with gradient accents
- Real-time stats cards
- Animated check-in list
- Color-coded anomaly reports

### Student Kiosk
- Mobile-first responsive design
- Large touch targets
- Clear progress indicators
- Visual feedback at each step
- Smooth animations

---

## 📝 Package Scripts

Add to `frontend/package.json`:
```json
{
  "scripts": {
    "dev:teacher": "vite --mode teacher",
    "dev:student": "vite --mode student",
    "build:teacher": "vite build --mode teacher",
    "build:student": "vite build --mode student"
  }
}
```

---

## 🔍 Troubleshooting

### WebSocket Connection Failed
- Ensure backend is running on port 6000
- Check CORS settings in backend config
- Verify proxy settings in vite.config.ts

### GPS Not Working
- Enable location services in browser
- Use HTTPS in production (required for geolocation)
- Check browser permissions

### Face Detection Issues
- Ensure good lighting
- Face camera directly
- Remove glasses/masks if needed
- Check webcam permissions

### OTP Expired
- Use resend feature (2 attempts)
- Teacher can restart session
- Check system time sync

---

## 🎯 Production Deployment

### Environment Variables
```env
# Backend (.env)
DATABASE_URL=postgresql://...
CORS_ORIGINS=https://teacher.isavs.com,https://student.isavs.com
CLASSROOM_LATITUDE=37.7749
CLASSROOM_LONGITUDE=-122.4194
GEOFENCE_RADIUS_METERS=50.0
```

### Build Commands
```bash
# Teacher Dashboard
cd frontend
npm run build:teacher
# Output: dist-teacher/

# Student Kiosk
npm run build:student
# Output: dist-student/
```

### Deployment
- Deploy teacher dashboard to: `teacher.isavs.com`
- Deploy student kiosk to: `student.isavs.com`
- Deploy backend to: `api.isavs.com`
- Update CORS origins accordingly

---

## 📚 API Endpoints Summary

| Endpoint | Method | Description |
|----------|--------|-------------|
| `/api/v1/session/start/{class_id}` | POST | Start session & generate OTPs |
| `/api/v1/session/{session_id}/otp/{student_id}` | GET | Get student OTP |
| `/api/v1/verify` | POST | Verify attendance (OTP + Face + GPS) |
| `/api/v1/reports` | GET | Get attendance reports |
| `/api/v1/reports/anomalies` | GET | Get anomaly reports |
| `/api/v1/students` | GET | List enrolled students |
| `/ws/dashboard` | WebSocket | Real-time updates |

---

## ✅ System Status

- ✅ Dual Portal Architecture (Ports 2000 & 2001)
- ✅ Teacher Dashboard with Sidebar
- ✅ Student Kiosk with GPS Lock
- ✅ Real-time WebSocket Updates
- ✅ Single Transaction Verification
- ✅ CLAHE Preprocessing
- ✅ 128-d Face Embeddings
- ✅ Cosine Similarity Matching
- ✅ Geofencing (50m radius)
- ✅ Proxy Detection & Account Locking
- ✅ Mobile-First Responsive Design

---

## 🎉 Ready to Use!

Your ISAVS 2026 Dual Portal System is now complete and ready for testing!

**Next Steps:**
1. Start all three services (backend, teacher, student)
2. Enroll some test students
3. Start a session from teacher dashboard
4. Verify attendance from student kiosk
5. Monitor real-time updates

**Support:**
- Check console logs for debugging
- Review anomaly reports for security issues
- Monitor WebSocket connection status
- Test GPS accuracy in different locations
