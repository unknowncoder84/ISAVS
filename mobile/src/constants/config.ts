/**
 * App Configuration
 * Centralized configuration for ISAVS Mobile
 */
import {AppConfig} from '../types';

export const APP_CONFIG: AppConfig = {
  // API Configuration
  apiBaseUrl: __DEV__ ? 'http://localhost:8000' : 'https://your-production-api.com',
  
  // BLE Configuration
  bleBeaconUUID: 'ISAVS-CLASSROOM-BEACON',
  bleRSSIThreshold: -70, // dBm
  
  // GPS Configuration
  gpsRadiusMeters: 50, // meters
  
  // Barometer Configuration
  barometerThresholdHpa: 0.5, // hPa
  
  // Motion Configuration
  motionCorrelationThreshold: 0.7, // Pearson correlation
  motionSamplingRateHz: 50, // Hz
  motionDurationSeconds: 2, // seconds
};

// Sensor thresholds
export const SENSOR_THRESHOLDS = {
  BLE_RSSI: -70.0, // dBm
  GPS_RADIUS: 50.0, // meters
  BAROMETER: 0.5, // hPa
  MOTION_CORRELATION: 0.7, // correlation coefficient
  FACE_CONFIDENCE: 0.6, // cosine similarity
};

// Timing constants
export const TIMING = {
  OTP_TTL_SECONDS: 300, // 5 minutes
  BLE_SCAN_DURATION_MS: 5000, // 5 seconds
  BLE_SCAN_INTERVAL_MS: 2000, // 2 seconds pause
  MOTION_COLLECTION_MS: 2000, // 2 seconds
  FRAME_CAPTURE_INTERVAL_MS: 200, // 200ms between frames
  SENSOR_UPDATE_INTERVAL_MS: 1000, // 1 second
};

// UI constants
export const UI = {
  COLORS: {
    PRIMARY: '#2563eb',
    SUCCESS: '#10b981',
    WARNING: '#f59e0b',
    ERROR: '#ef4444',
    GRAY: '#64748b',
    LIGHT_GRAY: '#94a3b8',
    WHITE: '#ffffff',
    BLACK: '#000000',
  },
  SPACING: {
    XS: 4,
    SM: 8,
    MD: 16,
    LG: 24,
    XL: 32,
  },
  FONT_SIZES: {
    XS: 12,
    SM: 14,
    MD: 16,
    LG: 20,
    XL: 24,
    XXL: 32,
  },
};

// Sensor names
export const SENSOR_NAMES = {
  BLE: 'BLE Proximity',
  GPS: 'GPS Location',
  BAROMETER: 'Barometer',
  MOTION: 'Motion Sensors',
  CAMERA: 'Camera',
};

// Error messages
export const ERROR_MESSAGES = {
  BLE_UNAVAILABLE: 'Bluetooth is not available on this device',
  BLE_PERMISSION_DENIED: 'Bluetooth permission denied',
  GPS_UNAVAILABLE: 'GPS is not available on this device',
  GPS_PERMISSION_DENIED: 'Location permission denied',
  BAROMETER_UNAVAILABLE: 'Barometer is not available on this device',
  MOTION_UNAVAILABLE: 'Motion sensors are not available on this device',
  CAMERA_UNAVAILABLE: 'Camera is not available on this device',
  CAMERA_PERMISSION_DENIED: 'Camera permission denied',
  NETWORK_ERROR: 'Network error. Please check your connection.',
  API_ERROR: 'Server error. Please try again later.',
  VERIFICATION_FAILED: 'Verification failed. Please try again.',
};

export default APP_CONFIG;
