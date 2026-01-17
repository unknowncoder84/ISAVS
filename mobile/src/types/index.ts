/**
 * TypeScript Type Definitions for ISAVS Mobile
 * Sensor Fusion Attendance System
 */

// ============== Sensor Data Types ==============

export interface AccelerometerData {
  x: number;
  y: number;
  z: number;
  timestamp: number;
}

export interface GyroscopeData {
  x: number;
  y: number;
  z: number;
  timestamp: number;
}

export interface MotionData {
  accelerometer: AccelerometerData[];
  gyroscope: GyroscopeData[];
  startTime: number;
  endTime: number;
}

// Legacy format for backend API
export interface MotionDataFlat {
  timestamps: number[];
  accelerometer_x: number[];
  accelerometer_y: number[];
  accelerometer_z: number[];
  gyroscope_x: number[];
  gyroscope_y: number[];
  gyroscope_z: number[];
}

export interface BeaconData {
  uuid: string;
  rssi: number;
  distance: number;
  name?: string;
}

export interface LocationData {
  latitude: number;
  longitude: number;
  accuracy: number;
  altitude?: number;
  timestamp: number;
}

export interface PressureData {
  pressure: number; // hPa
  timestamp: number;
  altitude?: number;
}

// ============== API Request/Response Types ==============

export interface SensorVerificationRequest {
  student_id: string;
  otp: string;
  face_image: string; // Base64
  session_id: string;
  
  // GPS
  latitude?: number;
  longitude?: number;
  
  // BLE
  ble_rssi?: number;
  ble_beacon_uuid?: string;
  
  // Barometer
  barometric_pressure?: number;
  
  // Motion
  motion_timestamps?: number[];
  accelerometer_x?: number[];
  accelerometer_y?: number[];
  accelerometer_z?: number[];
  gyroscope_x?: number[];
  gyroscope_y?: number[];
  gyroscope_z?: number[];
  
  // Frames
  frame_timestamps?: number[];
  frames_base64?: string[];
}

export interface FactorResults {
  face_verified: boolean;
  face_confidence: number;
  liveness_passed: boolean;
  id_verified: boolean;
  otp_verified: boolean;
  geofence_verified: boolean;
  distance_meters?: number;
  
  // Sensor fusion
  ble_verified?: boolean;
  ble_rssi?: number;
  barometer_verified?: boolean;
  pressure_difference_hpa?: number;
  motion_correlation_verified?: boolean;
  motion_correlation?: number;
}

export interface SensorVerificationResponse {
  success: boolean;
  factors: FactorResults;
  message: string;
  attendance_id?: number;
}

export interface OTPResponse {
  otp: string;
  remaining_seconds: number;
  student_id: string;
  student_name: string;
}

export interface SessionResponse {
  success: boolean;
  session_id: string;
  otp_count: number;
  expires_at: string;
  message: string;
}

// ============== Sensor Status ==============

export enum SensorStatus {
  IDLE = 'idle',
  SEARCHING = 'searching',
  READY = 'ready',
  FAILED = 'failed',
  UNAVAILABLE = 'unavailable',
}

export interface SensorReadiness {
  ble: SensorStatus;
  gps: SensorStatus;
  barometer: SensorStatus;
  motion: SensorStatus;
  camera: SensorStatus;
}

// ============== Validation Result ==============

export interface ValidationResult {
  passed: boolean;
  message: string;
  value?: number;
  threshold?: number;
}

// ============== App State ==============

export interface AppState {
  sessionId: string | null;
  studentId: string | null;
  otp: string | null;
  sensorReadiness: SensorReadiness;
  isVerifying: boolean;
}

// ============== Navigation Types ==============

export type RootStackParamList = {
  Home: undefined;
  StudentVerification: {sessionId: string};
  TeacherSession: undefined;
  VerificationResult: {result: SensorVerificationResponse};
  Settings: undefined;
};

// ============== Configuration ==============

export interface AppConfig {
  apiBaseUrl: string;
  bleBeaconUUID: string;
  bleRSSIThreshold: number;
  gpsRadiusMeters: number;
  barometerThresholdHpa: number;
  motionCorrelationThreshold: number;
  motionSamplingRateHz: number;
  motionDurationSeconds: number;
}

// ============== Error Types ==============

export interface SensorError {
  sensor: keyof SensorReadiness;
  error: string;
  code?: string;
}

export interface APIError {
  message: string;
  status?: number;
  details?: any;
}
