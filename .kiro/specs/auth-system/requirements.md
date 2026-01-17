# Requirements Document - Authentication & Role-Based Access Control

## Introduction

This document outlines the requirements for implementing a comprehensive authentication and authorization system for ISAVS (Intelligent Student Attendance Verification System). The system will support three user roles: Admin, Teacher, and Student, each with distinct portals and permissions. Authentication will be handled via Supabase Auth with Gmail login.

## Glossary

- **Admin**: System administrator with full access to manage teachers and approve student registrations
- **Teacher**: Faculty member who can manage classes, sessions, and view attendance reports
- **Student**: Enrolled student who can verify attendance and view their own records
- **Supabase Auth**: Authentication service provided by Supabase for user management
- **Role-Based Access Control (RBAC)**: Security paradigm that restricts system access based on user roles
- **Session Persistence**: Maintaining user login state across browser sessions
- **Portal**: Role-specific user interface with appropriate features and permissions

## Requirements

### Requirement 1: User Authentication with Supabase

**User Story:** As a user, I want to log in using my Gmail account through Supabase Auth, so that I can access the system securely without managing passwords.

#### Acceptance Criteria

1. WHEN a user clicks "Login with Gmail" THEN the system SHALL redirect to Supabase Auth Gmail OAuth flow
2. WHEN Gmail authentication succeeds THEN the system SHALL create or retrieve the user record from Supabase
3. WHEN a user logs in successfully THEN the system SHALL store the authentication token in local storage
4. WHEN a user returns to the application THEN the system SHALL automatically restore their session if the token is valid
5. WHEN a user clicks "Logout" THEN the system SHALL clear the authentication token and redirect to login page

---

### Requirement 2: Admin Portal and Teacher Management

**User Story:** As an admin, I want to manage teacher accounts, so that I can control who has faculty access to the system.

#### Acceptance Criteria

1. WHEN an admin logs in THEN the system SHALL display the admin portal with teacher management interface
2. WHEN an admin adds a new teacher THEN the system SHALL create a teacher account with email, name, and role='teacher'
3. WHEN an admin views the teacher list THEN the system SHALL display all teachers with their status and details
4. WHEN an admin deactivates a teacher THEN the system SHALL prevent that teacher from accessing the system
5. WHEN an admin reactivates a teacher THEN the system SHALL restore that teacher's access

---

### Requirement 3: Admin Portal and Student Approval

**User Story:** As an admin, I want to approve or reject student registration requests, so that only authorized students can use the system.

#### Acceptance Criteria

1. WHEN an admin views pending registrations THEN the system SHALL display all students with status='pending'
2. WHEN an admin approves a student THEN the system SHALL update student status to 'approved' and enable their account
3. WHEN an admin rejects a student THEN the system SHALL update student status to 'rejected' and prevent login
4. WHEN a student with status='pending' or 'rejected' attempts to verify attendance THEN the system SHALL deny access
5. WHEN an admin searches for students THEN the system SHALL filter by name, email, or student ID

---

### Requirement 4: Teacher Portal with Full Access

**User Story:** As a teacher, I want access to all attendance management features, so that I can manage my classes effectively.

#### Acceptance Criteria

1. WHEN a teacher logs in THEN the system SHALL display the teacher portal with dashboard, sessions, and reports
2. WHEN a teacher creates a session THEN the system SHALL generate OTPs for all approved students in that class
3. WHEN a teacher views attendance reports THEN the system SHALL display all attendance records with filtering options
4. WHEN a teacher enrolls a new student THEN the system SHALL create the student record with status='pending'
5. WHEN a teacher views anomalies THEN the system SHALL display all security alerts and proxy attempts

---

### Requirement 5: Student Portal with Limited Access

**User Story:** As a student, I want to view my own attendance records and profile, so that I can track my attendance history.

#### Acceptance Criteria

1. WHEN a student logs in THEN the system SHALL display the student portal with their profile and attendance history
2. WHEN a student views their profile THEN the system SHALL display their name, email, student ID, and enrollment status
3. WHEN a student views attendance history THEN the system SHALL display only their own attendance records
4. WHEN a student attempts to access teacher features THEN the system SHALL deny access and show error message
5. WHEN a student's account is not approved THEN the system SHALL display "Pending Approval" message

---

### Requirement 6: Student Registration Flow

**User Story:** As a new student, I want to register with my Gmail and provide my details, so that I can request access to the system.

#### Acceptance Criteria

1. WHEN a new user logs in with Gmail THEN the system SHALL check if they have an existing account
2. WHEN a new user has no account THEN the system SHALL display the registration form
3. WHEN a student submits registration THEN the system SHALL require name, student ID, and face enrollment
4. WHEN a student completes registration THEN the system SHALL set their status to 'pending' and notify admins
5. WHEN a student with pending status logs in THEN the system SHALL display "Awaiting admin approval" message

---

### Requirement 7: Role-Based Access Control

**User Story:** As a system, I want to enforce role-based permissions, so that users can only access features appropriate to their role.

#### Acceptance Criteria

1. WHEN a user accesses a route THEN the system SHALL verify their role matches the required permission
2. WHEN an unauthorized user attempts to access a protected route THEN the system SHALL redirect to their appropriate portal
3. WHEN an admin accesses any route THEN the system SHALL allow access to all features
4. WHEN a teacher accesses student-only routes THEN the system SHALL deny access
5. WHEN a student accesses admin or teacher routes THEN the system SHALL deny access

---

### Requirement 8: Session Persistence

**User Story:** As a user, I want my login session to persist across browser sessions, so that I don't have to log in every time.

#### Acceptance Criteria

1. WHEN a user logs in THEN the system SHALL store the Supabase session token in local storage
2. WHEN a user closes and reopens the browser THEN the system SHALL restore their session automatically
3. WHEN a session token expires THEN the system SHALL redirect to login page
4. WHEN a user logs out THEN the system SHALL clear all stored session data
5. WHEN a user's role changes THEN the system SHALL refresh their permissions on next page load

---

### Requirement 9: Separate Portal Interfaces

**User Story:** As a user, I want a portal interface tailored to my role, so that I see only relevant features and information.

#### Acceptance Criteria

1. WHEN an admin logs in THEN the system SHALL display admin portal at '/admin' route
2. WHEN a teacher logs in THEN the system SHALL display teacher portal at '/teacher' route
3. WHEN a student logs in THEN the system SHALL display student portal at '/student' route
4. WHEN a user navigates to root '/' THEN the system SHALL redirect to their role-specific portal
5. WHEN a user accesses a portal for a different role THEN the system SHALL redirect to their own portal

---

### Requirement 10: Database Schema for Users and Roles

**User Story:** As a system, I want to store user information with roles, so that I can manage authentication and authorization.

#### Acceptance Criteria

1. WHEN a user is created THEN the system SHALL store email, name, role, and Supabase user ID
2. WHEN a student is created THEN the system SHALL include student_id_card_number and approval_status
3. WHEN a teacher is created THEN the system SHALL include department and active status
4. WHEN an admin queries users THEN the system SHALL support filtering by role and status
5. WHEN a user's role is updated THEN the system SHALL enforce the new permissions immediately

---

## Database Schema Requirements

### Users Table
```sql
- id: SERIAL PRIMARY KEY
- supabase_user_id: UUID UNIQUE (from Supabase Auth)
- email: VARCHAR(255) UNIQUE
- name: VARCHAR(255)
- role: ENUM('admin', 'teacher', 'student')
- created_at: TIMESTAMPTZ
- updated_at: TIMESTAMPTZ
```

### Teachers Table (extends users)
```sql
- id: SERIAL PRIMARY KEY
- user_id: INTEGER REFERENCES users(id)
- department: VARCHAR(255)
- active: BOOLEAN DEFAULT TRUE
- created_at: TIMESTAMPTZ
```

### Students Table (updated)
```sql
- Add: user_id: INTEGER REFERENCES users(id)
- Add: approval_status: ENUM('pending', 'approved', 'rejected')
- Add: approved_by: INTEGER REFERENCES users(id)
- Add: approved_at: TIMESTAMPTZ
```

---

## Technical Requirements

### Frontend Routes
- `/login` - Login page with Gmail OAuth
- `/register` - Student registration form
- `/admin` - Admin portal (teacher management, student approvals)
- `/teacher` - Teacher portal (existing faculty dashboard)
- `/student` - Student portal (view own attendance)
- `/` - Root redirects to role-specific portal

### Backend Endpoints
- `POST /api/auth/login` - Verify Supabase token and get user role
- `POST /api/auth/register` - Register new student
- `GET /api/auth/me` - Get current user info
- `POST /api/auth/logout` - Clear session
- `GET /api/admin/teachers` - List all teachers
- `POST /api/admin/teachers` - Add new teacher
- `PUT /api/admin/teachers/:id` - Update teacher
- `GET /api/admin/students/pending` - List pending students
- `PUT /api/admin/students/:id/approve` - Approve student
- `PUT /api/admin/students/:id/reject` - Reject student
- `GET /api/student/attendance` - Get own attendance records
- `GET /api/student/profile` - Get own profile

### Security Requirements
- All API endpoints must verify Supabase JWT token
- Role-based middleware must check user permissions
- Student data must be filtered by user_id for students
- Admin and teacher routes must reject student access
- Session tokens must be stored securely (httpOnly cookies or secure localStorage)

---

## User Flows

### Admin Flow
1. Login with Gmail → Admin Portal
2. View pending students → Approve/Reject
3. View teachers → Add/Edit/Deactivate
4. Access all teacher features

### Teacher Flow
1. Login with Gmail → Teacher Portal
2. Create sessions → Generate OTPs
3. Enroll students → Set status='pending'
4. View reports → All students
5. Manage classes

### Student Flow
1. Login with Gmail → Check if registered
2. If not registered → Registration form → Submit → Pending approval
3. If pending → "Awaiting approval" message
4. If approved → Student Portal → View own attendance
5. Verify attendance via kiosk (existing flow)

---

## Success Criteria

1. ✅ Users can log in with Gmail via Supabase Auth
2. ✅ Three separate portals for Admin, Teacher, Student
3. ✅ Admin can manage teachers and approve students
4. ✅ Teachers have full access to existing features
5. ✅ Students can only view their own data
6. ✅ Sessions persist across browser restarts
7. ✅ Role-based access control enforced on all routes
8. ✅ Unapproved students cannot verify attendance
9. ✅ All existing features continue to work
10. ✅ UI is consistent with campus-connect theme
