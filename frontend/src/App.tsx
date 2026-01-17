import { BrowserRouter, Routes, Route, Navigate } from 'react-router-dom'
import { Suspense, lazy } from 'react'
import { AuthProvider, useAuth } from './contexts/AuthContext'
import ProtectedRoute from './components/ProtectedRoute'

// Lazy load components for better performance
const HomePage = lazy(() => import('./pages/HomePage'))
const LoginPage = lazy(() => import('./pages/LoginPage'))
const UnifiedLoginPage = lazy(() => import('./pages/UnifiedLoginPage'))
const StudentLoginPage = lazy(() => import('./pages/StudentLoginPage'))
const TeacherLoginPage = lazy(() => import('./pages/TeacherLoginPage'))
const RegisterPage = lazy(() => import('./pages/RegisterPage'))
const AdminDashboard = lazy(() => import('./pages/AdminDashboard'))
const StudentDashboard = lazy(() => import('./pages/StudentDashboard'))
const KioskView = lazy(() => import('./components/KioskView'))
const FacultyDashboard = lazy(() => import('./components/FacultyDashboard'))
const StudentEnrollment = lazy(() => import('./components/StudentEnrollment'))

// Loading spinner component
function LoadingSpinner() {
  return (
    <div className="min-h-screen flex items-center justify-center bg-[#0f0d1a]">
      <div className="text-center">
        <div className="w-16 h-16 border-4 border-indigo-500 border-t-transparent rounded-full animate-spin mx-auto mb-4"></div>
        <p className="text-white text-lg font-semibold">System Initializing...</p>
        <p className="text-zinc-500 text-sm mt-2">Loading ISAVS 2026</p>
      </div>
    </div>
  )
}

function RootRedirect() {
  const { user, loading } = useAuth()
  
  if (loading) return <LoadingSpinner />
  if (!user) return <Navigate to="/home" replace />
  
  if (user.role === 'admin') return <Navigate to="/admin" replace />
  if (user.role === 'teacher') return <Navigate to="/teacher" replace />
  if (user.role === 'student') return <Navigate to="/student" replace />
  
  return <Navigate to="/home" replace />
}

function App() {
  return (
    <BrowserRouter>
      <AuthProvider>
        <Suspense fallback={<LoadingSpinner />}>
          <Routes>
            <Route path="/home" element={<HomePage />} />
            <Route path="/login" element={<LoginPage />} />
            <Route path="/login/portal" element={<UnifiedLoginPage />} />
            <Route path="/login/student" element={<StudentLoginPage />} />
            <Route path="/login/teacher" element={<TeacherLoginPage />} />
            <Route path="/register" element={<RegisterPage />} />
            <Route path="/auth/callback" element={<LoginPage />} />
            
            <Route path="/admin" element={
              <ProtectedRoute allowedRoles={['admin']}>
                <AdminDashboard />
              </ProtectedRoute>
            } />
            
            <Route path="/teacher" element={
              <ProtectedRoute allowedRoles={['admin', 'teacher']}>
                <FacultyDashboard />
              </ProtectedRoute>
            } />
            
            <Route path="/student" element={
              <ProtectedRoute allowedRoles={['student']}>
                <StudentDashboard />
              </ProtectedRoute>
            } />
            
            <Route path="/enroll" element={
              <ProtectedRoute allowedRoles={['admin', 'teacher']}>
                <StudentEnrollment />
              </ProtectedRoute>
            } />
            
            <Route path="/kiosk" element={<KioskView sessionId="" />} />
            <Route path="/dashboard" element={<Navigate to="/teacher" replace />} />
            
            <Route path="/" element={<RootRedirect />} />
          </Routes>
        </Suspense>
      </AuthProvider>
    </BrowserRouter>
  )
}

export default App
