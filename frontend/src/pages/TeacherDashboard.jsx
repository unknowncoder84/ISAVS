/**
 * ISAVS 2026 - Teacher Dashboard (Port 2000)
 * Professional sidebar with Active Sessions, Student List, and Anomaly Reports
 * Real-time WebSocket updates for live attendance tracking
 */
import React, { useState, useEffect, useRef } from 'react';
import { startSession, getReports, getAnomalies, getStudents } from '../services/api';

const TeacherDashboard = () => {
  const [activeTab, setActiveTab] = useState('overview');
  const [classId, setClassId] = useState('');
  const [activeSession, setActiveSession] = useState(null);
  const [students, setStudents] = useState([]);
  const [attendanceRecords, setAttendanceRecords] = useState([]);
  const [anomalies, setAnomalies] = useState([]);
  const [statistics, setStatistics] = useState(null);
  const [isLoading, setIsLoading] = useState(false);
  const [error, setError] = useState(null);
  const [liveUpdates, setLiveUpdates] = useState([]);
  const wsRef = useRef(null);

  // WebSocket connection for real-time updates
  useEffect(() => {
    const ws = new WebSocket('ws://localhost:6000/ws/dashboard');
    wsRef.current = ws;

    ws.onopen = () => {
      console.log('✅ WebSocket connected');
    };

    ws.onmessage = (event) => {
      const data = JSON.parse(event.data);
      
      if (data.type === 'attendance_update') {
        setLiveUpdates(prev => [data.data, ...prev].slice(0, 10));
        fetchData(); // Refresh data
      } else if (data.type === 'anomaly_alert') {
        setAnomalies(prev => [data.data, ...prev]);
      }
    };

    ws.onerror = (error) => {
      console.error('WebSocket error:', error);
    };

    ws.onclose = () => {
      console.log('WebSocket disconnected');
    };


    // Cleanup on unmount
    return () => {
      if (wsRef.current) {
        wsRef.current.close();
      }
    };
  }, []);

  // Fetch data
  const fetchData = async () => {
    try {
      const [reportsData, anomaliesData, studentsData] = await Promise.all([
        getReports(),
        getAnomalies({ unreviewed_only: false }),
        getStudents(true),
      ]);
      
      setAttendanceRecords(reportsData.attendance_records || []);
      setStatistics(reportsData.statistics);
      setAnomalies(anomaliesData.anomalies || []);
      setStudents(studentsData.students || []);
    } catch (err) {
      console.error('Data fetch error:', err);
    }
  };

  useEffect(() => {
    fetchData();
    const interval = setInterval(fetchData, 10000);
    return () => clearInterval(interval);
  }, []);

  // Start Session Handler
  const handleStartSession = async () => {
    if (!classId.trim()) {
      setError('Please enter a Class ID');
      return;
    }
    
    try {
      setIsLoading(true);
      setError(null);
      const response = await startSession(classId);
      
      if (response.success) {
        setActiveSession({
          sessionId: response.session_id,
          otpCount: response.otp_count,
          expiresAt: response.expires_at
        });
        setClassId('');
        fetchData();
      }
    } catch (err) {
      setError(err.message || 'Failed to start session');
    } finally {
      setIsLoading(false);
    }
  };

  const copyToClipboard = (text) => {
    navigator.clipboard.writeText(text);
  };

  const totalStudents = statistics?.total_students || students.length || 0;
  const verifiedCount = statistics?.verified_count || 0;
  const attendanceRate = statistics?.attendance_percentage || 0;
  const proxyAlerts = anomalies.filter(a => a.anomaly_type === 'proxy_attempt').length;

  return (
    <div className="min-h-screen bg-[#0f0d1a] flex">
      {/* Sidebar */}
      <aside className="w-72 bg-[#1a1625] border-r border-white/10 flex flex-col">
        <div className="p-6 border-b border-white/10">
          <h1 className="text-2xl font-bold text-white">ISAVS 2026</h1>
          <p className="text-zinc-500 text-sm">Teacher Dashboard</p>
        </div>

        <nav className="flex-1 p-4 space-y-2">
          {[
            { id: 'overview', label: 'Overview', icon: '📊' },
            { id: 'session', label: 'Start Session', icon: '🎯' },
            { id: 'students', label: 'Student List', icon: '👥' },
            { id: 'anomalies', label: 'Anomaly Reports', icon: '⚠️' },
          ].map((tab) => (
            <button
              key={tab.id}
              onClick={() => setActiveTab(tab.id)}
              className={`w-full px-4 py-3 rounded-xl text-left transition-all flex items-center gap-3 ${
                activeTab === tab.id
                  ? 'bg-gradient-to-r from-indigo-500 to-purple-600 text-white shadow-lg'
                  : 'text-zinc-400 hover:bg-white/5 hover:text-white'
              }`}
            >
              <span className="text-xl">{tab.icon}</span>
              <span className="font-medium">{tab.label}</span>
            </button>
          ))}
        </nav>

        {/* Stats Summary */}
        <div className="p-4 border-t border-white/10 space-y-3">
          <div className="flex items-center justify-between text-sm">
            <span className="text-zinc-500">Total Students</span>
            <span className="text-white font-bold">{totalStudents}</span>
          </div>
          <div className="flex items-center justify-between text-sm">
            <span className="text-zinc-500">Attendance Rate</span>
            <span className="text-emerald-400 font-bold">{Math.round(attendanceRate)}%</span>
          </div>
          <div className="flex items-center justify-between text-sm">
            <span className="text-zinc-500">Proxy Alerts</span>
            <span className="text-red-400 font-bold">{proxyAlerts}</span>
          </div>
        </div>
      </aside>

      {/* Main Content */}
      <main className="flex-1 overflow-y-auto">
        <header className="bg-[#1a1625]/80 backdrop-blur-xl border-b border-white/10 p-6">
          <div className="flex items-center justify-between">
            <div>
              <h2 className="text-2xl font-bold text-white">
                {activeTab === 'overview' && 'Dashboard Overview'}
                {activeTab === 'session' && 'Start New Session'}
                {activeTab === 'students' && 'Student List'}
                {activeTab === 'anomalies' && 'Anomaly Reports'}
              </h2>
              <p className="text-zinc-500 text-sm mt-1">Real-time attendance monitoring</p>
            </div>
            <div className="flex items-center gap-3">
              <div className="px-3 py-1.5 rounded-full text-xs font-medium flex items-center gap-2 bg-emerald-500/20 text-emerald-400">
                <span className="w-2 h-2 rounded-full bg-emerald-400 animate-pulse"></span>
                Live
              </div>
            </div>
          </div>
        </header>

        <div className="p-6">
          {error && (
            <div className="mb-4 p-4 bg-red-500/10 border border-red-500/20 rounded-xl text-red-400 text-sm">
              {error}
            </div>
          )}


          {/* Overview Tab */}
          {activeTab === 'overview' && (
            <div className="space-y-6">
              {/* Stats Cards */}
              <div className="grid grid-cols-4 gap-4">
                <div className="bg-[#1a1625] border border-white/10 rounded-xl p-6">
                  <div className="flex items-center justify-between mb-2">
                    <span className="text-zinc-500 text-sm">Total Students</span>
                    <span className="text-2xl">👥</span>
                  </div>
                  <p className="text-3xl font-bold text-white">{totalStudents}</p>
                </div>
                <div className="bg-[#1a1625] border border-white/10 rounded-xl p-6">
                  <div className="flex items-center justify-between mb-2">
                    <span className="text-zinc-500 text-sm">Verified Today</span>
                    <span className="text-2xl">✓</span>
                  </div>
                  <p className="text-3xl font-bold text-emerald-400">{verifiedCount}</p>
                </div>
                <div className="bg-[#1a1625] border border-white/10 rounded-xl p-6">
                  <div className="flex items-center justify-between mb-2">
                    <span className="text-zinc-500 text-sm">Attendance Rate</span>
                    <span className="text-2xl">📈</span>
                  </div>
                  <p className="text-3xl font-bold text-indigo-400">{Math.round(attendanceRate)}%</p>
                </div>
                <div className="bg-[#1a1625] border border-white/10 rounded-xl p-6">
                  <div className="flex items-center justify-between mb-2">
                    <span className="text-zinc-500 text-sm">Alerts</span>
                    <span className="text-2xl">⚠️</span>
                  </div>
                  <p className="text-3xl font-bold text-red-400">{proxyAlerts}</p>
                </div>
              </div>

              {/* Recent Activity */}
              <div className="bg-[#1a1625] border border-white/10 rounded-xl p-6">
                <h3 className="text-lg font-semibold text-white mb-4">Recent Check-ins</h3>
                {attendanceRecords.length === 0 ? (
                  <p className="text-center text-zinc-500 py-8">No attendance records yet</p>
                ) : (
                  <div className="space-y-3">
                    {attendanceRecords.slice(0, 10).map((record) => (
                      <div
                        key={record.id}
                        className="flex items-center gap-4 p-3 bg-white/5 rounded-xl hover:bg-white/10 transition"
                      >
                        <div className={`w-10 h-10 rounded-full flex items-center justify-center text-sm font-bold ${
                          record.verification_status === 'verified'
                            ? 'bg-emerald-500/20 text-emerald-400'
                            : 'bg-red-500/20 text-red-400'
                        }`}>
                          {record.verification_status === 'verified' ? '✓' : '✗'}
                        </div>
                        <div className="flex-1">
                          <p className="text-white font-medium">{record.student_name}</p>
                          <p className="text-zinc-500 text-xs">{record.student_id_card_number}</p>
                        </div>
                        <div className="text-right">
                          <p className="text-zinc-400 text-sm">
                            {record.face_confidence ? `${(record.face_confidence * 100).toFixed(0)}%` : '-'}
                          </p>
                          <p className="text-zinc-600 text-xs">
                            {new Date(record.timestamp).toLocaleTimeString()}
                          </p>
                        </div>
                      </div>
                    ))}
                  </div>
                )}
              </div>
            </div>
          )}

          {/* Start Session Tab */}
          {activeTab === 'session' && (
            <div className="max-w-2xl mx-auto">
              <div className="bg-[#1a1625] border border-white/10 rounded-xl p-8">
                <div className="text-center mb-8">
                  <div className="w-20 h-20 bg-gradient-to-br from-indigo-500 to-purple-600 rounded-3xl flex items-center justify-center mx-auto mb-4">
                    <span className="text-4xl">🎯</span>
                  </div>
                  <h3 className="text-2xl font-bold text-white">Start New Session</h3>
                  <p className="text-zinc-500 mt-2">Generate unique 4-digit OTPs for all students</p>
                </div>

                <div className="space-y-4">
                  <div>
                    <label className="block text-sm font-medium text-zinc-400 mb-2">Class ID</label>
                    <input
                      type="text"
                      value={classId}
                      onChange={(e) => setClassId(e.target.value)}
                      onKeyDown={(e) => e.key === 'Enter' && handleStartSession()}
                      placeholder="e.g., CS101, MATH201"
                      className="w-full px-4 py-3 bg-white/5 border border-white/10 rounded-xl text-white placeholder-zinc-500 focus:outline-none focus:border-indigo-500/50"
                    />
                  </div>

                  <button
                    onClick={handleStartSession}
                    disabled={isLoading || !classId.trim()}
                    className={`w-full py-4 rounded-xl font-semibold text-lg transition-all ${
                      classId.trim() && !isLoading
                        ? 'bg-gradient-to-r from-indigo-500 to-purple-600 text-white hover:shadow-lg hover:scale-[1.02]'
                        : 'bg-zinc-800 text-zinc-500 cursor-not-allowed'
                    }`}
                  >
                    {isLoading ? 'Starting Session...' : '🚀 Start Session & Generate OTPs'}
                  </button>
                </div>

                {activeSession && (
                  <div className="mt-8 p-6 bg-emerald-500/10 border border-emerald-500/20 rounded-xl">
                    <div className="flex items-center gap-2 text-emerald-400 font-semibold mb-4">
                      <span className="w-2 h-2 bg-emerald-400 rounded-full animate-pulse"></span>
                      Session Active
                    </div>
                    <div className="text-center mb-4">
                      <p className="text-zinc-400 text-sm mb-2">Share this Session ID with students</p>
                      <div
                        onClick={() => copyToClipboard(activeSession.sessionId)}
                        className="bg-white/5 rounded-xl py-3 px-4 cursor-pointer hover:bg-white/10 transition"
                      >
                        <p className="text-lg font-mono font-bold text-white break-all">
                          {activeSession.sessionId}
                        </p>
                        <p className="text-xs text-zinc-500 mt-1">Click to copy</p>
                      </div>
                    </div>
                    <p className="text-xs text-emerald-400/70 text-center">
                      {activeSession.otpCount} students • OTPs valid for 60 seconds
                    </p>
                  </div>
                )}
              </div>
            </div>
          )}


          {/* Students Tab */}
          {activeTab === 'students' && (
            <div className="bg-[#1a1625] border border-white/10 rounded-xl p-6">
              <div className="flex items-center justify-between mb-6">
                <h3 className="text-lg font-semibold text-white">Enrolled Students</h3>
                <span className="text-zinc-500 text-sm">{students.length} total</span>
              </div>
              {students.length === 0 ? (
                <p className="text-center text-zinc-500 py-8">No students enrolled yet</p>
              ) : (
                <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-4">
                  {students.map((student) => (
                    <div
                      key={student.id}
                      className="bg-white/5 border border-white/10 rounded-xl p-4 hover:bg-white/10 transition"
                    >
                      <div className="flex items-center gap-3 mb-3">
                        {student.face_image ? (
                          <img
                            src={student.face_image}
                            alt={student.name}
                            className="w-12 h-12 rounded-full object-cover"
                          />
                        ) : (
                          <div className="w-12 h-12 rounded-full bg-indigo-500/20 flex items-center justify-center text-indigo-400 font-bold">
                            {student.name.charAt(0)}
                          </div>
                        )}
                        <div className="flex-1 min-w-0">
                          <p className="text-white font-medium truncate">{student.name}</p>
                          <p className="text-zinc-500 text-xs">{student.student_id_card_number}</p>
                        </div>
                      </div>
                      <div className="text-xs text-zinc-600">
                        Enrolled: {new Date(student.created_at).toLocaleDateString()}
                      </div>
                    </div>
                  ))}
                </div>
              )}
            </div>
          )}

          {/* Anomalies Tab */}
          {activeTab === 'anomalies' && (
            <div className="bg-[#1a1625] border border-white/10 rounded-xl p-6">
              <div className="flex items-center justify-between mb-6">
                <h3 className="text-lg font-semibold text-white">Anomaly Reports</h3>
                <span className="text-zinc-500 text-sm">{anomalies.length} total</span>
              </div>
              {anomalies.length === 0 ? (
                <p className="text-center text-zinc-500 py-8">No anomalies detected</p>
              ) : (
                <div className="space-y-3">
                  {anomalies.map((anomaly) => (
                    <div
                      key={anomaly.id}
                      className={`p-4 rounded-xl border ${
                        anomaly.anomaly_type === 'proxy_attempt'
                          ? 'bg-red-500/10 border-red-500/20'
                          : 'bg-amber-500/10 border-amber-500/20'
                      }`}
                    >
                      <div className="flex items-start gap-3">
                        <div className={`w-10 h-10 rounded-full flex items-center justify-center flex-shrink-0 ${
                          anomaly.anomaly_type === 'proxy_attempt'
                            ? 'bg-red-500/20 text-red-400'
                            : 'bg-amber-500/20 text-amber-400'
                        }`}>
                          {anomaly.anomaly_type === 'proxy_attempt' ? '🚨' : '⚠️'}
                        </div>
                        <div className="flex-1">
                          <div className="flex items-center justify-between mb-1">
                            <p className={`font-semibold ${
                              anomaly.anomaly_type === 'proxy_attempt' ? 'text-red-400' : 'text-amber-400'
                            }`}>
                              {anomaly.anomaly_type === 'proxy_attempt' ? 'PROXY ATTEMPT' : 'Identity Mismatch'}
                            </p>
                            <span className="text-zinc-600 text-xs">
                              {new Date(anomaly.timestamp).toLocaleString()}
                            </span>
                          </div>
                          <p className="text-white text-sm mb-1">{anomaly.student_name || 'Unknown Student'}</p>
                          <p className="text-zinc-400 text-sm">{anomaly.reason}</p>
                          {anomaly.face_confidence !== null && (
                            <p className="text-zinc-500 text-xs mt-2">
                              Face Confidence: {(anomaly.face_confidence * 100).toFixed(0)}%
                            </p>
                          )}
                        </div>
                      </div>
                    </div>
                  ))}
                </div>
              )}
            </div>
          )}
        </div>
      </main>
    </div>
  );
};

export default TeacherDashboard;
