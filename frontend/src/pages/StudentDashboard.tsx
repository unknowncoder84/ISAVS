/**
 * Enhanced Student Dashboard with Camera Attendance
 * Professional Blue/Purple Gradient Theme
 */
import { useState, useEffect, useCallback, useRef } from 'react'
import { useAuth } from '../contexts/AuthContext'
import { api } from '../services/api'
import { Link } from 'react-router-dom'
import WebcamCapture from '../components/WebcamCapture'
import StatCard from '../components/ui/StatCard'

// Animated Counter Component
const AnimatedCounter: React.FC<{ value: number; duration?: number; suffix?: string }> = ({ 
  value, duration = 1000, suffix = '' 
}) => {
  const [displayValue, setDisplayValue] = useState(0)
  
  useEffect(() => {
    let startTime: number
    let animationFrame: number
    
    const animate = (timestamp: number) => {
      if (!startTime) startTime = timestamp
      const progress = Math.min((timestamp - startTime) / duration, 1)
      const easeOut = 1 - Math.pow(1 - progress, 3)
      setDisplayValue(Math.floor(easeOut * value))
      
      if (progress < 1) {
        animationFrame = requestAnimationFrame(animate)
      }
    }
    
    animationFrame = requestAnimationFrame(animate)
    return () => cancelAnimationFrame(animationFrame)
  }, [value, duration])
  
  return <span>{displayValue}{suffix}</span>
}

export default function StudentDashboard() {
  const { user, logout } = useAuth()
  const [profile, setProfile] = useState<any>(null)
  const [attendance, setAttendance] = useState<any[]>([])
  const [stats, setStats] = useState<any>(null)
  const [loading, setLoading] = useState(true)
  const [showCamera, setShowCamera] = useState(false)
  const [sessionId, setSessionId] = useState('')
  const [otp, setOtp] = useState('')
  const [capturedImage, setCapturedImage] = useState<string>('')
  const [isVerifying, setIsVerifying] = useState(false)
  const [verificationResult, setVerificationResult] = useState<any>(null)
  const [error, setError] = useState<string | null>(null)

  useEffect(() => {
    loadData()
  }, [])

  const loadData = async () => {
    try {
      const [profileRes, attendanceRes, statsRes] = await Promise.all([
        api.get('/student/profile'),
        api.get('/student/attendance'),
        api.get('/student/attendance/stats')
      ])
      setProfile(profileRes.data)
      setAttendance(attendanceRes.data)
      setStats(statsRes.data)
    } catch (err) {
      console.error(err)
    } finally {
      setLoading(false)
    }
  }

  const handleFrameCapture = useCallback((frame: string) => {
    setCapturedImage(frame)
  }, [])

  const handleVerifyAttendance = async () => {
    if (!sessionId.trim() || !otp.trim() || !capturedImage) {
      setError('Please enter Session ID, OTP, and capture your face')
      return
    }

    setIsVerifying(true)
    setError(null)
    setVerificationResult(null)

    try {
      const response = await api.post('/verify', {
        session_id: sessionId.trim(),
        otp: otp.trim(),
        face_image: capturedImage
      })

      if (response.data.success) {
        setVerificationResult(response.data)
        setShowCamera(false)
        setSessionId('')
        setOtp('')
        setCapturedImage('')
        loadData() // Refresh data
      } else {
        setError(response.data.message || 'Verification failed')
      }
    } catch (err: any) {
      setError(err.response?.data?.detail || 'Verification failed')
    } finally {
      setIsVerifying(false)
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

  if (profile?.approval_status === 'pending') {
    return (
      <div className="min-h-screen bg-[#0f0d1a] flex items-center justify-center p-4">
        <div className="bg-[#1a1625] border border-white/10 rounded-2xl shadow-2xl p-8 max-w-md text-center">
          <div className="w-20 h-20 bg-amber-500/20 rounded-full flex items-center justify-center mx-auto mb-4">
            <svg className="w-10 h-10 text-amber-400" fill="none" stroke="currentColor" viewBox="0 0 24 24">
              <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M12 8v4l3 3m6-3a9 9 0 11-18 0 9 9 0 0118 0z" />
            </svg>
          </div>
          <h2 className="text-2xl font-bold text-white mb-4">Awaiting Approval</h2>
          <p className="text-zinc-400 mb-6">
            Your registration is pending admin approval. You'll be notified once approved.
          </p>
          <button onClick={logout} className="px-6 py-2 bg-white/10 text-white rounded-lg hover:bg-white/20 transition">
            Logout
          </button>
        </div>
      </div>
    )
  }

  if (profile?.approval_status === 'rejected') {
    return (
      <div className="min-h-screen bg-[#0f0d1a] flex items-center justify-center p-4">
        <div className="bg-[#1a1625] border border-white/10 rounded-2xl shadow-2xl p-8 max-w-md text-center">
          <div className="w-20 h-20 bg-red-500/20 rounded-full flex items-center justify-center mx-auto mb-4">
            <svg className="w-10 h-10 text-red-400" fill="none" stroke="currentColor" viewBox="0 0 24 24">
              <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M6 18L18 6M6 6l12 12" />
            </svg>
          </div>
          <h2 className="text-2xl font-bold text-white mb-4">Registration Rejected</h2>
          <p className="text-zinc-400 mb-6">
            {profile.rejection_reason || 'Your registration was rejected. Please contact admin.'}
          </p>
          <button onClick={logout} className="px-6 py-2 bg-white/10 text-white rounded-lg hover:bg-white/20 transition">
            Logout
          </button>
        </div>
      </div>
    )
  }

  const totalSessions = stats?.total_sessions || 0
  const attendedSessions = stats?.attended_sessions || 0
  const attendanceRate = stats?.attendance_rate || 0

  return (
    <div className="min-h-screen bg-[#0f0d1a]">
      {/* Header */}
      <header className="sticky top-0 z-50 bg-[#0f0d1a]/80 backdrop-blur-xl border-b border-white/5">
        <div className="max-w-7xl mx-auto px-4 py-4 flex items-center justify-between">
          <div className="flex items-center gap-4">
            <Link to="/" className="w-10 h-10 bg-white/5 hover:bg-white/10 rounded-xl flex items-center justify-center transition">
              <svg className="w-5 h-5 text-white" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M15 19l-7-7 7-7" />
              </svg>
            </Link>
            <div>
              <h1 className="text-xl font-bold text-white">Student Portal</h1>
              <p className="text-xs text-zinc-500">Welcome, {user?.name}</p>
            </div>
          </div>
          <button onClick={logout} className="px-4 py-2 bg-white/5 hover:bg-white/10 text-white rounded-xl transition">
            Logout
          </button>
        </div>
      </header>

      <main className="max-w-7xl mx-auto px-4 py-6">
        {/* Success Message */}
        {verificationResult && (
          <div className="mb-6 p-4 bg-emerald-500/10 border border-emerald-500/20 rounded-xl text-emerald-400 flex items-center gap-3 animate-fadeIn">
            <svg className="w-6 h-6" fill="none" stroke="currentColor" viewBox="0 0 24 24">
              <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M9 12l2 2 4-4m6 2a9 9 0 11-18 0 9 9 0 0118 0z" />
            </svg>
            <div className="flex-1">
              <p className="font-semibold">Attendance Verified!</p>
              <p className="text-sm text-emerald-400/70">{verificationResult.message}</p>
            </div>
            <button onClick={() => setVerificationResult(null)} className="text-emerald-300 hover:text-white">✕</button>
          </div>
        )}

        {/* Error Message */}
        {error && (
          <div className="mb-6 p-4 bg-red-500/10 border border-red-500/20 rounded-xl text-red-400 flex items-center gap-3 animate-fadeIn">
            <svg className="w-6 h-6" fill="none" stroke="currentColor" viewBox="0 0 24 24">
              <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M12 8v4m0 4h.01M21 12a9 9 0 11-18 0 9 9 0 0118 0z" />
            </svg>
            <span className="flex-1">{error}</span>
            <button onClick={() => setError(null)} className="text-red-300 hover:text-white">✕</button>
          </div>
        )}

        {/* Stats Grid */}
        <div className="grid grid-cols-1 md:grid-cols-3 gap-6 mb-6">
          <StatCard 
            title="Total Sessions" 
            value={totalSessions}
            icon={
              <svg className="w-6 h-6" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M9 5H7a2 2 0 00-2 2v12a2 2 0 002 2h10a2 2 0 002-2V7a2 2 0 00-2-2h-2M9 5a2 2 0 002 2h2a2 2 0 002-2M9 5a2 2 0 012-2h2a2 2 0 012 2" />
              </svg>
            }
          />
          <StatCard 
            title="Attended" 
            value={attendedSessions}
            icon={
              <svg className="w-6 h-6" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M9 12l2 2 4-4m6 2a9 9 0 11-18 0 9 9 0 0118 0z" />
              </svg>
            }
          />
          <StatCard 
            title="Attendance Rate" 
            value={`${Math.round(attendanceRate)}%`}
            icon={
              <svg className="w-6 h-6" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M13 7h8m0 0v8m0-8l-8 8-4-4-6 6" />
              </svg>
            }
            trend={attendanceRate > 80 ? { value: 12, positive: true } : undefined}
          />
        </div>

        <div className="grid grid-cols-1 lg:grid-cols-3 gap-6">
          {/* Main Content */}
          <div className="lg:col-span-2 space-y-6">
            {/* Mark Attendance Card */}
            <div className="bg-[#1a1625]/80 backdrop-blur-xl border border-white/10 rounded-2xl p-6">
              <div className="flex items-center justify-between mb-6">
                <div>
                  <h2 className="text-xl font-bold text-white">Mark Attendance</h2>
                  <p className="text-sm text-zinc-500">Use face recognition to verify your attendance</p>
                </div>
                <button
                  onClick={() => setShowCamera(!showCamera)}
                  className={`px-4 py-2 rounded-xl font-medium transition-all ${
                    showCamera
                      ? 'bg-red-500/20 text-red-400 hover:bg-red-500/30'
                      : 'bg-gradient-to-r from-indigo-500 to-purple-600 text-white hover:shadow-lg'
                  }`}
                >
                  {showCamera ? 'Cancel' : 'Start Verification'}
                </button>
              </div>

              {showCamera && (
                <div className="space-y-4 animate-fadeIn">
                  <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
                    <div>
                      <label className="block text-sm font-medium text-zinc-400 mb-2">Session ID</label>
                      <input
                        type="text"
                        value={sessionId}
                        onChange={(e) => setSessionId(e.target.value)}
                        placeholder="Enter session ID from teacher"
                        className="w-full px-4 py-3 bg-white/5 border border-white/10 rounded-xl text-white placeholder-zinc-500 focus:outline-none focus:border-indigo-500/50"
                      />
                    </div>
                    <div>
                      <label className="block text-sm font-medium text-zinc-400 mb-2">OTP</label>
                      <input
                        type="text"
                        value={otp}
                        onChange={(e) => setOtp(e.target.value)}
                        placeholder="Enter OTP"
                        className="w-full px-4 py-3 bg-white/5 border border-white/10 rounded-xl text-white placeholder-zinc-500 focus:outline-none focus:border-indigo-500/50 font-mono"
                      />
                    </div>
                  </div>

                  <div className="bg-white/5 rounded-xl p-4">
                    <p className="text-sm text-zinc-400 mb-3">Position your face in the frame</p>
                    <div className="flex justify-center">
                      <WebcamCapture 
                        onFrameCapture={handleFrameCapture}
                        showBoundingBox={true}
                        width={400}
                        height={300}
                      />
                    </div>
                  </div>

                  <button
                    onClick={handleVerifyAttendance}
                    disabled={isVerifying || !sessionId.trim() || !otp.trim() || !capturedImage}
                    className={`w-full py-4 rounded-xl font-semibold transition-all flex items-center justify-center gap-2 ${
                      sessionId.trim() && otp.trim() && capturedImage && !isVerifying
                        ? 'bg-gradient-to-r from-emerald-500 to-teal-600 text-white hover:shadow-lg'
                        : 'bg-zinc-800 text-zinc-500 cursor-not-allowed'
                    }`}
                  >
                    {isVerifying ? (
                      <>
                        <div className="w-5 h-5 border-2 border-white border-t-transparent rounded-full animate-spin"></div>
                        Verifying...
                      </>
                    ) : (
                      <>
                        <svg className="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                          <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M9 12l2 2 4-4m6 2a9 9 0 11-18 0 9 9 0 0118 0z" />
                        </svg>
                        Verify Attendance
                      </>
                    )}
                  </button>
                </div>
              )}
            </div>

            {/* Attendance History */}
            <div className="bg-[#1a1625]/80 backdrop-blur-xl border border-white/10 rounded-2xl p-6">
              <div className="flex items-center justify-between mb-6">
                <div>
                  <h2 className="text-xl font-bold text-white">Attendance History</h2>
                  <p className="text-sm text-zinc-500">{attendance.length} records</p>
                </div>
              </div>

              {attendance.length === 0 ? (
                <div className="text-center py-12">
                  <div className="w-16 h-16 bg-white/5 rounded-2xl flex items-center justify-center mx-auto mb-4">
                    <svg className="w-8 h-8 text-zinc-500" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                      <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M9 5H7a2 2 0 00-2 2v12a2 2 0 002 2h10a2 2 0 002-2V7a2 2 0 00-2-2h-2M9 5a2 2 0 002 2h2a2 2 0 002-2M9 5a2 2 0 012-2h2a2 2 0 012 2" />
                    </svg>
                  </div>
                  <p className="text-zinc-500">No attendance records yet</p>
                  <p className="text-zinc-600 text-sm mt-1">Mark your first attendance above</p>
                </div>
              ) : (
                <div className="overflow-x-auto">
                  <table className="w-full">
                    <thead>
                      <tr className="text-left text-zinc-500 text-sm border-b border-white/10">
                        <th className="pb-3 font-medium">Date & Time</th>
                        <th className="pb-3 font-medium">Class</th>
                        <th className="pb-3 font-medium">Status</th>
                        <th className="pb-3 font-medium">Confidence</th>
                      </tr>
                    </thead>
                    <tbody>
                      {attendance.map((record, i) => (
                        <tr key={record.id} className="border-b border-white/5 hover:bg-white/5 transition animate-fadeIn" style={{ animationDelay: `${i * 0.05}s` }}>
                          <td className="py-4 text-white">
                            {new Date(record.timestamp).toLocaleString()}
                          </td>
                          <td className="py-4 text-zinc-400">{record.class_id || 'N/A'}</td>
                          <td className="py-4">
                            <span className={`px-3 py-1 rounded-full text-xs font-medium ${
                              record.verification_status === 'verified'
                                ? 'bg-emerald-500/20 text-emerald-400'
                                : 'bg-red-500/20 text-red-400'
                            }`}>
                              {record.verification_status === 'verified' ? '✓ Verified' : '✗ Failed'}
                            </span>
                          </td>
                          <td className="py-4 text-zinc-400">
                            {record.face_confidence ? `${(record.face_confidence * 100).toFixed(1)}%` : 'N/A'}
                          </td>
                        </tr>
                      ))}
                    </tbody>
                  </table>
                </div>
              )}
            </div>
          </div>

          {/* Sidebar */}
          <div className="space-y-6">
            {/* Profile Card */}
            <div className="bg-[#1a1625]/80 backdrop-blur-xl border border-white/10 rounded-2xl p-6">
              <h3 className="text-lg font-semibold text-white mb-4">Profile</h3>
              <div className="text-center">
                <div className="w-20 h-20 bg-gradient-to-br from-indigo-500 to-purple-600 rounded-full flex items-center justify-center mx-auto mb-4 text-white text-2xl font-bold">
                  {user?.name?.charAt(0).toUpperCase()}
                </div>
                <p className="text-white font-semibold">{user?.name}</p>
                <p className="text-zinc-500 text-sm">{user?.email}</p>
                {profile?.student_id_card_number && (
                  <p className="text-zinc-400 text-xs mt-2 font-mono">ID: {profile.student_id_card_number}</p>
                )}
              </div>
            </div>

            {/* Quick Stats */}
            <div className="bg-[#1a1625]/80 backdrop-blur-xl border border-white/10 rounded-2xl p-6">
              <h3 className="text-lg font-semibold text-white mb-4">Quick Stats</h3>
              <div className="space-y-4">
                <div className="flex items-center justify-between">
                  <span className="text-zinc-400 text-sm">This Week</span>
                  <span className="text-white font-semibold">{attendedSessions} / {totalSessions}</span>
                </div>
                <div className="w-full bg-white/5 rounded-full h-2">
                  <div 
                    className="bg-gradient-to-r from-indigo-500 to-purple-600 h-2 rounded-full transition-all duration-1000"
                    style={{ width: `${attendanceRate}%` }}
                  ></div>
                </div>
                <div className="flex items-center justify-between text-sm">
                  <span className="text-zinc-500">Attendance Rate</span>
                  <span className="text-indigo-400 font-semibold">
                    <AnimatedCounter value={Math.round(attendanceRate)} suffix="%" />
                  </span>
                </div>
              </div>
            </div>

            {/* Instructions */}
            <div className="bg-[#1a1625]/80 backdrop-blur-xl border border-white/10 rounded-2xl p-6">
              <h3 className="text-lg font-semibold text-white mb-4">How to Mark Attendance</h3>
              <div className="space-y-3 text-sm text-zinc-400">
                <div className="flex items-start gap-3">
                  <div className="w-6 h-6 bg-indigo-500/20 rounded-full flex items-center justify-center flex-shrink-0 text-indigo-400 font-bold text-xs">1</div>
                  <p>Get Session ID and OTP from your teacher</p>
                </div>
                <div className="flex items-start gap-3">
                  <div className="w-6 h-6 bg-indigo-500/20 rounded-full flex items-center justify-center flex-shrink-0 text-indigo-400 font-bold text-xs">2</div>
                  <p>Click "Start Verification" and enter the details</p>
                </div>
                <div className="flex items-start gap-3">
                  <div className="w-6 h-6 bg-indigo-500/20 rounded-full flex items-center justify-center flex-shrink-0 text-indigo-400 font-bold text-xs">3</div>
                  <p>Position your face in the camera frame</p>
                </div>
                <div className="flex items-start gap-3">
                  <div className="w-6 h-6 bg-indigo-500/20 rounded-full flex items-center justify-center flex-shrink-0 text-indigo-400 font-bold text-xs">4</div>
                  <p>Click "Verify Attendance" to complete</p>
                </div>
              </div>
            </div>
          </div>
        </div>
      </main>
    </div>
  )
}
