/**
 * Student Enrollment - Blue/Purple Gradient Theme (Campus Connect Inspired)
 */
import React, { useState, useCallback } from 'react';
import { Link } from 'react-router-dom';
import WebcamCapture from './WebcamCapture';
import GradientButton from './ui/GradientButton';
import GradientCard from './ui/GradientCard';
import { enrollStudent, handleApiError } from '../services/api';

const StudentEnrollment: React.FC = () => {
  const [name, setName] = useState('');
  const [studentIdCard, setStudentIdCard] = useState('');
  const [capturedImage, setCapturedImage] = useState<string>('');
  const [isEnrolling, setIsEnrolling] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const [success, setSuccess] = useState<{ studentId: number; message: string } | null>(null);
  const [step, setStep] = useState<1 | 2 | 3>(1);

  const handleFrameCapture = useCallback((frame: string) => {
    setCapturedImage(frame);
  }, []);

  const handleEnroll = async () => {
    if (!name.trim() || !studentIdCard.trim() || !capturedImage) {
      setError('Please complete all fields');
      return;
    }

    setIsEnrolling(true);
    setError(null);

    try {
      const response = await enrollStudent({
        name: name.trim(),
        student_id_card_number: studentIdCard.trim(),
        face_image: capturedImage,
      });

      if (response.success) {
        setSuccess({ studentId: response.student_id!, message: response.message });
      } else {
        setError(response.message);
      }
    } catch (err) {
      setError(handleApiError(err));
    } finally {
      setIsEnrolling(false);
    }
  };

  const handleReset = () => {
    setName('');
    setStudentIdCard('');
    setCapturedImage('');
    setError(null);
    setSuccess(null);
    setStep(1);
  };

  // Success Screen
  if (success) {
    return (
      <div className="min-h-screen bg-[#0f0d1a] flex items-center justify-center p-4">
        <div className="w-full max-w-sm text-center animate-scaleIn">
          <div className="w-24 h-24 bg-gradient-to-br from-emerald-500 to-teal-600 rounded-full flex items-center justify-center mx-auto mb-6 shadow-2xl shadow-emerald-500/30">
            <svg className="w-12 h-12 text-white" fill="none" stroke="currentColor" viewBox="0 0 24 24">
              <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M5 13l4 4L19 7" />
            </svg>
          </div>
          <h1 className="text-2xl font-bold text-white mb-2">Enrollment Successful!</h1>
          <p className="text-zinc-400 mb-2">{success.message}</p>
          <p className="text-zinc-500 text-sm mb-8">
            Student ID: <span className="font-mono text-indigo-400">{success.studentId}</span>
          </p>
          <div className="space-y-3">
            <button onClick={handleReset} className="w-full py-3 bg-[#1a1625] border border-white/10 text-white rounded-xl font-medium hover:bg-[#231e30] transition">
              Enroll Another
            </button>
            <Link to="/dashboard">
              <GradientButton size="lg" fullWidth>
                Go to Dashboard
              </GradientButton>
            </Link>
          </div>
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
          <h1 className="text-lg font-semibold text-white">New Enrollment</h1>
          <div className="w-10"></div>
        </div>
      </header>

      <main className="max-w-lg mx-auto px-4 py-6">
        {/* Progress Steps */}
        <div className="flex items-center justify-center gap-3 mb-8">
          {[1, 2, 3].map((s) => (
            <React.Fragment key={s}>
              <div className={`w-10 h-10 rounded-full flex items-center justify-center font-semibold text-sm transition-all ${
                step >= s 
                  ? 'bg-gradient-to-br from-indigo-500 to-purple-600 text-white' 
                  : 'bg-white/5 text-zinc-500'
              }`}>
                {step > s ? '✓' : s}
              </div>
              {s < 3 && (
                <div className={`w-12 h-1 rounded-full transition-all ${step > s ? 'bg-indigo-500' : 'bg-white/10'}`}></div>
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

        {/* Step 1: Details */}
        {step === 1 && (
          <div className="animate-fadeInUp">
            <GradientCard>
              <div className="w-14 h-14 gradient-primary rounded-2xl flex items-center justify-center mb-5 shadow-soft">
                <svg className="w-7 h-7 text-white" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                  <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M16 7a4 4 0 11-8 0 4 4 0 018 0zM12 14a7 7 0 00-7 7h14a7 7 0 00-7-7z" />
                </svg>
              </div>
              <h2 className="text-xl font-semibold text-white mb-1">Student Details</h2>
              <p className="text-zinc-500 text-sm mb-6">Enter your information</p>

              <div className="space-y-4">
                <div>
                  <label className="block text-sm font-medium text-zinc-400 mb-2">Full Name</label>
                  <input
                    type="text"
                    value={name}
                    onChange={(e) => setName(e.target.value)}
                    placeholder="John Doe"
                    className="input-dark"
                  />
                </div>
                <div>
                  <label className="block text-sm font-medium text-zinc-400 mb-2">Student ID</label>
                  <input
                    type="text"
                    value={studentIdCard}
                    onChange={(e) => setStudentIdCard(e.target.value.toUpperCase())}
                    placeholder="STU001"
                    className="input-dark font-mono"
                  />
                </div>
                <GradientButton
                  onClick={() => setStep(2)}
                  disabled={!name.trim() || !studentIdCard.trim()}
                  size="lg"
                  fullWidth
                  className="mt-2"
                >
                  Continue
                </GradientButton>
              </div>
            </GradientCard>
          </div>
        )}

        {/* Step 2: Face Capture */}
        {step === 2 && (
          <div className="animate-fadeInUp">
            <GradientCard className="overflow-hidden p-0">
              <div className="gradient-primary px-6 py-4">
                <h2 className="text-white font-semibold flex items-center gap-2">
                  <svg className="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                    <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M3 9a2 2 0 012-2h.93a2 2 0 001.664-.89l.812-1.22A2 2 0 0110.07 4h3.86a2 2 0 011.664.89l.812 1.22A2 2 0 0018.07 7H19a2 2 0 012 2v9a2 2 0 01-2 2H5a2 2 0 01-2-2V9z" />
                  </svg>
                  Face Capture
                </h2>
              </div>
              <div className="p-6">
                <div className="flex justify-center mb-4">
                  <WebcamCapture onFrameCapture={handleFrameCapture} showBoundingBox={true} width={320} height={240} />
                </div>
                <p className="text-center text-sm text-zinc-500 mb-6">
                  Align your face and look at the camera
                </p>
                <div className="flex gap-3">
                  <button onClick={() => setStep(1)} className="flex-1 py-3 bg-white/5 border border-white/10 text-white rounded-xl font-medium hover:bg-white/10 transition">
                    ← Back
                  </button>
                  <GradientButton
                    onClick={() => setStep(3)}
                    disabled={!capturedImage}
                    className="flex-1"
                  >
                    Continue →
                  </GradientButton>
                </div>
              </div>
            </GradientCard>
          </div>
        )}

        {/* Step 3: Confirm */}
        {step === 3 && (
          <div className="animate-fadeInUp">
            <GradientCard>
              <h2 className="text-xl font-semibold text-white mb-1">Confirm Details</h2>
              <p className="text-zinc-500 text-sm mb-6">Review before submitting</p>

              <div className="bg-white/5 rounded-2xl p-4 mb-6 flex items-center gap-4">
                {capturedImage && (
                  <img src={capturedImage} alt="Face" className="w-16 h-16 rounded-xl object-cover border-2 border-primary/30" />
                )}
                <div>
                  <p className="font-semibold text-white text-lg">{name}</p>
                  <p className="text-sm text-zinc-400 font-mono">{studentIdCard}</p>
                </div>
              </div>

              <div className="flex gap-3">
                <button onClick={() => setStep(2)} className="flex-1 py-3 bg-white/5 border border-white/10 text-white rounded-xl font-medium hover:bg-white/10 transition">
                  ← Retake
                </button>
                <GradientButton
                  onClick={handleEnroll}
                  disabled={isEnrolling}
                  className="flex-1 bg-gradient-to-r from-emerald-500 to-teal-600"
                >
                  {isEnrolling ? (
                    <><span className="animate-spin">◐</span> Enrolling...</>
                  ) : (
                    <><svg className="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M5 13l4 4L19 7" /></svg> Enroll</>
                  )}
                </GradientButton>
              </div>
            </GradientCard>
          </div>
        )}
      </main>
    </div>
  );
};

export default StudentEnrollment;
