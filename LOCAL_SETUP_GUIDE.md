# 🚀 Local Development Setup - ISAVS 2026

## 📋 Current Configuration

### VITE_API_URL Explained

**For Local Development:**
- **VITE_API_URL is NOT set** in `frontend/.env`
- This is intentional! Vite uses a **proxy** instead
- Frontend calls `/api/v1/...` which Vite proxies to `http://localhost:6000`

**How it works:**
```
Frontend (Port 2001/2002) → /api/v1/endpoint
                          ↓ (Vite Proxy)
Backend (Port 6000)       → http://localhost:6000/api/v1/endpoint
```

**For Production (Netlify):**
- **VITE_API_URL must be set** to your backend URL
- Example: `VITE_API_URL=https://isavs-backend.onrender.com`
- Frontend will call: `https://isavs-backend.onrender.com/api/v1/endpoint`

---

## 🔧 Environment Variables

### Frontend (`frontend/.env`)
```env
# NO VITE_API_URL needed for local dev (uses proxy)

# Supabase (already configured)
VITE_SUPABASE_URL=https://textjheeqfwmrzjtfdyo.supabase.co
VITE_SUPABASE_ANON_KEY=eyJhbGc...
```

### Backend (`backend/.env`)
```env
# Database (already configured)
DATABASE_URL=postgresql://postgres.textjheeqfwmrzjtfdyo:...

# Supabase (already configured)
SUPABASE_URL=https://textjheeqfwmrzjtfdyo.supabase.co
SUPABASE_ANON_KEY=eyJhbGc...

# CORS (already configured for local ports)
CORS_ORIGINS=http://localhost:2001,http://localhost:2002,...
```

---

## 🚀 Start the App Locally

### Option 1: Start All Services (Recommended)

**Using Batch Script:**
```bash
start_dual_portals.bat
```

This starts:
- Backend on Port 6000
- Teacher Dashboard on Port 2001
- Student Kiosk on Port 2002

---

### Option 2: Start Services Individually

**Terminal 1 - Backend:**
```bash
cd backend
python -m uvicorn app.main:app --reload --port 6000
```

**Terminal 2 - Teacher Dashboard:**
```bash
cd frontend
npm run dev:teacher
```
Opens at: http://localhost:2001

**Terminal 3 - Student Kiosk:**
```bash
cd frontend
npm run dev:student
```
Opens at: http://localhost:2002

---

## 🌐 Access URLs

### Local Development
- **Backend API:** http://localhost:6000
- **API Docs:** http://localhost:6000/docs
- **Teacher Dashboard:** http://localhost:2001
- **Student Kiosk:** http://localhost:2002

### Network Access (Mobile Testing)
- **Backend:** http://192.168.0.227:6000
- **Teacher:** http://192.168.0.227:2001
- **Student:** http://192.168.0.227:2002

*(Replace 192.168.0.227 with your actual IP)*

---

## 🔍 How Vite Proxy Works

### Vite Configuration (`frontend/vite.config.ts`)
```typescript
server: {
  port: 2001, // or 2002 for student
  proxy: {
    '/api': {
      target: 'http://localhost:6000',
      changeOrigin: true,
    },
    '/ws': {
      target: 'ws://localhost:6000',
      ws: true,
    },
  },
}
```

### Request Flow
```
1. Frontend makes request: fetch('/api/v1/sessions')
2. Vite intercepts: Sees /api prefix
3. Vite proxies to: http://localhost:6000/api/v1/sessions
4. Backend responds
5. Vite forwards response to frontend
```

**Benefits:**
- No CORS issues in development
- Same-origin requests
- Easy to switch between local and production

---

## 🌍 Production vs Development

### Development (Local)
```env
# frontend/.env
# VITE_API_URL not set (uses proxy)
```

```typescript
// API calls
fetch('/api/v1/sessions') // Proxied to localhost:6000
```

### Production (Netlify)
```env
# Netlify Environment Variables
VITE_API_URL=https://isavs-backend.onrender.com
```

```typescript
// API calls (with VITE_API_URL set)
fetch('https://isavs-backend.onrender.com/api/v1/sessions')
```

---

## 🔧 API Service Configuration

### Check API Service (`frontend/src/services/api.ts`)

The API service should use:
```typescript
const API_URL = import.meta.env.VITE_API_URL || '/api/v1';

// In development: '/api/v1' (proxied)
// In production: 'https://backend-url.com/api/v1'
```

---

## 🐛 Troubleshooting

### Issue 1: API Calls Fail
**Error:** `Failed to fetch` or `Network error`

**Check:**
1. Is backend running on port 6000?
   ```bash
   curl http://localhost:6000/docs
   ```
2. Check Vite proxy in browser DevTools → Network tab
3. Look for proxy errors in terminal

**Fix:**
- Ensure backend is running first
- Check `vite.config.ts` proxy settings
- Restart frontend dev server

---

### Issue 2: CORS Errors
**Error:** `Access to fetch blocked by CORS policy`

**This shouldn't happen in local dev** because of Vite proxy!

**If it does:**
1. Check if you accidentally set `VITE_API_URL` in `.env`
2. Remove it for local development
3. Restart dev server

---

### Issue 3: Wrong Port
**Error:** Frontend opens on wrong port

**Fix:**
```bash
# For teacher (should be 2001)
npm run dev:teacher

# For student (should be 2002)
npm run dev:student
```

Check `vite.config.ts`:
```typescript
if (isTeacher) {
  port = 2001
} else if (isStudent) {
  port = 2002
}
```

---

## 📊 Port Summary

| Service | Port | URL |
|---------|------|-----|
| Backend API | 6000 | http://localhost:6000 |
| Teacher Dashboard | 2001 | http://localhost:2001 |
| Student Kiosk | 2002 | http://localhost:2002 |

---

## 🎯 Quick Start Commands

### Start Everything
```bash
# Windows
start_dual_portals.bat

# Manual (3 terminals)
# Terminal 1
cd backend && python -m uvicorn app.main:app --reload --port 6000

# Terminal 2
cd frontend && npm run dev:teacher

# Terminal 3
cd frontend && npm run dev:student
```

### Test Backend
```bash
curl http://localhost:6000/docs
# Should open FastAPI documentation
```

### Test Frontend
```bash
# Open in browser
http://localhost:2001  # Teacher
http://localhost:2002  # Student
```

---

## 🌐 For Netlify Deployment

When deploying to Netlify, you MUST set:

```env
VITE_API_URL=https://your-backend-url.onrender.com
```

**Why?**
- Netlify serves static files (no proxy)
- Frontend needs full backend URL
- CORS must be configured on backend

**Backend CORS Update:**
```env
CORS_ORIGINS=https://teacher.netlify.app,https://student.netlify.app
```

---

## ✅ Verification Checklist

- [ ] Backend running on port 6000
- [ ] Teacher dashboard on port 2001
- [ ] Student kiosk on port 2002
- [ ] API calls work (check Network tab)
- [ ] No CORS errors
- [ ] WebSocket connection works
- [ ] GPS functionality works
- [ ] Face recognition works

---

## 📚 Related Files

- `frontend/.env` - Frontend environment variables
- `backend/.env` - Backend environment variables
- `frontend/vite.config.ts` - Vite proxy configuration
- `start_dual_portals.bat` - Start all services
- `NETLIFY_DEPLOYMENT_GUIDE.md` - Production deployment

---

## 🎉 Summary

**Local Development:**
- ✅ No `VITE_API_URL` needed
- ✅ Vite proxy handles API calls
- ✅ Backend on 6000, Frontend on 2001/2002
- ✅ No CORS issues

**Production (Netlify):**
- ✅ Set `VITE_API_URL` to backend URL
- ✅ Configure CORS on backend
- ✅ Deploy frontend to Netlify
- ✅ Deploy backend to Render/Railway

**Ready to start?** Run `start_dual_portals.bat`! 🚀
