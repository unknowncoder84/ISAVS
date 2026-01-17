# 🔐 Dummy Login Credentials

## ⚠️ Important Note

This system uses **Google OAuth** for authentication. You need to:
1. Enable Google OAuth in Supabase
2. Login with your actual Gmail account
3. The system will automatically assign roles based on database records

---

## 🎯 How Authentication Works

### Current System (OAuth)
- Users login with their **real Gmail account**
- After login, the system checks the database for their role
- Roles: `student`, `teacher`, `admin`

### For Testing Without OAuth

If you want to test without setting up OAuth, you can create a **demo mode** or use the following approach:

---

## 🧪 Testing Accounts (After OAuth Setup)

### Step 1: Enable OAuth
1. Go to: https://supabase.com/dashboard/project/textjheeqfwmrzjtfdyo/auth/providers
2. Enable Google
3. Add redirect: `http://localhost:3001/auth/callback`

### Step 2: Login with Gmail
Use any Gmail account to login

### Step 3: Assign Roles in Database

After first login, run these SQL commands in Supabase:

#### Create Admin User
```sql
-- Replace with your Gmail email
INSERT INTO admins (email, name, created_at)
VALUES ('your-email@gmail.com', 'Admin User', NOW());
```

#### Create Teacher User
```sql
-- Replace with your Gmail email
INSERT INTO admins (email, name, role, created_at)
VALUES ('teacher-email@gmail.com', 'Teacher User', 'teacher', NOW());
```

#### Create Student User
```sql
-- First, enroll the student through the enrollment page
-- Then approve them:
UPDATE students 
SET approval_status = 'approved' 
WHERE email = 'student-email@gmail.com';
```

---

## 🚀 Quick Demo Setup (Without Real OAuth)

### Option 1: Mock Authentication (Development Only)

Create a demo mode by modifying `AuthContext.tsx`:

```typescript
// Add demo users
const DEMO_USERS = {
  'admin@demo.com': { email: 'admin@demo.com', name: 'Admin Demo', role: 'admin' },
  'teacher@demo.com': { email: 'teacher@demo.com', name: 'Teacher Demo', role: 'teacher' },
  'student@demo.com': { email: 'student@demo.com', name: 'Student Demo', role: 'student' }
};

// Add demo login function
const demoLogin = (email: string) => {
  const user = DEMO_USERS[email];
  if (user) {
    setUser(user);
    localStorage.setItem('user', JSON.stringify(user));
  }
};
```

### Demo Credentials
```
Admin:
Email: admin@demo.com
Password: (not needed in demo mode)

Teacher:
Email: teacher@demo.com
Password: (not needed in demo mode)

Student:
Email: student@demo.com
Password: (not needed in demo mode)
```

---

## 📝 Recommended Approach for Hackathon Demo

### 1. Use Real Gmail Accounts

**Admin Account:**
- Email: Your personal Gmail
- Role: Admin (set in database)

**Teacher Account:**
- Email: Another Gmail (or same with different role)
- Role: Teacher (set in database)

**Student Account:**
- Email: Another Gmail
- Role: Student (enroll through UI, then approve)

### 2. Database Setup Script

Run this in Supabase SQL Editor:

```sql
-- Create admin
INSERT INTO admins (email, name, created_at)
VALUES ('your-admin-email@gmail.com', 'Admin User', NOW());

-- Create teacher (using admins table with role)
INSERT INTO admins (email, name, role, created_at)
VALUES ('your-teacher-email@gmail.com', 'Teacher User', 'teacher', NOW());

-- For students, use the enrollment UI, then approve:
-- UPDATE students SET approval_status = 'approved' WHERE email = 'student@gmail.com';
```

---

## 🎬 Demo Flow for Hackathon

### Scenario 1: Admin Demo
1. Login with admin Gmail
2. Go to Admin Dashboard
3. Show pending student approvals
4. Approve/reject students
5. Manage system

### Scenario 2: Teacher Demo
1. Login with teacher Gmail
2. Go to Teacher Dashboard
3. Start a new session
4. Show OTP generation
5. Enroll a student
6. View analytics

### Scenario 3: Student Demo
1. Login with student Gmail
2. Register as new student (if not enrolled)
3. Wait for approval (or approve via admin)
4. View attendance dashboard
5. See attendance history

---

## 🔧 Quick Setup for Demo

### 1. Create 3 Gmail Accounts (or use existing)
```
admin-demo@gmail.com
teacher-demo@gmail.com
student-demo@gmail.com
```

### 2. Enable OAuth in Supabase
- Takes 2 minutes
- See `QUICK_FIX_OAUTH.md`

### 3. Login and Assign Roles
```sql
-- Admin
INSERT INTO admins (email, name) VALUES ('admin-demo@gmail.com', 'Admin Demo');

-- Teacher
INSERT INTO admins (email, name, role) VALUES ('teacher-demo@gmail.com', 'Teacher Demo', 'teacher');

-- Student (enroll through UI first)
UPDATE students SET approval_status = 'approved' WHERE email = 'student-demo@gmail.com';
```

### 4. Test All Portals
- Admin: http://localhost:3001/login
- Teacher: http://localhost:3001/login/teacher
- Student: http://localhost:3001/login/student

---

## 💡 Alternative: Create Demo Mode

If you don't want to use real OAuth for the hackathon demo, I can create a demo mode that:
- Shows a simple email input
- Automatically logs you in based on email pattern
- No real authentication needed

**Demo Mode Emails:**
```
admin@demo.local    → Admin Dashboard
teacher@demo.local  → Teacher Dashboard
student@demo.local  → Student Dashboard
```

Would you like me to implement this demo mode?

---

## 📊 Summary

### Current System (Production-Ready)
- ✅ Real OAuth with Gmail
- ✅ Secure authentication
- ✅ Role-based access control
- ⚠️ Requires OAuth setup (2 min)

### Demo Mode (Hackathon-Friendly)
- ✅ No OAuth needed
- ✅ Instant testing
- ✅ Simple email-based login
- ⚠️ Not secure (demo only)

**Recommendation:** Use real OAuth for hackathon demo - it's more impressive and only takes 2 minutes to set up!

---

## 🎯 Next Steps

1. **Enable OAuth** (2 min) - See `QUICK_FIX_OAUTH.md`
2. **Create 3 Gmail accounts** (or use existing)
3. **Login and assign roles** (SQL commands above)
4. **Test all portals** (3 different dashboards)
5. **Prepare demo script** (show all features)

**Total setup time: 10 minutes** ⏱️

---

**Need help? Check these files:**
- `QUICK_FIX_OAUTH.md` - Enable OAuth
- `START_HERE_FINAL.md` - Complete guide
- `SERVERS_RESTARTED_READY.md` - System overview
