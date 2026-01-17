# 🎓 Deploy Student Site - Quick Guide

## ✅ Setup Complete!

I've created everything you need to deploy both Teacher and Student sites separately.

---

## 📦 What Was Created

### 1. Separate HTML Files
- **`frontend/index-teacher.html`** - Teacher Dashboard entry point
- **`frontend/index-student.html`** - Student Kiosk entry point

### 2. Build Scripts (in package.json)
- **`npm run build:teacher:netlify`** - Builds teacher site
- **`npm run build:student:netlify`** - Builds student site

### 3. How It Works
```bash
# Teacher build
cp index-teacher.html index.html  # Copy teacher HTML
npm run build:teacher             # Build with teacher mode

# Student build
cp index-student.html index.html  # Copy student HTML
npm run build:student             # Build with student mode
```

---

## 🚀 Deploy Student Site to Netlify

### Step 1: Go to Netlify
https://app.netlify.com

### Step 2: Add New Site
1. Click **"Add new site"**
2. Choose **"Import an existing project"**
3. Select **GitHub**
4. Choose repository: **`unknowncoder84/ISAVS`**

### Step 3: Configure Build Settings

```
Site name: isavs-student-kiosk
Branch: main
Base directory: frontend
Build command: npm run build:student:netlify
Publish directory: frontend/dist
```

### Step 4: Add Environment Variables

Click "Add environment variables" and add:

```
VITE_API_URL=https://your-backend-url.com
VITE_SUPABASE_URL=https://textjheeqfwmrzjtfdyo.supabase.co
VITE_SUPABASE_ANON_KEY=eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJpc3MiOiJzdXBhYmFzZSIsInJlZiI6InRleHRqaGVlcWZ3bXJ6anRmZHlvIiwicm9sZSI6ImFub24iLCJpYXQiOjE3Njg1NTY1MDgsImV4cCI6MjA4NDEzMjUwOH0.vt6ssfPvYQtSa1kX3lhzkz52T8ng2rRMA8TPywR0huQ
NODE_VERSION=18
```

### Step 5: Deploy!
Click **"Deploy site"**

Wait 2-3 minutes and your Student Kiosk will be live! 🎉

---

## 🔄 Update Teacher Site Build Command

Your teacher site should also use the new build command for consistency.

### Go to Teacher Site Settings
1. Open your teacher site in Netlify
2. Go to **Site settings** → **Build & deploy** → **Build settings**
3. Click **"Edit settings"**
4. Change build command to: **`npm run build:teacher:netlify`**
5. Click **"Save"**
6. Trigger a new deploy

---

## 📊 Your Deployment URLs

After both sites are deployed:

```
Teacher Dashboard: https://isavs-teacher.netlify.app
Student Kiosk:     https://isavs-student.netlify.app
Backend API:       https://your-backend.onrender.com
```

---

## ✅ Verification Checklist

### Teacher Site
- [ ] Build command: `npm run build:teacher:netlify`
- [ ] Loads Teacher Dashboard
- [ ] Shows "Teacher Dashboard" in title
- [ ] Can start sessions
- [ ] Real-time updates work

### Student Site
- [ ] Build command: `npm run build:student:netlify`
- [ ] Loads Student Kiosk
- [ ] Shows "Student Kiosk" in title
- [ ] GPS check works
- [ ] OTP entry works
- [ ] Face scan works

---

## 🔧 Troubleshooting

### Issue: Wrong Portal Loads
**Problem:** Teacher site shows student portal or vice versa

**Fix:**
1. Check build command in Netlify settings
2. Should be `build:teacher:netlify` or `build:student:netlify`
3. Clear cache and redeploy

### Issue: 404 Error
**Problem:** Page not found

**Fix:**
1. Check publish directory is `frontend/dist`
2. Check base directory is `frontend`
3. Verify build completed successfully

### Issue: Environment Variables Not Working
**Problem:** API calls fail

**Fix:**
1. Go to Site settings → Environment variables
2. Verify all variables are set
3. Redeploy after adding variables

---

## 🎯 Quick Commands

### Local Testing
```bash
# Test teacher build
cd frontend
npm run build:teacher:netlify
npm run preview

# Test student build
npm run build:student:netlify
npm run preview
```

### Update Both Sites
```bash
# Make changes
git add .
git commit -m "Update both portals"
git push

# Both Netlify sites will auto-deploy!
```

---

## 📚 Related Documentation

- **Full Guide:** `DEPLOY_STUDENT_SITE.md`
- **Netlify Setup:** `NETLIFY_DEPLOYMENT_GUIDE.md`
- **Quick Deploy:** `NETLIFY_QUICK_DEPLOY.md`
- **Local Setup:** `LOCAL_SETUP_GUIDE.md`

---

## 🎉 Summary

**What You Have:**
- ✅ Separate HTML files for teacher and student
- ✅ Dedicated build scripts for each portal
- ✅ Ready to deploy to Netlify
- ✅ Auto-deploy on git push

**Next Steps:**
1. Deploy student site to Netlify (5 minutes)
2. Update teacher site build command (2 minutes)
3. Test both sites
4. Update backend CORS with both URLs

**Your dual portal system will be fully deployed!** 🚀
