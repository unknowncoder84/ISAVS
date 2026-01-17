# 🚀 Netlify Deployment Guide - ISAVS 2026

## 📋 Overview

ISAVS has 3 components that need deployment:
1. **Teacher Dashboard** (Frontend) → Netlify
2. **Student Kiosk** (Frontend) → Netlify
3. **Backend API** → Render/Railway/Heroku (not Netlify)

**Note:** Netlify is for static sites (frontend only). The backend needs a different platform.

---

## 🎯 Quick Deployment (3 Steps)

### Step 1: Deploy Teacher Dashboard to Netlify
### Step 2: Deploy Student Kiosk to Netlify
### Step 3: Deploy Backend API to Render/Railway

---

## 📱 OPTION 1: Deploy via Netlify Dashboard (Easiest)

### A. Deploy Teacher Dashboard

**1. Login to Netlify**
- Go to: https://app.netlify.com
- Login with GitHub account

**2. Create New Site**
- Click "Add new site" → "Import an existing project"
- Choose "Deploy with GitHub"
- Select repository: `unknowncoder84/ISAVS`
- Click "Configure"

**3. Build Settings**
```
Base directory: frontend
Build command: npm run build:teacher
Publish directory: frontend/dist
```

**4. Environment Variables**
Click "Add environment variables":
```
VITE_API_URL=https://your-backend-url.com
VITE_SUPABASE_URL=your_supabase_url
VITE_SUPABASE_ANON_KEY=your_supabase_key
```

**5. Deploy**
- Click "Deploy site"
- Wait 2-3 minutes
- Your Teacher Dashboard will be live at: `https://random-name.netlify.app`

**6. Custom Domain (Optional)**
- Site settings → Domain management
- Add custom domain: `teacher.yourdomain.com`

---

### B. Deploy Student Kiosk

**Repeat the same process but with different settings:**

**Build Settings:**
```
Base directory: frontend
Build command: npm run build:student
Publish directory: frontend/dist
```

**Environment Variables:**
```
VITE_API_URL=https://your-backend-url.com
VITE_SUPABASE_URL=your_supabase_url
VITE_SUPABASE_ANON_KEY=your_supabase_key
```

**Result:**
- Student Kiosk will be live at: `https://another-random-name.netlify.app`
- Optional custom domain: `student.yourdomain.com`

---

## 💻 OPTION 2: Deploy via Netlify CLI (Advanced)

### Install Netlify CLI
```bash
npm install -g netlify-cli
```

### Login to Netlify
```bash
netlify login
```

### Deploy Teacher Dashboard
```bash
cd frontend

# Create .env.production file
echo "VITE_API_URL=https://your-backend-url.com" > .env.production
echo "VITE_SUPABASE_URL=your_supabase_url" >> .env.production
echo "VITE_SUPABASE_ANON_KEY=your_supabase_key" >> .env.production

# Build
npm run build:teacher

# Deploy
netlify deploy --prod --dir=dist --site=teacher-dashboard
```

### Deploy Student Kiosk
```bash
# Build
npm run build:student

# Deploy
netlify deploy --prod --dir=dist --site=student-kiosk
```

---

## 🔧 Backend Deployment (Required!)

**Important:** Netlify doesn't support Python backends. Use one of these:

### Option A: Deploy to Render (Recommended - Free Tier)

**1. Go to Render**
- Visit: https://render.com
- Sign up with GitHub

**2. Create New Web Service**
- Click "New +" → "Web Service"
- Connect repository: `unknowncoder84/ISAVS`
- Name: `isavs-backend`

**3. Settings**
```
Root Directory: backend
Build Command: pip install -r requirements.txt
Start Command: uvicorn app.main:app --host 0.0.0.0 --port $PORT
```

**4. Environment Variables**
```
DATABASE_URL=your_postgresql_url
SUPABASE_URL=your_supabase_url
SUPABASE_KEY=your_supabase_key
CORS_ORIGINS=https://teacher-dashboard.netlify.app,https://student-kiosk.netlify.app
```

**5. Deploy**
- Click "Create Web Service"
- Backend will be live at: `https://isavs-backend.onrender.com`

---

### Option B: Deploy to Railway (Alternative)

**1. Go to Railway**
- Visit: https://railway.app
- Sign up with GitHub

**2. New Project**
- Click "New Project" → "Deploy from GitHub repo"
- Select: `unknowncoder84/ISAVS`

**3. Settings**
```
Root Directory: backend
Start Command: uvicorn app.main:app --host 0.0.0.0 --port $PORT
```

**4. Add PostgreSQL**
- Click "New" → "Database" → "PostgreSQL"
- Railway will auto-configure DATABASE_URL

**5. Environment Variables**
Add in Variables tab:
```
SUPABASE_URL=your_supabase_url
SUPABASE_KEY=your_supabase_key
CORS_ORIGINS=https://teacher-dashboard.netlify.app,https://student-kiosk.netlify.app
```

---

## 📝 Create Netlify Configuration Files

### For Teacher Dashboard

Create `frontend/netlify-teacher.toml`:
```toml
[build]
  base = "frontend"
  command = "npm run build:teacher"
  publish = "dist"
  
[build.environment]
  NODE_VERSION = "18"

[[redirects]]
  from = "/*"
  to = "/index.html"
  status = 200

[[headers]]
  for = "/*"
  [headers.values]
    X-Frame-Options = "DENY"
    X-Content-Type-Options = "nosniff"
    X-XSS-Protection = "1; mode=block"
    Referrer-Policy = "strict-origin-when-cross-origin"
```

### For Student Kiosk

Create `frontend/netlify-student.toml`:
```toml
[build]
  base = "frontend"
  command = "npm run build:student"
  publish = "dist"
  
[build.environment]
  NODE_VERSION = "18"

[[redirects]]
  from = "/*"
  to = "/index.html"
  status = 200

[[headers]]
  for = "/*"
  [headers.values]
    X-Frame-Options = "DENY"
    X-Content-Type-Options = "nosniff"
    X-XSS-Protection = "1; mode=block"
    Referrer-Policy = "strict-origin-when-cross-origin"
```

---

## 🗄️ Database Setup

### Option 1: Supabase (Recommended - Free Tier)

**1. Create Supabase Project**
- Go to: https://supabase.com
- Create new project
- Note your project URL and anon key

**2. Run Migration**
- Go to SQL Editor in Supabase dashboard
- Copy contents of `FINAL_DATABASE_MIGRATION.sql`
- Paste and run

**3. Get Connection Details**
```
SUPABASE_URL=https://xxxxx.supabase.co
SUPABASE_ANON_KEY=your_anon_key
DATABASE_URL=postgresql://postgres:[password]@db.xxxxx.supabase.co:5432/postgres
```

---

### Option 2: Neon (Alternative - Free Tier)

**1. Create Neon Project**
- Go to: https://neon.tech
- Create new project
- Copy connection string

**2. Run Migration**
```bash
psql "your_neon_connection_string" -f FINAL_DATABASE_MIGRATION.sql
```

---

## 🔐 Environment Variables Setup

### Frontend (.env.production)
```env
VITE_API_URL=https://isavs-backend.onrender.com
VITE_SUPABASE_URL=https://xxxxx.supabase.co
VITE_SUPABASE_ANON_KEY=your_anon_key
```

### Backend (Render/Railway)
```env
DATABASE_URL=postgresql://user:pass@host:5432/dbname
SUPABASE_URL=https://xxxxx.supabase.co
SUPABASE_KEY=your_service_role_key
CORS_ORIGINS=https://teacher-dashboard.netlify.app,https://student-kiosk.netlify.app
SECRET_KEY=your_secret_key_here
```

---

## 🚀 Complete Deployment Workflow

### Step 1: Prepare Repository
```bash
cd frontend

# Create production env file
cat > .env.production << EOF
VITE_API_URL=https://your-backend-url.com
VITE_SUPABASE_URL=your_supabase_url
VITE_SUPABASE_ANON_KEY=your_supabase_key
EOF

# Test build locally
npm run build:teacher
npm run build:student
```

### Step 2: Deploy Backend First
1. Deploy to Render/Railway
2. Wait for deployment to complete
3. Note the backend URL (e.g., `https://isavs-backend.onrender.com`)
4. Run database migration

### Step 3: Deploy Teacher Dashboard
1. Go to Netlify dashboard
2. Import from GitHub
3. Set build command: `npm run build:teacher`
4. Set base directory: `frontend`
5. Add environment variables with backend URL
6. Deploy

### Step 4: Deploy Student Kiosk
1. Create another Netlify site
2. Same repository
3. Set build command: `npm run build:student`
4. Set base directory: `frontend`
5. Add environment variables with backend URL
6. Deploy

### Step 5: Update CORS
1. Go to backend deployment (Render/Railway)
2. Update `CORS_ORIGINS` environment variable with actual Netlify URLs
3. Redeploy backend

---

## ✅ Verification Checklist

### Teacher Dashboard
- [ ] Site is live on Netlify
- [ ] Can access the dashboard
- [ ] Can login with Supabase auth
- [ ] Can start attendance session
- [ ] WebSocket connection works
- [ ] API calls to backend work

### Student Kiosk
- [ ] Site is live on Netlify
- [ ] Can access the kiosk
- [ ] GPS check works
- [ ] OTP verification works
- [ ] Face scan works
- [ ] Attendance submission works

### Backend
- [ ] API is live and accessible
- [ ] Database connection works
- [ ] CORS configured correctly
- [ ] All endpoints responding
- [ ] Geofencing working

---

## 🐛 Troubleshooting

### Build Fails on Netlify
**Error:** `Command failed with exit code 1`

**Solution:**
1. Check build logs in Netlify dashboard
2. Ensure `package.json` has correct scripts
3. Verify Node version (should be 18)
4. Check for missing dependencies

### CORS Errors
**Error:** `Access to fetch blocked by CORS policy`

**Solution:**
1. Update backend `CORS_ORIGINS` with actual Netlify URLs
2. Include both HTTP and HTTPS
3. No trailing slashes
4. Redeploy backend

### Environment Variables Not Working
**Error:** `VITE_API_URL is undefined`

**Solution:**
1. Ensure variables start with `VITE_`
2. Rebuild after adding variables
3. Check Netlify dashboard → Site settings → Environment variables
4. Clear cache and redeploy

### Database Connection Fails
**Error:** `Connection refused`

**Solution:**
1. Check DATABASE_URL format
2. Ensure database allows external connections
3. Verify SSL mode (add `?sslmode=require`)
4. Check firewall rules

---

## 💰 Cost Estimate

### Free Tier (Recommended for Testing)
- **Netlify:** 2 sites free (Teacher + Student)
- **Render:** 1 free web service (Backend)
- **Supabase:** Free tier (500MB database)
- **Total:** $0/month

### Production Tier
- **Netlify Pro:** $19/month per site = $38/month
- **Render Starter:** $7/month (Backend)
- **Supabase Pro:** $25/month
- **Total:** ~$70/month

---

## 📊 Deployment URLs

After deployment, you'll have:

```
Teacher Dashboard: https://isavs-teacher.netlify.app
Student Kiosk:     https://isavs-student.netlify.app
Backend API:       https://isavs-backend.onrender.com
Database:          Supabase/Neon hosted
```

---

## 🎯 Quick Deploy Script

Create `deploy.sh`:
```bash
#!/bin/bash

echo "🚀 Deploying ISAVS to Netlify..."

# Build Teacher Dashboard
echo "📱 Building Teacher Dashboard..."
cd frontend
npm run build:teacher
netlify deploy --prod --dir=dist --site=teacher-dashboard

# Build Student Kiosk
echo "📱 Building Student Kiosk..."
npm run build:student
netlify deploy --prod --dir=dist --site=student-kiosk

echo "✅ Deployment complete!"
echo "Teacher: https://isavs-teacher.netlify.app"
echo "Student: https://isavs-student.netlify.app"
```

Make executable:
```bash
chmod +x deploy.sh
./deploy.sh
```

---

## 📚 Additional Resources

- **Netlify Docs:** https://docs.netlify.com
- **Render Docs:** https://render.com/docs
- **Railway Docs:** https://docs.railway.app
- **Supabase Docs:** https://supabase.com/docs

---

## 🎉 Summary

1. **Frontend (Netlify):** Deploy Teacher + Student portals separately
2. **Backend (Render/Railway):** Deploy Python FastAPI backend
3. **Database (Supabase/Neon):** Run migration script
4. **Configure:** Update environment variables and CORS
5. **Test:** Verify all components work together

**Ready to deploy? Start with Step 1!** 🚀
