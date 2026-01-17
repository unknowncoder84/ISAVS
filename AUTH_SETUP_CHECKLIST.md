# Authentication System Setup Checklist

## 📋 Complete Setup Guide

Follow these steps in order to get the authentication system running.

---

## Phase 1: Database Setup ✅

### Step 1: Run Migration Script

- [ ] Open Supabase Dashboard: https://supabase.com/dashboard
- [ ] Navigate to your project: `textjheeqfwmrzjtfdyo`
- [ ] Click **SQL Editor** in left sidebar
- [ ] Click **New Query**
- [ ] Open file: `backend/migration_auth_system.sql`
- [ ] Copy entire contents
- [ ] Paste into SQL Editor
- [ ] Click **Run** (or Ctrl+Enter)
- [ ] Verify success message appears
- [ ] Check for any errors in output

**Expected Output:**
```
✅ Authentication system migration completed successfully!
📝 Next steps:
1. Create first admin user
2. Install supabase Python client
3. Update backend/.env
4. Start implementing backend auth services
```

### Step 2: Verify Tables Created

- [ ] In SQL Editor, run:
```sql
SELECT table_name FROM information_schema.tables 
WHERE table_schema = 'public' 
AND table_name IN ('users', 'teachers');
```

**Expected Output:**
```
users
teachers
```

### Step 3: Verify Students Table Updated

- [ ] In SQL Editor, run:
```sql
SELECT column_name FROM information_schema.columns 
WHERE table_name = 'students' 
AND column_name IN ('user_id', 'approval_status');
```

**Expected Output:**
```
user_id
approval_status
```

### Step 4: Check Existing Students

- [ ] In SQL Editor, run:
```sql
SELECT COUNT(*) as approved_students 
FROM students 
WHERE approval_status = 'approved';
```

**Expected Output:** Should show count of your existing students (all auto-approved)

---

## Phase 2: Create Admin User ✅

### Step 5: Create Your Admin Account

- [ ] In SQL Editor, run (replace with YOUR Gmail):
```sql
INSERT INTO users (email, name, role, supabase_user_id)
VALUES ('your-email@gmail.com', 'Admin User', 'admin', gen_random_uuid())
ON CONFLICT (email) DO NOTHING;
```

### Step 6: Verify Admin Created

- [ ] In SQL Editor, run:
```sql
SELECT * FROM users WHERE role = 'admin';
```

**Expected Output:** Should show your admin user with:
- email: your-email@gmail.com
- name: Admin User
- role: admin
- supabase_user_id: (some UUID)

---

## Phase 3: Configure Supabase OAuth ✅

### Step 7: Enable Google OAuth

- [ ] In Supabase Dashboard, click **Authentication** in left sidebar
- [ ] Click **Providers** tab
- [ ] Scroll to **Google** provider
- [ ] Toggle **Enable** to ON
- [ ] Click **Save**

### Step 8: Add Redirect URLs

- [ ] In Google provider settings, find **Redirect URLs** section
- [ ] Add these URLs:
  - `http://localhost:5173/auth/callback`
  - `http://localhost:3000/auth/callback`
  - `http://127.0.0.1:5173/auth/callback`
- [ ] Click **Save**

### Step 9: Get OAuth Credentials (Optional)

If you want to use your own Google OAuth app:
- [ ] Go to Google Cloud Console
- [ ] Create OAuth 2.0 credentials
- [ ] Add to Supabase provider settings

Otherwise, Supabase provides default credentials.

---

## Phase 4: Configure Backend ✅

### Step 10: Get JWT Secret

- [ ] In Supabase Dashboard, click **Settings** (gear icon)
- [ ] Click **API** in left sidebar
- [ ] Scroll to **JWT Settings** section
- [ ] Copy the **JWT Secret** value (long string)
- [ ] Keep this secret safe!

### Step 11: Update .env File

- [ ] Open `backend/.env` in your editor
- [ ] Add this line at the end:
```env
SUPABASE_JWT_SECRET=paste-your-jwt-secret-here
```
- [ ] Save the file

### Step 12: Verify .env Configuration

- [ ] Check that `backend/.env` has all these:
```env
DATABASE_URL=postgresql://...
SUPABASE_URL=https://textjheeqfwmrzjtfdyo.supabase.co
SUPABASE_ANON_KEY=eyJhbGci...
SUPABASE_SERVICE_KEY=eyJhbGci...
SUPABASE_JWT_SECRET=your-jwt-secret-here  ← NEW
```

---

## Phase 5: Install Dependencies ✅

### Step 13: Install Python Packages

- [ ] Open terminal
- [ ] Navigate to backend:
```bash
cd backend
```
- [ ] Install new dependencies:
```bash
pip install supabase gotrue
```
- [ ] Verify installation:
```bash
pip list | grep supabase
pip list | grep gotrue
```

**Expected Output:**
```
supabase         2.x.x
gotrue           2.x.x
```

---

## Phase 6: Restart Backend ✅

### Step 14: Stop Current Backend

- [ ] Find terminal running backend
- [ ] Press **Ctrl+C** to stop
- [ ] Wait for graceful shutdown

### Step 15: Start Backend

- [ ] In backend directory, run:
```bash
uvicorn app.main:app --reload --port 8000
```
- [ ] Wait for startup messages
- [ ] Look for "Application startup complete"

**Expected Output:**
```
INFO:     Uvicorn running on http://127.0.0.1:8000
INFO:     Application startup complete.
```

### Step 16: Check for Errors

- [ ] Look at backend terminal output
- [ ] Check for any import errors
- [ ] Check for any configuration errors
- [ ] If errors, check previous steps

---

## Phase 7: Test Backend ✅

### Step 17: Get Test Token

- [ ] Go to Supabase Dashboard
- [ ] Click **Authentication** > **Users**
- [ ] Find your admin user (your-email@gmail.com)
- [ ] Click on the user
- [ ] Scroll to **Access Token** section
- [ ] Click **Copy** to copy JWT token
- [ ] Save token for testing (valid for 1 hour)

### Step 18: Test Login Endpoint

- [ ] Open terminal (new window)
- [ ] Run this command (replace TOKEN):
```bash
curl -X POST http://localhost:8000/api/v1/auth/login \
  -H "Content-Type: application/json" \
  -d '{"token": "YOUR_TOKEN_HERE"}'
```

**Expected Output:**
```json
{
  "success": true,
  "user": {
    "id": 1,
    "email": "your-email@gmail.com",
    "name": "Admin User",
    "role": "admin",
    "created_at": "2026-01-17T..."
  },
  "message": "Login successful"
}
```

### Step 19: Test Get Current User

- [ ] Run this command (replace TOKEN):
```bash
curl -X GET http://localhost:8000/api/v1/auth/me \
  -H "Authorization: Bearer YOUR_TOKEN_HERE"
```

**Expected Output:**
```json
{
  "id": 1,
  "email": "your-email@gmail.com",
  "name": "Admin User",
  "role": "admin",
  "created_at": "2026-01-17T..."
}
```

### Step 20: Test Admin Endpoint

- [ ] Run this command (replace TOKEN):
```bash
curl -X GET http://localhost:8000/api/v1/admin/teachers \
  -H "Authorization: Bearer YOUR_TOKEN_HERE"
```

**Expected Output:**
```json
[]
```
(Empty array because no teachers created yet)

### Step 21: Test Create Teacher

- [ ] Run this command (replace TOKEN):
```bash
curl -X POST http://localhost:8000/api/v1/admin/teachers \
  -H "Authorization: Bearer YOUR_TOKEN_HERE" \
  -H "Content-Type: application/json" \
  -d '{
    "email": "teacher@example.com",
    "name": "Test Teacher",
    "department": "Computer Science"
  }'
```

**Expected Output:**
```json
{
  "id": 1,
  "user_id": 2,
  "email": "teacher@example.com",
  "name": "Test Teacher",
  "department": "Computer Science",
  "active": true,
  "created_at": "2026-01-17T..."
}
```

---

## Phase 8: Verify Everything ✅

### Step 22: Check Database

- [ ] In Supabase SQL Editor, run:
```sql
-- Check users
SELECT id, email, name, role FROM users;

-- Check teachers
SELECT * FROM teachers;

-- Check students approval status
SELECT id, name, approval_status FROM students LIMIT 5;
```

### Step 23: Check Backend Logs

- [ ] Look at backend terminal
- [ ] Should see successful API requests
- [ ] No error messages
- [ ] Status codes: 200, 201

### Step 24: Test Existing Features

- [ ] Open frontend: http://localhost:5173
- [ ] Test student enrollment (should still work)
- [ ] Test session creation (should still work)
- [ ] Test verification (should still work for approved students)

---

## ✅ Success Criteria

You're ready to proceed if:

- [x] Database migration completed without errors
- [x] Admin user created successfully
- [x] Google OAuth enabled in Supabase
- [x] JWT secret added to .env
- [x] Dependencies installed (supabase, gotrue)
- [x] Backend restarted successfully
- [x] Login endpoint returns success
- [x] Admin endpoints work with token
- [x] No errors in backend logs
- [x] Existing features still work

---

## 🐛 Troubleshooting

### Issue: "Table 'users' does not exist"
**Solution:** Run migration script again (Step 1)

### Issue: "Invalid or expired token"
**Solution:** Get fresh token from Supabase Dashboard (Step 17)

### Issue: "Module not found: supabase"
**Solution:** Install dependencies (Step 13)

### Issue: "User not registered"
**Solution:** Create admin user (Step 5)

### Issue: "Insufficient permissions"
**Solution:** Check user role is 'admin' (Step 6)

### Issue: Backend won't start
**Solution:** 
1. Check .env has all required variables
2. Check no syntax errors in new files
3. Check port 8000 is not in use

### Issue: OAuth not working
**Solution:**
1. Check Google provider is enabled
2. Check redirect URLs are correct
3. Check OAuth credentials (if using custom)

---

## 📊 Progress Tracker

### Database Setup
- [ ] Migration script executed
- [ ] Tables created (users, teachers)
- [ ] Students table updated
- [ ] Existing students approved
- [ ] Admin user created

### Supabase Configuration
- [ ] Google OAuth enabled
- [ ] Redirect URLs added
- [ ] JWT secret obtained
- [ ] .env updated

### Backend Setup
- [ ] Dependencies installed
- [ ] Backend restarted
- [ ] No startup errors
- [ ] All imports working

### Testing
- [ ] Login endpoint works
- [ ] Get user endpoint works
- [ ] Admin endpoints work
- [ ] Teacher creation works
- [ ] Existing features work

---

## 🎯 Next Steps

Once all checkboxes are complete:

1. **Document any issues** you encountered
2. **Test all endpoints** with Postman
3. **Create test data** (teachers, pending students)
4. **Ready for frontend** implementation

---

## 📞 Need Help?

If stuck on any step:

1. Check backend terminal for error messages
2. Check Supabase Dashboard for database errors
3. Review `AUTH_BACKEND_QUICK_START.md` for details
4. Check `AUTH_IMPLEMENTATION_COMPLETE.md` for technical info

---

**Estimated Time**: 15-20 minutes  
**Difficulty**: Easy (follow steps carefully)  
**Status**: Backend Ready ✅  
**Next**: Frontend Implementation 🎨
