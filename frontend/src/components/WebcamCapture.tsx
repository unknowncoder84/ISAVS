/**
 * Webcam Capture Component - Enhanced with better UI
 */
import React, { useRef, useCallback, useEffect, useState } from 'react';
import Webcam from 'react-webcam';

interface WebcamCaptureProps {
  onFrameCapture: (frame: string) => void;
  showBoundingBox?: boolean;
  captureInterval?: number;
  width?: number;
  height?: number;
}

const WebcamCapture: React.FC<WebcamCaptureProps> = ({
  onFrameCapture,
  showBoundingBox = true,
  captureInterval = 500,
  width = 640,
  height = 480,
}) => {
  const webcamRef = useRef<Webcam>(null);
  const [isReady, setIsReady] = useState(false);
  const [hasError, setHasError] = useState(false);

  const videoConstraints = {
    width,
    height,
    facingMode: 'user',
  };

  const captureFrame = useCallback(() => {
    if (webcamRef.current) {
      const imageSrc = webcamRef.current.getScreenshot();
      if (imageSrc) {
        onFrameCapture(imageSrc);
      }
    }
  }, [onFrameCapture]);

  useEffect(() => {
    if (!isReady) return;
    const interval = setInterval(captureFrame, captureInterval);
    return () => clearInterval(interval);
  }, [captureFrame, captureInterval, isReady]);

  if (hasError) {
    return (
      <div 
        className="flex flex-col items-center justify-center bg-slate-100 rounded-xl border-2 border-dashed border-slate-300"
        style={{ width, height }}
      >
        <svg className="w-12 h-12 text-slate-400 mb-3" fill="none" stroke="currentColor" viewBox="0 0 24 24">
          <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M15 10l4.553-2.276A1 1 0 0121 8.618v6.764a1 1 0 01-1.447.894L15 14M5 18h8a2 2 0 002-2V8a2 2 0 00-2-2H5a2 2 0 00-2 2v8a2 2 0 002 2z" />
        </svg>
        <p className="text-slate-500 text-sm text-center px-4">Camera access denied or unavailable</p>
        <button 
          onClick={() => window.location.reload()}
          className="mt-3 text-sm text-blue-600 hover:text-blue-700"
        >
          Try Again
        </button>
      </div>
    );
  }

  return (
    <div className="relative rounded-xl overflow-hidden bg-black" style={{ width: '100%', maxWidth: width }}>
      <Webcam
        ref={webcamRef}
        audio={false}
        screenshotFormat="image/jpeg"
        videoConstraints={videoConstraints}
        onUserMedia={() => setIsReady(true)}
        onUserMediaError={() => setHasError(true)}
        className="w-full h-auto"
        style={{ aspectRatio: `${width}/${height}` }}
      />
      
      {/* Face guide overlay */}
      {showBoundingBox && isReady && (
        <div className="absolute inset-0 pointer-events-none">
          {/* Center oval guide */}
          <div className="absolute inset-0 flex items-center justify-center">
            <div 
              className="border-2 border-white/50 rounded-full"
              style={{ width: '50%', height: '70%' }}
            />
          </div>
          {/* Corner brackets */}
          <svg className="absolute inset-0 w-full h-full" viewBox="0 0 100 100" preserveAspectRatio="none">
            <path d="M25,15 L15,15 L15,25" fill="none" stroke="#22c55e" strokeWidth="0.5" />
            <path d="M75,15 L85,15 L85,25" fill="none" stroke="#22c55e" strokeWidth="0.5" />
            <path d="M25,85 L15,85 L15,75" fill="none" stroke="#22c55e" strokeWidth="0.5" />
            <path d="M75,85 L85,85 L85,75" fill="none" stroke="#22c55e" strokeWidth="0.5" />
          </svg>
        </div>
      )}
      
      {/* Status indicator */}
      <div className={`absolute bottom-3 left-3 px-3 py-1.5 rounded-full text-xs font-medium flex items-center gap-1.5 ${
        isReady ? 'bg-emerald-500/90 text-white' : 'bg-amber-500/90 text-white'
      }`}>
        <span className={`w-2 h-2 rounded-full ${isReady ? 'bg-white animate-pulse' : 'bg-white'}`}></span>
        {isReady ? 'Camera Ready' : 'Loading...'}
      </div>
    </div>
  );
};

export default WebcamCapture;
