/**
 * Teacher App Entry Point (Port 3000)
 * Focused on Session Management, OTP Generation, and Real-time Dashboard
 */
import { BrowserRouter, Routes, Route, Navigate } from 'react-router-dom'
import { Suspense, lazy } from 'react'
import { AuthProvider, useAuth } from './contexts/AuthContext'
import ProtectedRoute from './components/ProtectedRoute'

// Lazy load teacher-specific components
const TeacherLoginPage = lazy(() => import('./pages/TeacherLoginPage'))
const FacultyDashboard = lazy(() => import('./components/FacultyDashboard'))
const StudentEnrollment = lazy(() => import('./components/StudentEnrollment'))

// Loading spinner
function LoadingSpinner() {
  return (
    <div className="min-h-screen flex items-center justify-center bg-[#0f0d1a]">
      <div className="text-center">
        <div className="w-16 h-16 border-4 border-indigo-500 border-t-transparent rounded-full animate-spin mx-auto mb-4"></div>
        <p className="text-white text-lg font-semibold">Teacher Portal Loading...</p>
        <p className="text-zinc-500 text-sm mt-2">ISAVS 2026 - Port 3000</p>
      </div>
    </div>
  )
}

function RootRedirect() {
  const { user, loading } = useAuth()
  
  if (loading) return <LoadingSpinner />
  if (!user) return <Navigate to="/login" replace />
  
  // Only allow teachers and admins
  if (user.role === 'teacher' || user.role === 'admin') {
    return <Navigate to="/dashboard" replace />
  }
  
  return <Navigate to="/login" replace />
}

function TeacherApp() {
  return (
    <BrowserRouter>
      <AuthProvider>
        <Suspense fallback={<LoadingSpinner />}>
          <Routes>
            <Route path="/login" element={<TeacherLoginPage />} />
            
            <Route path="/dashboard" element={
              <ProtectedRoute allowedRoles={['admin', 'teacher']}>
                <FacultyDashboard />
              </ProtectedRoute>
            } />
            
            <Route path="/enroll" element={
              <ProtectedRoute allowedRoles={['admin', 'teacher']}>
                <StudentEnrollment />
              </ProtectedRoute>
            } />
            
            <Route path="/" element={<RootRedirect />} />
            <Route path="*" element={<Navigate to="/" replace />} />
          </Routes>
        </Suspense>
      </AuthProvider>
    </BrowserRouter>
  )
}

export default TeacherApp
