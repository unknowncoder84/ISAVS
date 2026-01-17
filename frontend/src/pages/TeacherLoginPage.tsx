import { useAuth } from '../contexts/AuthContext'
import { useEffect } from 'react'
import { useNavigate, Link } from 'react-router-dom'
import { FaGoogle, FaChalkboardTeacher } from 'react-icons/fa'

export default function TeacherLoginPage() {
  const { user, loading, login } = useAuth()
  const navigate = useNavigate()

  useEffect(() => {
    if (user) {
      if (user.role === 'teacher') {
        navigate('/teacher')
      } else if (user.role === 'admin') {
        navigate('/admin')
      } else if (user.role === 'student') {
        navigate('/student')
      }
    }
  }, [user, navigate])

  if (loading) {
    return (
      <div className="min-h-screen flex items-center justify-center bg-gradient-to-br from-indigo-600 via-purple-600 to-pink-600">
        <div className="bg-white/10 backdrop-blur-lg rounded-2xl p-8">
          <div className="animate-spin rounded-full h-12 w-12 border-4 border-white border-t-transparent"></div>
        </div>
      </div>
    )
  }

  return (
    <div className="min-h-screen flex items-center justify-center bg-gradient-to-br from-indigo-600 via-purple-600 to-pink-600 p-4">
      <div className="bg-white rounded-3xl shadow-2xl overflow-hidden max-w-4xl w-full grid md:grid-cols-2">
        {/* Left Side - Branding */}
        <div className="bg-gradient-to-br from-indigo-700 to-purple-700 p-12 text-white flex flex-col justify-center">
          <div className="mb-8">
            <FaChalkboardTeacher className="text-6xl mb-4" />
            <h1 className="text-4xl font-bold mb-4">Teacher Portal</h1>
            <p className="text-indigo-100 text-lg">
              Manage attendance sessions, enroll students, and access comprehensive analytics.
            </p>
          </div>
          
          <div className="space-y-4 mt-8">
            <div className="flex items-start space-x-3">
              <div className="bg-white/20 rounded-full p-2 mt-1">
                <svg className="w-5 h-5" fill="currentColor" viewBox="0 0 20 20">
                  <path fillRule="evenodd" d="M16.707 5.293a1 1 0 010 1.414l-8 8a1 1 0 01-1.414 0l-4-4a1 1 0 011.414-1.414L8 12.586l7.293-7.293a1 1 0 011.414 0z" clipRule="evenodd" />
                </svg>
              </div>
              <div>
                <h3 className="font-semibold">Create Sessions</h3>
                <p className="text-sm text-indigo-100">Start attendance sessions for your classes</p>
              </div>
            </div>
            
            <div className="flex items-start space-x-3">
              <div className="bg-white/20 rounded-full p-2 mt-1">
                <svg className="w-5 h-5" fill="currentColor" viewBox="0 0 20 20">
                  <path fillRule="evenodd" d="M16.707 5.293a1 1 0 010 1.414l-8 8a1 1 0 01-1.414 0l-4-4a1 1 0 011.414-1.414L8 12.586l7.293-7.293a1 1 0 011.414 0z" clipRule="evenodd" />
                </svg>
              </div>
              <div>
                <h3 className="font-semibold">Enroll Students</h3>
                <p className="text-sm text-indigo-100">Register new students with face recognition</p>
              </div>
            </div>
            
            <div className="flex items-start space-x-3">
              <div className="bg-white/20 rounded-full p-2 mt-1">
                <svg className="w-5 h-5" fill="currentColor" viewBox="0 0 20 20">
                  <path fillRule="evenodd" d="M16.707 5.293a1 1 0 010 1.414l-8 8a1 1 0 01-1.414 0l-4-4a1 1 0 011.414-1.414L8 12.586l7.293-7.293a1 1 0 011.414 0z" clipRule="evenodd" />
                </svg>
              </div>
              <div>
                <h3 className="font-semibold">View Reports</h3>
                <p className="text-sm text-indigo-100">Access detailed attendance analytics</p>
              </div>
            </div>
          </div>
        </div>

        {/* Right Side - Login Form */}
        <div className="p-12 flex flex-col justify-center">
          <div className="mb-8">
            <h2 className="text-3xl font-bold text-gray-800 mb-2">Faculty Access</h2>
            <p className="text-gray-600">Sign in to manage your classes</p>
          </div>

          <button
            onClick={() => login('teacher')}
            className="w-full bg-gradient-to-r from-indigo-600 to-purple-600 text-white py-4 rounded-xl font-semibold hover:shadow-xl transition-all duration-300 transform hover:scale-105 flex items-center justify-center space-x-3"
          >
            <FaGoogle className="text-xl" />
            <span>Continue with Gmail</span>
          </button>

          <div className="mt-4 p-3 bg-indigo-50 border border-indigo-200 rounded-lg">
            <p className="text-xs text-indigo-800 text-center">
              🎯 Demo Mode Active - Click to login as Teacher
            </p>
          </div>

          <div className="mt-6 text-center">
            <p className="text-sm text-gray-600">
              Authorized faculty members only
            </p>
          </div>

          <div className="mt-8 pt-8 border-t border-gray-200">
            <p className="text-center text-sm text-gray-500">
              Are you a student?{' '}
              <Link to="/login/student" className="text-blue-600 font-semibold hover:underline">
                Student Login
              </Link>
            </p>
          </div>

          <div className="mt-6 text-center">
            <Link to="/" className="text-sm text-gray-500 hover:text-gray-700">
              ← Back to Home
            </Link>
          </div>
        </div>
      </div>
    </div>
  )
}
