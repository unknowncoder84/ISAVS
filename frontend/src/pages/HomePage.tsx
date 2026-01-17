import { Link } from 'react-router-dom'

export default function HomePage() {
  return (
    <div className="min-h-screen bg-[#0f0d1a] relative overflow-hidden">
      {/* Animated Background */}
      <div className="absolute inset-0 overflow-hidden">
        <div className="absolute -top-1/2 -left-1/2 w-full h-full bg-gradient-to-br from-indigo-500/20 to-purple-500/20 rounded-full blur-3xl animate-pulse"></div>
        <div className="absolute -bottom-1/2 -right-1/2 w-full h-full bg-gradient-to-tl from-purple-500/20 to-pink-500/20 rounded-full blur-3xl animate-pulse" style={{ animationDelay: '1s' }}></div>
      </div>

      {/* Content */}
      <div className="relative z-10">
        {/* Header */}
        <div className="container mx-auto px-4 py-12">
          <div className="text-center">
            <div className="inline-block p-4 bg-gradient-to-br from-indigo-500 to-purple-600 rounded-2xl shadow-2xl shadow-indigo-500/50 mb-6">
              <svg className="w-16 h-16 text-white" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M12 4.354a4 4 0 110 5.292M15 21H3v-1a6 6 0 0112 0v1zm0 0h6v-1a6 6 0 00-9-5.197M13 7a4 4 0 11-8 0 4 4 0 018 0z" />
              </svg>
            </div>
            <h1 className="text-6xl font-bold text-white mb-4">ISAVS</h1>
            <p className="text-xl text-zinc-400">Intelligent Student Attendance Verification System</p>
            <p className="text-sm text-zinc-500 mt-2">Secure biometric attendance with face recognition</p>
          </div>
        </div>

        {/* Main Content */}
        <div className="container mx-auto px-4 py-12">
          <div className="text-center mb-12">
            <h2 className="text-3xl font-bold text-white mb-3">Choose Your Portal</h2>
            <p className="text-zinc-400">Select your role to continue</p>
          </div>

          <div className="grid md:grid-cols-3 gap-8 max-w-6xl mx-auto">
            {/* Student Portal */}
            <Link to="/login/portal">
              <div className="bg-[#1a1625]/80 backdrop-blur-xl border border-white/10 rounded-2xl shadow-2xl p-8 hover:border-indigo-500/50 transition-all duration-300 transform hover:scale-105 cursor-pointer group">
                <div className="text-center">
                  <div className="bg-gradient-to-br from-blue-500 to-purple-500 rounded-2xl w-20 h-20 flex items-center justify-center mx-auto mb-6 group-hover:scale-110 transition-transform shadow-lg shadow-blue-500/50">
                    <svg className="w-10 h-10 text-white" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                      <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M16 7a4 4 0 11-8 0 4 4 0 018 0zM12 14a7 7 0 00-7 7h14a7 7 0 00-7-7z" />
                    </svg>
                  </div>
                  <h3 className="text-2xl font-bold text-white mb-3">Student Portal</h3>
                  <p className="text-zinc-400 mb-6 text-sm">
                    Mark attendance with face recognition, view records, and track your progress
                  </p>
                  <div className="bg-gradient-to-r from-blue-500 to-purple-500 text-white py-3 rounded-xl font-semibold group-hover:shadow-lg group-hover:shadow-blue-500/50 transition-all">
                    Student Login →
                  </div>
                </div>
              </div>
            </Link>

            {/* Teacher Portal */}
            <Link to="/login/portal">
              <div className="bg-[#1a1625]/80 backdrop-blur-xl border border-white/10 rounded-2xl shadow-2xl p-8 hover:border-indigo-500/50 transition-all duration-300 transform hover:scale-105 cursor-pointer group">
                <div className="text-center">
                  <div className="bg-gradient-to-br from-indigo-500 to-purple-600 rounded-2xl w-20 h-20 flex items-center justify-center mx-auto mb-6 group-hover:scale-110 transition-transform shadow-lg shadow-indigo-500/50">
                    <svg className="w-10 h-10 text-white" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                      <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M21 13.255A23.931 23.931 0 0112 15c-3.183 0-6.22-.62-9-1.745M16 6V4a2 2 0 00-2-2h-4a2 2 0 00-2 2v2m4 6h.01M5 20h14a2 2 0 002-2V8a2 2 0 00-2-2H5a2 2 0 00-2 2v10a2 2 0 002 2z" />
                    </svg>
                  </div>
                  <h3 className="text-2xl font-bold text-white mb-3">Teacher Portal</h3>
                  <p className="text-zinc-400 mb-6 text-sm">
                    Manage sessions, generate OTPs, enroll students, and view analytics
                  </p>
                  <div className="bg-gradient-to-r from-indigo-500 to-purple-600 text-white py-3 rounded-xl font-semibold group-hover:shadow-lg group-hover:shadow-indigo-500/50 transition-all">
                    Teacher Login →
                  </div>
                </div>
              </div>
            </Link>

            {/* Admin Portal */}
            <Link to="/login">
              <div className="bg-[#1a1625]/80 backdrop-blur-xl border border-white/10 rounded-2xl shadow-2xl p-8 hover:border-purple-500/50 transition-all duration-300 transform hover:scale-105 cursor-pointer group">
                <div className="text-center">
                  <div className="bg-gradient-to-br from-purple-500 to-pink-600 rounded-2xl w-20 h-20 flex items-center justify-center mx-auto mb-6 group-hover:scale-110 transition-transform shadow-lg shadow-purple-500/50">
                    <svg className="w-10 h-10 text-white" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                      <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M9 12l2 2 4-4m5.618-4.016A11.955 11.955 0 0112 2.944a11.955 11.955 0 01-8.618 3.04A12.02 12.02 0 003 9c0 5.591 3.824 10.29 9 11.622 5.176-1.332 9-6.03 9-11.622 0-1.042-.133-2.052-.382-3.016z" />
                    </svg>
                  </div>
                  <h3 className="text-2xl font-bold text-white mb-3">Admin Portal</h3>
                  <p className="text-zinc-400 mb-6 text-sm">
                    Approve students, manage teachers, and oversee the entire system
                  </p>
                  <div className="bg-gradient-to-r from-purple-500 to-pink-600 text-white py-3 rounded-xl font-semibold group-hover:shadow-lg group-hover:shadow-purple-500/50 transition-all">
                    Admin Login →
                  </div>
                </div>
              </div>
            </Link>
          </div>
        </div>

        {/* Features */}
        <div className="container mx-auto px-4 py-12">
          <div className="grid md:grid-cols-3 gap-6 max-w-4xl mx-auto">
            <div className="bg-white/5 backdrop-blur-xl border border-white/10 rounded-xl p-6 text-center">
              <div className="w-12 h-12 bg-emerald-500/20 rounded-lg flex items-center justify-center mx-auto mb-4">
                <svg className="w-6 h-6 text-emerald-400" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                  <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M9 12l2 2 4-4m6 2a9 9 0 11-18 0 9 9 0 0118 0z" />
                </svg>
              </div>
              <h4 className="text-white font-semibold mb-2">Face Recognition</h4>
              <p className="text-zinc-500 text-sm">Advanced AI-powered biometric verification</p>
            </div>
            <div className="bg-white/5 backdrop-blur-xl border border-white/10 rounded-xl p-6 text-center">
              <div className="w-12 h-12 bg-blue-500/20 rounded-lg flex items-center justify-center mx-auto mb-4">
                <svg className="w-6 h-6 text-blue-400" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                  <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M12 15v2m-6 4h12a2 2 0 002-2v-6a2 2 0 00-2-2H6a2 2 0 00-2 2v6a2 2 0 002 2zm10-10V7a4 4 0 00-8 0v4h8z" />
                </svg>
              </div>
              <h4 className="text-white font-semibold mb-2">Secure & Private</h4>
              <p className="text-zinc-500 text-sm">End-to-end encrypted data protection</p>
            </div>
            <div className="bg-white/5 backdrop-blur-xl border border-white/10 rounded-xl p-6 text-center">
              <div className="w-12 h-12 bg-purple-500/20 rounded-lg flex items-center justify-center mx-auto mb-4">
                <svg className="w-6 h-6 text-purple-400" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                  <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M13 10V3L4 14h7v7l9-11h-7z" />
                </svg>
              </div>
              <h4 className="text-white font-semibold mb-2">Real-time</h4>
              <p className="text-zinc-500 text-sm">Instant verification and updates</p>
            </div>
          </div>
        </div>

        {/* Footer */}
        <div className="container mx-auto px-4 py-8 text-center">
          <p className="text-zinc-500 text-sm">
            © 2026 ISAVS. All rights reserved.
          </p>
        </div>
      </div>
    </div>
  )
}
