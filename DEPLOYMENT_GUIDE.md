# 🚀 ISAVS Deployment Guide

## Overview

ISAVS consists of two parts that need to be deployed separately:
1. **Frontend** (React + Vite) → Deploy on **Netlify** (Free)
2. **Backend** (Python + FastAPI) → Deploy on **Render/Railway** (Free tier available)

---

## 📦 Part 1: Deploy Backend (Python API)

### Option A: Deploy on Render (Recommended - Free)

1. **Create Render Account**
   - Go to: https://render.com
   - Sign up with GitHub

2. **Create New Web Service**
   - Click "New +" → "Web Service"
   - Connect your GitHub repository
   - Select the `backend` folder

3. **Configure Service**
   ```
   Name: isavs-backend
   Environment: Python 3
   Build Command: pip install -r requirements.txt
   Start Command: uvicorn app.main:app --host 0.0.0.0 --port $PORT
   ```

4. **Add Environment Variables**
   Go to "Environment" tab and add all variables from `backend/.env`:
   ```
   DATABASE_URL=your-supabase-connection-string
   SUPABASE_URL=https://textjheeqfwmrzjtfdyo.supabase.co
   SUPABASE_ANON_KEY=your-anon-key
   SUPABASE_SERVICE_KEY=your-service-key
   SUPABASE_JWT_SECRET=your-jwt-secret
   SECRET_KEY=your-secret-key
   CORS_ORIGINS=https://your-netlify-site.netlify.app
   ```

5. **Deploy**
   - Click "Create Web Service"
   - Wait for deployment (5-10 minutes)
   - Copy your backend URL: `https://isavs-backend.onrender.com`

### Option B: Deploy on Railway (Alternative - Free)

1. Go to: https://railway.app
2. Sign up with GitHub
3. Click "New Project" → "Deploy from GitHub repo"
4. Select your repository
5. Add environment variables
6. Deploy!

---

## 📦 Part 2: Deploy Frontend (React)

### Deploy on Netlify (Free)

1. **Create Netlify Account**
   - Go to: https://netlify.com
   - Sign up with GitHub

2. **Connect Repository**
   - Click "Add new site" → "Import an existing project"
   - Choose GitHub
   - Select your repository
   - Set base directory: `frontend`

3. **Configure Build Settings**
   ```
   Build command: npm run build
   Publish directory: frontend/dist
   ```

4. **Add Environment Variables**
   Go to "Site settings" → "Environment variables":
   ```
   VITE_API_URL=https://your-backend-url.onrender.com/api/v1
   VITE_SUPABASE_URL=https://textjheeqfwmrzjtfdyo.supabase.co
   VITE_SUPABASE_ANON_KEY=your-anon-key
   ```

5. **Deploy**
   - Click "Deploy site"
   - Wait for build (2-3 minutes)
   - Your site will be live at: `https://your-site.netlify.app`

6. **Update Supabase Redirect URLs**
   - Go to Supabase Dashboard → Authentication → URL Configuration
   - Add your Netlify URL: `https://your-site.netlify.app/auth/callback`

---

## 🔧 Local Development Setup

### 1. Start Backend (Port 8000)
```bash
cd backend
pip install -r requirements.txt
uvicorn app.main:app --reload --port 8000
```

### 2. Start Frontend (Port 3001)
```bash
cd frontend
npm install
npm run dev
```

### 3. Access Application
- Frontend: http://localhost:3001
- Backend API: http://localhost:8000
- API Docs: http://localhost:8000/docs

---

## ✅ Post-Deployment Checklist

### Backend
- [ ] Backend deployed and running
- [ ] All environment variables added
- [ ] Database connected (Supabase)
- [ ] API accessible at `/docs` endpoint
- [ ] CORS configured for frontend URL

### Frontend
- [ ] Frontend deployed on Netlify
- [ ] Environment variables configured
- [ ] Backend API URL updated
- [ ] OAuth redirect URLs updated in Supabase
- [ ] Can access all pages (home, login, dashboards)

### Supabase
- [ ] Google OAuth enabled
- [ ] Redirect URLs updated with production URLs
- [ ] Database migration completed
- [ ] Admin user created
- [ ] JWT secret added to backend

---

## 🐛 Troubleshooting

### Backend Issues

**"Application failed to start"**
- Check all environment variables are set
- Verify Python version is 3.9+
- Check build logs for errors

**"Database connection failed"**
- Verify DATABASE_URL is correct
- Check Supabase connection string
- Ensure IP is whitelisted in Supabase

### Frontend Issues

**"API calls failing"**
- Verify VITE_API_URL points to deployed backend
- Check CORS is configured in backend
- Verify backend is running

**"OAuth not working"**
- Update redirect URLs in Supabase
- Check VITE_SUPABASE_URL is correct
- Verify Google OAuth is enabled

---

## 💰 Cost Breakdown

### Free Tier (Recommended for Testing)
- **Netlify**: Free (100GB bandwidth/month)
- **Render**: Free (750 hours/month)
- **Supabase**: Free (500MB database, 2GB bandwidth)
- **Total**: $0/month

### Paid Tier (For Production)
- **Netlify Pro**: $19/month (1TB bandwidth)
- **Render Starter**: $7/month (always-on)
- **Supabase Pro**: $25/month (8GB database)
- **Total**: $51/month

---

## 🔗 Useful Links

### Deployment Platforms
- **Netlify**: https://netlify.com
- **Render**: https://render.com
- **Railway**: https://railway.app
- **Vercel**: https://vercel.com (alternative to Netlify)

### Documentation
- **Netlify Docs**: https://docs.netlify.com
- **Render Docs**: https://render.com/docs
- **Supabase Docs**: https://supabase.com/docs

---

## 📝 Quick Deploy Commands

### Deploy Frontend to Netlify (CLI)
```bash
cd frontend
npm install -g netlify-cli
netlify login
netlify init
netlify deploy --prod
```

### Deploy Backend to Render (Git Push)
```bash
git add .
git commit -m "Deploy backend"
git push origin main
# Render auto-deploys on push
```

---

## 🎉 Success!

Once deployed, you'll have:
- ✅ Frontend live on Netlify
- ✅ Backend API running on Render
- ✅ Database on Supabase
- ✅ OAuth working with production URLs
- ✅ Separate portals for students, teachers, and admins

**Total deployment time: 30 minutes** 🚀
