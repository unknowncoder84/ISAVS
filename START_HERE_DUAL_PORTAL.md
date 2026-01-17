# 🚀 START HERE - ISAVS 2026 Dual Portal System

## ⚡ Quick Launch (30 Seconds)

### Windows One-Click Start
```bash
start_dual_portals.bat
```

This will automatically start:
- ✅ Backend API (Port 6000)
- ✅ Teacher Dashboard (Port 2000)
- ✅ Student Kiosk (Port 2001)

---

## 🎯 What You Get

### Two Separate Portals

**1. Teacher Dashboard (Port 2000)**
- Professional sidebar interface
- Start sessions with one click
- Real-time student check-ins
- Anomaly reports and alerts
- Live statistics

**2. Student Kiosk (Port 2001)**
- Mobile-first design
- 4-step verification flow
- GPS location check
- OTP entry
- Face scan verification

---

## 📋 5-Minute Test

### Step 1: Start Everything
```bash
start_dual_portals.bat
```

Wait for all three services to start (about 10 seconds).

### Step 2: Open Both Portals
- Teacher: http://localhost:2000
- Student: http://localhost:2001

### Step 3: Teacher Creates Session
1. Go to http://localhost:2000
2. Click "Start Session" in sidebar
3. Enter Class ID: `CS101`
4. Click "🚀 Start Session & Generate OTPs"
5. **Copy the Session ID** (long UUID string)

### Step 4: Student Verifies
1. Go to http://localhost:2001
2. **Paste the Session ID**
3. Enter Student ID: `STU001` (or any enrolled student)
4. Click "Continue →"
5. Allow GPS when prompted
6. Enter the 4-digit OTP shown on screen
7. Align face with camera
8. Click "✓ Verify Attendance"

### Step 5: See Real-time Update
1. Go back to http://localhost:2000
2. Click "Overview" in sidebar
3. See the student appear in "Recent Check-ins"
4. Watch stats update automatically

**Done! You just verified attendance with GPS + OTP + Face Recognition!** 🎉

---

## 📁 Key Files

### React Components
```
frontend/src/pages/
├── TeacherDashboard.jsx  ← Port 2000 interface
└── StudentPortal.jsx     ← Port 2001 interface
```

### Backend
```
backend/app/
├── main.py              ← FastAPI app with WebSocket
├── api/endpoints.py     ← All API routes
└── core/config.py       ← CORS for both ports
```

### Configuration
```
frontend/
├── vite.config.ts       ← Port configuration
├── teacher.html         ← Teacher entry point
├── student.html         ← Student entry point
├── package.json         ← npm scripts
```

---

## 🎨 Features Implemented

### Teacher Dashboard
✅ Professional sidebar navigation
✅ Start session & generate OTPs
✅ Real-time WebSocket updates
✅ Student list with photos
✅ Anomaly reports (proxy attempts)
✅ Live statistics dashboard
✅ Session ID copy-to-clipboard

### Student Kiosk
✅ Mobile-first responsive design
✅ 4-step verification flow
✅ GPS geofencing (50m radius)
✅ OTP input with countdown
✅ Face scan with CLAHE preprocessing
✅ Real-time face detection indicator
✅ Detailed result screen

### Backend
✅ CORS for both ports (2000 & 2001)
✅ WebSocket for real-time updates
✅ Single-transaction verification
✅ Proxy detection & account locking
✅ 128-d face embeddings
✅ Cosine similarity matching (0.6 threshold)

---

## 🔐 Security Features

### Multi-Factor Verification
1. **ID Check** - Student exists in database
2. **OTP Validation** - 4-digit code, 60-second expiry
3. **GPS Geofencing** - Within 50 meters
4. **Face Recognition** - 0.6 similarity threshold
5. **Liveness Detection** - Optional smile-to-verify

### Proxy Detection
- OTP valid + Face mismatch = **PROXY ATTEMPT**
- Account locked for 60 minutes
- Red alert in teacher dashboard
- Anomaly report created

---

## 📊 Architecture

```
Port 2000 (Teacher)  ←→  Port 6000 (Backend)  ←→  Port 2001 (Student)
                              ↓
                         Database
                         (Supabase)
```

### Communication
- **REST API** - HTTP requests for data
- **WebSocket** - Real-time updates to teacher
- **CORS** - Allows both ports to access backend

---

## 🛠️ Manual Start (If Needed)

### Terminal 1: Backend
```bash
cd backend
python -m uvicorn app.main:app --reload --port 6000
```

### Terminal 2: Teacher Dashboard
```bash
cd frontend
npm run dev:teacher
```

### Terminal 3: Student Kiosk
```bash
cd frontend
npm run dev:student
```

---

## 📚 Documentation

### Comprehensive Guides
- **DUAL_PORTAL_SYSTEM_GUIDE.md** - Complete system documentation
- **DUAL_PORTAL_QUICK_START.md** - Quick reference guide
- **DUAL_PORTAL_ARCHITECTURE.md** - Technical architecture
- **DUAL_PORTAL_IMPLEMENTATION_COMPLETE.md** - Implementation details

### API Documentation
- Swagger UI: http://localhost:6000/docs
- ReDoc: http://localhost:6000/redoc

---

## 🔍 Troubleshooting

### Backend Won't Start
```bash
# Check if port 6000 is in use
netstat -ano | findstr :6000

# Install dependencies
cd backend
pip install -r requirements.txt
```

### Frontend Won't Start
```bash
cd frontend
npm install
npm run dev:teacher  # or dev:student
```

### WebSocket Not Connecting
- Ensure backend is running on port 6000
- Check browser console for errors
- Verify CORS settings in `backend/app/core/config.py`

### GPS Not Working
- Enable location services in browser
- Grant permission when prompted
- Use HTTPS in production (required for geolocation)

### Face Not Detected
- Ensure good lighting
- Face camera directly
- Check webcam permissions
- Try different browser

---

## 🎯 What's Different from Before?

### Old System
- Single unified app on port 2000
- Mixed teacher/student interface
- No real-time updates
- Manual refresh needed

### New Dual Portal System
- ✅ Separate teacher (2000) and student (2001) portals
- ✅ Professional sidebar for teachers
- ✅ Mobile-first kiosk for students
- ✅ Real-time WebSocket updates
- ✅ GPS lock before verification
- ✅ Clear 4-step flow
- ✅ Better security with proxy detection

---

## 🚀 Production Deployment

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

### Deploy To
- Teacher: `teacher.isavs.com`
- Student: `student.isavs.com`
- Backend: `api.isavs.com`

### Update CORS
```python
# backend/app/core/config.py
CORS_ORIGINS: str = "https://teacher.isavs.com,https://student.isavs.com"
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
- ✅ Can start session
- ✅ Session ID displayed
- ✅ WebSocket shows "Live"
- ✅ Stats cards populated

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
- ✅ No CORS errors

---

## 📞 Need Help?

### Check Logs
- **Backend**: Terminal running uvicorn
- **Frontend**: Browser console (F12)
- **WebSocket**: Network tab → WS

### Common Issues
1. **Port in use** → Kill process or change port
2. **CORS error** → Check backend CORS_ORIGINS
3. **Face not detected** → Check lighting and camera
4. **GPS failed** → Enable location services
5. **WebSocket failed** → Ensure backend is running

---

## 🎯 Next Steps

### After Testing
1. Enroll more students
2. Test with multiple sessions
3. Try proxy detection (wrong face)
4. Check anomaly reports
5. Monitor real-time updates

### For Production
1. Set up production database
2. Configure classroom GPS coordinates
3. Deploy to cloud hosting
4. Set up SSL certificates
5. Update CORS origins

---

## 📖 Learn More

### Key Concepts
- **Dual Portal**: Separate interfaces for different user types
- **WebSocket**: Real-time bidirectional communication
- **Geofencing**: GPS-based location verification
- **Face Recognition**: 128-d embeddings with cosine similarity
- **Proxy Detection**: Security feature to prevent fraud

### Technologies Used
- **Frontend**: React + TypeScript + Vite
- **Backend**: FastAPI + Python
- **Database**: Supabase PostgreSQL
- **Face Recognition**: face_recognition library
- **Real-time**: WebSocket
- **Styling**: Tailwind CSS

---

## 🎊 You're Ready!

Your ISAVS 2026 Dual Portal System is **complete and ready to use**!

### Quick Start Reminder
```bash
# One command to start everything
start_dual_portals.bat

# Then open:
# Teacher: http://localhost:2000
# Student: http://localhost:2001
```

**Happy Testing!** 🚀

---

**Built with ❤️ for ISAVS 2026**
**Lead Systems Architect | January 17, 2026**
