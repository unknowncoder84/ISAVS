/**
 * Countdown Timer Component - Enhanced circular design
 */
import React, { useEffect, useState, useCallback } from 'react';

interface CountdownTimerProps {
  durationSeconds: number;
  onExpire: () => void;
  isActive: boolean;
  size?: number;
}

const CountdownTimer: React.FC<CountdownTimerProps> = ({
  durationSeconds,
  onExpire,
  isActive,
  size = 100,
}) => {
  const [remainingSeconds, setRemainingSeconds] = useState(durationSeconds);
  const [progress, setProgress] = useState(100);

  const reset = useCallback(() => {
    setRemainingSeconds(durationSeconds);
    setProgress(100);
  }, [durationSeconds]);

  useEffect(() => {
    reset();
  }, [durationSeconds, reset]);

  useEffect(() => {
    if (!isActive) return;

    const interval = setInterval(() => {
      setRemainingSeconds((prev) => {
        const newValue = prev - 1;
        if (newValue <= 0) {
          clearInterval(interval);
          onExpire();
          return 0;
        }
        setProgress((newValue / durationSeconds) * 100);
        return newValue;
      });
    }, 1000);

    return () => clearInterval(interval);
  }, [isActive, durationSeconds, onExpire]);

  const strokeWidth = 6;
  const radius = (size - strokeWidth) / 2;
  const circumference = 2 * Math.PI * radius;
  const strokeDashoffset = circumference - (progress / 100) * circumference;

  const getColor = () => {
    if (remainingSeconds <= 10) return { stroke: '#ef4444', bg: '#fef2f2', text: '#dc2626' };
    if (remainingSeconds <= 20) return { stroke: '#f59e0b', bg: '#fffbeb', text: '#d97706' };
    return { stroke: '#22c55e', bg: '#f0fdf4', text: '#16a34a' };
  };

  const colors = getColor();

  return (
    <div className="flex flex-col items-center">
      <div 
        className="relative rounded-full shadow-lg"
        style={{ width: size, height: size, backgroundColor: colors.bg }}
      >
        <svg className="transform -rotate-90" width={size} height={size}>
          {/* Background circle */}
          <circle
            cx={size / 2}
            cy={size / 2}
            r={radius}
            fill="none"
            stroke="#e5e7eb"
            strokeWidth={strokeWidth}
          />
          {/* Progress circle */}
          <circle
            cx={size / 2}
            cy={size / 2}
            r={radius}
            fill="none"
            stroke={colors.stroke}
            strokeWidth={strokeWidth}
            strokeLinecap="round"
            strokeDasharray={circumference}
            strokeDashoffset={strokeDashoffset}
            className="transition-all duration-1000 ease-linear"
          />
        </svg>
        
        {/* Timer text */}
        <div className="absolute inset-0 flex flex-col items-center justify-center">
          <span className="text-2xl sm:text-3xl font-bold" style={{ color: colors.text }}>
            {remainingSeconds}
          </span>
          <span className="text-[10px] uppercase tracking-wider text-slate-400">sec</span>
        </div>
      </div>
      
      <p className={`mt-2 text-xs font-medium ${remainingSeconds <= 10 ? 'text-red-500' : 'text-slate-500'}`}>
        {remainingSeconds > 0 ? 'OTP expires in' : '⚠️ OTP Expired'}
      </p>
    </div>
  );
};

export default CountdownTimer;
