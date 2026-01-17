# 🚀 Phase 2: React Native Project Setup - Getting Started

**Status**: Ready to begin  
**Prerequisites**: Phase 1 complete ✅  
**Estimated Time**: 2-3 days

---

## 📋 Phase 2 Overview

Phase 2 focuses on setting up the React Native mobile application foundation with all necessary sensor libraries and configurations.

### Tasks (2.1-2.4)
- [ ] 2.1 Initialize React Native project with TypeScript
- [ ] 2.2 Install sensor libraries (BLE, accelerometer, barometer, camera, GPS)
- [ ] 2.3 Create TypeScript types and interfaces
- [ ] 2.4 Set up API client service

---

## 🛠️ Task 2.1: Initialize React Native Project

### Prerequisites
```bash
# Install Node.js (v18 or higher)
node --version

# Install React Native CLI
npm install -g react-native-cli

# For iOS (macOS only)
xcode-select --install
pod --version

# For Android
# Install Android Studio and configure ANDROID_HOME
```

### Create Project
```bash
# Navigate to project root
cd /path/to/isavs-2026

# Create React Native app with TypeScript
npx react-native init ISAVSMobile --template react-native-template-typescript

# Navigate to mobile app
cd ISAVSMobile

# Test installation
npx react-native run-android  # or run-ios
```

### Folder Structure
```
ISAVSMobile/
├── src/
│   ├── components/      # React components
│   ├── services/        # Business logic and API calls
│   ├── hooks/           # Custom React hooks
│   ├── types/           # TypeScript type definitions
│   ├── screens/         # Screen components
│   ├── navigation/      # Navigation configuration
│   ├── utils/           # Utility functions
│   └── constants/       # Constants and configuration
├── android/             # Android native code
├── ios/                 # iOS native code
├── package.json
└── tsconfig.json
```

### Core Dependencies
```bash
# Navigation
npm install @react-navigation/native @react-navigation/stack
npm install react-native-screens react-native-safe-area-context

# HTTP client
npm install axios

# Storage
npm install @react-native-async-storage/async-storage

# UI components (optional)
npm install react-native-paper
```

---

## 📱 Task 2.2: Install Sensor Libraries

### BLE (Bluetooth Low Energy)
```bash
npm install react-native-ble-manager
```

**iOS Configuration** (`ios/Info.plist`):
```xml
<key>NSBluetoothAlwaysUsageDescription</key>
<string>We need Bluetooth to detect classroom proximity</string>
<key>NSBluetoothPeripheralUsageDescription</key>
<string>We need Bluetooth to broadcast classroom beacon</string>
```

**Android Configuration** (`android/app/src/main/AndroidManifest.xml`):
```xml
<uses-permission android:name="android.permission.BLUETOOTH"/>
<uses-permission android:name="android.permission.BLUETOOTH_ADMIN"/>
<uses-permission android:name="android.permission.BLUETOOTH_SCAN"/>
<uses-permission android:name="android.permission.BLUETOOTH_CONNECT"/>
<uses-permission android:name="android.permission.ACCESS_FINE_LOCATION"/>
```

### Motion Sensors (Accelerometer + Gyroscope)
```bash
npm install react-native-sensors
```

**iOS Configuration** (`ios/Info.plist`):
```xml
<key>NSMotionUsageDescription</key>
<string>We need motion sensors for liveness detection</string>
```

### Barometer
```bash
npm install react-native-barometer
```

### Camera (High-Performance)
```bash
npm install react-native-vision-camera
```

**iOS Configuration** (`ios/Info.plist`):
```xml
<key>NSCameraUsageDescription</key>
<string>We need camera access for face verification</string>
```

**Android Configuration** (`android/app/src/main/AndroidManifest.xml`):
```xml
<uses-permission android:name="android.permission.CAMERA"/>
```

### GPS (Geolocation)
```bash
npm install @react-native-community/geolocation
```

**iOS Configuration** (`ios/Info.plist`):
```xml
<key>NSLocationWhenInUseUsageDescription</key>
<string>We need your location to verify classroom attendance</string>
<key>NSLocationAlwaysUsageDescription</key>
<string>We need your location to verify classroom attendance</string>
```

**Android Configuration** (`android/app/src/main/AndroidManifest.xml`):
```xml
<uses-permission android:name="android.permission.ACCESS_FINE_LOCATION"/>
<uses-permission android:name="android.permission.ACCESS_COARSE_LOCATION"/>
```

### Install Pods (iOS)
```bash
cd ios
pod install
cd ..
```

---

## 📝 Task 2.3: Create TypeScript Types

Create `src/types/index.ts`:

```typescript
// Sensor data types
export interface MotionData {
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
}

export interface LocationData {
  latitude: number;
  longitude: number;
  accuracy: number;
}

export interface PressureData {
  pressure: number; // hPa
  timestamp: number;
}

// API request/response types
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

// Sensor status
export enum SensorStatus {
  IDLE = 'idle',
  SEARCHING = 'searching',
  READY = 'ready',
  FAILED = 'failed',
}

export interface SensorReadiness {
  ble: SensorStatus;
  gps: SensorStatus;
  barometer: SensorStatus;
  motion: SensorStatus;
  camera: SensorStatus;
}

// Validation result
export interface ValidationResult {
  passed: boolean;
  message: string;
}
```

---

## 🌐 Task 2.4: Set Up API Client

Create `src/services/api.ts`:

```typescript
import axios, { AxiosInstance, AxiosError } from 'axios';
import { SensorVerificationRequest, SensorVerificationResponse } from '../types';

class APIClient {
  private client: AxiosInstance;
  
  constructor(baseURL: string) {
    this.client = axios.create({
      baseURL,
      timeout: 30000, // 30 seconds
      headers: {
        'Content-Type': 'application/json',
      },
    });
    
    // Request interceptor
    this.client.interceptors.request.use(
      (config) => {
        console.log(`API Request: ${config.method?.toUpperCase()} ${config.url}`);
        return config;
      },
      (error) => {
        return Promise.reject(error);
      }
    );
    
    // Response interceptor
    this.client.interceptors.response.use(
      (response) => {
        console.log(`API Response: ${response.status} ${response.config.url}`);
        return response;
      },
      (error: AxiosError) => {
        console.error(`API Error: ${error.message}`);
        return Promise.reject(error);
      }
    );
  }
  
  async verifyAttendance(
    request: SensorVerificationRequest
  ): Promise<SensorVerificationResponse> {
    const response = await this.client.post<SensorVerificationResponse>(
      '/api/v1/verify',
      request
    );
    return response.data;
  }
  
  async getOTP(sessionId: string, studentId: string): Promise<string> {
    const response = await this.client.get(
      `/api/v1/session/${sessionId}/otp/${studentId}`
    );
    return response.data.otp;
  }
  
  async resendOTP(sessionId: string, studentId: string): Promise<void> {
    await this.client.post('/api/v1/otp/resend', {
      session_id: sessionId,
      student_id: studentId,
    });
  }
}

// Singleton instance
const apiClient = new APIClient('http://localhost:8000'); // Update with your backend URL

export default apiClient;
```

---

## ✅ Verification Checklist

After completing Phase 2, verify:

- [ ] React Native project runs on Android/iOS
- [ ] All sensor libraries installed
- [ ] Permissions configured in Info.plist and AndroidManifest.xml
- [ ] TypeScript types defined
- [ ] API client service created
- [ ] No build errors
- [ ] App launches successfully

---

## 🐛 Common Issues

### Issue: Metro bundler fails to start
**Solution**: Clear cache
```bash
npx react-native start --reset-cache
```

### Issue: iOS build fails
**Solution**: Clean and reinstall pods
```bash
cd ios
rm -rf Pods Podfile.lock
pod install
cd ..
```

### Issue: Android build fails
**Solution**: Clean gradle
```bash
cd android
./gradlew clean
cd ..
```

### Issue: Permission denied errors
**Solution**: Ensure all permissions are added to Info.plist and AndroidManifest.xml

---

## 📚 Resources

- [React Native Documentation](https://reactnative.dev/docs/getting-started)
- [react-native-ble-manager](https://github.com/innoveit/react-native-ble-manager)
- [react-native-sensors](https://github.com/react-native-sensors/react-native-sensors)
- [react-native-vision-camera](https://github.com/mrousavy/react-native-vision-camera)
- [TypeScript Handbook](https://www.typescriptlang.org/docs/handbook/intro.html)

---

## 🎯 Next Phase

After Phase 2 completion, proceed to:
**Phase 3: BLE Proximity Module** (Tasks 3.1-3.6)

---

**Ready to start Phase 2!** 🚀
