# ⚡ Netlify Quick Deploy - ISAVS 2026

## 🚀 Deploy in 10 Minutes

### Prerequisites
- [x] Code pushed to GitHub: https://github.com/unknowncoder84/ISAVS
- [ ] Netlify account (free): https://app.netlify.com
- [ ] Supabase account (free): https://supabase.com
- [ ] Render account (free): https://render.com

---

## 📋 Step-by-Step Deployment

### STEP 1: Deploy Backend (5 minutes)

**1.1 Go to Render**
- Visit: https://render.com
- Click "Get Started" → Sign up with GitHub

**1.2 Create Web Service**
- Click "New +" → "Web Service"
- Click "Connect account" → Authorize GitHub
- Select repository: `unknowncoder84/ISAVS`

**1.3 Configure Service**
```
Name: isavs-backend
Region: Choose closest to you
Branch: main
Root Directory: backend
Runtime: Python 3
Build Command: pip install -r requirements.txt
Start Command: uvicorn app.main:app --host 0.0.0.0 --port $PORT
Instance Type: Free
```

**1.4 Add Environment Variables**
Click "Advanced" → Add Environment Variables:
```
DATABASE_URL=postgresql://user:pass@host:5432/db
CORS_ORIGINS=*
SECRET_KEY=your-secret-key-here
```

**1.5 Deploy**
- Click "Create Web Service"
- Wait 3-5 minutes
- Copy your backend URL: `https://isavs-backend.onrender.com`

---

### STEP 2: Setup Database (3 minutes)

**2.1 Create Supabase Project**
- Go to: https://supabase.com
- Click "New project"
- Fill in:
  - Name: `isavs-2026`
  - Database Password: (save this!)
  - Region: Choose closest
- Click "Create new project"

**2.2 Run Migration**
- Wait for project to be ready (2 minutes)
- Go to "SQL Editor" in left sidebar
- Click "New query"
- Copy entire contents of `FINAL_DATABASE_MIGRATION.sql`
- Paste and click "Run"
- Should see: ✅ Migration Complete!

**2.3 Get Connection Details**
- Go to "Settings" → "Database"
- Copy:
  - Project URL: `https://xxxxx.supabase.co`
  - Anon key: `eyJhbGc...` (long string)
  - Connection string: `postgresql://...`

**2.4 Update Backend**
- Go back to Render dashboard
- Click your `isavs-backend` service
- Go to "Environment" tab
- Update `DATABASE_URL` with Supabase connection string
- Click "Save Changes" (will auto-redeploy)

---

### STEP 3: Deploy Teacher Dashboard (2 minutes)

**3.1 Go to Netlify**
- Visit: https://app.netlify.com
- Sign up with GitHub

**3.2 Import Project**
- Click "Add new site" → "Import an existing project"
- Click "Deploy with GitHub"
- Authorize Netlify
- Select: `unknowncoder84/ISAVS`

**3.3 Configure Build**
```
Site name: isavs-teacher (or leave auto-generated)
Branch: main
Base directory: frontend
Build command: npm run build:teacher
Publish directory: frontend/dist
```

**3.4 Add Environment Variables**
Click "Show advanced" → "New variable":
```
VITE_API_URL = https://isavs-backend.onrender.com
VITE_SUPABASE_URL = https://xxxxx.supabase.co
VITE_SUPABASE_ANON_KEY = your_anon_key_here
```

**3.5 Deploy**
- Click "Deploy site"
- Wait 2-3 minutes
- Your site will be live at: `https://random-name.netlify.app`
- Click "Site settings" → "Change site name" to customize

---

### STEP 4: Deploy Student Kiosk (2 minutes)

**4.1 Create Another Site**
- In Netlify dashboard, click "Add new site"
- Import same repository: `unknowncoder84/ISAVS`

**4.2 Configure Build**
```
Site name: isavs-student
Branch: main
Base directory: frontend
Build command: npm run build:student
Publish directory: frontend/dist
```

**4.3 Add Same Environment Variables**
```
VITE_API_URL = https://isavs-backend.onrender.com
VITE_SUPABASE_URL = https://xxxxx.supabase.co
VITE_SUPABASE_ANON_KEY = your_anon_key_here
```

**4.4 Deploy**
- Click "Deploy site"
- Wait 2-3 minutes
- Your site will be live at: `https://another-name.netlify.app`

---

### STEP 5: Update CORS (1 minute)

**5.1 Get Netlify URLs**
Copy both URLs:
- Teacher: `https://isavs-teacher.netlify.app`
- Student: `https://isavs-student.netlify.app`

**5.2 Update Backend CORS**
- Go to Render dashboard
- Click `isavs-backend`
- Go to "Environment" tab
- Update `CORS_ORIGINS`:
```
CORS_ORIGINS=https://isavs-teacher.netlify.app,https://isavs-student.netlify.app
```
- Click "Save Changes"

---

## ✅ Verification

### Test Teacher Dashboard
1. Open: `https://isavs-teacher.netlify.app`
2. Should see login page
3. Try to login (create account if needed)
4. Should see dashboard

### Test Student Kiosk
1. Open: `https://isavs-student.netlify.app`
2. Should see session entry page
3. Enter test session ID
4. GPS check should work (allow location)

### Test Backend
1. Open: `https://isavs-backend.onrender.com/docs`
2. Should see FastAPI documentation
3. Try a test endpoint

---

## 🎯 Your Deployment URLs

After completing all steps, save these:

```
✅ Teacher Dashboard: https://isavs-teacher.netlify.app
✅ Student Kiosk:     https://isavs-student.netlify.app
✅ Backend API:       https://isavs-backend.onrender.com
✅ Database:          Supabase (managed)
```

---

## 🐛 Common Issues

### Issue 1: Build Fails on Netlify
**Error:** `npm ERR! missing script: build:teacher`

**Fix:**
- Check that `package.json` has the build scripts
- Ensure base directory is set to `frontend`
- Try clearing cache: Site settings → Build & deploy → Clear cache

### Issue 2: Blank Page After Deploy
**Error:** White screen, no content

**Fix:**
- Check browser console for errors
- Verify environment variables are set
- Check that `VITE_API_URL` doesn't have trailing slash
- Redeploy after fixing

### Issue 3: CORS Error
**Error:** `Access to fetch blocked by CORS policy`

**Fix:**
- Update `CORS_ORIGINS` in Render with exact Netlify URLs
- No trailing slashes
- Include both sites
- Redeploy backend

### Issue 4: Database Connection Failed
**Error:** `Connection refused`

**Fix:**
- Check `DATABASE_URL` format in Render
- Ensure Supabase allows external connections
- Add `?sslmode=require` to connection string
- Verify password is correct

---

## 💡 Pro Tips

### Custom Domains
**Teacher Dashboard:**
- Netlify: Site settings → Domain management
- Add: `teacher.yourdomain.com`

**Student Kiosk:**
- Add: `student.yourdomain.com`

### Auto Deploy on Push
- Already configured! 
- Push to GitHub → Auto deploys to Netlify
- Check: Site settings → Build & deploy → Deploy contexts

### Environment Variables
- Update in Netlify: Site settings → Environment variables
- Must redeploy after changes
- Use "Trigger deploy" button

### Monitoring
- Netlify: Analytics tab (free)
- Render: Metrics tab (free)
- Supabase: Database → Logs

---

## 📊 Deployment Checklist

- [ ] Backend deployed to Render
- [ ] Database created on Supabase
- [ ] Migration script executed
- [ ] Teacher dashboard deployed to Netlify
- [ ] Student kiosk deployed to Netlify
- [ ] Environment variables configured
- [ ] CORS updated with Netlify URLs
- [ ] Teacher dashboard tested
- [ ] Student kiosk tested
- [ ] Backend API tested
- [ ] GPS functionality tested
- [ ] Face recognition tested
- [ ] OTP verification tested

---

## 🎉 Success!

If all steps completed:
- ✅ Your system is live on the internet
- ✅ Accessible from any device
- ✅ Free tier (no cost)
- ✅ Auto-deploys on git push
- ✅ SSL/HTTPS enabled
- ✅ CDN for fast loading

**Share your links:**
- Teacher: `https://isavs-teacher.netlify.app`
- Student: `https://isavs-student.netlify.app`

---

## 📞 Need Help?

- **Netlify Docs:** https://docs.netlify.com
- **Render Docs:** https://render.com/docs
- **Supabase Docs:** https://supabase.com/docs
- **GitHub Issues:** https://github.com/unknowncoder84/ISAVS/issues

**Deployment time:** ~10 minutes total
**Cost:** $0 (free tier)
**Maintenance:** Auto-updates on git push

🚀 **Ready? Start with Step 1!**
