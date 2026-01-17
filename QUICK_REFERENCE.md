# ⚡ Quick Reference Card

## 🌐 URLs
```
Frontend:  http://localhost:3001
Backend:   http://localhost:8000
API Docs:  http://localhost:8000/docs
```

## 🚪 Portal URLs
```
Home:      http://localhost:3001/home
Student:   http://localhost:3001/login/student
Teacher:   http://localhost:3001/login/teacher
Admin:     http://localhost:3001/login
```

## ⚡ Quick Commands
```bash
# Start both servers
start_dev.bat

# Or manually:
cd backend && uvicorn app.main:app --reload --port 8000
cd frontend && npm run dev
```

## 🔧 Fix OAuth (2 min)
1. Go to: https://supabase.com/dashboard/project/textjheeqfwmrzjtfdyo/auth/providers
2. Enable Google
3. Add redirect: `http://localhost:3001/auth/callback`
4. Save

## 📚 Key Documents
- `READY_TO_USE_NOW.md` - Start here!
- `QUICK_FIX_OAUTH.md` - Fix OAuth error
- `VISUAL_GUIDE.md` - See what it looks like
- `DEPLOYMENT_GUIDE.md` - Deploy to production

## ✅ Status
- ✅ Backend running (port 8000)
- ✅ Frontend running (port 3001)
- ✅ Supabase connected
- ✅ 3 separate login pages created
- ✅ Modern gradient UI
- ✅ Deployment ready
- ⚠️ OAuth needs enabling (2 min)

## 🎯 What to Do Now
1. Open http://localhost:3001
2. Enable OAuth (2 min)
3. Test all three portals
4. Enjoy your professional UI! 🎉
