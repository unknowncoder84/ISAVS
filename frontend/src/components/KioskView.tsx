/**
 * Kiosk View - Student Face Scan & OTP Verification
 * Blue/Purple Gradient Theme (Campus Connect Inspired)
 */
import React, { useState, useCallback } from 'react';
import { Link } from 'react-router-dom';
import WebcamCapture from './WebcamCapture';
import CountdownTimer from './CountdownTimer';
import OTPInput from './OTPInput';
import GradientButton from './ui/GradientButton';
import GradientCard from './ui/GradientCard';
import { verifyAttendance, resendOTP, getStudentOTP, handleApiError, VerifyResponse } from '../services/api';

interface KioskViewProps {
  sessionId: string;
}

const KioskView: React.FC<KioskViewProps> = ({ sessionId }) => {
  const [studentId, setStudentId] = useState('');
  const [otp, setOtp] = useState('');
  const [currentFrame, setCurrentFrame] = useState<string>('');
  const [isTimerActive, setIsTimerActive] = useState(false);
  const [isOtpExpired, setIsOtpExpired] = useState(false);
  const [resendAttemptsRemaining, setResendAttemptsRemaining] = useState(2);
  const [isVerifying, setIsVerifying] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const [verificationResult, setVerificationResult] = useState<VerifyResponse | null>(null);
  const [demoOtp, setDemoOtp] = useState<string | null>(null);
  const [step, setStep] = useState<'id' | 'otp' | 'face' | 'result'>('id');
  const [studentName, setStudentName] = useState('');
  const [location, setLocation] = useState<{ latitude: number; longitude: number } | null>(null);
  const [locationError, setLocationError] = useState<string | null>(null);

  const handleFrameCapture = useCallback((frame: string) => {
    setCurrentFrame(frame);
  }, []);

  const handleOtpExpire = useCallback(() => {
    setIsOtpExpired(true);
  }, []);

  const handleResendOtp = async () => {
    if (resendAttemptsRemaining <= 0 || !studentId) return;
    try {
      const response = await resendOTP(sessionId, studentId);
      if (response.success) {
        setResendAttemptsRemaining(response.attempts_remaining);
        setIsOtpExpired(false);
        setOtp('');
        setIsTimerActive(true);
        setError(null);
      }
    } catch (err) {
      setError(handleApiError(err));
    }
  };

  const handleStudentIdSubmit = async () => {
    if (!studentId.trim()) {
      setError('Please enter your Student ID');
      return;
    }
    setError(null);
    try {
      const otpData = await getStudentOTP(sessionId, studentId.trim().toUpperCase());
      setDemoOtp(otpData.otp);
      if (otpData.student_name) {
        setStudentName(otpData.student_name);
      }
      setIsTimerActive(true);
      setStep('otp');
    } catch (err: any) {
      const errorMsg = err?.response?.data?.detail || 'Student ID not found. Please check your ID and try again.';
      setError(errorMsg);
    }
  };

  const handleOtpComplete = (completedOtp: string) => {
    setOtp(completedOtp);
    // Request geolocation when OTP is complete
    requestGeolocation();
    setStep('face');
  };

  const requestGeolocation = () => {
    if ('geolocation' in navigator) {
      navigator.geolocation.getCurrentPosition(
        (position) => {
          setLocation({
            latitude: position.coords.latitude,
            longitude: position.coords.longitude
          });
          setLocationError(null);
        },
        (error) => {
          console.error('Geolocation error:', error);
          setLocationError('Location access denied. Verification may fail.');
        },
        {
          enableHighAccuracy: true,
          timeout: 10000,
          maximumAge: 0
        }
      );
    } else {
      setLocationError('Geolocation not supported by browser');
    }
  };

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
      setError(handleApiError(err));
    } finally {
      setIsVerifying(false);
    }
  };

  const handleReset = () => {
    setStudentId('');
    setOtp('');
    setCurrentFrame('');
    setIsTimerActive(false);
    setIsOtpExpired(false);
    setResendAttemptsRemaining(2);
    setError(null);
    setVerificationResult(null);
    setDemoOtp(null);
    setStep('id');
    setStudentName('');
    setLocation(null);
    setLocationError(null);
  };

  // Result Screen
  if (step === 'result' && verificationResult) {
    return (
      <div className="min-h-screen bg-[#0f0d1a] flex items-center justify-center p-4">
        <div className="w-full max-w-sm text-center animate-scaleIn">
          <div className={`w-24 h-24 rounded-full flex items-center justify-center mx-auto mb-6 shadow-2xl ${
            verificationResult.success 
              ? 'bg-gradient-to-br from-emerald-500 to-teal-600 shadow-emerald-500/30' 
              : 'bg-gradient-to-br from-red-500 to-rose-600 shadow-red-500/30'
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
          <h1 className="text-2xl font-bold text-white mb-2">
            {verificationResult.success ? 'Attendance Marked!' : 'Verification Failed'}
          </h1>
          <p className="text-zinc-400 mb-6">{verificationResult.message}</p>
          
          {verificationResult.success && verificationResult.factors?.face_confidence && (
            <div className="space-y-2 mb-6">
              <p className="text-zinc-500 text-sm">
                Face Match: {(verificationResult.factors.face_confidence * 100).toFixed(0)}%
              </p>
              {verificationResult.factors.distance_meters !== undefined && (
                <p className="text-zinc-500 text-sm">
                  Distance: {verificationResult.factors.distance_meters.toFixed(0)}m from classroom
                </p>
              )}
            </div>
          )}

          <button
            onClick={handleReset}
            className="w-full py-3 bg-[#1a1625] border border-white/10 text-white rounded-xl font-medium hover:bg-[#231e30] transition"
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
      <header className="sticky top-0 z-50 bg-[#0f0d1a]/80 backdrop-blur-xl border-b border-white/5">
        <div className="max-w-lg mx-auto px-4 py-4 flex items-center justify-between">
          <Link to="/" className="w-10 h-10 bg-white/5 hover:bg-white/10 rounded-xl flex items-center justify-center transition">
            <svg className="w-5 h-5 text-white" fill="none" stroke="currentColor" viewBox="0 0 24 24">
              <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M15 19l-7-7 7-7" />
            </svg>
          </Link>
          <div className="text-center">
            <h1 className="text-lg font-semibold text-white">
              {step === 'id' && 'Student Verification'}
              {step === 'otp' && 'Enter OTP'}
              {step === 'face' && 'Face Scan'}
            </h1>
            <p className="text-xs text-zinc-500 font-mono">{sessionId.substring(0, 8)}...</p>
          </div>
          <div className="w-10"></div>
        </div>
      </header>

      <main className="max-w-lg mx-auto px-4 py-6">
        {/* Progress */}
        <div className="flex items-center justify-center gap-3 mb-8">
          {['id', 'otp', 'face'].map((s, i) => (
            <React.Fragment key={s}>
              <div className={`w-10 h-10 rounded-full flex items-center justify-center font-semibold text-sm transition-all ${
                step === s ? 'bg-gradient-to-br from-indigo-500 to-purple-600 text-white scale-110' :
                ['id', 'otp', 'face'].indexOf(step) > i ? 'bg-emerald-500 text-white' : 'bg-white/10 text-zinc-500'
              }`}>
                {['id', 'otp', 'face'].indexOf(step) > i ? '✓' : i + 1}
              </div>
              {i < 2 && (
                <div className={`w-10 h-1 rounded-full transition-all ${['id', 'otp', 'face'].indexOf(step) > i ? 'bg-emerald-500' : 'bg-white/10'}`}></div>
              )}
            </React.Fragment>
          ))}
        </div>

        {/* Error */}
        {error && (
          <div className="mb-6 p-4 bg-red-500/10 border border-red-500/20 rounded-xl text-red-400 text-sm flex items-center gap-3 animate-fadeIn">
            <svg className="w-5 h-5 flex-shrink-0" fill="none" stroke="currentColor" viewBox="0 0 24 24">
              <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M12 8v4m0 4h.01M21 12a9 9 0 11-18 0 9 9 0 0118 0z" />
            </svg>
            <span className="flex-1">{error}</span>
            <button onClick={() => setError(null)} className="text-red-300 hover:text-white">✕</button>
          </div>
        )}

        {/* Step 1: Student ID */}
        {step === 'id' && (
          <div className="animate-fadeInUp">
            <GradientCard>
              <div className="w-14 h-14 gradient-primary rounded-2xl flex items-center justify-center mb-5 shadow-soft">
                <svg className="w-7 h-7 text-white" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                  <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M16 7a4 4 0 11-8 0 4 4 0 018 0zM12 14a7 7 0 00-7 7h14a7 7 0 00-7-7z" />
                </svg>
              </div>
              <h2 className="text-xl font-semibold text-white mb-1">Enter Student ID</h2>
              <p className="text-zinc-500 text-sm mb-6">Your unique student identifier</p>

              <input
                type="text"
                value={studentId}
                onChange={(e) => setStudentId(e.target.value.toUpperCase())}
                onKeyDown={(e) => e.key === 'Enter' && handleStudentIdSubmit()}
                placeholder="e.g., STU001"
                className="input-dark font-mono mb-4"
                autoFocus
              />

              <GradientButton
                onClick={handleStudentIdSubmit}
                disabled={!studentId.trim()}
                size="lg"
                fullWidth
              >
                Continue
              </GradientButton>
            </GradientCard>
          </div>
        )}

        {/* Step 2: OTP */}
        {step === 'otp' && (
          <div className="animate-fadeInUp">
            <GradientCard>
              {/* Demo OTP Display */}
              {demoOtp && (
                <div className="mb-6 p-4 bg-amber-500/10 border border-amber-500/20 rounded-xl text-center">
                  {studentName && <p className="text-white font-medium mb-1">Welcome, {studentName}!</p>}
                  <p className="text-amber-400 text-sm mb-1">Your OTP Code</p>
                  <p className="text-3xl font-mono font-bold text-white tracking-[0.3em]">{demoOtp}</p>
                </div>
              )}

              <div className="flex flex-col items-center gap-6">
                <OTPInput
                  onOTPComplete={handleOtpComplete}
                  disabled={isOtpExpired}
                  error={isOtpExpired ? 'OTP Expired' : undefined}
                />
                
                <CountdownTimer
                  durationSeconds={60}
                  onExpire={handleOtpExpire}
                  isActive={isTimerActive && !isOtpExpired}
                  size={80}
                />
              </div>

              {isOtpExpired && (
                <div className="mt-6 text-center">
                  {resendAttemptsRemaining > 0 ? (
                    <button onClick={handleResendOtp} className="text-primary hover:text-primary-light font-medium text-sm">
                      Resend OTP ({resendAttemptsRemaining} left)
                    </button>
                  ) : (
                    <p className="text-red-400 text-sm">No resend attempts remaining</p>
                  )}
                </div>
              )}

              <button
                onClick={() => setStep('id')}
                className="w-full mt-6 py-3 bg-white/5 border border-white/10 text-white rounded-xl font-medium hover:bg-white/10 transition"
              >
                ← Back
              </button>
            </GradientCard>
          </div>
        )}

        {/* Step 3: Face Scan */}
        {step === 'face' && (
          <div className="animate-fadeInUp">
            <GradientCard className="overflow-hidden p-0">
              <div className="p-6">
                <div className="text-center mb-4">
                  <p className="text-zinc-400 text-sm">Align your face and blink naturally</p>
                </div>

                <div className="relative flex justify-center mb-6">
                  <div className="relative">
                    <WebcamCapture
                      onFrameCapture={handleFrameCapture}
                      showBoundingBox={true}
                      width={280}
                      height={280}
                    />
                    
                    {/* Smiley Face Feedback */}
                    <div className="absolute top-2 right-2 z-10">
                      {currentFrame ? (
                        <div className="w-12 h-12 bg-emerald-500/90 backdrop-blur-sm rounded-full flex items-center justify-center shadow-lg animate-scaleIn">
                          <svg className="w-7 h-7 text-white" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                            <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M14.828 14.828a4 4 0 01-5.656 0M9 10h.01M15 10h.01M21 12a9 9 0 11-18 0 9 9 0 0118 0z" />
                          </svg>
                        </div>
                      ) : (
                        <div className="w-12 h-12 bg-zinc-700/90 backdrop-blur-sm rounded-full flex items-center justify-center shadow-lg">
                          <svg className="w-7 h-7 text-zinc-400" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                            <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M9 12h6m-6 4h6m2 5H7a2 2 0 01-2-2V5a2 2 0 012-2h5.586a1 1 0 01.707.293l5.414 5.414a1 1 0 01.293.707V19a2 2 0 01-2 2z" />
                          </svg>
                        </div>
                      )}
                    </div>
                    
                    {/* Scanning overlay */}
                    <div className="absolute inset-0 pointer-events-none">
                      <div className="absolute inset-4 border-2 border-primary/50 rounded-full"></div>
                      <div className="absolute inset-4 border-2 border-transparent border-t-primary rounded-full animate-spin" style={{animationDuration: '2s'}}></div>
                    </div>
                  </div>
                </div>

                {/* Face Detection Status */}
                <div className="text-center mb-4">
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

                <GradientButton
                  onClick={handleVerify}
                  disabled={isVerifying || !currentFrame}
                  size="lg"
                  fullWidth
                  className="bg-gradient-to-r from-emerald-500 to-teal-600 mb-3"
                >
                  {isVerifying ? (
                    <><span className="animate-spin">◐</span> Verifying...</>
                  ) : (
                    <><svg className="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M9 12l2 2 4-4m6 2a9 9 0 11-18 0 9 9 0 0118 0z" /></svg> Verify Attendance</>
                  )}
                </GradientButton>

                <button
                  onClick={() => setStep('otp')}
                  className="w-full py-3 bg-white/5 border border-white/10 text-white rounded-xl font-medium hover:bg-white/10 transition"
                >
                  ← Back
                </button>
              </div>
            </GradientCard>
          </div>
        )}
      </main>
    </div>
  );
};

export default KioskView;
