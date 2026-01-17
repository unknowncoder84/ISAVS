# Design Document - Authentication & Role-Based Access Control System

## Overview

This document outlines the technical design for implementing a comprehensive authentication and authorization system for ISAVS. The system will use Supabase Auth for Gmail OAuth, implement role-based access control (RBAC) with three user roles (Admin, Teacher, Student), and provide separate portal interfaces for each role.

**Key Features**:
- Gmail OAuth authentication via Supabase
- Three user roles with distinct permissions
- Separate portal UIs for each role
- Admin approval workflow for students
- Session persistence across browser sessions
- Secure API with JWT token verification
- Integration with existing attendance system

---

## Architecture

### High-Level Architecture

```
┌─────────────────────────────────────────────────────────────┐
│                         Frontend (React)                     │
├─────────────────────────────────────────────────────────────┤
│  Login Page  │  Admin Portal  │  Teacher Portal  │  Student │
│              │  - Teachers    │  - Dashboard     │  Portal  │
│              │  - Students    │  - Sessions      │  - Profile│
│              │  - Approvals   │  - Reports       │  - History│
└──────────────┴────────────────┴──────────────────┴──────────┘
                              │
                              │ HTTPS/REST API
                              │ JWT Token Auth
                              ▼
┌─────────────────────────────────────────────────────────────┐
│                      Backend (FastAPI)                       │
├─────────────────────────────────────────────────────────────┤
│  Auth Middleware  │  Role Guards  │  API Endpoints          │
│  - JWT Verify     │  - Admin      │  - Auth                 │
│  - Token Refresh  │  - Teacher    │  - Admin                │
│  - Session Mgmt   │  - Student    │  - Teacher              │
│                   │               │  - Student              │
└───────────────────┴───────────────┴─────────────────────────┘
                              │
                              │ SQL Queries
                              ▼
┌─────────────────────────────────────────────────────────────┐
│                    Supabase (PostgreSQL)                     │
├─────────────────────────────────────────────────────────────┤
│  Auth Service     │  Database Tables                         │
│  - Gmail OAuth    │  - users                                 │
│  - JWT Tokens     │  - teachers                              │
│  - User Mgmt      │  - students (updated)                    │
│                   │  - attendance (existing)                 │
└───────────────────┴──────────────────────────────────────────┘
```

### Authentication Flow

```
User Flow:
1. User clicks "Login with Gmail"
2. Redirect to Supabase Auth (Gmail OAuth)
3. User authorizes with Google
4. Supabase returns JWT token
5. Frontend stores token in localStorage
6. Frontend calls /api/auth/me to get user role
7. Redirect to role-specific portal

API Request Flow:
1. Frontend sends request with JWT token in header
2. Backend middleware verifies token with Supabase
3. Backend extracts user_id from token
4. Backend queries database for user role
5. Backend checks role permissions
6. If authorized → Process request
7. If unauthorized → Return 403 Forbidden
```

---

## Components and Interfaces

### Frontend Components

#### 1. Authentication Components

**LoginPage** (`frontend/src/pages/LoginPage.tsx`)
```typescript
interface LoginPageProps {}

// Features:
// - Supabase Auth UI for Gmail login
// - Redirect to role-specific portal after login
// - Link to student registration
// - Campus-connect gradient theme
```

**RegisterPage** (`frontend/src/pages/RegisterPage.tsx`)
```typescript
interface RegisterPageProps {}

// Features:
// - Student registration form
// - Name, student ID, email (pre-filled from Gmail)
// - Face enrollment (webcam capture)
// - Submit for admin approval
```

**ProtectedRoute** (`frontend/src/components/ProtectedRoute.tsx`)
```typescript
interface ProtectedRouteProps {
  children: React.ReactNode;
  requiredRole?: 'admin' | 'teacher' | 'student';
  allowedRoles?: Array<'admin' | 'teacher' | 'student'>;
}

// Features:
// - Check if user is authenticated
// - Check if user has required role
// - Redirect to login if not authenticated
// - Redirect to appropriate portal if wrong role
```

#### 2. Admin Portal Components

**AdminDashboard** (`frontend/src/pages/AdminDashboard.tsx`)
```typescript
interface AdminDashboardProps {}

// Features:
// - Overview stats (pending students, active teachers)
// - Quick actions (approve students, add teachers)
// - Navigation to teacher/student management
```

**TeacherManagement** (`frontend/src/components/admin/TeacherManagement.tsx`)
```typescript
interface TeacherManagementProps {}

// Features:
// - List all teachers
// - Add new teacher (email, name, department)
// - Edit teacher details
// - Activate/deactivate teacher accounts
// - Search and filter
```

**StudentApproval** (`frontend/src/components/admin/StudentApproval.tsx`)
```typescript
interface StudentApprovalProps {}

// Features:
// - List pending student registrations
// - View student details and face photo
// - Approve/reject with reason
// - Bulk approve
// - Search and filter
```

#### 3. Teacher Portal Components

**TeacherDashboard** (`frontend/src/pages/TeacherDashboard.tsx`)
```typescript
// Existing FacultyDashboard component
// Add role check to ensure only teachers/admins can access
```

#### 4. Student Portal Components

**StudentDashboard** (`frontend/src/pages/StudentDashboard.tsx`)
```typescript
interface StudentDashboardProps {}

// Features:
// - Student profile (name, ID, photo, status)
// - Attendance history (own records only)
// - Attendance rate statistics
// - Upcoming sessions
```

**StudentProfile** (`frontend/src/components/student/StudentProfile.tsx`)
```typescript
interface StudentProfileProps {
  student: Student;
}

// Features:
// - Display student information
// - Show approval status
// - Edit profile (limited fields)
```

**AttendanceHistory** (`frontend/src/components/student/AttendanceHistory.tsx`)
```typescript
interface AttendanceHistoryProps {
  studentId: number;
}

// Features:
// - List attendance records
// - Filter by date range
// - Show verification details
// - Export to CSV
```

#### 5. Shared Components

**AuthContext** (`frontend/src/contexts/AuthContext.tsx`)
```typescript
interface AuthContextType {
  user: User | null;
  loading: boolean;
  login: (token: string) => Promise<void>;
  logout: () => Promise<void>;
  refreshUser: () => Promise<void>;
}

// Features:
// - Manage authentication state
// - Store/retrieve JWT token
// - Provide user info to components
// - Handle login/logout
```

---

### Backend Services

#### 1. Authentication Service

**auth_service.py** (`backend/app/services/auth_service.py`)
```python
class AuthService:
    def verify_token(self, token: str) -> dict:
        """Verify Supabase JWT token"""
        
    def get_user_by_supabase_id(self, supabase_id: str) -> User:
        """Get user from database by Supabase user ID"""
        
    def create_user(self, email: str, name: str, role: str, supabase_id: str) -> User:
        """Create new user in database"""
        
    def get_user_role(self, user_id: int) -> str:
        """Get user role"""
```

#### 2. Admin Service

**admin_service.py** (`backend/app/services/admin_service.py`)
```python
class AdminService:
    def list_teachers(self) -> List[Teacher]:
        """List all teachers"""
        
    def create_teacher(self, user_id: int, department: str) -> Teacher:
        """Create teacher record"""
        
    def update_teacher(self, teacher_id: int, data: dict) -> Teacher:
        """Update teacher details"""
        
    def deactivate_teacher(self, teacher_id: int) -> bool:
        """Deactivate teacher account"""
        
    def list_pending_students(self) -> List[Student]:
        """List students with status='pending'"""
        
    def approve_student(self, student_id: int, admin_id: int) -> Student:
        """Approve student registration"""
        
    def reject_student(self, student_id: int, admin_id: int, reason: str) -> Student:
        """Reject student registration"""
```

#### 3. Student Service

**student_service.py** (`backend/app/services/student_service.py`)
```python
class StudentService:
    def get_student_by_user_id(self, user_id: int) -> Student:
        """Get student by user ID"""
        
    def get_attendance_history(self, student_id: int) -> List[AttendanceRecord]:
        """Get student's attendance records"""
        
    def get_attendance_stats(self, student_id: int) -> dict:
        """Calculate attendance statistics"""
        
    def update_profile(self, student_id: int, data: dict) -> Student:
        """Update student profile"""
```

#### 4. Middleware

**auth_middleware.py** (`backend/app/middleware/auth_middleware.py`)
```python
async def verify_jwt_token(request: Request, call_next):
    """Middleware to verify JWT token on all protected routes"""
    
async def require_role(required_role: str):
    """Dependency to check user role"""
    
async def get_current_user(token: str = Depends(oauth2_scheme)):
    """Dependency to get current authenticated user"""
```

---

## Data Models

### Database Schema

#### 1. Users Table (New)

```sql
CREATE TABLE users (
    id SERIAL PRIMARY KEY,
    supabase_user_id UUID UNIQUE NOT NULL,
    email VARCHAR(255) UNIQUE NOT NULL,
    name VARCHAR(255) NOT NULL,
    role VARCHAR(20) NOT NULL CHECK (role IN ('admin', 'teacher', 'student')),
    created_at TIMESTAMPTZ DEFAULT NOW(),
    updated_at TIMESTAMPTZ DEFAULT NOW()
);

CREATE INDEX idx_users_supabase_id ON users(supabase_user_id);
CREATE INDEX idx_users_email ON users(email);
CREATE INDEX idx_users_role ON users(role);
```

#### 2. Teachers Table (New)

```sql
CREATE TABLE teachers (
    id SERIAL PRIMARY KEY,
    user_id INTEGER UNIQUE REFERENCES users(id) ON DELETE CASCADE,
    department VARCHAR(255),
    active BOOLEAN DEFAULT TRUE,
    created_at TIMESTAMPTZ DEFAULT NOW(),
    updated_at TIMESTAMPTZ DEFAULT NOW()
);

CREATE INDEX idx_teachers_user_id ON teachers(user_id);
CREATE INDEX idx_teachers_active ON teachers(active);
```

#### 3. Students Table (Updated)

```sql
-- Add new columns to existing students table
ALTER TABLE students 
ADD COLUMN user_id INTEGER UNIQUE REFERENCES users(id) ON DELETE SET NULL,
ADD COLUMN approval_status VARCHAR(20) DEFAULT 'pending' 
    CHECK (approval_status IN ('pending', 'approved', 'rejected')),
ADD COLUMN approved_by INTEGER REFERENCES users(id) ON DELETE SET NULL,
ADD COLUMN approved_at TIMESTAMPTZ,
ADD COLUMN rejection_reason TEXT;

CREATE INDEX idx_students_user_id ON students(user_id);
CREATE INDEX idx_students_approval_status ON students(approval_status);
```

### Pydantic Models

#### Request/Response Models

```python
# Auth Models
class LoginRequest(BaseModel):
    token: str  # Supabase JWT token

class LoginResponse(BaseModel):
    success: bool
    user: UserResponse
    message: str

class RegisterRequest(BaseModel):
    name: str
    student_id_card_number: str
    face_image: str  # base64
    # email comes from Supabase token

class UserResponse(BaseModel):
    id: int
    email: str
    name: str
    role: str
    created_at: datetime

# Admin Models
class CreateTeacherRequest(BaseModel):
    email: str
    name: str
    department: str

class TeacherResponse(BaseModel):
    id: int
    user_id: int
    email: str
    name: str
    department: str
    active: bool
    created_at: datetime

class ApproveStudentRequest(BaseModel):
    student_id: int

class RejectStudentRequest(BaseModel):
    student_id: int
    reason: str

class PendingStudentResponse(BaseModel):
    id: int
    name: str
    student_id_card_number: str
    email: str
    face_image_base64: str
    created_at: datetime
    approval_status: str

# Student Models
class StudentProfileResponse(BaseModel):
    id: int
    name: str
    student_id_card_number: str
    email: str
    approval_status: str
    created_at: datetime

class AttendanceRecordResponse(BaseModel):
    id: int
    session_id: int
    class_id: str
    timestamp: datetime
    verification_status: str
    face_confidence: float
```

---

## API Endpoints

### Authentication Endpoints

```python
# POST /api/auth/login
# Verify Supabase token and return user info
Request: { "token": "jwt_token" }
Response: { "success": true, "user": {...}, "message": "Login successful" }

# POST /api/auth/register
# Register new student (requires valid Supabase token)
Request: { "name": "...", "student_id_card_number": "...", "face_image": "..." }
Response: { "success": true, "student_id": 123, "message": "Registration submitted" }

# GET /api/auth/me
# Get current user info
Headers: { "Authorization": "Bearer jwt_token" }
Response: { "id": 1, "email": "...", "name": "...", "role": "student" }

# POST /api/auth/logout
# Logout (clear session)
Response: { "success": true, "message": "Logged out" }
```

### Admin Endpoints

```python
# GET /api/admin/teachers
# List all teachers (admin only)
Response: { "teachers": [...] }

# POST /api/admin/teachers
# Create new teacher (admin only)
Request: { "email": "...", "name": "...", "department": "..." }
Response: { "success": true, "teacher": {...} }

# PUT /api/admin/teachers/{teacher_id}
# Update teacher (admin only)
Request: { "department": "...", "active": true }
Response: { "success": true, "teacher": {...} }

# GET /api/admin/students/pending
# List pending student registrations (admin only)
Response: { "students": [...] }

# PUT /api/admin/students/{student_id}/approve
# Approve student (admin only)
Response: { "success": true, "student": {...} }

# PUT /api/admin/students/{student_id}/reject
# Reject student (admin only)
Request: { "reason": "..." }
Response: { "success": true, "student": {...} }
```

### Student Endpoints

```python
# GET /api/student/profile
# Get own profile (student only)
Response: { "id": 1, "name": "...", "student_id": "...", "status": "approved" }

# GET /api/student/attendance
# Get own attendance history (student only)
Query: ?start_date=2026-01-01&end_date=2026-01-31
Response: { "records": [...], "stats": {...} }

# PUT /api/student/profile
# Update own profile (student only, limited fields)
Request: { "name": "..." }
Response: { "success": true, "student": {...} }
```

### Updated Existing Endpoints

```python
# POST /api/enroll
# Add approval_status='pending' for new students
# Only teachers/admins can enroll

# POST /api/verify
# Check if student is approved before allowing verification
# Reject if approval_status != 'approved'
```

---

## Security

### Authentication Flow

1. **Login**:
   - User authenticates with Gmail via Supabase
   - Supabase returns JWT token
   - Frontend stores token in localStorage
   - Frontend calls `/api/auth/me` to get user role
   - Redirect to role-specific portal

2. **API Requests**:
   - Frontend includes JWT token in Authorization header
   - Backend middleware verifies token with Supabase
   - Backend extracts user_id from token
   - Backend queries database for user role
   - Backend checks role permissions

3. **Session Persistence**:
   - JWT token stored in localStorage
   - Token includes expiration time
   - Frontend checks token validity on app load
   - Auto-refresh token before expiration
   - Redirect to login if token expired

### Authorization Rules

```python
# Role Hierarchy
admin > teacher > student

# Permissions Matrix
┌──────────────────┬───────┬─────────┬─────────┐
│ Action           │ Admin │ Teacher │ Student │
├──────────────────┼───────┼─────────┼─────────┤
│ Manage Teachers  │   ✓   │    ✗    │    ✗    │
│ Approve Students │   ✓   │    ✗    │    ✗    │
│ Create Sessions  │   ✓   │    ✓    │    ✗    │
│ View All Reports │   ✓   │    ✓    │    ✗    │
│ Enroll Students  │   ✓   │    ✓    │    ✗    │
│ View Own Data    │   ✓   │    ✓    │    ✓    │
│ Verify Attendance│   ✗   │    ✗    │    ✓*   │
└──────────────────┴───────┴─────────┴─────────┘
* Only if approved
```

### Security Measures

1. **JWT Token Verification**:
   - Verify signature with Supabase public key
   - Check expiration time
   - Validate issuer and audience

2. **Role-Based Access Control**:
   - Middleware checks user role on every request
   - Database queries filtered by user_id for students
   - Admin/teacher routes reject student access

3. **Data Isolation**:
   - Students can only access their own data
   - Teachers can access all students in their classes
   - Admins can access all data

4. **Input Validation**:
   - Pydantic models validate all inputs
   - SQL injection prevention (parameterized queries)
   - XSS prevention (sanitize outputs)

5. **Rate Limiting**:
   - Limit login attempts (5 per minute)
   - Limit API requests (100 per minute per user)
   - Limit registration attempts (3 per hour per IP)

---

## Error Handling

### Error Response Format

```python
class ErrorResponse(BaseModel):
    success: bool = False
    error: str
    code: str
    details: Optional[dict] = None

# Example errors:
{
    "success": false,
    "error": "Unauthorized",
    "code": "AUTH_REQUIRED",
    "details": {"message": "Please log in to access this resource"}
}

{
    "success": false,
    "error": "Forbidden",
    "code": "INSUFFICIENT_PERMISSIONS",
    "details": {"required_role": "admin", "user_role": "student"}
}

{
    "success": false,
    "error": "Not Approved",
    "code": "STUDENT_NOT_APPROVED",
    "details": {"status": "pending", "message": "Your registration is pending admin approval"}
}
```

### Error Codes

```python
# Authentication Errors
AUTH_REQUIRED = "Authentication required"
INVALID_TOKEN = "Invalid or expired token"
TOKEN_EXPIRED = "Token has expired"

# Authorization Errors
INSUFFICIENT_PERMISSIONS = "Insufficient permissions"
FORBIDDEN = "Access forbidden"

# Student Approval Errors
STUDENT_NOT_APPROVED = "Student not approved"
STUDENT_REJECTED = "Student registration rejected"

# Validation Errors
INVALID_INPUT = "Invalid input data"
MISSING_FIELD = "Required field missing"

# Resource Errors
NOT_FOUND = "Resource not found"
ALREADY_EXISTS = "Resource already exists"
```

---

## Testing Strategy

### Unit Tests

1. **Auth Service Tests**:
   - Token verification
   - User creation
   - Role retrieval

2. **Admin Service Tests**:
   - Teacher CRUD operations
   - Student approval/rejection
   - Permission checks

3. **Student Service Tests**:
   - Profile retrieval
   - Attendance history
   - Data isolation

4. **Middleware Tests**:
   - JWT verification
   - Role checking
   - Error handling

### Integration Tests

1. **Auth Flow Tests**:
   - Login with Gmail
   - Token storage
   - Session persistence
   - Logout

2. **Admin Flow Tests**:
   - Add teacher
   - Approve student
   - Reject student
   - View pending registrations

3. **Teacher Flow Tests**:
   - Access dashboard
   - Create session
   - View reports
   - Enroll student

4. **Student Flow Tests**:
   - Register
   - View profile
   - View attendance
   - Verify attendance (if approved)

### End-to-End Tests

1. **Complete User Journeys**:
   - New student registration → approval → verification
   - Admin adds teacher → teacher creates session
   - Student views attendance history

2. **Security Tests**:
   - Unauthorized access attempts
   - Role escalation attempts
   - Token tampering
   - SQL injection attempts

---

## Migration Strategy

### Phase 1: Database Migration

```sql
-- 1. Create new tables
CREATE TABLE users (...);
CREATE TABLE teachers (...);

-- 2. Update students table
ALTER TABLE students ADD COLUMN user_id ...;
ALTER TABLE students ADD COLUMN approval_status ...;

-- 3. Migrate existing data
-- Set all existing students to 'approved'
UPDATE students SET approval_status = 'approved';

-- 4. Create indexes
CREATE INDEX ...;
```

### Phase 2: Backend Migration

1. Add auth middleware
2. Add auth endpoints
3. Add admin endpoints
4. Add student endpoints
5. Update existing endpoints (add role checks)
6. Test all endpoints

### Phase 3: Frontend Migration

1. Add Supabase Auth
2. Create login/register pages
3. Create admin portal
4. Create student portal
5. Update existing pages (add auth checks)
6. Test all flows

### Phase 4: Data Migration

1. Create first admin user (manual)
2. Migrate existing students (set approved)
3. Create teacher accounts for existing faculty
4. Test with real data

---

## Deployment Checklist

### Supabase Configuration

- [ ] Enable Gmail OAuth provider
- [ ] Configure OAuth redirect URLs
- [ ] Set up Row Level Security (RLS) policies
- [ ] Create auth policies
- [ ] Test OAuth flow

### Backend Deployment

- [ ] Update environment variables
- [ ] Run database migrations
- [ ] Deploy new API endpoints
- [ ] Test API with Postman
- [ ] Monitor error logs

### Frontend Deployment

- [ ] Update Supabase config
- [ ] Build production bundle
- [ ] Deploy to hosting
- [ ] Test all user flows
- [ ] Monitor console errors

### Post-Deployment

- [ ] Create first admin user
- [ ] Test admin portal
- [ ] Test teacher portal
- [ ] Test student portal
- [ ] Monitor performance
- [ ] Gather user feedback

---

## Performance Considerations

### Database Optimization

1. **Indexes**:
   - Index on users.supabase_user_id
   - Index on users.email
   - Index on students.user_id
   - Index on students.approval_status

2. **Query Optimization**:
   - Use JOIN instead of multiple queries
   - Paginate large result sets
   - Cache frequently accessed data

3. **Connection Pooling**:
   - Use Supabase connection pooler
   - Configure pool size based on load

### Frontend Optimization

1. **Code Splitting**:
   - Lazy load portal components
   - Split by route

2. **Caching**:
   - Cache user info in context
   - Cache static data (teacher list, etc.)

3. **Optimistic Updates**:
   - Update UI immediately
   - Sync with backend in background

---

## Future Enhancements

1. **Email Notifications**:
   - Student approved/rejected
   - Teacher account created
   - Session reminders

2. **Two-Factor Authentication**:
   - SMS verification
   - Authenticator app

3. **Audit Logging**:
   - Track all admin actions
   - Log approval/rejection reasons
   - Monitor suspicious activity

4. **Advanced Permissions**:
   - Department-based access
   - Class-based access
   - Custom roles

5. **Mobile App Integration**:
   - Native mobile login
   - Biometric authentication
   - Push notifications

---

## Success Metrics

1. **Authentication**:
   - Login success rate > 95%
   - Token refresh success rate > 99%
   - Session persistence works 100%

2. **Authorization**:
   - Zero unauthorized access incidents
   - Role checks work 100%
   - Data isolation verified

3. **User Experience**:
   - Login time < 2 seconds
   - Portal load time < 1 second
   - Approval process < 24 hours

4. **System Performance**:
   - API response time < 200ms
   - Database query time < 50ms
   - Zero downtime during migration

---

**Design Status**: Complete and ready for implementation! 🎉
