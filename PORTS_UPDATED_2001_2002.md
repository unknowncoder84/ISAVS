# ✅ ISAVS 2026 - Ports Updated & Running!

## 🚀 System Status: LIVE

All services are running with the new port configuration:

### Port Configuration
- **Backend API**: Port 6000 ✅
- **Teacher Dashboard**: Port 2001 ✅ (Changed from 2000)
- **Student Kiosk**: Port 2002 ✅ (Changed from 2001)

---

## 🌐 Access URLs

| Service | URL | Purpose |
|---------|-----|---------|
| **Backend API** | http://localhost:6000 | FastAPI server |
| **Teacher Dashboard** | http://localhost:2001 | Session management & monitoring |
| **Student Kiosk** | http://localhost:2002 | Attendance verification |
| **API Docs** | http://localhost:6000/docs | Swagger UI |

---

## 🎯 Complete Test Flow (5 Minutes)

### Step 1: Open Both Portals
Open two browser windows/tabs:
- **Window 1**: http://localhost:2001 (Teacher Dashboard)
- **Window 2**: http://localhost:2002 (Student Kiosk)

### Step 2: Teacher Creates Session (Port 2001)
1. In Teacher Dashboard (http://localhost:2001)
2. Click **"Start Session"** in the sidebar
3. Enter Class ID: `CS101`
4. Click **"🚀 Start Session & Generate OTPs"**
5. **Copy the Session ID** (long UUID string like: a1b2c3d4-e5f6-7890-abcd-ef1234567890)
6. Keep this window open to watch real-time updates

### Step 3: Student Verifies (Port 2002)
1. In Student Kiosk (http://localhost:2002)
2. **Paste the Session ID** from teacher
3. Enter Student ID: `STU001` (or any enrolled student)
4. Click **"Continue →"**

5. **GPS Check** (Step 2)
   - Allow location access when prompted
   - System checks if within 50m of classroom
   - If successful, automatically proceeds to OTP

6. **OTP Entry** (Step 3)
   - You'll see the 4-digit OTP displayed on screen (demo mode)
   - Enter the OTP: `1234` (or whatever is shown)
   - Automatically proceeds to face scan

7. **Face Scan** (Step 4)
   - Allow camera access when prompted
   - Align your face with the camera
   - Wait for "Face Detected" indicator
   - Click **"✓ Verify Attendance"**

8. **Result**
   - See success/failure screen
   - View face confidence score
   - See distance from classroom

### Step 4: Watch Real-time Update (Port 2001)
1. Go back to Teacher Dashboard (http://localhost:2001)
2. Click **"Overview"** in sidebar
3. See the student appear in **"Recent Check-ins"**
4. Watch stats update automatically:
   - Verified Today: increases
   - Attendance Rate: updates
5. Check **"Anomalies"** tab for any security alerts

---

## 🔄 WebSocket Real-time Updates

The Teacher Dashboard receives instant updates via WebSocket:
- Student check-ins appear immediately
- No manual refresh needed
- Anomaly alerts show in real-time
- Stats update automatically

**WebSocket URL**: `ws://localhost:6000/ws/dashboard`

---

## 🔐 Security Features in Action

### Multi-Factor Verification
Each verification checks:
1. ✅ **Student ID** - Exists in database
2. ✅ **OTP** - Valid 4-digit code (60-second expiry)
3. ✅ **GPS** - Within 50 meters of classroom
4. ✅ **Face Recognition** - 0.6 cosine similarity threshold
5. ✅ **Liveness** - Optional smile detection

### Proxy Detection
If someone tries to use another person's OTP:
- OTP valid ✅ + Face mismatch ❌ = **PROXY ATTEMPT**
- Account locked for 60 minutes
- Red alert in Teacher Dashboard
- Anomaly report created

---

## 📊 What to Look For

### Teacher Dashboard (Port 2001)
- ✅ Sidebar with 4 tabs visible
- ✅ "Start Session" button works
- ✅ Session ID can be copied
- ✅ Stats cards show numbers
- ✅ WebSocket indicator shows "Live"
- ✅ Recent check-ins update in real-time
- ✅ Anomalies color-coded (red/amber)

### Student Kiosk (Port 2002)
- ✅ Progress indicator shows 4 steps
- ✅ Session ID input accepts UUID
- ✅ GPS check shows distance
- ✅ OTP displayed (demo mode)
- ✅ Webcam preview visible
- ✅ Face detection indicator works
- ✅ Result screen shows details

---

## 🎨 UI Features

### Teacher Dashboard Design
- **Sidebar Navigation**: Professional left sidebar
- **Color Scheme**: Indigo/Purple gradient
- **Real-time**: WebSocket status indicator
- **Stats Cards**: Total Students, Attendance Rate, Alerts
- **Live Feed**: Recent check-ins with confidence scores

### Student Kiosk Design
- **Mobile-First**: Large touch-friendly buttons
- **Color Scheme**: Purple/Pink gradient
- **Progress**: Visual step indicator (1→2→3→4)
- **Clear Feedback**: Large icons and status messages
- **Responsive**: Works on desktop, tablet, mobile

---

## 🛠️ Troubleshooting

### If Teacher Dashboard Won't Load (Port 2001)
```bash
# Check if port is in use
netstat -ano | findstr :2001

# Restart teacher dashboard
cd frontend
npm run dev:teacher
```

### If Student Kiosk Won't Load (Port 2002)
```bash
# Check if port is in use
netstat -ano | findstr :2002

# Restart student kiosk
cd frontend
npm run dev:student
```

### If Backend Has Issues (Port 6000)
```bash
# Check backend logs
# Look for CORS origins in output
# Should show: http://localhost:2001, http://localhost:2002

# Restart backend
cd backend
python -m uvicorn app.main:app --reload --port 6000
```

### CORS Errors
If you see CORS errors in browser console:
- Backend CORS is configured for ports 2001 and 2002
- Check backend logs show correct CORS origins
- Restart backend if needed

### WebSocket Not Connecting
- Ensure backend is running on port 6000
- Check browser console for WebSocket errors
- Look for "Live" indicator in Teacher Dashboard

---

## 📝 Quick Commands

### Start All Services
```bash
# Option 1: Use batch file
start_dual_portals.bat

# Option 2: Manual start
# Terminal 1
cd backend
python -m uvicorn app.main:app --reload --port 6000

# Terminal 2
cd frontend
npm run dev:teacher

# Terminal 3
cd frontend
npm run dev:student
```

### Stop All Services
- Close the terminal windows
- Or press Ctrl+C in each terminal

---

## ✅ Verification Checklist

Before testing:
- [ ] Backend running on port 6000
- [ ] Teacher dashboard on port 2001
- [ ] Student kiosk on port 2002
- [ ] At least one student enrolled
- [ ] Webcam permissions granted
- [ ] Location services enabled
- [ ] Database connected (Supabase)

During testing:
- [ ] Teacher can start session
- [ ] Session ID can be copied
- [ ] Student can enter session ID
- [ ] GPS check passes
- [ ] OTP is displayed
- [ ] Face is detected
- [ ] Verification succeeds
- [ ] Teacher sees real-time update

---

## 🎉 Success!

Your ISAVS 2026 Dual Portal System is now running on:
- **Teacher**: http://localhost:2001
- **Student**: http://localhost:2002
- **Backend**: http://localhost:6000

**Ready to test the complete flow!** 🚀

---

## 📚 Additional Resources

- **Complete Guide**: `DUAL_PORTAL_SYSTEM_GUIDE.md`
- **Quick Start**: `DUAL_PORTAL_QUICK_START.md`
- **Architecture**: `DUAL_PORTAL_ARCHITECTURE.md`
- **Visual Guide**: `DUAL_PORTAL_VISUAL_GUIDE.md`

---

**Updated**: January 17, 2026
**Ports**: Teacher 2001 | Student 2002 | Backend 6000
**Status**: ✅ All Services Running
