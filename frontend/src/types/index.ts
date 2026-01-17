// Type definitions for ISAVS Frontend

export interface VerificationResult {
  success: boolean;
  factors: FactorResults;
  message: string;
  attendanceId?: number;
}

export interface FactorResults {
  faceVerified: boolean;
  faceConfidence: number;
  livenessPassed: boolean;
  idVerified: boolean;
  otpVerified: boolean;
}

export interface AttendanceRecord {
  id: number;
  studentName: string;
  studentId: string;
  timestamp: Date;
  verificationStatus: 'verified' | 'failed';
}

export interface Anomaly {
  id: number;
  studentId?: number;
  studentName?: string;
  reason: string;
  anomalyType: 'verification_failed' | 'identity_mismatch' | 'proxy_attempt' | 'session_locked';
  faceConfidence?: number;
  timestamp: Date;
  reviewed: boolean;
}

export interface BoundingBox {
  x: number;
  y: number;
  width: number;
  height: number;
}

export type VerificationStatus = 'pending' | 'success' | 'failed' | 'expired';
