# ISAVS Setup Guide - Database & Deployment

## 🗄️ Step 1: Setup Supabase Database

### 1.1 Go to Supabase SQL Editor
1. Open [Supabase Dashboard](https://supabase.com/dashboard)
2. Select your project: `textjheeqfwmrzjtfdyo`
3. Go to **SQL Editor** → **New Query**

### 1.2 Run the Database Schema
Copy and paste the entire content from `backend/app/db/schema.sql` and click **Run**

This creates:
- `students` - Student records with facial embeddings
- `classes` - Class definitions
- `class_enrollments` - Student-class relationships
- `attendance_sessions` - Active attendance sessions
- `attendance` - Attendance records
- `anomalies` - Proxy/fraud detection logs
- `otp_resend_tracking` - OTP resend limits
- `verification_sessions` - Three-strike tracking

### 1.3 Verify Tables Created
Go to **Table Editor** in Supabase - you should see all 8 tables listed.

---

## 🔧 Step 2: Backend Configuration

Your `.env` file is already configured:
```
DATABASE_URL=postgresql://postgres.textjheeqfwmrzjtfdyo:1903200525102005RS@aws-0-ap-south-1.pooler.supabase.com:6543/postgres
SUPABASE_URL=https://textjheeqfwmrzjtfdyo.supabase.co
```

### Start Backend
```bash
cd backend
pip install -r requirements.txt
uvicorn app.main:app --reload --host 0.0.0.0 --port 8000
```

---

## 🎨 Step 3: Frontend Setup

```bash
cd frontend
npm install
npm run dev
```

---

## 🚀 Step 4: Deployment

### Option A: Railway (Recommended)
1. Push code to GitHub
2. Connect Railway to your repo
3. Add environment variables from `.env`
4. Deploy!

### Option B: Render
1. Create Web Service for backend
2. Create Static Site for frontend
3. Configure environment variables

### Option C: Vercel + Railway
- Frontend on Vercel (free)
- Backend on Railway

---

## ✅ Verify Everything Works

1. Open frontend: http://localhost:5173
2. Go to Dashboard → Start Session
3. Enroll a student with face capture
4. Test attendance verification

---

## 🔒 Security Notes for Production

1. Change `SECRET_KEY` in `.env`
2. Enable Row Level Security in Supabase
3. Use HTTPS only
4. Restrict CORS origins
