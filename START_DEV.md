# 🚀 Quick Start - Development Mode

## Start Both Servers (2 Commands)

### Terminal 1: Start Backend
```bash
cd backend
uvicorn app.main:app --reload --port 8000
```

### Terminal 2: Start Frontend
```bash
cd frontend
npm run dev
```

## Access Application

- **Frontend**: http://localhost:3001
- **Backend API**: http://localhost:8000
- **API Docs**: http://localhost:8000/docs

## What You'll See

1. **Home Page** - Choose your portal (Student/Teacher/Admin)
2. **Login Pages** - Separate beautiful login for each role
3. **Dashboards** - Role-specific dashboards after login

## First Time Setup

If this is your first time running:

1. **Enable Google OAuth** (2 min)
   - Follow `QUICK_FIX_OAUTH.md`

2. **Run Database Migration** (1 min)
   - Follow `START_HERE_NOW.md`

3. **Create Admin User** (30 sec)
   - Run SQL in Supabase

4. **Add JWT Secret** (30 sec)
   - Add to `backend/.env`

**Total setup: 4 minutes**

Then just start the servers and go to http://localhost:3001! 🎉
