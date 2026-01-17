# 🚀 ISAVS 2026 - Dual Portal Quick Start

## One-Click Launch

### Windows
```bash
# Start everything at once
start_dual_portals.bat

# Or start individually
start_backend.bat          # Port 6000
start_teacher_dashboard.bat # Port 2000
start_student_kiosk.bat     # Port 2001
```

### Manual Start
```bash
# Terminal 1: Backend
cd backend
python -m uvicorn app.main:app --reload --port 6000

# Terminal 2: Teacher Dashboard
cd frontend
npm run dev:teacher

# Terminal 3: Student Kiosk
cd frontend
npm run dev:student
```

---

## 🎯 Access Points

| Service | URL | Purpose |
|---------|-----|---------|
| **Backend API** | http://localhost:6000 | FastAPI server |
| **Teacher Dashboard** | http://localhost:2000 | Session management & monitoring |
| **Student Kiosk** | http://localhost:2001 | Attendance verification |
| **API Docs** | http://localhost:6000/docs | Swagger UI |

---

## 📋 Test Flow (5 Minutes)

### Step 1: Enroll a Student (Backend)
```bash
# Use Swagger UI at http://localhost:6000/docs
# POST /api/v1/enroll
{
  "name": "John Doe",
  "student_id_card_number": "STU001",
  "face_image": "base64_image_here"
}
```

### Step 2: Teacher Dashboard (Port 2000)
1. Open http://localhost:2000
2. Click "Start Session" in sidebar
3. Enter Class ID: `CS101`
4. Click "🚀 Start Session & Generate OTPs"
5. **Copy the Session ID** (long UUID)
6. Switch to "Overview" tab to watch live updates

### Step 3: Student Kiosk (Port 2001)
1. Open http://localhost:2001
2. **Paste Session ID** from teacher
3. Enter Student ID: `STU001`
4. Click "Continue →"
5. **Allow GPS** when prompted
6. Enter the **4-digit OTP** shown on screen
7. **Align face** with camera
8. Click "✓ Verify Attendance"
9. See success screen!

### Step 4: Check Teacher Dashboard
- Go back to http://localhost:2000
- See the student appear in "Recent Check-ins"
- Check stats updated in real-time

---

## 🎨 UI Features

### Teacher Dashboard (Port 2000)
```
┌─────────────────────────────────────────┐
│  SIDEBAR          │  MAIN CONTENT       │
│  ─────────        │  ─────────────      │
│  📊 Overview      │  Stats Cards        │
│  🎯 Start Session │  Recent Activity    │
│  👥 Student List  │  Live Updates       │
│  ⚠️  Anomalies    │  WebSocket Feed     │
│                   │                     │
│  Stats Summary:   │                     │
│  • Total: 50      │                     │
│  • Rate: 95%      │                     │
│  • Alerts: 2      │                     │
└─────────────────────────────────────────┘
```

### Student Kiosk (Port 2001)
```
┌─────────────────────────────────────────┐
│         ISAVS 2026 Student Kiosk        │
├─────────────────────────────────────────┤
│                                         │
│   Progress: [1] → [2] → [3] → [4]      │
│                                         │
│   ┌───────────────────────────────┐    │
│   │                               │    │
│   │   Current Step Content        │    │
│   │   (Session ID / GPS / OTP /   │    │
│   │    Face Scan)                 │    │
│   │                               │    │
│   └───────────────────────────────┘    │
│                                         │
│   [Large Action Button]                │
│                                         │
└─────────────────────────────────────────┘
```

---

## 🔐 Security Features

### Automatic Checks
- ✅ **GPS Geofencing**: Must be within 50m
- ✅ **OTP Validation**: 60-second expiry
- ✅ **Face Matching**: 0.6 cosine similarity threshold
- ✅ **Proxy Detection**: OTP valid + Face mismatch = LOCK
- ✅ **Account Locking**: 3 strikes or proxy attempt

### Real-time Alerts
- 🚨 **Red Alert**: Proxy attempt detected
- ⚠️ **Amber Alert**: Identity mismatch
- ✅ **Green**: Successful verification

---

## 📊 WebSocket Messages

Teacher Dashboard receives:
```json
{
  "type": "attendance_update",
  "data": {
    "student_name": "John Doe",
    "student_id": "STU001",
    "status": "verified",
    "confidence": 0.87,
    "timestamp": "2026-01-17T10:30:00Z"
  }
}
```

```json
{
  "type": "anomaly_alert",
  "data": {
    "student_name": "Jane Smith",
    "reason": "PROXY ATTEMPT DETECTED",
    "anomaly_type": "proxy_attempt",
    "timestamp": "2026-01-17T10:31:00Z"
  }
}
```

---

## 🛠️ Troubleshooting

### Backend Not Starting
```bash
# Check if port 6000 is in use
netstat -ano | findstr :6000

# Install dependencies
cd backend
pip install -r requirements.txt
```

### Frontend Build Errors
```bash
cd frontend
npm install
npm run dev:teacher  # or dev:student
```

### WebSocket Not Connecting
- Ensure backend is running on port 6000
- Check browser console for errors
- Verify CORS settings in backend config

### GPS Not Working
- Enable location services in browser
- Grant permission when prompted
- Check browser console for geolocation errors

### Face Not Detected
- Ensure good lighting
- Face camera directly
- Check webcam permissions
- Try different browser

---

## 📝 Configuration

### Backend (.env)
```env
DATABASE_URL=postgresql://...
CORS_ORIGINS=http://localhost:2000,http://localhost:2001
CLASSROOM_LATITUDE=37.7749
CLASSROOM_LONGITUDE=-122.4194
GEOFENCE_RADIUS_METERS=50.0
OTP_TTL_SECONDS=60
FACE_SIMILARITY_THRESHOLD=0.6
```

### Frontend (vite.config.ts)
```typescript
// Port 2000: Teacher Dashboard
// Port 2001: Student Kiosk
// Port 6000: Backend API
```

---

## 🎯 Key Endpoints

### Session Management
```bash
# Start session
POST /api/v1/session/start/CS101

# Get student OTP
GET /api/v1/session/{session_id}/otp/STU001
```

### Verification
```bash
# Verify attendance (single transaction)
POST /api/v1/verify
{
  "student_id": "STU001",
  "otp": "1234",
  "face_image": "base64...",
  "session_id": "uuid",
  "latitude": 37.7749,
  "longitude": -122.4194
}
```

### Reports
```bash
# Get attendance reports
GET /api/v1/reports

# Get anomalies
GET /api/v1/reports/anomalies
```

---

## ✅ System Checklist

Before testing:
- [ ] Backend running on port 6000
- [ ] Teacher dashboard on port 2000
- [ ] Student kiosk on port 2001
- [ ] At least one student enrolled
- [ ] Webcam permissions granted
- [ ] Location services enabled
- [ ] Database connected

---

## 🎉 Success Indicators

### Teacher Dashboard
- ✅ Sidebar navigation works
- ✅ Session starts successfully
- ✅ Session ID displayed
- ✅ Stats cards show data
- ✅ WebSocket status: "Live"

### Student Kiosk
- ✅ Session ID accepted
- ✅ GPS check passes
- ✅ OTP displayed
- ✅ Face detected
- ✅ Verification succeeds

### Backend
- ✅ Health check: http://localhost:6000/health
- ✅ API docs: http://localhost:6000/docs
- ✅ WebSocket connected
- ✅ Database queries working

---

## 📞 Support

**Check Logs:**
- Backend: Terminal running uvicorn
- Frontend: Browser console (F12)
- WebSocket: Network tab → WS

**Common Issues:**
1. Port already in use → Kill process or change port
2. CORS error → Check backend CORS_ORIGINS
3. Face not detected → Check lighting and camera
4. GPS failed → Enable location services

---

## 🚀 Ready to Go!

Your ISAVS 2026 Dual Portal System is ready for action!

**Quick Test:**
1. Run `start_dual_portals.bat`
2. Open both portals in separate browser windows
3. Start a session from teacher dashboard
4. Verify attendance from student kiosk
5. Watch real-time updates!

**Production Deployment:**
- See `DUAL_PORTAL_SYSTEM_GUIDE.md` for full details
- Build with `npm run build:teacher` and `npm run build:student`
- Deploy to separate domains
- Update CORS origins

---

**Built with ❤️ for ISAVS 2026**
