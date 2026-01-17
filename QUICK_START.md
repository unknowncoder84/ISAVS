# 🚀 Quick Start Guide - ISAVS

## 3 Steps to Get Running

### Step 1: Setup Database (2 minutes)

1. Open https://supabase.com/dashboard
2. Select project: `textjheeqfwmrzjtfdyo`
3. Click **SQL Editor** → **New Query**
4. Copy entire content of `backend/FRESH_DATABASE_SETUP.sql`
5. Paste and click **Run**
6. ✅ Done! All tables created

### Step 2: Verify Servers (30 seconds)

Both servers should already be running:
- ✅ Backend: http://127.0.0.1:8000
- ✅ Frontend: http://localhost:3000

If not running:
```bash
# Terminal 1 - Backend
cd backend
uvicorn app.main:app --reload --port 8000

# Terminal 2 - Frontend
cd frontend
npm run dev
```

### Step 3: Test the System (2 minutes)

#### A. Enroll Yourself
1. Go to http://localhost:3000
2. Click **"Enroll Student"**
3. Enter your name
4. Enter Student ID: `STU001`
5. Click **"Capture Photo"** (good lighting!)
6. Click **"Enroll"**
7. ✅ Success! You're enrolled

#### B. Mark Attendance
1. Go to **Dashboard**
2. Click **"Session"** tab
3. Enter Class ID: `CS101`
4. Click **"Start Session"**
5. Copy the **full Session ID** (long UUID)
6. Open new tab: http://localhost:3000/kiosk
7. Paste Session ID
8. Click **"Get OTP"**
9. Enter your Student ID: `STU001`
10. Enter the OTP shown
11. Click **"Verify with Face"**
12. Capture your face
13. ✅ Attendance marked!

#### C. Check Dashboard
1. Go back to Dashboard
2. Click **"Attendance"** tab
3. See your attendance record
4. Click **"Students"** tab
5. See your photo and details

---

## 🎯 That's It!

Your system is now fully working with:
- ✅ Face recognition
- ✅ OTP verification
- ✅ Account locking on proxy attempts
- ✅ Real-time dashboard
- ✅ Photo storage

---

## 🔧 Quick Troubleshooting

### "Could not find column" error
→ Run the database setup SQL again

### Face not recognized
→ Re-enroll with better lighting, face centered

### Account locked
→ Dashboard → Students → Click "Unlock"

### Session not found
→ Use the FULL session ID (UUID), not truncated

---

## 📚 More Help

- `COMPLETE_SYSTEM_CHECKLIST.md` - Full feature list
- `DATABASE_SETUP_GUIDE.md` - Database details
- `FACE_RECOGNITION_UPDATE.md` - Face recognition info
- `SETUP_GUIDE.md` - Detailed setup

---

## 🎉 Enjoy Your Smart Attendance System!

Everything is working and ready to use. Have fun testing!
