# 🚀 Complete Auth System Setup

## ✅ What's Already Done

- Backend code (auth, admin, student services)
- Frontend code (login, admin, student portals)
- Dependencies installed (supabase, gotrue, react-router-dom)

## 📋 Setup Steps (5 minutes)

### Step 1: Run Database Migration

1. Open Supabase Dashboard: https://supabase.com/dashboard
2. Go to your project: `textjheeqfwmrzjtfdyo`
3. Click **SQL Editor** → **New Query**
4. Copy entire contents of `backend/migration_auth_system.sql`
5. Paste and click **Run**

### Step 2: Create Admin User

In SQL Editor, run (replace with YOUR Gmail):

```sql
INSERT INTO users (email, name, role, supabase_user_id)
VALUES ('your-email@gmail.com', 'Admin User', 'admin', gen_random_uuid())
ON CONFLICT (email) DO NOTHING;
```

### Step 3: Enable Google OAuth

1. Supabase Dashboard → **Authentication** → **Providers**
2. Find **Google** provider
3. Toggle **Enable** to ON
4. Add redirect URL: `http://localhost:5173/auth/callback`
5. Click **Save**

### Step 4: Get JWT Secret

1. Supabase Dashboard → **Settings** → **API**
2. Scroll to **JWT Settings**
3. Copy the **JWT Secret** value
4. Open `backend/.env`
5. Add line: `SUPABASE_JWT_SECRET=paste-secret-here`

### Step 5: Test the System

Backend is already running on port 8000.
Frontend is already running on port 5173.

Just go to: **http://localhost:5173**

## 🎯 Test Flow

1. **Go to http://localhost:5173**
2. Click "Login with Gmail"
3. Authorize with Google
4. You'll be redirected based on your role:
   - **Admin** → `/admin` (approve students, manage teachers)
   - **Teacher** → `/teacher` (existing dashboard)
   - **Student** → `/student` (view attendance)

## 🔐 User Roles

### Admin Portal (`/admin`)
- Approve/reject student registrations
- View pending students with photos
- Manage teachers (add, edit, deactivate)
- Full system access

### Teacher Portal (`/teacher`)
- Existing faculty dashboard
- Create sessions
- Enroll students (they'll be pending)
- View reports

### Student Portal (`/student`)
- View own profile
- View attendance history
- See attendance statistics
- **Pending approval screen** if not approved

## 📝 Quick Test Checklist

- [ ] Migration ran successfully
- [ ] Admin user created
- [ ] Google OAuth enabled
- [ ] JWT secret added to .env
- [ ] Can login with Gmail
- [ ] Redirected to correct portal
- [ ] Admin can see pending students
- [ ] Student sees "pending approval" if not approved

## 🐛 Troubleshooting

**"User not registered"**
- Make sure you created the admin user with YOUR Gmail

**"Invalid token"**
- Check JWT secret is in backend/.env
- Restart backend if you just added it

**OAuth not working**
- Check redirect URL is exactly: `http://localhost:5173/auth/callback`
- Make sure Google provider is enabled

**Can't see admin portal**
- Check your user role is 'admin' in database:
  ```sql
  SELECT * FROM users WHERE email = 'your-email@gmail.com';
  ```

## 🎉 Success!

Once you can login and see your portal, the system is working!

**New students** can:
1. Login with Gmail
2. Fill registration form
3. Capture face photo
4. Submit for approval
5. Wait for admin approval
6. Then access student portal

**Admins** can:
1. See all pending registrations
2. View student photos
3. Approve or reject with reason
4. Manage teachers

Everything is ready to go! 🚀
