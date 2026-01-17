/**
 * Unified Professional Login Page
 * With Dummy Credentials for Teachers and Students
 */
import { useState, useEffect } from 'react'
import { useAuth } from '../contexts/AuthContext'
import { useNavigate, Link } from 'react-router-dom'

// Dummy credentials
const DUMMY_CREDENTIALS = {
  teachers: [
    { email: 'teacher1@isavs.edu', password: 'teacher123', name: 'Dr. Sarah Johnson', id: 'T001' },
    { email: 'teacher2@isavs.edu', password: 'teacher123', name: 'Prof. Michael Chen', id: 'T002' }
  ],
  students: [
    { email: 'student1@isavs.edu', password: 'student123', name: 'John Smith', id: 'S001' },
    { email: 'student2@isavs.edu', password: 'student123', name: 'Emma Davis', id: 'S002' }
  ]
}

export default function UnifiedLoginPage() {
  const { user, loading, login } = useAuth()
  const navigate = useNavigate()
  const [activeTab, setActiveTab] = useState<'teacher' | 'student'>('teacher')
  const [email, setEmail] = useState('')
  const [password, setPassword] = useState('')
  const [error, setError] = useState('')
  const [showCredentials, setShowCredentials] = useState(false)

  useEffect(() => {
    if (user) {
      if (user.role === 'admin') navigate('/admin')
      else if (user.role === 'teacher') navigate('/teacher')
      else if (user.role === 'student') navigate('/student')
    }
  }, [user, navigate])

  const handleLogin = async (e: React.FormEvent) => {
    e.preventDefault()
    setError('')

    // Check credentials
    const credentials = activeTab === 'teacher' ? DUMMY_CREDENTIALS.teachers : DUMMY_CREDENTIALS.students
    const user = credentials.find(c => c.email === email && c.password === password)

    if (user) {
      // Store user info in localStorage
      const userData = {
        id: parseInt(user.id.substring(1)),
        email: user.email,
        name: user.name,
        role: activeTab
      }
      localStorage.setItem('demo_user', JSON.stringify(userData))
      
      // Trigger login
      await login(activeTab)
      
      // Navigate
      if (activeTab === 'teacher') {
        navigate('/teacher')
      } else {
        navigate('/student')
      }
    } else {
      setError('Invalid email or password')
    }
  }

  if (loading) {
    return (
      <div className="min-h-screen bg-[#0f0d1a] flex items-center justify-center">
        <div className="text-center">
          <div className="w-16 h-16 border-4 border-indigo-500 border-t-transparent rounded-full animate-spin mx-auto mb-4"></div>
          <p className="text-white">Loading...</p>
        </div>
      </div>
    )
  }

  return (
    <div className="min-h-screen bg-[#0f0d1a] relative overflow-hidden">
      {/* Animated Background */}
      <div className="absolute inset-0 overflow-hidden">
        <div className="absolute -top-1/2 -left-1/2 w-full h-full bg-gradient-to-br from-indigo-500/20 to-purple-500/20 rounded-full blur-3xl animate-pulse"></div>
        <div className="absolute -bottom-1/2 -right-1/2 w-full h-full bg-gradient-to-tl from-purple-500/20 to-pink-500/20 rounded-full blur-3xl animate-pulse" style={{ animationDelay: '1s' }}></div>
      </div>

      {/* Content */}
      <div className="relative z-10 min-h-screen flex items-center justify-center p-4">
        <div className="w-full max-w-md">
          {/* Logo */}
          <div className="text-center mb-8">
            <div className="inline-block p-4 bg-gradient-to-br from-indigo-500 to-purple-600 rounded-2xl shadow-2xl shadow-indigo-500/50 mb-4">
              <svg className="w-12 h-12 text-white" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M12 4.354a4 4 0 110 5.292M15 21H3v-1a6 6 0 0112 0v1zm0 0h6v-1a6 6 0 00-9-5.197M13 7a4 4 0 11-8 0 4 4 0 018 0z" />
              </svg>
            </div>
            <h1 className="text-4xl font-bold text-white mb-2">ISAVS</h1>
            <p className="text-zinc-400">Intelligent Student Attendance Verification System</p>
          </div>

          {/* Login Card */}
          <div className="bg-[#1a1625]/80 backdrop-blur-xl border border-white/10 rounded-2xl shadow-2xl overflow-hidden">
            {/* Tabs */}
            <div className="flex border-b border-white/10">
              <button
                onClick={() => {
                  setActiveTab('teacher')
                  setEmail('')
                  setPassword('')
                  setError('')
                }}
                className={`flex-1 py-4 px-6 font-semibold transition-all ${
                  activeTab === 'teacher'
                    ? 'bg-gradient-to-r from-indigo-500 to-purple-600 text-white'
                    : 'text-zinc-400 hover:text-white hover:bg-white/5'
                }`}
              >
                <div className="flex items-center justify-center gap-2">
                  <svg className="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                    <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M21 13.255A23.931 23.931 0 0112 15c-3.183 0-6.22-.62-9-1.745M16 6V4a2 2 0 00-2-2h-4a2 2 0 00-2-2v2m4 6h.01M5 20h14a2 2 0 002-2V8a2 2 0 00-2-2H5a2 2 0 00-2 2v10a2 2 0 002 2z" />
                  </svg>
                  Teacher
                </div>
              </button>
              <button
                onClick={() => {
                  setActiveTab('student')
                  setEmail('')
                  setPassword('')
                  setError('')
                }}
                className={`flex-1 py-4 px-6 font-semibold transition-all ${
                  activeTab === 'student'
                    ? 'bg-gradient-to-r from-indigo-500 to-purple-600 text-white'
                    : 'text-zinc-400 hover:text-white hover:bg-white/5'
                }`}
              >
                <div className="flex items-center justify-center gap-2">
                  <svg className="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                    <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M16 7a4 4 0 11-8 0 4 4 0 018 0zM12 14a7 7 0 00-7 7h14a7 7 0 00-7-7z" />
                  </svg>
                  Student
                </div>
              </button>
            </div>

            {/* Form */}
            <div className="p-8">
              <form onSubmit={handleLogin} className="space-y-6">
                {/* Error Message */}
                {error && (
                  <div className="p-4 bg-red-500/10 border border-red-500/20 rounded-xl text-red-400 text-sm flex items-center gap-3 animate-fadeIn">
                    <svg className="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                      <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M12 8v4m0 4h.01M21 12a9 9 0 11-18 0 9 9 0 0118 0z" />
                    </svg>
                    {error}
                  </div>
                )}

                {/* Email */}
                <div>
                  <label className="block text-sm font-medium text-zinc-400 mb-2">Email Address</label>
                  <input
                    type="email"
                    value={email}
                    onChange={(e) => setEmail(e.target.value)}
                    placeholder={activeTab === 'teacher' ? 'teacher1@isavs.edu' : 'student1@isavs.edu'}
                    className="w-full px-4 py-3 bg-white/5 border border-white/10 rounded-xl text-white placeholder-zinc-500 focus:outline-none focus:border-indigo-500/50 transition"
                    required
                  />
                </div>

                {/* Password */}
                <div>
                  <label className="block text-sm font-medium text-zinc-400 mb-2">Password</label>
                  <input
                    type="password"
                    value={password}
                    onChange={(e) => setPassword(e.target.value)}
                    placeholder="Enter your password"
                    className="w-full px-4 py-3 bg-white/5 border border-white/10 rounded-xl text-white placeholder-zinc-500 focus:outline-none focus:border-indigo-500/50 transition"
                    required
                  />
                </div>

                {/* Login Button */}
                <button
                  type="submit"
                  className="w-full py-4 bg-gradient-to-r from-indigo-500 to-purple-600 text-white rounded-xl font-semibold hover:shadow-lg hover:shadow-indigo-500/25 transition-all transform hover:scale-[1.02]"
                >
                  Sign In
                </button>

                {/* Show Credentials Button */}
                <button
                  type="button"
                  onClick={() => setShowCredentials(!showCredentials)}
                  className="w-full py-3 bg-white/5 border border-white/10 text-zinc-400 rounded-xl text-sm hover:bg-white/10 hover:text-white transition"
                >
                  {showCredentials ? 'Hide' : 'Show'} Demo Credentials
                </button>

                {/* Credentials Display */}
                {showCredentials && (
                  <div className="p-4 bg-indigo-500/10 border border-indigo-500/20 rounded-xl animate-fadeIn">
                    <p className="text-xs font-semibold text-indigo-400 mb-3">
                      {activeTab === 'teacher' ? 'Teacher Accounts' : 'Student Accounts'}
                    </p>
                    <div className="space-y-3">
                      {(activeTab === 'teacher' ? DUMMY_CREDENTIALS.teachers : DUMMY_CREDENTIALS.students).map((cred, i) => (
                        <div key={i} className="bg-white/5 rounded-lg p-3">
                          <div className="flex items-center justify-between mb-2">
                            <p className="text-white font-medium text-sm">{cred.name}</p>
                            <span className="text-xs text-zinc-500 font-mono">{cred.id}</span>
                          </div>
                          <div className="space-y-1 text-xs">
                            <p className="text-zinc-400">
                              <span className="text-zinc-600">Email:</span> <span className="font-mono text-indigo-400">{cred.email}</span>
                            </p>
                            <p className="text-zinc-400">
                              <span className="text-zinc-600">Password:</span> <span className="font-mono text-indigo-400">{cred.password}</span>
                            </p>
                          </div>
                          <button
                            type="button"
                            onClick={() => {
                              setEmail(cred.email)
                              setPassword(cred.password)
                            }}
                            className="mt-2 w-full py-1.5 bg-indigo-500/20 text-indigo-400 rounded text-xs font-medium hover:bg-indigo-500/30 transition"
                          >
                            Use These Credentials
                          </button>
                        </div>
                      ))}
                    </div>
                  </div>
                )}
              </form>

              {/* Admin Link */}
              <div className="mt-6 pt-6 border-t border-white/10 text-center">
                <p className="text-zinc-500 text-sm mb-2">Administrator?</p>
                <Link
                  to="/login"
                  className="text-indigo-400 hover:text-indigo-300 font-medium text-sm transition"
                >
                  Admin Login →
                </Link>
              </div>

              {/* Back to Home */}
              <div className="mt-4 text-center">
                <Link
                  to="/"
                  className="text-zinc-500 hover:text-zinc-400 text-sm transition"
                >
                  ← Back to Home
                </Link>
              </div>
            </div>
          </div>

          {/* Info Card */}
          <div className="mt-6 bg-white/5 backdrop-blur-xl border border-white/10 rounded-xl p-4">
            <div className="flex items-start gap-3">
              <div className="w-8 h-8 bg-indigo-500/20 rounded-lg flex items-center justify-center flex-shrink-0">
                <svg className="w-4 h-4 text-indigo-400" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                  <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M13 16h-1v-4h-1m1-4h.01M21 12a9 9 0 11-18 0 9 9 0 0118 0z" />
                </svg>
              </div>
              <div className="flex-1">
                <p className="text-white text-sm font-medium mb-1">Demo Mode Active</p>
                <p className="text-zinc-400 text-xs">
                  Use the credentials above to test the system. Click "Show Demo Credentials" to see all available accounts.
                </p>
              </div>
            </div>
          </div>
        </div>
      </div>
    </div>
  )
}
