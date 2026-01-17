/**
 * Faculty Dashboard - Full Featured with Real Data, Graphs, Calendar, Analytics
 * Blue/Purple Gradient Theme (Campus Connect Inspired)
 */
import React, { useState, useEffect, useCallback, useRef } from 'react';
import { Link } from 'react-router-dom';
import StatCard from './ui/StatCard';
import {
  getReports,
  getAnomalies,
  startSession,
  getStudents,
  handleApiError,
  unlockStudentAccount,
  deleteStudent,
  AttendanceRecord,
  Anomaly,
  AttendanceStatistics,
} from '../services/api';

type TabType = 'overview' | 'session' | 'attendance' | 'students' | 'analytics' | 'calendar';

// Interactive Grid Background Component
const GridBackground: React.FC = () => {
  const containerRef = useRef<HTMLDivElement>(null);
  const [mousePos, setMousePos] = useState({ x: 0, y: 0 });

  useEffect(() => {
    const handleMouseMove = (e: MouseEvent) => {
      if (containerRef.current) {
        const rect = containerRef.current.getBoundingClientRect();
        setMousePos({
          x: e.clientX - rect.left,
          y: e.clientY - rect.top
        });
      }
    };
    window.addEventListener('mousemove', handleMouseMove);
    return () => window.removeEventListener('mousemove', handleMouseMove);
  }, []);

  return (
    <div ref={containerRef} className="fixed inset-0 overflow-hidden pointer-events-none z-0">
      <div className="absolute inset-0 grid grid-cols-12 grid-rows-8 gap-8 p-8 opacity-30">
        {Array.from({ length: 96 }).map((_, i) => {
          const col = i % 12;
          const row = Math.floor(i / 12);
          const cellX = (col + 0.5) * (100 / 12);
          const cellY = (row + 0.5) * (100 / 8);
          const dist = Math.sqrt(
            Math.pow((mousePos.x / window.innerWidth * 100) - cellX, 2) +
            Math.pow((mousePos.y / window.innerHeight * 100) - cellY, 2)
          );
          const scale = Math.max(0.3, 1 - dist / 30);
          const opacity = Math.max(0.2, 1 - dist / 25);
          
          return (
            <div
              key={i}
              className="flex items-center justify-center transition-all duration-300"
              style={{ transform: `scale(${scale})`, opacity }}
            >
              <div className="w-1.5 h-1.5 bg-indigo-500/50 rounded-full" />
            </div>
          );
        })}
      </div>
    </div>
  );
};


// Animated Counter Component
const AnimatedCounter: React.FC<{ value: number; duration?: number; suffix?: string }> = ({ 
  value, duration = 1000, suffix = '' 
}) => {
  const [displayValue, setDisplayValue] = useState(0);
  
  useEffect(() => {
    let startTime: number;
    let animationFrame: number;
    
    const animate = (timestamp: number) => {
      if (!startTime) startTime = timestamp;
      const progress = Math.min((timestamp - startTime) / duration, 1);
      const easeOut = 1 - Math.pow(1 - progress, 3);
      setDisplayValue(Math.floor(easeOut * value));
      
      if (progress < 1) {
        animationFrame = requestAnimationFrame(animate);
      }
    };
    
    animationFrame = requestAnimationFrame(animate);
    return () => cancelAnimationFrame(animationFrame);
  }, [value, duration]);
  
  return <span>{displayValue}{suffix}</span>;
};

// Real-time Clock Component
const LiveClock: React.FC = () => {
  const [time, setTime] = useState(new Date());
  
  useEffect(() => {
    const timer = setInterval(() => setTime(new Date()), 1000);
    return () => clearInterval(timer);
  }, []);
  
  return (
    <div className="text-right">
      <p className="text-2xl font-bold text-white font-mono">
        {time.toLocaleTimeString('en-US', { hour: '2-digit', minute: '2-digit', second: '2-digit' })}
      </p>
      <p className="text-xs text-zinc-500">
        {time.toLocaleDateString('en-US', { weekday: 'long', month: 'short', day: 'numeric' })}
      </p>
    </div>
  );
};

const FacultyDashboard: React.FC = () => {
  const [activeTab, setActiveTab] = useState<TabType>('overview');
  const [attendanceRecords, setAttendanceRecords] = useState<AttendanceRecord[]>([]);
  const [anomalies, setAnomalies] = useState<Anomaly[]>([]);
  const [statistics, setStatistics] = useState<AttendanceStatistics | null>(null);
  const [students, setStudents] = useState<any[]>([]);
  const [isLoading, setIsLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const [classId, setClassId] = useState('');
  const [activeSession, setActiveSession] = useState<{ sessionId: string; otpCount: number } | null>(null);
  const [copied, setCopied] = useState(false);
  const [currentMonth, setCurrentMonth] = useState(new Date());
  const [lastUpdated, setLastUpdated] = useState<Date | null>(null);

  // Real attendance data for graph (will be populated from API)
  const [weeklyData, setWeeklyData] = useState<number[]>([0, 0, 0, 0, 0, 0, 0]);
  const weekDays = ['Mon', 'Tue', 'Wed', 'Thu', 'Fri', 'Sat', 'Sun'];

  const fetchData = useCallback(async () => {
    setIsLoading(true);
    setError(null);
    try {
      const [reportsData, anomaliesData, studentsData] = await Promise.all([
        getReports(),
        getAnomalies({ unreviewed_only: false }),
        getStudents(true), // Fetch with images
      ]);
      
      setAttendanceRecords(reportsData.attendance_records || []);
      setStatistics(reportsData.statistics);
      setAnomalies(anomaliesData.anomalies || []);
      setStudents(studentsData.students || []);
      setLastUpdated(new Date());
      
      // Calculate weekly data from real records
      const now = new Date();
      const weekStart = new Date(now);
      weekStart.setDate(now.getDate() - now.getDay() + 1);
      
      const dailyCounts = [0, 0, 0, 0, 0, 0, 0];
      (reportsData.attendance_records || []).forEach((record: AttendanceRecord) => {
        const recordDate = new Date(record.timestamp);
        const dayDiff = Math.floor((recordDate.getTime() - weekStart.getTime()) / (1000 * 60 * 60 * 24));
        if (dayDiff >= 0 && dayDiff < 7 && record.verification_status === 'verified') {
          dailyCounts[dayDiff]++;
        }
      });
      
      // Convert to percentages based on total students
      const total = studentsData.students?.length || 1;
      setWeeklyData(dailyCounts.map(c => Math.min(100, Math.round((c / total) * 100))));
      
    } catch (err) {
      console.log('Data fetch:', err);
    } finally {
      setIsLoading(false);
    }
  }, []);

  useEffect(() => {
    fetchData();
    const interval = setInterval(fetchData, 10000); // Refresh every 10 seconds
    return () => clearInterval(interval);
  }, [fetchData]);


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
        setActiveSession({ sessionId: response.session_id, otpCount: response.otp_count });
        setClassId('');
        fetchData(); // Refresh data
      }
    } catch (err) {
      setError(handleApiError(err));
    } finally {
      setIsLoading(false);
    }
  };

  const copyToClipboard = (text: string) => {
    navigator.clipboard.writeText(text);
    setCopied(true);
    setTimeout(() => setCopied(false), 2000);
  };

  // Calendar helpers
  const getDaysInMonth = (date: Date) => {
    const year = date.getFullYear();
    const month = date.getMonth();
    const firstDay = new Date(year, month, 1).getDay();
    const daysInMonth = new Date(year, month + 1, 0).getDate();
    return { firstDay, daysInMonth };
  };

  const { firstDay, daysInMonth } = getDaysInMonth(currentMonth);
  const monthNames = ['January', 'February', 'March', 'April', 'May', 'June', 'July', 'August', 'September', 'October', 'November', 'December'];

  // Real stats from API
  const totalStudents = statistics?.total_students || students.length || 0;
  const verifiedCount = statistics?.verified_count || 0;
  const attendanceRate = statistics?.attendance_percentage || 0;
  const proxyAlerts = anomalies.length;

  // Animated Graph component with real data
  const AttendanceGraph = () => {
    const maxValue = Math.max(...weeklyData, 1);
    return (
      <div className="bg-[#1a1625]/80 backdrop-blur-xl border border-white/10 rounded-2xl p-6 relative overflow-hidden">
        <div className="absolute inset-0 bg-gradient-to-br from-indigo-500/5 to-purple-500/5"></div>
        <div className="relative z-10">
          <div className="flex items-center justify-between mb-6">
            <div>
              <h3 className="text-lg font-semibold text-white">Weekly Attendance</h3>
              <p className="text-xs text-zinc-500">Real-time data from this week</p>
            </div>
            <div className="flex items-center gap-2">
              <span className="w-2 h-2 bg-emerald-400 rounded-full animate-pulse"></span>
              <span className="text-xs text-emerald-400">Live</span>
            </div>
          </div>
          <div className="flex items-end justify-between gap-3 h-44">
            {weeklyData.map((value, i) => (
              <div key={i} className="flex-1 flex flex-col items-center gap-2">
                <div className="w-full bg-white/5 rounded-lg relative h-32 overflow-hidden group">
                  <div 
                    className="absolute bottom-0 w-full bg-gradient-to-t from-indigo-600 via-indigo-500 to-purple-500 rounded-lg transition-all duration-1000 ease-out group-hover:from-indigo-500 group-hover:to-purple-400"
                    style={{ 
                      height: `${(value / maxValue) * 100}%`,
                      boxShadow: value > 0 ? '0 0 20px rgba(99, 102, 241, 0.4)' : 'none'
                    }}
                  >
                    <div className="absolute inset-0 bg-gradient-to-t from-transparent to-white/20"></div>
                  </div>
                  <div className="absolute top-2 left-1/2 -translate-x-1/2 text-xs font-bold text-white opacity-0 group-hover:opacity-100 transition-opacity">
                    {value}%
                  </div>
                </div>
                <span className="text-xs text-zinc-500 font-medium">{weekDays[i]}</span>
              </div>
            ))}
          </div>
        </div>
      </div>
    );
  };


  // Icon components for StatCard
  const UsersIcon = () => (
    <svg className="w-6 h-6" fill="none" stroke="currentColor" viewBox="0 0 24 24">
      <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M17 20h5v-2a3 3 0 00-5.356-1.857M17 20H7m10 0v-2c0-.656-.126-1.283-.356-1.857M7 20H2v-2a3 3 0 015.356-1.857M7 20v-2c0-.656.126-1.283.356-1.857m0 0a5.002 5.002 0 019.288 0M15 7a3 3 0 11-6 0 3 3 0 016 0z" />
    </svg>
  );

  const CheckCircleIcon = () => (
    <svg className="w-6 h-6" fill="none" stroke="currentColor" viewBox="0 0 24 24">
      <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M9 12l2 2 4-4m6 2a9 9 0 11-18 0 9 9 0 0118 0z" />
    </svg>
  );

  const CheckIcon = () => (
    <svg className="w-6 h-6" fill="none" stroke="currentColor" viewBox="0 0 24 24">
      <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M5 13l4 4L19 7" />
    </svg>
  );

  const AlertIcon = () => (
    <svg className="w-6 h-6" fill="none" stroke="currentColor" viewBox="0 0 24 24">
      <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M12 9v2m0 4h.01m-6.938 4h13.856c1.54 0 2.502-1.667 1.732-3L13.732 4c-.77-1.333-2.694-1.333-3.464 0L3.34 16c-.77 1.333.192 3 1.732 3z" />
    </svg>
  );

  // Calendar Component with session markers
  const CalendarView = () => {
    // Get days with sessions from attendance records
    const sessionDays = new Set<number>();
    attendanceRecords.forEach(record => {
      const date = new Date(record.timestamp);
      if (date.getMonth() === currentMonth.getMonth() && date.getFullYear() === currentMonth.getFullYear()) {
        sessionDays.add(date.getDate());
      }
    });

    return (
      <div className="bg-[#1a1625]/80 backdrop-blur-xl border border-white/10 rounded-2xl p-6">
        <div className="flex items-center justify-between mb-6">
          <h3 className="text-lg font-semibold text-white">{monthNames[currentMonth.getMonth()]} {currentMonth.getFullYear()}</h3>
          <div className="flex gap-2">
            <button onClick={() => setCurrentMonth(new Date(currentMonth.getFullYear(), currentMonth.getMonth() - 1))} className="w-8 h-8 bg-white/5 hover:bg-white/10 rounded-lg flex items-center justify-center text-white transition">
              <svg className="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M15 19l-7-7 7-7" /></svg>
            </button>
            <button onClick={() => setCurrentMonth(new Date(currentMonth.getFullYear(), currentMonth.getMonth() + 1))} className="w-8 h-8 bg-white/5 hover:bg-white/10 rounded-lg flex items-center justify-center text-white transition">
              <svg className="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M9 5l7 7-7 7" /></svg>
            </button>
          </div>
        </div>
        <div className="grid grid-cols-7 gap-1 mb-2">
          {['Su', 'Mo', 'Tu', 'We', 'Th', 'Fr', 'Sa'].map(day => (
            <div key={day} className="text-center text-xs text-zinc-500 py-2 font-medium">{day}</div>
          ))}
        </div>
        <div className="grid grid-cols-7 gap-1">
          {Array(firstDay).fill(null).map((_, i) => <div key={`empty-${i}`} className="aspect-square"></div>)}
          {Array(daysInMonth).fill(null).map((_, i) => {
            const day = i + 1;
            const isToday = day === new Date().getDate() && currentMonth.getMonth() === new Date().getMonth() && currentMonth.getFullYear() === new Date().getFullYear();
            const hasSession = sessionDays.has(day);
            return (
              <button key={day} className={`aspect-square rounded-lg flex items-center justify-center text-sm transition-all relative ${isToday ? 'bg-indigo-500 text-white shadow-lg shadow-indigo-500/30' : hasSession ? 'bg-emerald-500/20 text-emerald-400 hover:bg-emerald-500/30' : 'text-zinc-400 hover:bg-white/5'}`}>
                {day}
                {hasSession && !isToday && <span className="absolute bottom-1 w-1 h-1 bg-emerald-400 rounded-full"></span>}
              </button>
            );
          })}
        </div>
        <div className="flex items-center gap-4 mt-4 pt-4 border-t border-white/5">
          <div className="flex items-center gap-2"><div className="w-3 h-3 rounded-full bg-indigo-500"></div><span className="text-xs text-zinc-400">Today</span></div>
          <div className="flex items-center gap-2"><div className="w-3 h-3 rounded-full bg-emerald-500/50"></div><span className="text-xs text-zinc-400">Has Records</span></div>
        </div>
      </div>
    );
  };


  return (
    <div className="min-h-screen bg-[#0f0d1a] relative">
      <GridBackground />
      
      {/* Header */}
      <header className="sticky top-0 z-50 bg-[#0f0d1a]/80 backdrop-blur-xl border-b border-white/5">
        <div className="max-w-7xl mx-auto px-4 py-4 flex items-center justify-between">
          <div className="flex items-center gap-4">
            <Link to="/" className="w-10 h-10 bg-white/5 hover:bg-white/10 rounded-xl flex items-center justify-center transition group">
              <svg className="w-5 h-5 text-white group-hover:-translate-x-0.5 transition-transform" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M15 19l-7-7 7-7" />
              </svg>
            </Link>
            <div>
              <h1 className="text-xl font-bold text-white">Dashboard</h1>
              <p className="text-xs text-zinc-500">
                {lastUpdated ? `Updated ${lastUpdated.toLocaleTimeString()}` : 'Loading...'}
              </p>
            </div>
          </div>
          <div className="flex items-center gap-4">
            <LiveClock />
            <div className="flex items-center gap-3">
              <button className="w-10 h-10 bg-white/5 hover:bg-white/10 rounded-xl flex items-center justify-center transition relative group">
                <svg className="w-5 h-5 text-white" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                  <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M15 17h5l-1.405-1.405A2.032 2.032 0 0118 14.158V11a6.002 6.002 0 00-4-5.659V5a2 2 0 10-4 0v.341C7.67 6.165 6 8.388 6 11v3.159c0 .538-.214 1.055-.595 1.436L4 17h5m6 0v1a3 3 0 11-6 0v-1m6 0H9" />
                </svg>
                {proxyAlerts > 0 && (
                  <span className="absolute -top-1 -right-1 w-5 h-5 bg-red-500 rounded-full text-xs text-white flex items-center justify-center animate-pulse">
                    {proxyAlerts}
                  </span>
                )}
              </button>
              <button onClick={fetchData} disabled={isLoading} className="w-10 h-10 bg-white/5 hover:bg-white/10 rounded-xl flex items-center justify-center transition">
                <svg className={`w-5 h-5 text-white ${isLoading ? 'animate-spin' : ''}`} fill="none" stroke="currentColor" viewBox="0 0 24 24">
                  <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M4 4v5h.582m15.356 2A8.001 8.001 0 004.582 9m0 0H9m11 11v-5h-.581m0 0a8.003 8.003 0 01-15.357-2m15.357 2H15" />
                </svg>
              </button>
              <div className={`px-3 py-1.5 rounded-full text-xs font-medium flex items-center gap-2 ${isLoading ? 'bg-amber-500/20 text-amber-400' : 'bg-emerald-500/20 text-emerald-400'}`}>
                <span className={`w-2 h-2 rounded-full ${isLoading ? 'bg-amber-400 animate-pulse' : 'bg-emerald-400'}`}></span>
                {isLoading ? 'Syncing' : 'Live'}
              </div>
            </div>
          </div>
        </div>
      </header>

      <main className="relative z-10 max-w-7xl mx-auto px-4 py-6">
        {/* Stats Grid */}
        <div className="grid grid-cols-2 lg:grid-cols-4 gap-4 mb-6">
          <StatCard 
            title="Total Students" 
            value={totalStudents} 
            icon={<UsersIcon />}
          />
          <StatCard 
            title="Attendance Rate" 
            value={`${Math.round(attendanceRate)}%`}
            icon={<CheckCircleIcon />}
            trend={attendanceRate > 80 ? { value: 12, positive: true } : undefined}
          />
          <StatCard 
            title="Verified Today" 
            value={verifiedCount} 
            icon={<CheckIcon />}
          />
          <StatCard 
            title="Alerts" 
            value={proxyAlerts} 
            icon={<AlertIcon />}
          />
        </div>


        {/* Error */}
        {error && (
          <div className="mb-4 p-4 bg-red-500/10 border border-red-500/20 rounded-xl text-red-400 text-sm flex items-center gap-3 animate-fadeIn">
            <svg className="w-5 h-5 flex-shrink-0" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M12 8v4m0 4h.01M21 12a9 9 0 11-18 0 9 9 0 0118 0z" /></svg>
            <span className="flex-1">{error}</span>
            <button onClick={() => setError(null)} className="text-red-300 hover:text-white transition">✕</button>
          </div>
        )}

        {/* Tabs */}
        <div className="flex gap-2 mb-6 overflow-x-auto pb-2 scrollbar-hide">
          {[
            { id: 'overview' as TabType, label: 'Overview', icon: '📊' },
            { id: 'session' as TabType, label: 'Start Session', icon: '🎯' },
            { id: 'attendance' as TabType, label: 'Attendance', icon: '📋' },
            { id: 'students' as TabType, label: 'Students', icon: '👥' },
            { id: 'analytics' as TabType, label: 'Analytics', icon: '📈' },
            { id: 'calendar' as TabType, label: 'Calendar', icon: '📅' },
          ].map((tab) => (
            <button 
              key={tab.id} 
              onClick={() => setActiveTab(tab.id)} 
              className={`px-4 py-2.5 rounded-xl text-sm font-medium whitespace-nowrap transition-all flex items-center gap-2 ${
                activeTab === tab.id 
                  ? 'bg-gradient-to-r from-indigo-500 to-purple-600 text-white shadow-lg shadow-indigo-500/25' 
                  : 'bg-white/5 text-zinc-400 hover:bg-white/10 hover:text-white'
              }`}
            >
              <span>{tab.icon}</span>{tab.label}
            </button>
          ))}
        </div>

        {/* Tab Content */}
        <div className="grid grid-cols-1 lg:grid-cols-3 gap-6">
          {/* Main Content */}
          <div className="lg:col-span-2">
            {/* Overview Tab */}
            {activeTab === 'overview' && (
              <div className="space-y-6 animate-fadeIn">
                <AttendanceGraph />
                <div className="bg-[#1a1625]/80 backdrop-blur-xl border border-white/10 rounded-2xl p-6">
                  <h3 className="text-lg font-semibold text-white mb-4">Recent Activity</h3>
                  {attendanceRecords.length === 0 ? (
                    <div className="text-center py-8">
                      <p className="text-zinc-500">No attendance records yet</p>
                      <p className="text-zinc-600 text-sm mt-1">Start a session to begin tracking</p>
                    </div>
                  ) : (
                    <div className="space-y-3">
                      {attendanceRecords.slice(0, 5).map((record, i) => (
                        <div key={record.id} className="flex items-center gap-4 p-3 bg-white/5 rounded-xl hover:bg-white/10 transition animate-fadeInUp" style={{ animationDelay: `${i * 0.1}s` }}>
                          <div className={`w-10 h-10 rounded-full flex items-center justify-center text-sm font-bold ${record.verification_status === 'verified' ? 'bg-emerald-500/20 text-emerald-400' : 'bg-red-500/20 text-red-400'}`}>
                            {record.verification_status === 'verified' ? '✓' : '✗'}
                          </div>
                          <div className="flex-1 min-w-0">
                            <p className="text-white font-medium truncate">{record.student_name}</p>
                            <p className="text-zinc-500 text-xs">{record.student_id_card_number}</p>
                          </div>
                          <div className="text-right">
                            <p className="text-zinc-400 text-sm">{record.face_confidence ? `${(record.face_confidence * 100).toFixed(0)}%` : '-'}</p>
                            <p className="text-zinc-600 text-xs">{new Date(record.timestamp).toLocaleTimeString()}</p>
                          </div>
                        </div>
                      ))}
                    </div>
                  )}
                </div>
              </div>
            )}


            {/* Session Tab */}
            {activeTab === 'session' && (
              <div className="bg-[#1a1625]/80 backdrop-blur-xl border border-white/10 rounded-2xl p-6 animate-fadeIn">
                <div className="max-w-md mx-auto">
                  <div className="text-center mb-8">
                    <div className="w-20 h-20 bg-gradient-to-br from-indigo-500 to-purple-600 rounded-3xl flex items-center justify-center mx-auto mb-4 shadow-lg shadow-indigo-500/25 animate-float">
                      <svg className="w-10 h-10 text-white" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M12 6v6m0 0v6m0-6h6m-6 0H6" /></svg>
                    </div>
                    <h3 className="text-2xl font-bold text-white">Start New Session</h3>
                    <p className="text-zinc-500 mt-1">Generate unique OTPs for attendance</p>
                  </div>
                  <div className="space-y-4">
                    <div>
                      <label className="block text-sm font-medium text-zinc-400 mb-2">Class ID</label>
                      <input type="text" value={classId} onChange={(e) => setClassId(e.target.value)} onKeyDown={(e) => e.key === 'Enter' && handleStartSession()} placeholder="e.g., CS101, MATH201" className="w-full px-4 py-3 bg-white/5 border border-white/10 rounded-xl text-white placeholder-zinc-500 focus:outline-none focus:border-indigo-500/50 transition" />
                    </div>
                    <button onClick={handleStartSession} disabled={isLoading || !classId.trim()} className={`w-full py-4 rounded-xl font-semibold transition-all ${classId.trim() && !isLoading ? 'bg-gradient-to-r from-indigo-500 to-purple-600 text-white hover:shadow-lg hover:shadow-indigo-500/25 hover:scale-[1.02]' : 'bg-zinc-800 text-zinc-500 cursor-not-allowed'}`}>
                      {isLoading ? 'Starting...' : 'Start Session & Generate OTPs'}
                    </button>
                  </div>
                  {activeSession && (
                    <div className="mt-8 p-6 bg-emerald-500/10 border border-emerald-500/20 rounded-2xl animate-scaleIn">
                      <div className="flex items-center gap-2 text-emerald-400 font-semibold mb-4">
                        <svg className="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M9 12l2 2 4-4m6 2a9 9 0 11-18 0 9 9 0 0118 0z" /></svg>
                        Session Active
                      </div>
                      <div className="text-center mb-4">
                        <p className="text-zinc-400 text-sm mb-2">Share this FULL Session ID with students</p>
                        <div 
                          onClick={() => copyToClipboard(activeSession.sessionId)}
                          className="bg-white/5 rounded-xl py-3 px-4 cursor-pointer hover:bg-white/10 transition group"
                        >
                          <p className="text-lg font-mono font-bold text-white break-all">{activeSession.sessionId}</p>
                          <p className="text-xs text-zinc-500 mt-1 group-hover:text-indigo-400">Click to copy</p>
                        </div>
                      </div>
                      <button onClick={() => copyToClipboard(activeSession.sessionId)} className={`w-full py-3 rounded-xl font-medium transition-all flex items-center justify-center gap-2 ${copied ? 'bg-emerald-500 text-white' : 'bg-white/10 text-white hover:bg-white/20'}`}>
                        {copied ? <><svg className="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M5 13l4 4L19 7" /></svg> Copied!</> : <><svg className="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M8 16H6a2 2 0 01-2-2V6a2 2 0 012-2h8a2 2 0 012 2v2m-6 12h8a2 2 0 002-2v-8a2 2 0 00-2-2h-8a2 2 0 00-2 2v8a2 2 0 002 2z" /></svg> Copy Session ID</>}
                      </button>
                      <p className="mt-4 text-xs text-emerald-400/70 text-center">{activeSession.otpCount} students • OTPs valid for 60 seconds</p>
                    </div>
                  )}
                </div>
              </div>
            )}

            {/* Attendance Tab */}
            {activeTab === 'attendance' && (
              <div className="bg-[#1a1625]/80 backdrop-blur-xl border border-white/10 rounded-2xl p-6 animate-fadeIn">
                <div className="flex items-center justify-between mb-6">
                  <div>
                    <h3 className="text-lg font-semibold text-white">Attendance Records</h3>
                    <p className="text-xs text-zinc-500">{attendanceRecords.length} total records</p>
                  </div>
                  <button className="px-4 py-2 bg-indigo-500/20 text-indigo-400 rounded-lg text-sm font-medium hover:bg-indigo-500/30 transition">Export CSV</button>
                </div>
                {attendanceRecords.length === 0 ? (
                  <div className="text-center py-12">
                    <div className="w-16 h-16 bg-white/5 rounded-2xl flex items-center justify-center mx-auto mb-4"><svg className="w-8 h-8 text-zinc-500" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M9 5H7a2 2 0 00-2 2v12a2 2 0 002 2h10a2 2 0 002-2V7a2 2 0 00-2-2h-2M9 5a2 2 0 002 2h2a2 2 0 002-2M9 5a2 2 0 012-2h2a2 2 0 012 2" /></svg></div>
                    <p className="text-zinc-500">No attendance records yet</p>
                  </div>
                ) : (
                  <div className="overflow-x-auto">
                    <table className="w-full">
                      <thead><tr className="text-left text-zinc-500 text-sm border-b border-white/10"><th className="pb-3 font-medium">Name</th><th className="pb-3 font-medium">ID</th><th className="pb-3 font-medium">Status</th><th className="pb-3 font-medium">Confidence</th><th className="pb-3 font-medium">Time</th></tr></thead>
                      <tbody>
                        {attendanceRecords.map((record, i) => (
                          <tr key={record.id} className="border-b border-white/5 hover:bg-white/5 transition animate-fadeIn" style={{ animationDelay: `${i * 0.05}s` }}>
                            <td className="py-3 text-white font-medium">{record.student_name}</td>
                            <td className="py-3 text-zinc-400 font-mono text-sm">{record.student_id_card_number}</td>
                            <td className="py-3"><span className={`px-2 py-1 rounded-full text-xs font-medium ${record.verification_status === 'verified' ? 'bg-emerald-500/20 text-emerald-400' : 'bg-red-500/20 text-red-400'}`}>{record.verification_status === 'verified' ? '✓ Verified' : '✗ Failed'}</span></td>
                            <td className="py-3 text-zinc-400">{record.face_confidence ? `${(record.face_confidence * 100).toFixed(0)}%` : '-'}</td>
                            <td className="py-3 text-zinc-500 text-sm">{new Date(record.timestamp).toLocaleTimeString()}</td>
                          </tr>
                        ))}
                      </tbody>
                    </table>
                  </div>
                )}
              </div>
            )}


            {/* Students Tab */}
            {activeTab === 'students' && (
              <div className="bg-[#1a1625]/80 backdrop-blur-xl border border-white/10 rounded-2xl p-6 animate-fadeIn">
                <div className="flex items-center justify-between mb-6">
                  <div>
                    <h3 className="text-lg font-semibold text-white">Enrolled Students</h3>
                    <p className="text-xs text-zinc-500">{students.length} students registered</p>
                  </div>
                  <Link to="/enroll" className="px-4 py-2 bg-gradient-to-r from-indigo-500 to-purple-600 text-white rounded-lg text-sm font-medium hover:shadow-lg hover:shadow-indigo-500/25 transition flex items-center gap-2">
                    <svg className="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M12 4v16m8-8H4" /></svg>
                    Add Student
                  </Link>
                </div>
                {students.length === 0 ? (
                  <div className="text-center py-12">
                    <div className="w-16 h-16 bg-white/5 rounded-2xl flex items-center justify-center mx-auto mb-4"><svg className="w-8 h-8 text-zinc-500" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M17 20h5v-2a3 3 0 00-5.356-1.857M17 20H7m10 0v-2c0-.656-.126-1.283-.356-1.857M7 20H2v-2a3 3 0 015.356-1.857M7 20v-2c0-.656.126-1.283.356-1.857m0 0a5.002 5.002 0 019.288 0M15 7a3 3 0 11-6 0 3 3 0 016 0z" /></svg></div>
                    <p className="text-zinc-500 mb-4">No students enrolled yet</p>
                    <Link to="/enroll" className="text-indigo-400 hover:text-indigo-300 font-medium">Enroll your first student →</Link>
                  </div>
                ) : (
                  <div className="grid grid-cols-1 gap-3">
                    {students.map((student, i) => (
                      <div key={student.id} className="bg-white/5 rounded-xl p-4 border border-white/5 hover:border-indigo-500/30 transition animate-fadeInUp" style={{ animationDelay: `${i * 0.05}s` }}>
                        <div className="flex items-center gap-4">
                          {/* Show face photo if available, otherwise show initial */}
                          {student.face_image ? (
                            <img 
                              src={student.face_image} 
                              alt={student.name}
                              className="w-12 h-12 rounded-full object-cover border-2 border-indigo-500/50 shadow-lg"
                            />
                          ) : (
                            <div className="w-12 h-12 bg-gradient-to-br from-indigo-500 to-purple-600 rounded-full flex items-center justify-center text-white font-bold text-lg shadow-lg">
                              {student.name.charAt(0).toUpperCase()}
                            </div>
                          )}
                          <div className="flex-1 min-w-0">
                            <p className="text-white font-medium truncate">{student.name}</p>
                            <p className="text-zinc-500 text-sm font-mono">{student.student_id_card_number}</p>
                          </div>
                          <div className="text-xs text-zinc-600">{new Date(student.created_at).toLocaleDateString()}</div>
                          <div className="flex gap-2">
                            <button
                              onClick={async () => {
                                if (window.confirm(`Unlock account for ${student.name}?`)) {
                                  try {
                                    const result = await unlockStudentAccount(student.student_id_card_number);
                                    alert(result.message);
                                    fetchData();
                                  } catch (err) {
                                    alert(handleApiError(err));
                                  }
                                }
                              }}
                              className="px-3 py-1.5 bg-emerald-500/20 text-emerald-400 rounded-lg text-xs font-medium hover:bg-emerald-500/30 transition flex items-center gap-1"
                              title="Unlock Account"
                            >
                              <svg className="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M8 11V7a4 4 0 118 0m-4 8v2m-6 4h12a2 2 0 002-2v-6a2 2 0 00-2-2H6a2 2 0 00-2 2v6a2 2 0 002 2z" /></svg>
                              Unlock
                            </button>
                            <button
                              onClick={async () => {
                                if (window.confirm(`Delete ${student.name}? This cannot be undone!`)) {
                                  try {
                                    await deleteStudent(student.id);
                                    alert('Student deleted successfully');
                                    fetchData();
                                  } catch (err) {
                                    alert(handleApiError(err));
                                  }
                                }
                              }}
                              className="px-3 py-1.5 bg-red-500/20 text-red-400 rounded-lg text-xs font-medium hover:bg-red-500/30 transition flex items-center gap-1"
                              title="Delete Student"
                            >
                              <svg className="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M19 7l-.867 12.142A2 2 0 0116.138 21H7.862a2 2 0 01-1.995-1.858L5 7m5 4v6m4-6v6m1-10V4a1 1 0 00-1-1h-4a1 1 0 00-1 1v3M4 7h16" /></svg>
                              Delete
                            </button>
                          </div>
                        </div>
                      </div>
                    ))}
                  </div>
                )}
              </div>
            )}

            {/* Analytics Tab */}
            {activeTab === 'analytics' && (
              <div className="space-y-6 animate-fadeIn">
                <AttendanceGraph />
                <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
                  <div className="bg-[#1a1625]/80 backdrop-blur-xl border border-white/10 rounded-2xl p-6">
                    <h3 className="text-lg font-semibold text-white mb-4">Attendance Distribution</h3>
                    <div className="flex items-center justify-center">
                      <div className="relative w-40 h-40">
                        <svg className="w-full h-full transform -rotate-90" viewBox="0 0 100 100">
                          <circle cx="50" cy="50" r="40" fill="none" stroke="rgba(255,255,255,0.1)" strokeWidth="12" />
                          <circle cx="50" cy="50" r="40" fill="none" stroke="url(#gradient)" strokeWidth="12" strokeDasharray={`${attendanceRate * 2.51} 251`} strokeLinecap="round" className="transition-all duration-1000" />
                          <defs><linearGradient id="gradient" x1="0%" y1="0%" x2="100%" y2="0%"><stop offset="0%" stopColor="#6366f1" /><stop offset="100%" stopColor="#a855f7" /></linearGradient></defs>
                        </svg>
                        <div className="absolute inset-0 flex items-center justify-center flex-col">
                          <span className="text-3xl font-bold text-white"><AnimatedCounter value={Math.round(attendanceRate)} suffix="%" /></span>
                          <span className="text-xs text-zinc-500">Attendance</span>
                        </div>
                      </div>
                    </div>
                    <div className="flex justify-center gap-8 mt-6">
                      <div className="text-center"><p className="text-2xl font-bold text-emerald-400"><AnimatedCounter value={verifiedCount} /></p><p className="text-xs text-zinc-500">Present</p></div>
                      <div className="text-center"><p className="text-2xl font-bold text-red-400"><AnimatedCounter value={Math.max(0, totalStudents - verifiedCount)} /></p><p className="text-xs text-zinc-500">Absent</p></div>
                    </div>
                  </div>
                  <div className="bg-[#1a1625]/80 backdrop-blur-xl border border-white/10 rounded-2xl p-6">
                    <h3 className="text-lg font-semibold text-white mb-4">Alert Summary</h3>
                    {anomalies.length === 0 ? (
                      <div className="text-center py-8">
                        <div className="w-12 h-12 bg-emerald-500/20 rounded-xl flex items-center justify-center mx-auto mb-3"><svg className="w-6 h-6 text-emerald-400" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M9 12l2 2 4-4m6 2a9 9 0 11-18 0 9 9 0 0118 0z" /></svg></div>
                        <p className="text-zinc-500 text-sm">No alerts detected</p>
                      </div>
                    ) : (
                      <div className="space-y-3">
                        {anomalies.slice(0, 4).map((anomaly, i) => (
                          <div key={i} className="flex items-center gap-3 p-3 bg-red-500/10 border border-red-500/20 rounded-xl animate-fadeIn" style={{ animationDelay: `${i * 0.1}s` }}>
                            <div className="w-8 h-8 bg-red-500/20 rounded-lg flex items-center justify-center"><svg className="w-4 h-4 text-red-400" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M12 9v2m0 4h.01m-6.938 4h13.856c1.54 0 2.502-1.667 1.732-3L13.732 4c-.77-1.333-2.694-1.333-3.464 0L3.34 16c-.77 1.333.192 3 1.732 3z" /></svg></div>
                            <div className="flex-1 min-w-0"><p className="text-white text-sm font-medium truncate">{anomaly.anomaly_type.replace('_', ' ')}</p><p className="text-zinc-500 text-xs truncate">{anomaly.reason}</p></div>
                          </div>
                        ))}
                      </div>
                    )}
                  </div>
                </div>
              </div>
            )}

            {/* Calendar Tab */}
            {activeTab === 'calendar' && (
              <div className="animate-fadeIn">
                <CalendarView />
              </div>
            )}
          </div>


          {/* Sidebar */}
          <div className="space-y-6">
            {/* Quick Actions */}
            <div className="bg-[#1a1625]/80 backdrop-blur-xl border border-white/10 rounded-2xl p-6">
              <h3 className="text-lg font-semibold text-white mb-4">Quick Actions</h3>
              <div className="space-y-3">
                <button onClick={() => setActiveTab('session')} className="w-full flex items-center gap-3 p-3 bg-indigo-500/10 border border-indigo-500/20 rounded-xl text-left hover:bg-indigo-500/20 hover:scale-[1.02] transition-all">
                  <div className="w-10 h-10 bg-gradient-to-br from-indigo-500 to-purple-600 rounded-lg flex items-center justify-center shadow-lg"><svg className="w-5 h-5 text-white" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M12 6v6m0 0v6m0-6h6m-6 0H6" /></svg></div>
                  <div><p className="text-white font-medium text-sm">Start Session</p><p className="text-zinc-500 text-xs">Generate OTPs</p></div>
                </button>
                <Link to="/enroll" className="w-full flex items-center gap-3 p-3 bg-emerald-500/10 border border-emerald-500/20 rounded-xl text-left hover:bg-emerald-500/20 hover:scale-[1.02] transition-all">
                  <div className="w-10 h-10 bg-gradient-to-br from-emerald-500 to-teal-600 rounded-lg flex items-center justify-center shadow-lg"><svg className="w-5 h-5 text-white" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M18 9v3m0 0v3m0-3h3m-3 0h-3m-2-5a4 4 0 11-8 0 4 4 0 018 0zM3 20a6 6 0 0112 0v1H3v-1z" /></svg></div>
                  <div><p className="text-white font-medium text-sm">Enroll Student</p><p className="text-zinc-500 text-xs">Add new student</p></div>
                </Link>
                <button className="w-full flex items-center gap-3 p-3 bg-amber-500/10 border border-amber-500/20 rounded-xl text-left hover:bg-amber-500/20 hover:scale-[1.02] transition-all">
                  <div className="w-10 h-10 bg-gradient-to-br from-amber-500 to-orange-600 rounded-lg flex items-center justify-center shadow-lg"><svg className="w-5 h-5 text-white" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M12 10v6m0 0l-3-3m3 3l3-3m2 8H7a2 2 0 01-2-2V5a2 2 0 012-2h5.586a1 1 0 01.707.293l5.414 5.414a1 1 0 01.293.707V19a2 2 0 01-2 2z" /></svg></div>
                  <div><p className="text-white font-medium text-sm">Export Report</p><p className="text-zinc-500 text-xs">Download CSV</p></div>
                </button>
              </div>
            </div>

            {/* Recent Activity */}
            <div className="bg-[#1a1625]/80 backdrop-blur-xl border border-white/10 rounded-2xl p-6">
              <div className="flex items-center justify-between mb-4">
                <h3 className="text-lg font-semibold text-white">Live Feed</h3>
                <span className="flex items-center gap-1 text-xs text-emerald-400">
                  <span className="w-1.5 h-1.5 bg-emerald-400 rounded-full animate-pulse"></span>
                  Real-time
                </span>
              </div>
              <div className="space-y-3">
                {attendanceRecords.slice(0, 5).map((record, i) => (
                  <div key={record.id} className="flex items-center gap-3 animate-fadeIn" style={{ animationDelay: `${i * 0.1}s` }}>
                    <div className={`w-8 h-8 rounded-full flex items-center justify-center text-xs font-bold ${record.verification_status === 'verified' ? 'bg-emerald-500/20 text-emerald-400' : 'bg-red-500/20 text-red-400'}`}>
                      {record.verification_status === 'verified' ? '✓' : '✗'}
                    </div>
                    <div className="flex-1 min-w-0">
                      <p className="text-white text-sm font-medium truncate">{record.student_name}</p>
                      <p className="text-zinc-500 text-xs">{new Date(record.timestamp).toLocaleTimeString()}</p>
                    </div>
                  </div>
                ))}
                {attendanceRecords.length === 0 && <p className="text-zinc-500 text-sm text-center py-4">No recent activity</p>}
              </div>
            </div>

            {/* Mini Calendar */}
            <CalendarView />
          </div>
        </div>
      </main>
    </div>
  );
};

export default FacultyDashboard;
