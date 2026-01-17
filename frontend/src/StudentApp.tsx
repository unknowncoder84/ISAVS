/**
 * Student App Entry Point (Port 3001)
 * Focused on Verification Kiosk (Webcam + OTP + GPS Check)
 */
import { BrowserRouter, Routes, Route, Navigate } from 'react-router-dom'
import { Suspense, lazy } from 'react'
import { AuthProvider, useAuth } from './contexts/AuthContext'
import ProtectedRoute from './components/ProtectedRoute'

// Lazy load student-specific components
const StudentLoginPage = lazy(() => import('./pages/StudentLoginPage'))
const StudentDashboard = lazy(() => import('./pages/StudentDashboard'))
const KioskView = lazy(() => import('./components/KioskView'))

// Loading spinner
function LoadingSpinner() {
  return (
    <div className="min-h-screen flex items-center justify-center bg-[#0f0d1a]">
      <div className="text-center">
        <div className="w-16 h-16 border-4 border-purple-500 border-t-transparent rounded-full animate-spin mx-auto mb-4"></div>
        <p className="text-white text-lg font-semibold">Student Portal Loading...</p>
        <p className="text-zinc-500 text-sm mt-2">ISAVS 2026 - Port 3001</p>
      </div>
    </div>
  )
}

function RootRedirect() {
  const { user, loading } = useAuth()
  
  if (loading) return <LoadingSpinner />
  if (!user) return <Navigate to="/login" replace />
  
  // Only allow students
  if (user.role === 'student') {
    return <Navigate to="/dashboard" replace />
  }
  
  return <Navigate to="/login" replace />
}

function StudentApp() {
  return (
    <BrowserRouter>
      <AuthProvider>
        <Suspense fallback={<LoadingSpinner />}>
          <Routes>
            <Route path="/login" element={<StudentLoginPage />} />
            
            <Route path="/dashboard" element={
              <ProtectedRoute allowedRoles={['student']}>
                <StudentDashboard />
              </ProtectedRoute>
            } />
            
            <Route path="/kiosk" element={<KioskView sessionId="" />} />
            
            <Route path="/" element={<RootRedirect />} />
            <Route path="*" element={<Navigate to="/" replace />} />
          </Routes>
        </Suspense>
      </AuthProvider>
    </BrowserRouter>
  )
}

export default StudentApp
