/**
 * ISAVS 2026 - Student Kiosk (Port 2001)
 * Mobile-first interface with GPS Check, OTP Input, and Face Scan
 * Flow: GPS Lock → OTP Entry → Face Verification
 */
import React, { useState, useCallback, useEffect } from 'react';
import WebcamCapture from '../components/WebcamCapture';
import OTPInput from '../components/OTPInput';
import { verifyAttendance, getStudentOTP } from '../services/api';

const StudentPortal = () => {
  const [step, setStep] = useState('session'); // session → gps → otp → face → result
  const [sessionId, setSessionId] = useState('');
  const [studentId, setStudentId] = useState('');
  const [otp, setOtp] = useState('');
  const [currentFrame, setCurrentFrame] = useState('');
  const [location, setLocation] = useState(null);
  const [locationError, setLocationError] = useState(null);
  const [isVerifying, setIsVerifying] = useState(false);
  const [error, setError] = useState(null);
  const [verificationResult, setVerificationResult] = useState(null);
  const [demoOtp, setDemoOtp] = useState(null);
  const [studentName, setStudentName] = useState('');
  const [gpsDistance, setGpsDistance] = useState(null);
  const [gpsFailureCount, setGpsFailureCount] = useState(0);
  const [wifiSsid, setWifiSsid] = useState(null);
  const [gpsAccuracy, setGpsAccuracy] = useState(null);

  // GPS Check - runs when student enters session with HIGH ACCURACY
  const checkGPS = useCallback(() => {
    if ('geolocation' in navigator) {
      navigator.geolocation.getCurrentPosition(
        (position) => {
          const userLat = position.coords.latitude;
          const userLon = position.coords.longitude;
          const accuracy = position.coords.accuracy; // GPS accuracy in meters
          
          setLocation({ 
            latitude: userLat, 
            longitude: userLon,
            accuracy: accuracy 
          });
          setGpsAccuracy(accuracy);
          
          // Calculate distance (mock - in production, compare with classroom coords)
          // For demo, we'll simulate distance
          const mockDistance = Math.random() * 100; // 0-100 meters
          setGpsDistance(mockDistance);
          
          // INCREASED THRESHOLD: 100 meters (was 50m) to account for indoor GPS drift
          const MAX_DISTANCE = 100;
          
          if (mockDistance > MAX_DISTANCE) {
            const newFailureCount = gpsFailureCount + 1;
            setGpsFailureCount(newFailureCount);
            
            // After 2 GPS failures, allow WiFi fallback
            if (newFailureCount >= 2) {
              setLocationError(`GPS failed ${newFailureCount} times. You can verify using WiFi instead.`);
              setError('GPS Check Failed: Try WiFi verification');
            } else {
              setLocationError(`You are ${mockDistance.toFixed(0)}m from classroom. Must be within ${MAX_DISTANCE}m. (Attempt ${newFailureCount}/2)`);
              setError('GPS Check Failed: Too far from classroom');
            }
          } else {
            setLocationError(null);
            setGpsFailureCount(0); // Reset on success
            setStep('otp');
          }
        },
        (error) => {
          console.error('Geolocation error:', error);
          const newFailureCount = gpsFailureCount + 1;
          setGpsFailureCount(newFailureCount);
          
          if (newFailureCount >= 2) {
            setLocationError(`GPS failed ${newFailureCount} times. You can verify using WiFi instead.`);
            setError('GPS Check Failed: Try WiFi verification');
          } else {
            setLocationError(`Location access denied (Attempt ${newFailureCount}/2)`);
            setError('GPS Check Failed: Enable location services');
          }
        },
        {
          enableHighAccuracy: true,  // HIGH ACCURACY MODE - uses GPS instead of network location
          timeout: 10000,
          maximumAge: 0  // Don't use cached location
        }
      );
    } else {
      setLocationError('Geolocation not supported');
      setError('GPS Check Failed: Browser not supported');
    }
  }, [gpsFailureCount]);

  // WiFi Fallback Verification
  const checkWiFiFallback = useCallback(async () => {
    try {
      // Note: Browser WiFi API is limited for security reasons
      // In production, this would be handled by a native mobile app
      // For web, we'll prompt user to enter WiFi SSID manually
      const ssid = prompt('Enter your WiFi network name (SSID):');
      
      if (ssid) {
        setWifiSsid(ssid);
        
        // Verify with backend
        const response = await fetch(`${import.meta.env.VITE_API_URL}/api/verify-wifi`, {
          method: 'POST',
          headers: { 'Content-Type': 'application/json' },
          body: JSON.stringify({ 
            session_id: sessionId,
            wifi_ssid: ssid 
          })
        });
        
        const data = await response.json();
        
        if (data.verified) {
          setLocationError(null);
          setError(null);
          setStep('otp');
        } else {
          setError('WiFi network not recognized. Please connect to college WiFi.');
        }
      }
    } catch (err) {
      console.error('WiFi verification error:', err);
      setError('WiFi verification failed');
    }
  }, [sessionId]);

  // Handle Session ID Submit
  const handleSessionSubmit = async () => {
    if (!sessionId.trim() || !studentId.trim()) {
      setError('Please enter both Session ID and Student ID');
      return;
    }

    setError(null);
    
    try {
      // Fetch OTP for this student
      const otpData = await getStudentOTP(sessionId.trim(), studentId.trim().toUpperCase());
      setDemoOtp(otpData.otp);
      if (otpData.student_name) {
        setStudentName(otpData.student_name);
      }
      
      // Move to GPS check
      setStep('gps');
      checkGPS();
    } catch (err) {
      setError(err?.response?.data?.detail || 'Invalid Session ID or Student ID');
    }
  };

  // Handle OTP Complete
  const handleOtpComplete = (completedOtp) => {
    setOtp(completedOtp);
    setStep('face');
  };

  // Handle Frame Capture
  const handleFrameCapture = useCallback((frame) => {
    setCurrentFrame(frame);
  }, []);

  // Handle Verify
  const handleVerify = async () => {
    if (!studentId || !otp || !currentFrame) {
      setError('Please complete all steps');
      return;
    }

    setIsVerifying(true);
    setError(null);

    try {
      const result = await verifyAttendance({
        student_id: studentId,
        otp: otp,
        face_image: currentFrame,
        session_id: sessionId,
        latitude: location?.latitude,
        longitude: location?.longitude
      });

      setVerificationResult(result);
      setStep('result');
    } catch (err) {
      setError(err?.response?.data?.detail || 'Verification failed');
    } finally {
      setIsVerifying(false);
    }
  };

  // Reset
  const handleReset = () => {
    setStep('session');
    setSessionId('');
    setStudentId('');
    setOtp('');
    setCurrentFrame('');
    setLocation(null);
    setLocationError(null);
    setError(null);
    setVerificationResult(null);
    setDemoOtp(null);
    setStudentName('');
    setGpsDistance(null);
  };

  // Result Screen
  if (step === 'result' && verificationResult) {
    return (
      <div className="min-h-screen bg-[#0f0d1a] flex items-center justify-center p-4">
        <div className="w-full max-w-md text-center">
          <div className={`w-24 h-24 rounded-full flex items-center justify-center mx-auto mb-6 ${
            verificationResult.success
              ? 'bg-gradient-to-br from-emerald-500 to-teal-600'
              : 'bg-gradient-to-br from-red-500 to-rose-600'
          }`}>
            {verificationResult.success ? (
              <svg className="w-12 h-12 text-white" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M5 13l4 4L19 7" />
              </svg>
            ) : (
              <svg className="w-12 h-12 text-white" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M6 18L18 6M6 6l12 12" />
              </svg>
            )}
          </div>

          <h1 className="text-3xl font-bold text-white mb-2">
            {verificationResult.success ? 'Attendance Marked!' : 'Verification Failed'}
          </h1>
          <p className="text-zinc-400 mb-6">{verificationResult.message}</p>

          {verificationResult.success && verificationResult.factors?.face_confidence && (
            <div className="bg-[#1a1625] border border-white/10 rounded-xl p-4 mb-6">
              <div className="space-y-2 text-sm">
                <div className="flex justify-between">
                  <span className="text-zinc-500">Face Match</span>
                  <span className="text-emerald-400 font-bold">
                    {(verificationResult.factors.face_confidence * 100).toFixed(0)}%
                  </span>
                </div>
                {verificationResult.factors.distance_meters !== undefined && (
                  <div className="flex justify-between">
                    <span className="text-zinc-500">Distance</span>
                    <span className="text-indigo-400 font-bold">
                      {verificationResult.factors.distance_meters.toFixed(0)}m
                    </span>
                  </div>
                )}
              </div>
            </div>
          )}

          <button
            onClick={handleReset}
            className="w-full py-3 bg-gradient-to-r from-indigo-500 to-purple-600 text-white rounded-xl font-semibold hover:shadow-lg transition"
          >
            Verify Another Student
          </button>
        </div>
      </div>
    );
  }

  return (
    <div className="min-h-screen bg-[#0f0d1a]">
      {/* Header */}
      <header className="bg-[#1a1625] border-b border-white/10 p-4">
        <div className="max-w-lg mx-auto">
          <h1 className="text-xl font-bold text-white text-center">ISAVS 2026</h1>
          <p className="text-zinc-500 text-sm text-center">Student Verification Kiosk</p>
        </div>
      </header>

      <main className="max-w-lg mx-auto px-4 py-6">

        {/* Progress Indicator */}
        <div className="flex items-center justify-center gap-3 mb-8">
          {['session', 'gps', 'otp', 'face'].map((s, i) => (
            <React.Fragment key={s}>
              <div className={`w-10 h-10 rounded-full flex items-center justify-center font-semibold text-sm transition-all ${
                step === s ? 'bg-gradient-to-br from-indigo-500 to-purple-600 text-white scale-110' :
                ['session', 'gps', 'otp', 'face'].indexOf(step) > i ? 'bg-emerald-500 text-white' : 'bg-white/10 text-zinc-500'
              }`}>
                {['session', 'gps', 'otp', 'face'].indexOf(step) > i ? '✓' : i + 1}
              </div>
              {i < 3 && (
                <div className={`w-8 h-1 rounded-full transition-all ${
                  ['session', 'gps', 'otp', 'face'].indexOf(step) > i ? 'bg-emerald-500' : 'bg-white/10'
                }`}></div>
              )}
            </React.Fragment>
          ))}
        </div>

        {/* Error Display */}
        {error && (
          <div className="mb-6 p-4 bg-red-500/10 border border-red-500/20 rounded-xl text-red-400 text-sm flex items-center gap-3">
            <svg className="w-5 h-5 flex-shrink-0" fill="none" stroke="currentColor" viewBox="0 0 24 24">
              <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M12 8v4m0 4h.01M21 12a9 9 0 11-18 0 9 9 0 0118 0z" />
            </svg>
            <span className="flex-1">{error}</span>
            <button onClick={() => setError(null)} className="text-red-300 hover:text-white">✕</button>
          </div>
        )}

        {/* Step 1: Session & Student ID */}
        {step === 'session' && (
          <div className="bg-[#1a1625] border border-white/10 rounded-xl p-6">
            <div className="text-center mb-6">
              <div className="w-16 h-16 bg-gradient-to-br from-indigo-500 to-purple-600 rounded-2xl flex items-center justify-center mx-auto mb-4">
                <span className="text-3xl">🎯</span>
              </div>
              <h2 className="text-2xl font-bold text-white mb-2">Verify Attendance</h2>
              <p className="text-zinc-500 text-sm">Enter your session and student ID</p>
            </div>

            <div className="space-y-4">
              <div>
                <label className="block text-sm font-medium text-zinc-400 mb-2">Session ID</label>
                <input
                  type="text"
                  value={sessionId}
                  onChange={(e) => setSessionId(e.target.value)}
                  placeholder="Provided by teacher"
                  className="w-full px-4 py-3 bg-white/5 border border-white/10 rounded-xl text-white placeholder-zinc-500 focus:outline-none focus:border-indigo-500/50 font-mono"
                />
              </div>

              <div>
                <label className="block text-sm font-medium text-zinc-400 mb-2">Student ID</label>
                <input
                  type="text"
                  value={studentId}
                  onChange={(e) => setStudentId(e.target.value.toUpperCase())}
                  onKeyDown={(e) => e.key === 'Enter' && handleSessionSubmit()}
                  placeholder="e.g., STU001"
                  className="w-full px-4 py-3 bg-white/5 border border-white/10 rounded-xl text-white placeholder-zinc-500 focus:outline-none focus:border-indigo-500/50 font-mono"
                />
              </div>

              <button
                onClick={handleSessionSubmit}
                disabled={!sessionId.trim() || !studentId.trim()}
                className={`w-full py-4 rounded-xl font-semibold text-lg transition-all ${
                  sessionId.trim() && studentId.trim()
                    ? 'bg-gradient-to-r from-indigo-500 to-purple-600 text-white hover:shadow-lg hover:scale-[1.02]'
                    : 'bg-zinc-800 text-zinc-500 cursor-not-allowed'
                }`}
              >
                Continue →
              </button>
            </div>
          </div>
        )}

        {/* Step 2: GPS Check */}
        {step === 'gps' && (
          <div className="bg-[#1a1625] border border-white/10 rounded-xl p-6">
            <div className="text-center">
              <div className="w-20 h-20 bg-gradient-to-br from-blue-500 to-cyan-600 rounded-full flex items-center justify-center mx-auto mb-4 animate-pulse">
                <span className="text-4xl">📍</span>
              </div>
              <h2 className="text-2xl font-bold text-white mb-2">GPS Check</h2>
              <p className="text-zinc-500 text-sm mb-6">Verifying your location...</p>

              {locationError ? (
                <div className="p-4 bg-red-500/10 border border-red-500/20 rounded-xl text-red-400 mb-4">
                  <p className="font-semibold mb-1">Location Check Failed</p>
                  <p className="text-sm">{locationError}</p>
                  {gpsAccuracy && (
                    <p className="text-xs mt-2 text-zinc-500">GPS Accuracy: ±{gpsAccuracy.toFixed(0)}m</p>
                  )}
                </div>
              ) : gpsDistance !== null ? (
                <div className={`p-4 rounded-xl mb-4 ${
                  gpsDistance <= 100
                    ? 'bg-emerald-500/10 border border-emerald-500/20 text-emerald-400'
                    : 'bg-red-500/10 border border-red-500/20 text-red-400'
                }`}>
                  <p className="font-semibold mb-1">
                    {gpsDistance <= 100 ? '✓ Within Range' : '✗ Too Far'}
                  </p>
                  <p className="text-sm">Distance: {gpsDistance.toFixed(0)}m from classroom (Max: 100m)</p>
                  {gpsAccuracy && (
                    <p className="text-xs mt-2 text-zinc-500">GPS Accuracy: ±{gpsAccuracy.toFixed(0)}m</p>
                  )}
                </div>
              ) : (
                <div className="flex items-center justify-center gap-2 text-zinc-400">
                  <div className="w-2 h-2 bg-indigo-400 rounded-full animate-pulse"></div>
                  <span>Checking location with high accuracy GPS...</span>
                </div>
              )}

              {locationError && (
                <div className="space-y-3">
                  <button
                    onClick={checkGPS}
                    className="w-full py-3 bg-indigo-500 text-white rounded-xl font-semibold hover:bg-indigo-600 transition"
                  >
                    🔄 Retry GPS Check ({gpsFailureCount}/2)
                  </button>
                  
                  {gpsFailureCount >= 2 && (
                    <button
                      onClick={checkWiFiFallback}
                      className="w-full py-3 bg-cyan-500 text-white rounded-xl font-semibold hover:bg-cyan-600 transition flex items-center justify-center gap-2"
                    >
                      <span>📶</span>
                      <span>Verify Using WiFi Instead</span>
                    </button>
                  )}
                </div>
              )}

              {!locationError && gpsDistance !== null && gpsDistance <= 100 && (
                >
                  Retry GPS Check
                </button>
              )}
            </div>
          </div>
        )}

        {/* Step 3: OTP Input */}
        {step === 'otp' && (
          <div className="bg-[#1a1625] border border-white/10 rounded-xl p-6">
            <div className="text-center mb-6">
              <div className="w-16 h-16 bg-gradient-to-br from-purple-500 to-pink-600 rounded-2xl flex items-center justify-center mx-auto mb-4">
                <span className="text-3xl">🔐</span>
              </div>
              <h2 className="text-2xl font-bold text-white mb-2">Enter OTP</h2>
              {studentName && <p className="text-zinc-400 mb-2">Welcome, {studentName}!</p>}
              <p className="text-zinc-500 text-sm">Enter your 4-digit code</p>
            </div>

            {/* Demo OTP Display */}
            {demoOtp && (
              <div className="mb-6 p-4 bg-amber-500/10 border border-amber-500/20 rounded-xl text-center">
                <p className="text-amber-400 text-sm mb-1">Your OTP Code</p>
                <p className="text-3xl font-mono font-bold text-white tracking-[0.3em]">{demoOtp}</p>
                <p className="text-zinc-500 text-xs mt-2">Valid for 60 seconds</p>
              </div>
            )}

            <div className="flex justify-center mb-6">
              <OTPInput onOTPComplete={handleOtpComplete} disabled={false} />
            </div>

            <button
              onClick={() => setStep('session')}
              className="w-full py-3 bg-white/5 border border-white/10 text-white rounded-xl font-medium hover:bg-white/10 transition"
            >
              ← Back
            </button>
          </div>
        )}

        {/* Step 4: Face Scan */}
        {step === 'face' && (
          <div className="bg-[#1a1625] border border-white/10 rounded-xl p-6">
            <div className="text-center mb-6">
              <div className="w-16 h-16 bg-gradient-to-br from-emerald-500 to-teal-600 rounded-2xl flex items-center justify-center mx-auto mb-4">
                <span className="text-3xl">📸</span>
              </div>
              <h2 className="text-2xl font-bold text-white mb-2">Face Scan</h2>
              <p className="text-zinc-500 text-sm">Align your face and blink naturally</p>
            </div>

            <div className="relative flex justify-center mb-6">
              <div className="relative">
                <WebcamCapture
                  onFrameCapture={handleFrameCapture}
                  showBoundingBox={true}
                  width={320}
                  height={320}
                />
                
                {/* Face Detection Indicator */}
                <div className="absolute top-2 right-2 z-10">
                  {currentFrame ? (
                    <div className="w-12 h-12 bg-emerald-500/90 backdrop-blur-sm rounded-full flex items-center justify-center shadow-lg">
                      <svg className="w-7 h-7 text-white" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                        <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M5 13l4 4L19 7" />
                      </svg>
                    </div>
                  ) : (
                    <div className="w-12 h-12 bg-zinc-700/90 backdrop-blur-sm rounded-full flex items-center justify-center shadow-lg">
                      <div className="w-2 h-2 bg-zinc-400 rounded-full animate-pulse"></div>
                    </div>
                  )}
                </div>
              </div>
            </div>

            {/* Status */}
            <div className="text-center mb-6">
              {currentFrame ? (
                <div className="flex items-center justify-center gap-2 text-emerald-400 text-sm font-medium">
                  <div className="w-2 h-2 bg-emerald-400 rounded-full animate-pulse"></div>
                  Face Detected - Ready to Verify
                </div>
              ) : (
                <div className="flex items-center justify-center gap-2 text-zinc-500 text-sm">
                  <div className="w-2 h-2 bg-zinc-500 rounded-full"></div>
                  Searching for face...
                </div>
              )}
            </div>

            <button
              onClick={handleVerify}
              disabled={isVerifying || !currentFrame}
              className={`w-full py-4 rounded-xl font-semibold text-lg transition-all mb-3 ${
                !isVerifying && currentFrame
                  ? 'bg-gradient-to-r from-emerald-500 to-teal-600 text-white hover:shadow-lg hover:scale-[1.02]'
                  : 'bg-zinc-800 text-zinc-500 cursor-not-allowed'
              }`}
            >
              {isVerifying ? (
                <span className="flex items-center justify-center gap-2">
                  <span className="animate-spin">◐</span> Verifying...
                </span>
              ) : (
                '✓ Verify Attendance'
              )}
            </button>

            <button
              onClick={() => setStep('otp')}
              className="w-full py-3 bg-white/5 border border-white/10 text-white rounded-xl font-medium hover:bg-white/10 transition"
            >
              ← Back
            </button>
          </div>
        )}
      </main>
    </div>
  );
};

export default StudentPortal;
