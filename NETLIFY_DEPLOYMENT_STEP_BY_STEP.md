# 🚀 Deploy to Netlify - Step by Step Guide

## ✅ Prerequisites

- ✅ Code pushed to GitHub: https://github.com/Anuj-Gaud/Hackathon
- ✅ Frontend configured with `netlify.toml`
- ✅ Environment variables ready

---

## 📋 Quick Deployment (10 Minutes)

### Step 1: Sign Up / Login to Netlify (2 min)

1. **Go to Netlify:**
   - Visit: https://www.netlify.com/
   
2. **Sign Up with GitHub:**
   - Click "Sign up" or "Log in"
   - Choose "Sign up with GitHub"
   - Authorize Netlify to access your GitHub account

---

### Step 2: Import Your Project (3 min)

1. **Click "Add new site":**
   - On Netlify dashboard, click "Add new site"
   - Select "Import an existing project"

2. **Connect to GitHub:**
   - Click "Deploy with GitHub"
   - Authorize Netlify if prompted
   - Search for "Hackathon" repository
   - Click on "Anuj-Gaud/Hackathon"

3. **Configure Build Settings:**
   ```
   Base directory: frontend
   Build command: npm run build
   Publish directory: frontend/dist
   ```

4. **Click "Deploy site"**

---

### Step 3: Add Environment Variables (3 min)

1. **Go to Site Settings:**
   - Click on your site name
   - Go to "Site configuration" → "Environment variables"

2. **Add These Variables:**
   ```
   VITE_SUPABASE_URL=https://textjheeqfwmrzjtfdyo.supabase.co
   VITE_SUPABASE_ANON_KEY=your-supabase-anon-key
   VITE_API_URL=your-backend-url (we'll add this later)
   ```

3. **Get Supabase Keys:**
   - Go to: https://supabase.com/dashboard/project/textjheeqfwmrzjtfdyo/settings/api
   - Copy "Project URL" → Use as `VITE_SUPABASE_URL`
   - Copy "anon public" key → Use as `VITE_SUPABASE_ANON_KEY`

4. **Save Variables**

---

### Step 4: Trigger Redeploy (1 min)

1. **Go to Deploys Tab:**
   - Click "Deploys" in the top menu

2. **Trigger Deploy:**
   - Click "Trigger deploy" → "Deploy site"
   - Wait for build to complete (2-3 minutes)

---

### Step 5: Get Your Live URL (1 min)

1. **Copy Your URL:**
   - Once deployed, you'll see a URL like: `https://your-site-name.netlify.app`
   - Click on it to view your live site!

2. **Optional - Custom Domain:**
   - Go to "Domain management"
   - Click "Add custom domain"
   - Follow instructions to add your domain

---

## 🎯 Visual Step-by-Step

### 1. Netlify Dashboard

```
┌─────────────────────────────────────┐
│ Netlify Dashboard                   │
│                                     │
│ [Add new site ▼]                   │
│   ├─ Import an existing project    │
│   ├─ Start from a template         │
│   └─ Deploy manually                │
└─────────────────────────────────────┘
```

### 2. Import from GitHub

```
┌─────────────────────────────────────┐
│ Import an existing project          │
│                                     │
│ Connect to Git provider:            │
│ [GitHub] [GitLab] [Bitbucket]      │
│                                     │
│ Search repositories:                │
│ [Hackathon                    🔍]   │
│                                     │
│ ✓ Anuj-Gaud/Hackathon              │
│   └─ Select                         │
└─────────────────────────────────────┘
```

### 3. Build Settings

```
┌─────────────────────────────────────┐
│ Site settings for Hackathon         │
│                                     │
│ Base directory:                     │
│ [frontend                      ]    │
│                                     │
│ Build command:                      │
│ [npm run build                 ]    │
│                                     │
│ Publish directory:                  │
│ [frontend/dist                 ]    │
│                                     │
│ [Deploy site]                       │
└─────────────────────────────────────┘
```

### 4. Environment Variables

```
┌─────────────────────────────────────┐
│ Environment variables               │
│                                     │
│ Key: VITE_SUPABASE_URL             │
│ Value: https://textjheeqfwmrz...   │
│ [Add variable]                      │
│                                     │
│ Key: VITE_SUPABASE_ANON_KEY        │
│ Value: eyJhbGciOiJIUzI1NiIsInR...  │
│ [Add variable]                      │
│                                     │
│ Key: VITE_API_URL                  │
│ Value: (backend URL - add later)   │
│ [Add variable]                      │
│                                     │
│ [Save]                              │
└─────────────────────────────────────┘
```

---

## 🔧 Troubleshooting

### Build Failed?

**Check Build Logs:**
1. Go to "Deploys" tab
2. Click on the failed deploy
3. Read the error message

**Common Issues:**

1. **"npm: command not found"**
   - Solution: Make sure base directory is set to `frontend`

2. **"Module not found"**
   - Solution: Check if all dependencies are in `package.json`

3. **"Build command failed"**
   - Solution: Try changing build command to `npm install && npm run build`

4. **Environment variables not working**
   - Solution: Make sure variable names start with `VITE_`
   - Redeploy after adding variables

---

## 📝 After Deployment Checklist

- [ ] Site is live and accessible
- [ ] All pages load correctly
- [ ] Login pages display properly
- [ ] Images and styles load
- [ ] No console errors

---

## 🎨 Your Deployed Site

Once deployed, you'll have:

**Live URL**: `https://your-site-name.netlify.app`

**Features Working**:
- ✅ Home page with 3 portals
- ✅ Student login page
- ✅ Teacher login page
- ✅ Admin login page
- ✅ Beautiful gradient UI
- ✅ Responsive design

**Not Working Yet** (need backend):
- ⚠️ OAuth login (need to add Netlify URL to Supabase)
- ⚠️ API calls (need backend deployed)
- ⚠️ Face recognition (need backend)

---

## 🔗 Update OAuth Redirect URLs

After deployment, update Supabase OAuth settings:

1. **Go to Supabase:**
   - https://supabase.com/dashboard/project/textjheeqfwmrzjtfdyo/auth/providers

2. **Add Netlify URL:**
   - In "Redirect URLs", add:
   ```
   https://your-site-name.netlify.app/auth/callback
   ```

3. **Update Google OAuth:**
   - Go to Google Cloud Console
   - Add authorized redirect URI:
   ```
   https://textjheeqfwmrzjtfdyo.supabase.co/auth/v1/callback
   ```

---

## 🚀 Next Steps

### 1. Deploy Backend (15 min)

Your frontend is live, but you need the backend for full functionality.

**Options:**
- **Render** (Recommended): https://render.com/
- **Railway**: https://railway.app/
- **Heroku**: https://heroku.com/

See `DEPLOYMENT_GUIDE.md` for backend deployment.

### 2. Update Frontend Environment Variables

Once backend is deployed:
1. Get backend URL (e.g., `https://your-app.onrender.com`)
2. Go to Netlify → Site settings → Environment variables
3. Update `VITE_API_URL` with backend URL
4. Trigger redeploy

### 3. Test Everything

- Login with Gmail
- Test all 3 portals
- Verify face recognition works
- Check attendance tracking

---

## 💡 Pro Tips

### Automatic Deployments

Netlify automatically deploys when you push to GitHub:
```bash
# Make changes
git add .
git commit -m "Update frontend"
git push origin main

# Netlify will automatically deploy!
```

### Preview Deployments

Create a branch for testing:
```bash
git checkout -b feature/new-feature
git push origin feature/new-feature

# Netlify creates a preview URL!
```

### Custom Domain

1. Buy domain from Namecheap, GoDaddy, etc.
2. Go to Netlify → Domain management
3. Add custom domain
4. Update DNS records
5. Enable HTTPS (automatic)

---

## 📊 Deployment Summary

**What You'll Have:**

```
Frontend (Netlify):
├─ Live URL: https://your-site-name.netlify.app
├─ Automatic deployments from GitHub
├─ HTTPS enabled
├─ CDN for fast loading
└─ Free tier: 100GB bandwidth/month

Backend (Deploy Next):
├─ API endpoints
├─ Face recognition
├─ Database connection
└─ OAuth handling
```

---

## 🎯 Quick Commands

### Check Deployment Status
```bash
# Visit Netlify dashboard
https://app.netlify.com/

# Or use Netlify CLI
npm install -g netlify-cli
netlify status
```

### Redeploy
```bash
# From Netlify dashboard
Deploys → Trigger deploy → Deploy site

# Or push to GitHub
git push origin main
```

---

## 🆘 Need Help?

### Netlify Support
- Docs: https://docs.netlify.com/
- Community: https://answers.netlify.com/
- Status: https://www.netlifystatus.com/

### Your Documentation
- Complete guide: `DEPLOYMENT_GUIDE.md`
- OAuth setup: `FIX_OAUTH_SECRET_ERROR.md`
- System overview: `FINAL_COMPLETE_GUIDE.md`

---

## ✅ Success Checklist

- [ ] Signed up for Netlify
- [ ] Connected GitHub repository
- [ ] Configured build settings
- [ ] Added environment variables
- [ ] Deployed successfully
- [ ] Site is live and accessible
- [ ] Updated OAuth redirect URLs
- [ ] Tested all pages load

---

**Your frontend will be live in 10 minutes!** 🎉

**Next**: Deploy backend to complete the system.

---

## 🎬 Quick Start Commands

```bash
# 1. Make sure code is pushed
git push origin main

# 2. Go to Netlify
# Visit: https://www.netlify.com/

# 3. Import project
# Click: Add new site → Import from GitHub

# 4. Configure
# Base: frontend
# Build: npm run build
# Publish: frontend/dist

# 5. Deploy!
# Click: Deploy site

# Done! 🚀
```

---

**Time to deploy: 10 minutes** ⏱️

**Your professional attendance system will be live!** ✨
