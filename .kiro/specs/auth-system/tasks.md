# Implementation Plan - Authentication & Role-Based Access Control

This task list provides step-by-step instructions for implementing the authentication and authorization system. Tasks are organized in phases for incremental development.

---

## Phase 1: Database Setup & Supabase Configuration

- [ ] 1. Set up Supabase Auth
  - Enable Gmail OAuth provider in Supabase dashboard
  - Configure OAuth redirect URLs (http://localhost:5173/auth/callback, production URL)
  - Copy Supabase URL and anon key to environment variables
  - Test Gmail OAuth flow manually
  - _Requirements: 1.1, 1.2_

- [ ] 2. Create database migration script
  - Create `backend/migration_auth_system.sql` file
  - Add CREATE TABLE statements for users and teachers
  - Add ALTER TABLE statements for students (user_id, approval_status, approved_by, approved_at, rejection_reason)
  - Add indexes for performance
  - Add foreign key constraints
  - _Requirements: 10.1, 10.2, 10.3_

- [ ] 3. Run database migration
  - Execute migration script in Supabase SQL Editor
  - Verify tables created successfully
  - Verify indexes created
  - Test foreign key constraints
  - _Requirements: 10.1, 10.2, 10.3_

- [ ] 4. Create first admin user
  - Manually insert admin user into users table
  - Use your Gmail email as admin
  - Set role='admin'
  - Generate UUID for supabase_user_id (will be updated on first login)
  - _Requirements: 2.1_

- [ ] 5. Update existing students to approved status
  - Run UPDATE query to set approval_status='approved' for all existing students
  - This ensures existing students can continue using the system
  - _Requirements: 3.4_

---

## Phase 2: Backend Authentication

- [ ] 6. Install Supabase Python client
  - Add `supabase` to requirements.txt
  - Run `pip install supabase`
  - _Requirements: 1.1_

- [ ] 7. Create auth service
  - Create `backend/app/services/auth_service.py`
  - Implement `verify_token()` - verify Supabase JWT token
  - Implement `get_user_by_supabase_id()` - get user from database
  - Implement `create_user()` - create new user
  - Implement `get_user_role()` - get user role
  - _Requirements: 1.2, 1.3, 7.1_

- [ ] 8. Create auth middleware
  - Create `backend/app/middleware/auth_middleware.py`
  - Implement `verify_jwt_token()` - middleware to verify JWT on all requests
  - Implement `get_current_user()` - dependency to get authenticated user
  - Implement `require_role()` - dependency to check user role
  - _Requirements: 7.1, 7.2, 7.3_

- [ ] 9. Create auth models
  - Create `backend/app/models/auth.py`
  - Define LoginRequest, LoginResponse models
  - Define RegisterRequest model
  - Define UserResponse model
  - _Requirements: 1.1, 6.1_

- [ ] 10. Create auth endpoints
  - Update `backend/app/api/endpoints.py`
  - Add `POST /api/auth/login` - verify token and return user info
  - Add `POST /api/auth/register` - register new student
  - Add `GET /api/auth/me` - get current user info
  - Add `POST /api/auth/logout` - logout (clear session)
  - _Requirements: 1.1, 1.2, 1.3, 6.1_

- [ ] 11. Test auth endpoints
  - Test login with valid Supabase token
  - Test login with invalid token
  - Test register new student
  - Test get current user
  - Test logout
  - _Requirements: 1.1, 1.2, 1.3, 6.1_

---

## Phase 3: Backend Admin Features

- [ ] 12. Create admin service
  - Create `backend/app/services/admin_service.py`
  - Implement `list_teachers()` - get all teachers
  - Implement `create_teacher()` - create new teacher
  - Implement `update_teacher()` - update teacher details
  - Implement `deactivate_teacher()` - deactivate teacher
  - Implement `list_pending_students()` - get pending students
  - Implement `approve_student()` - approve student
  - Implement `reject_student()` - reject student
  - _Requirements: 2.2, 2.3, 2.4, 3.1, 3.2, 3.3_

- [ ] 13. Create admin models
  - Create `backend/app/models/admin.py`
  - Define CreateTeacherRequest, TeacherResponse models
  - Define ApproveStudentRequest, RejectStudentRequest models
  - Define PendingStudentResponse model
  - _Requirements: 2.2, 3.1_

- [ ] 14. Create admin endpoints
  - Update `backend/app/api/endpoints.py`
  - Add `GET /api/admin/teachers` - list all teachers (admin only)
  - Add `POST /api/admin/teachers` - create teacher (admin only)
  - Add `PUT /api/admin/teachers/:id` - update teacher (admin only)
  - Add `GET /api/admin/students/pending` - list pending students (admin only)
  - Add `PUT /api/admin/students/:id/approve` - approve student (admin only)
  - Add `PUT /api/admin/students/:id/reject` - reject student (admin only)
  - _Requirements: 2.1, 2.2, 2.3, 3.1, 3.2, 3.3_

- [ ] 15. Test admin endpoints
  - Test list teachers as admin
  - Test create teacher as admin
  - Test list pending students as admin
  - Test approve student as admin
  - Test reject student as admin
  - Test admin endpoints as non-admin (should fail)
  - _Requirements: 2.1, 2.2, 2.3, 3.1, 3.2, 3.3_

---

## Phase 4: Backend Student Features

- [ ] 16. Create student service
  - Create `backend/app/services/student_service.py`
  - Implement `get_student_by_user_id()` - get student by user ID
  - Implement `get_attendance_history()` - get student's attendance records
  - Implement `get_attendance_stats()` - calculate attendance statistics
  - Implement `update_profile()` - update student profile
  - _Requirements: 5.2, 5.3_

- [ ] 17. Create student models
  - Create `backend/app/models/student.py`
  - Define StudentProfileResponse model
  - Define AttendanceRecordResponse model
  - _Requirements: 5.2, 5.3_

- [ ] 18. Create student endpoints
  - Update `backend/app/api/endpoints.py`
  - Add `GET /api/student/profile` - get own profile (student only)
  - Add `GET /api/student/attendance` - get own attendance history (student only)
  - Add `PUT /api/student/profile` - update own profile (student only)
  - _Requirements: 5.1, 5.2, 5.3_

- [ ] 19. Update existing endpoints with approval check
  - Update `POST /api/verify` endpoint
  - Add check for student approval_status
  - Reject verification if status != 'approved'
  - Return friendly error message
  - _Requirements: 3.4, 5.5_

- [ ] 20. Test student endpoints
  - Test get profile as student
  - Test get attendance history as student
  - Test update profile as student
  - Test verify attendance as unapproved student (should fail)
  - Test verify attendance as approved student (should succeed)
  - _Requirements: 5.1, 5.2, 5.3, 5.4, 5.5_

---

## Phase 5: Frontend Authentication

- [ ] 21. Install Supabase JavaScript client
  - Add `@supabase/supabase-js` to package.json
  - Run `npm install`
  - _Requirements: 1.1_

- [ ] 22. Create Supabase client
  - Create `frontend/src/lib/supabase.ts`
  - Initialize Supabase client with URL and anon key
  - Export client instance
  - _Requirements: 1.1_

- [ ] 23. Create auth context
  - Create `frontend/src/contexts/AuthContext.tsx`
  - Implement AuthProvider component
  - Implement useAuth hook
  - Store user state (user, loading, error)
  - Implement login() function
  - Implement logout() function
  - Implement refreshUser() function
  - Store JWT token in localStorage
  - _Requirements: 1.3, 1.4, 8.1, 8.2_

- [ ] 24. Create login page
  - Create `frontend/src/pages/LoginPage.tsx`
  - Add Supabase Auth UI component for Gmail login
  - Handle OAuth callback
  - Store token in localStorage
  - Call /api/auth/login to get user role
  - Redirect to role-specific portal
  - Add link to student registration
  - Style with campus-connect gradient theme
  - _Requirements: 1.1, 1.2, 9.1_

- [ ] 25. Create register page
  - Create `frontend/src/pages/RegisterPage.tsx`
  - Add registration form (name, student ID)
  - Add webcam capture for face enrollment
  - Pre-fill email from Gmail OAuth
  - Submit to /api/auth/register
  - Show "Pending approval" message after submission
  - Style with campus-connect gradient theme
  - _Requirements: 6.1, 6.2, 6.3, 6.4_

- [ ] 26. Create protected route component
  - Create `frontend/src/components/ProtectedRoute.tsx`
  - Check if user is authenticated
  - Check if user has required role
  - Redirect to login if not authenticated
  - Redirect to appropriate portal if wrong role
  - Show loading spinner while checking
  - _Requirements: 7.1, 7.2, 7.3, 7.4, 7.5_

- [ ] 27. Update App.tsx with routing
  - Add React Router routes
  - Add /login route (LoginPage)
  - Add /register route (RegisterPage)
  - Add /admin route (AdminDashboard, protected, admin only)
  - Add /teacher route (TeacherDashboard, protected, teacher/admin)
  - Add /student route (StudentDashboard, protected, student only)
  - Add / route (redirect to role-specific portal)
  - Wrap app with AuthProvider
  - _Requirements: 9.1, 9.2, 9.3, 9.4, 9.5_

- [ ] 28. Test authentication flow
  - Test login with Gmail
  - Test token storage in localStorage
  - Test session persistence (close/reopen browser)
  - Test logout
  - Test protected routes
  - _Requirements: 1.1, 1.2, 1.3, 1.4, 1.5, 8.1, 8.2, 8.3, 8.4, 8.5_

---

## Phase 6: Frontend Admin Portal

- [ ] 29. Create admin dashboard
  - Create `frontend/src/pages/AdminDashboard.tsx`
  - Add overview stats (pending students count, active teachers count)
  - Add navigation tabs (Teachers, Students)
  - Add quick actions (Approve Students, Add Teacher)
  - Style with campus-connect gradient theme
  - _Requirements: 2.1, 9.2_

- [ ] 30. Create teacher management component
  - Create `frontend/src/components/admin/TeacherManagement.tsx`
  - Fetch teachers from /api/admin/teachers
  - Display teachers in table/grid
  - Add "Add Teacher" button with modal/form
  - Add edit/deactivate actions for each teacher
  - Add search and filter functionality
  - Style with campus-connect gradient theme
  - _Requirements: 2.2, 2.3, 2.4, 2.5_

- [ ] 31. Create student approval component
  - Create `frontend/src/components/admin/StudentApproval.tsx`
  - Fetch pending students from /api/admin/students/pending
  - Display students in cards with photo
  - Add approve/reject buttons for each student
  - Add rejection reason modal
  - Add bulk approve functionality
  - Add search and filter functionality
  - Style with campus-connect gradient theme
  - _Requirements: 3.1, 3.2, 3.3, 3.4, 3.5_

- [ ] 32. Test admin portal
  - Test viewing teacher list
  - Test adding new teacher
  - Test editing teacher
  - Test deactivating teacher
  - Test viewing pending students
  - Test approving student
  - Test rejecting student
  - Test search and filter
  - _Requirements: 2.1, 2.2, 2.3, 2.4, 2.5, 3.1, 3.2, 3.3, 3.4, 3.5_

---

## Phase 7: Frontend Teacher Portal

- [ ] 33. Update teacher dashboard with auth
  - Update `frontend/src/components/FacultyDashboard.tsx`
  - Add role check (teacher or admin only)
  - Keep all existing features
  - Add user info display (name, role)
  - Add logout button
  - _Requirements: 4.1, 4.2, 4.3, 4.4, 4.5_

- [ ] 34. Update enrollment flow with pending status
  - Update `frontend/src/components/StudentEnrollment.tsx`
  - Set approval_status='pending' for new students
  - Show message "Student enrolled, pending admin approval"
  - _Requirements: 4.4_

- [ ] 35. Test teacher portal
  - Test accessing dashboard as teacher
  - Test creating session
  - Test enrolling student (should be pending)
  - Test viewing reports
  - Test viewing anomalies
  - Test logout
  - _Requirements: 4.1, 4.2, 4.3, 4.4, 4.5_

---

## Phase 8: Frontend Student Portal

- [ ] 36. Create student dashboard
  - Create `frontend/src/pages/StudentDashboard.tsx`
  - Add student profile section (name, ID, photo, status)
  - Add attendance history section
  - Add attendance rate statistics
  - Add upcoming sessions (if any)
  - Add logout button
  - Style with campus-connect gradient theme
  - _Requirements: 5.1, 5.2, 5.3_

- [ ] 37. Create student profile component
  - Create `frontend/src/components/student/StudentProfile.tsx`
  - Fetch profile from /api/student/profile
  - Display student information
  - Show approval status with badge
  - Add edit profile button (limited fields)
  - Style with campus-connect gradient theme
  - _Requirements: 5.2_

- [ ] 38. Create attendance history component
  - Create `frontend/src/components/student/AttendanceHistory.tsx`
  - Fetch attendance from /api/student/attendance
  - Display records in table/list
  - Add date range filter
  - Add export to CSV button
  - Show verification details (confidence, timestamp)
  - Style with campus-connect gradient theme
  - _Requirements: 5.3_

- [ ] 39. Create pending approval screen
  - Create `frontend/src/components/student/PendingApproval.tsx`
  - Show "Awaiting admin approval" message
  - Show registration details
  - Show estimated approval time
  - Add contact admin button
  - Style with campus-connect gradient theme
  - _Requirements: 5.5, 6.4_

- [ ] 40. Test student portal
  - Test viewing profile as student
  - Test viewing attendance history
  - Test filtering attendance by date
  - Test exporting attendance to CSV
  - Test pending approval screen
  - Test logout
  - _Requirements: 5.1, 5.2, 5.3, 5.4, 5.5_

---

## Phase 9: Integration & Testing

- [ ] 41. Test complete admin flow
  - Login as admin
  - Add new teacher
  - View pending students
  - Approve student
  - Reject student
  - Verify approved student can login
  - Verify rejected student cannot verify attendance
  - Logout
  - _Requirements: 2.1, 2.2, 2.3, 3.1, 3.2, 3.3_

- [ ] 42. Test complete teacher flow
  - Login as teacher
  - Create session
  - Enroll new student (should be pending)
  - View reports
  - View anomalies
  - Logout
  - _Requirements: 4.1, 4.2, 4.3, 4.4, 4.5_

- [ ] 43. Test complete student flow
  - Register new student
  - Login (should see pending approval)
  - Admin approves student
  - Login again (should see dashboard)
  - View profile
  - View attendance history
  - Verify attendance at kiosk
  - Logout
  - _Requirements: 5.1, 5.2, 5.3, 6.1, 6.2, 6.3, 6.4_

- [ ] 44. Test role-based access control
  - Try accessing admin routes as teacher (should fail)
  - Try accessing admin routes as student (should fail)
  - Try accessing teacher routes as student (should fail)
  - Try accessing student routes as teacher (should redirect)
  - Verify data isolation (students can only see own data)
  - _Requirements: 7.1, 7.2, 7.3, 7.4, 7.5_

- [ ] 45. Test session persistence
  - Login as each role
  - Close browser
  - Reopen browser
  - Verify still logged in
  - Verify redirected to correct portal
  - _Requirements: 8.1, 8.2, 8.3, 8.4, 8.5_

- [ ] 46. Test error handling
  - Test login with invalid token
  - Test accessing protected routes without token
  - Test accessing routes with wrong role
  - Test approving non-existent student
  - Test verifying attendance as unapproved student
  - Verify friendly error messages shown
  - _Requirements: All_

- [ ] 47. Test UI/UX
  - Verify all pages use campus-connect gradient theme
  - Verify all buttons work
  - Verify all forms validate inputs
  - Verify loading states shown
  - Verify error messages clear
  - Verify responsive design works
  - _Requirements: 9.1, 9.2, 9.3, 9.4, 9.5_

---

## Phase 10: Documentation & Deployment

- [ ] 48. Create admin user guide
  - Document how to add teachers
  - Document how to approve/reject students
  - Document how to view reports
  - Add screenshots
  - _Requirements: 2.1, 3.1_

- [ ] 49. Create teacher user guide
  - Document how to create sessions
  - Document how to enroll students
  - Document how to view reports
  - Add screenshots
  - _Requirements: 4.1_

- [ ] 50. Create student user guide
  - Document how to register
  - Document how to view attendance
  - Document how to verify attendance
  - Add screenshots
  - _Requirements: 5.1, 6.1_

- [ ] 51. Update API documentation
  - Document all new endpoints
  - Add request/response examples
  - Add authentication requirements
  - Add error codes
  - _Requirements: All_

- [ ] 52. Create deployment guide
  - Document Supabase setup steps
  - Document environment variables
  - Document database migration steps
  - Document first admin user creation
  - Document testing checklist
  - _Requirements: All_

- [ ] 53. Deploy to production
  - Run database migration on production
  - Deploy backend with new endpoints
  - Deploy frontend with new pages
  - Create first admin user
  - Test all flows in production
  - Monitor error logs
  - _Requirements: All_

---

## Checkpoint Tasks

- [ ] 54. Checkpoint 1: After Phase 2
  - Ensure all tests pass
  - Verify auth endpoints work
  - Verify JWT token verification works
  - Ask user if questions arise

- [ ] 55. Checkpoint 2: After Phase 4
  - Ensure all tests pass
  - Verify all backend endpoints work
  - Verify role-based access control works
  - Ask user if questions arise

- [ ] 56. Checkpoint 3: After Phase 8
  - Ensure all tests pass
  - Verify all frontend pages work
  - Verify complete user flows work
  - Ask user if questions arise

- [ ] 57. Final Checkpoint
  - Ensure all tests pass
  - Verify system works end-to-end
  - Verify documentation complete
  - Ready for production deployment

---

## Notes

- Each task should be completed in order
- Test thoroughly after each phase
- Keep existing features working
- Use campus-connect gradient theme throughout
- Follow security best practices
- Document any issues or blockers

---

**Total Tasks**: 57 (including 4 checkpoints)
**Estimated Time**: 15-20 hours
**Status**: Ready for implementation! 🚀
