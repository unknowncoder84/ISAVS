# 🔐 Authentication System Implementation Plan

**Date**: January 17, 2026  
**Status**: Requirements Complete - Ready for Design Phase

---

## 📋 What You Requested

You want to add a complete authentication and authorization system with:

1. **Gmail Login** via Supabase Auth
2. **Three User Roles**: Admin, Teacher, Student
3. **Separate Portals** for each role
4. **Admin Features**:
   - Add/manage teachers
   - Approve/reject student registrations
5. **Teacher Features**:
   - Full access to all existing features
   - Can enroll students (pending approval)
6. **Student Features**:
   - View own attendance records
   - View own profile
   - Limited access
7. **Session Persistence**: Stay logged in across browser sessions
8. **Approval Workflow**: Students must be approved before they can verify attendance

---

## ✅ Requirements Document Created

I've created a comprehensive requirements document at:
**`.kiro/specs/auth-system/requirements.md`**

This document includes:
- 10 detailed requirements with acceptance criteria
- Database schema requirements
- API endpoint specifications
- User flows for each role
- Security requirements
- Success criteria

---

## 🎯 What Needs to Be Built

### 1. Database Changes
```sql
-- New tables
- users (email, role, supabase_user_id)
- teachers (user_id, department, active)

-- Updated tables
- students (add: user_id, approval_status, approved_by)
```

### 2. Backend (Python/FastAPI)
```
New endpoints:
- POST /api/auth/login
- POST /api/auth/register
- GET /api/auth/me
- POST /api/auth/logout
- GET /api/admin/teachers
- POST /api/admin/teachers
- PUT /api/admin/teachers/:id
- GET /api/admin/students/pending
- PUT /api/admin/students/:id/approve
- PUT /api/admin/students/:id/reject
- GET /api/student/attendance
- GET /api/student/profile

New middleware:
- JWT token verification
- Role-based access control
```

### 3. Frontend (React/TypeScript)
```
New pages:
- /login - Gmail OAuth login
- /register - Student registration
- /admin - Admin portal
- /teacher - Teacher portal (existing dashboard)
- /student - Student portal

New components:
- LoginPage
- RegisterPage
- AdminDashboard
- TeacherManagement
- StudentApproval
- StudentPortal
- ProtectedRoute
- RoleGuard

Updated components:
- App.tsx (add routing and auth)
- All existing components (add auth checks)
```

### 4. Supabase Configuration
```
- Enable Gmail OAuth provider
- Configure redirect URLs
- Set up Row Level Security (RLS)
- Create auth policies
```

---

## 📊 Implementation Estimate

This is a **LARGE** feature that will take significant time:

### Phase 1: Database & Auth Setup (2-3 hours)
- Create new tables
- Set up Supabase Auth
- Configure Gmail OAuth
- Create migration scripts

### Phase 2: Backend API (3-4 hours)
- Auth endpoints
- Admin endpoints
- Student endpoints
- Middleware and guards
- Update existing endpoints

### Phase 3: Frontend Auth (2-3 hours)
- Login page
- Register page
- Auth context/hooks
- Protected routes
- Session persistence

### Phase 4: Admin Portal (2-3 hours)
- Teacher management UI
- Student approval UI
- Admin dashboard

### Phase 5: Student Portal (2-3 hours)
- Student dashboard
- Attendance history
- Profile view

### Phase 6: Integration & Testing (2-3 hours)
- Connect all pieces
- Test all user flows
- Fix bugs
- Update existing features

**Total Estimate**: 13-19 hours of development

---

## 🚀 Next Steps

### Option 1: Create Full Spec (Recommended)
Let me create the complete design and task list:
1. Design document with architecture
2. Task list with step-by-step implementation
3. Then we implement together

### Option 2: Start Implementation Now
We can start building immediately, but this is risky without proper planning for such a large feature.

### Option 3: Incremental Approach
Build in smaller phases:
1. First: Basic Gmail login
2. Then: Role-based routing
3. Then: Admin portal
4. Then: Student portal
5. Finally: Approval workflow

---

## ⚠️ Important Considerations

### 1. Breaking Changes
This will require changes to:
- All existing API endpoints (add auth)
- All existing frontend pages (add auth checks)
- Database schema (add user tables)
- Enrollment flow (add approval step)

### 2. Data Migration
Existing students need to be:
- Linked to user accounts
- Set to 'approved' status
- Given default credentials

### 3. Supabase Setup
You'll need to:
- Enable Gmail OAuth in Supabase dashboard
- Configure OAuth redirect URLs
- Set up environment variables
- Test OAuth flow

### 4. Testing
Each role needs thorough testing:
- Admin can manage teachers ✓
- Admin can approve students ✓
- Teachers have full access ✓
- Students have limited access ✓
- Unapproved students blocked ✓
- Sessions persist ✓

---

## 🎨 UI Design Notes

### Login Page
```
┌─────────────────────────────────┐
│                                 │
│         ISAVS Logo              │
│                                 │
│   Intelligent Student           │
│   Attendance Verification       │
│                                 │
│   ┌─────────────────────────┐  │
│   │  🔐 Login with Gmail    │  │
│   └─────────────────────────┘  │
│                                 │
│   New student? Register here    │
│                                 │
└─────────────────────────────────┘
```

### Admin Portal
```
┌─────────────────────────────────┐
│ Admin Dashboard                 │
├─────────────────────────────────┤
│ Tabs: Teachers | Students       │
├─────────────────────────────────┤
│                                 │
│ Pending Student Approvals (5)   │
│ ┌─────────────────────────────┐ │
│ │ John Doe - ID: 12345        │ │
│ │ [Approve] [Reject]          │ │
│ └─────────────────────────────┘ │
│                                 │
│ Teachers (12)                   │
│ ┌─────────────────────────────┐ │
│ │ Dr. Smith - Active          │ │
│ │ [Edit] [Deactivate]         │ │
│ └─────────────────────────────┘ │
│                                 │
└─────────────────────────────────┘
```

### Student Portal
```
┌─────────────────────────────────┐
│ Student Dashboard               │
├─────────────────────────────────┤
│ Welcome, John Doe!              │
│ Student ID: 12345               │
│ Status: ✓ Approved              │
├─────────────────────────────────┤
│                                 │
│ My Attendance History           │
│ ┌─────────────────────────────┐ │
│ │ Jan 17 - CS101 - ✓ Present │ │
│ │ Jan 16 - MATH201 - ✓ Present│ │
│ │ Jan 15 - CS101 - ✗ Absent  │ │
│ └─────────────────────────────┘ │
│                                 │
│ Attendance Rate: 85%            │
│                                 │
└─────────────────────────────────┘
```

---

## 🔒 Security Checklist

- [ ] Supabase JWT tokens verified on all API calls
- [ ] Role-based middleware on all protected routes
- [ ] Students can only access their own data
- [ ] Admin/Teacher routes reject student access
- [ ] Session tokens stored securely
- [ ] CORS configured correctly
- [ ] SQL injection prevention (parameterized queries)
- [ ] XSS prevention (sanitize inputs)
- [ ] CSRF protection (if using cookies)
- [ ] Rate limiting on auth endpoints

---

## 📚 Documentation Needed

After implementation:
- [ ] Admin user guide
- [ ] Teacher user guide
- [ ] Student user guide
- [ ] API documentation
- [ ] Deployment guide
- [ ] Troubleshooting guide

---

## ❓ Questions to Consider

1. **Who is the first admin?**
   - Manual database insert?
   - Hardcoded email?
   - First user becomes admin?

2. **Can teachers approve students?**
   - Or only admins?

3. **Can students update their profile?**
   - Change name?
   - Update photo?

4. **What happens to existing students?**
   - Auto-approve all?
   - Require re-registration?

5. **Email notifications?**
   - When student approved?
   - When teacher added?

---

## 🎯 Recommendation

Given the complexity of this feature, I recommend:

1. **Review the requirements document** (`.kiro/specs/auth-system/requirements.md`)
2. **Let me create the design document** with detailed architecture
3. **Let me create the task list** with step-by-step implementation
4. **Then we implement together** in phases

This ensures:
- ✅ Nothing is missed
- ✅ Proper planning
- ✅ Clear implementation path
- ✅ Easier debugging
- ✅ Better code quality

---

## 🚀 Ready to Proceed?

**Option A**: Let me create the design and task list (recommended)
**Option B**: Start implementing now (risky but faster)
**Option C**: Build incrementally in small phases

Which approach would you like to take?

---

**Status**: Requirements complete, awaiting your decision on next steps! 📋
