# Authentication Backend - Quick Start Guide

## 🚀 Get Started in 5 Minutes

### Step 1: Run Database Migration

1. Open Supabase Dashboard: https://supabase.com/dashboard
2. Go to your project: `textjheeqfwmrzjtfdyo`
3. Click **SQL Editor** in left sidebar
4. Click **New Query**
5. Copy and paste the entire contents of `backend/migration_auth_system.sql`
6. Click **Run** (or press Ctrl+Enter)
7. Verify success message appears

### Step 2: Create First Admin User

In the same SQL Editor, run this query (replace with your Gmail):

```sql
INSERT INTO users (email, name, role, supabase_user_id)
VALUES ('your-email@gmail.com', 'Admin User', 'admin', gen_random_uuid())
ON CONFLICT (email) DO NOTHING;
```

### Step 3: Configure Supabase OAuth

1. In Supabase Dashboard, go to **Authentication** > **Providers**
2. Find **Google** provider
3. Click **Enable**
4. Add these redirect URLs:
   - `http://localhost:5173/auth/callback`
   - `http://localhost:3000/auth/callback`
5. Click **Save**

### Step 4: Get JWT Secret

1. In Supabase Dashboard, go to **Settings** > **API**
2. Scroll down to **JWT Settings**
3. Copy the **JWT Secret** value
4. Add to `backend/.env`:

```env
SUPABASE_JWT_SECRET=your-jwt-secret-here
```

### Step 5: Install Dependencies

```bash
cd backend
pip install supabase gotrue
```

### Step 6: Restart Backend

```bash
# Stop the current backend (Ctrl+C)
# Then restart:
uvicorn app.main:app --reload --port 8000
```

---

## 🧪 Test the Backend

### Test 1: Login Endpoint

You'll need a valid Supabase token. To get one:

1. Go to Supabase Dashboard > Authentication > Users
2. Click on your admin user
3. Copy the **Access Token** (JWT)

Then test with curl:

```bash
curl -X POST http://localhost:8000/api/v1/auth/login \
  -H "Content-Type: application/json" \
  -d '{"token": "YOUR_SUPABASE_TOKEN_HERE"}'
```

Expected response:
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

### Test 2: Get Current User

```bash
curl -X GET http://localhost:8000/api/v1/auth/me \
  -H "Authorization: Bearer YOUR_SUPABASE_TOKEN_HERE"
```

### Test 3: List Teachers (Admin Only)

```bash
curl -X GET http://localhost:8000/api/v1/admin/teachers \
  -H "Authorization: Bearer YOUR_SUPABASE_TOKEN_HERE"
```

### Test 4: Create Teacher (Admin Only)

```bash
curl -X POST http://localhost:8000/api/v1/admin/teachers \
  -H "Authorization: Bearer YOUR_SUPABASE_TOKEN_HERE" \
  -H "Content-Type: application/json" \
  -d '{
    "email": "teacher@example.com",
    "name": "Test Teacher",
    "department": "Computer Science"
  }'
```

### Test 5: List Pending Students (Admin Only)

```bash
curl -X GET http://localhost:8000/api/v1/admin/students/pending \
  -H "Authorization: Bearer YOUR_SUPABASE_TOKEN_HERE"
```

---

## 🔍 Verify Database Changes

Run these queries in Supabase SQL Editor to verify:

```sql
-- Check users table
SELECT * FROM users;

-- Check teachers table
SELECT * FROM teachers;

-- Check students with approval status
SELECT id, name, student_id_card_number, approval_status 
FROM students 
LIMIT 10;

-- Check existing students are approved
SELECT COUNT(*) as approved_count 
FROM students 
WHERE approval_status = 'approved';
```

---

## 🐛 Troubleshooting

### Error: "Invalid or expired token"
- Make sure you're using a fresh token from Supabase
- Tokens expire after 1 hour
- Get a new token from Supabase Dashboard > Authentication > Users

### Error: "User not registered"
- Make sure you created the admin user in Step 2
- Check the email matches your Supabase user

### Error: "Insufficient permissions"
- Make sure your user has role='admin'
- Check with: `SELECT * FROM users WHERE email = 'your-email@gmail.com';`

### Error: "Module not found: supabase"
- Run: `pip install supabase gotrue`
- Make sure you're in the backend directory

### Error: "Table 'users' does not exist"
- Run the migration script from Step 1
- Verify with: `SELECT * FROM users;`

---

## 📝 API Endpoints Reference

### Authentication
- `POST /api/v1/auth/login` - Login with Supabase token
- `POST /api/v1/auth/register` - Register new student
- `GET /api/v1/auth/me` - Get current user
- `POST /api/v1/auth/logout` - Logout

### Admin (Requires Admin Role)
- `GET /api/v1/admin/teachers` - List teachers
- `POST /api/v1/admin/teachers` - Create teacher
- `PUT /api/v1/admin/teachers/:id` - Update teacher
- `GET /api/v1/admin/students/pending` - List pending students
- `PUT /api/v1/admin/students/:id/approve` - Approve student
- `PUT /api/v1/admin/students/:id/reject` - Reject student

### Student (Requires Student Role)
- `GET /api/v1/student/profile` - Get own profile
- `GET /api/v1/student/attendance` - Get attendance history
- `GET /api/v1/student/attendance/stats` - Get stats
- `PUT /api/v1/student/profile` - Update profile

---

## ✅ Success Checklist

- [ ] Database migration completed
- [ ] First admin user created
- [ ] Supabase OAuth configured
- [ ] JWT secret added to .env
- [ ] Dependencies installed
- [ ] Backend restarted
- [ ] Login endpoint tested
- [ ] Admin endpoints tested
- [ ] No errors in backend logs

---

## 🎯 Next Steps

Once backend is working:

1. **Test with Postman**: Import endpoints and test all flows
2. **Check logs**: Monitor `backend` terminal for any errors
3. **Verify data**: Check Supabase dashboard for created records
4. **Ready for frontend**: Once all tests pass, start frontend implementation

---

## 💡 Tips

- Keep Supabase Dashboard open for monitoring
- Use Postman for easier API testing
- Check backend logs for detailed error messages
- Test each endpoint before moving to frontend
- Create test users for each role (admin, teacher, student)

---

**Need Help?** Check the logs in your backend terminal for detailed error messages.

**Ready for Frontend?** Once all backend tests pass, proceed to frontend implementation (Phases 5-8).
