# 📸 Camera & BLE Status Report

**Date**: January 17, 2026  
**Status**: Implementation Complete

---

## 📸 Camera Implementation

### Web Frontend (Kiosk View)
**Status**: ✅ **FULLY IMPLEMENTED**

**File**: `frontend/src/components/WebcamCapture.tsx`

**Features**:
- Real-time webcam feed
- Face detection overlay (oval guide)
- Automatic capture on face detection
- Manual capture button
- Preview before submission
- Retake functionality
- Base64 encoding for API submission

**How It Works**:
1. User clicks "Capture Face"
2. Webcam activates
3. Oval guide shows where to position face
4. User captures photo
5. Preview shown with Retake/Use Photo options
6. Photo sent to backend as base64

**Testing**:
```
1. Go to: http://localhost:5173/kiosk?session=<session_id>
2. Enter student ID and OTP
3. Click "Capture Face"
4. Allow camera permissions
5. Position face in oval
6. Click capture button
7. Review and submit
```

---

### Mobile App (React Native)
**Status**: ✅ **FULLY IMPLEMENTED**

**File**: `mobile/src/components/FaceVerificationCamera.tsx`

**Features**:
- Native camera integration (react-native-vision-camera)
- Real-time face detection
- Face quality checks (lighting, blur, size)
- Automatic capture when face is good quality
- Manual capture fallback
- Face guide overlay
- Photo preview
- Base64 encoding

**Advanced Features**:
- Motion detection during capture (anti-spoofing)
- Barometer data collection (floor verification)
- BLE beacon scanning (proximity verification)
- GPS location tracking (geofencing)

**How It Works**:
1. User opens verification screen
2. Camera activates automatically
3. Face guide overlay appears
4. System checks face quality in real-time
5. Auto-captures when quality is good
6. Collects sensor data (motion, barometer, BLE, GPS)
7. Submits everything to backend

**Testing**:
```
1. Run mobile app on physical device (camera doesn't work in simulator)
2. Navigate to verification screen
3. Grant camera permissions
4. Position face in guide
5. Wait for auto-capture or tap manually
6. Review and submit
```

---

## 📡 BLE (Bluetooth Low Energy) Implementation

### Status: ✅ **FULLY IMPLEMENTED**

**Purpose**: Verify student is physically present in classroom by detecting BLE beacons

**Files**:
- `mobile/src/services/BLEScanner.ts` - Core BLE scanning
- `mobile/src/services/BeaconManager.ts` - Beacon management
- `mobile/src/hooks/useBLEProximity.ts` - React hook for BLE
- `mobile/src/components/BLEStatusIndicator.tsx` - UI component

---

### How BLE Works in ISAVS

#### 1. Classroom Setup
```
Faculty places BLE beacon in classroom:
- Beacon UUID: "ISAVS-CLASSROOM-BEACON"
- Transmit power: -59 dBm (adjustable)
- Range: ~10-50 meters
```

#### 2. Student Verification
```
When student verifies attendance:
1. Mobile app scans for BLE beacons
2. Detects classroom beacon
3. Measures RSSI (signal strength)
4. Calculates distance from beacon
5. Sends beacon data to backend
6. Backend validates proximity
```

#### 3. Backend Validation
```python
# backend/app/services/sensor_validation_service.py

def validate_ble_proximity(rssi: float, expected_rssi: float = -59.0) -> bool:
    """
    Validate BLE proximity using RSSI (Received Signal Strength Indicator)
    
    RSSI values:
    - -30 to -50 dBm: Very close (< 1 meter)
    - -50 to -70 dBm: Close (1-5 meters)
    - -70 to -90 dBm: Medium (5-15 meters)
    - -90 to -100 dBm: Far (15-50 meters)
    - < -100 dBm: Too far or no signal
    """
    threshold = 15.0  # Allow 15 dBm variance
    return abs(rssi - expected_rssi) <= threshold
```

---

### BLE Features

#### 1. Real-time Scanning
```typescript
// mobile/src/services/BLEScanner.ts

class BLEScanner {
  async startScanning(): Promise<void> {
    // Scan for BLE devices
    // Filter by classroom beacon UUID
    // Measure RSSI
    // Calculate distance
  }
  
  async stopScanning(): Promise<void> {
    // Stop BLE scan
    // Clean up resources
  }
}
```

#### 2. Proximity Detection
```typescript
// mobile/src/hooks/useBLEProximity.ts

export const useBLEProximity = () => {
  const [isNearBeacon, setIsNearBeacon] = useState(false);
  const [distance, setDistance] = useState<number | null>(null);
  const [rssi, setRSSI] = useState<number | null>(null);
  
  // Automatically scans and updates proximity
  // Returns real-time beacon data
};
```

#### 3. Visual Feedback
```typescript
// mobile/src/components/BLEStatusIndicator.tsx

<BLEStatusIndicator 
  isNearBeacon={true}
  distance={5.2}
  rssi={-65}
/>

// Shows:
// ✓ Beacon Detected
// Distance: 5.2m
// Signal: Strong
```

---

### BLE Setup Requirements

#### Hardware Needed:
1. **BLE Beacon** (any of these):
   - iBeacon (Apple)
   - Eddystone (Google)
   - Generic BLE beacon
   - Raspberry Pi with BLE
   - Old smartphone as beacon

2. **Mobile Device**:
   - Android 5.0+ with BLE support
   - iOS 10+ with BLE support

#### Software Setup:

**1. Configure Beacon**:
```javascript
// mobile/src/constants/config.ts

export const BLE_CONFIG = {
  CLASSROOM_BEACON_UUID: 'ISAVS-CLASSROOM-BEACON',
  EXPECTED_RSSI: -59,  // Adjust based on your beacon
  SCAN_DURATION: 5000, // 5 seconds
  PROXIMITY_THRESHOLD: 15 // dBm variance allowed
};
```

**2. Grant Permissions** (Android):
```xml
<!-- mobile/android/app/src/main/AndroidManifest.xml -->
<uses-permission android:name="android.permission.BLUETOOTH" />
<uses-permission android:name="android.permission.BLUETOOTH_ADMIN" />
<uses-permission android:name="android.permission.BLUETOOTH_SCAN" />
<uses-permission android:name="android.permission.BLUETOOTH_CONNECT" />
<uses-permission android:name="android.permission.ACCESS_FINE_LOCATION" />
```

**3. Grant Permissions** (iOS):
```xml
<!-- mobile/ios/Info.plist -->
<key>NSBluetoothAlwaysUsageDescription</key>
<string>We need Bluetooth to verify you're in the classroom</string>
<key>NSLocationWhenInUseUsageDescription</key>
<string>We need location for BLE scanning</string>
```

---

### BLE Testing

#### Without Physical Beacon (Development):
```typescript
// BLE is optional - system works without it
// Backend accepts null BLE data
// Useful for testing without hardware
```

#### With Physical Beacon (Production):
```
1. Place beacon in classroom
2. Note beacon UUID and RSSI
3. Update config.ts with beacon details
4. Run mobile app
5. Check BLE status indicator
6. Verify attendance
7. Backend validates BLE proximity
```

---

## 🎯 Current Implementation Status

### ✅ What's Working:

#### Camera (Web):
- ✅ Webcam capture
- ✅ Face detection overlay
- ✅ Preview and retake
- ✅ Base64 encoding
- ✅ API integration

#### Camera (Mobile):
- ✅ Native camera
- ✅ Real-time face detection
- ✅ Quality checks
- ✅ Auto-capture
- ✅ Motion detection
- ✅ Sensor fusion

#### BLE (Mobile):
- ✅ BLE scanning
- ✅ Beacon detection
- ✅ RSSI measurement
- ✅ Distance calculation
- ✅ Proximity validation
- ✅ Visual feedback

#### Backend:
- ✅ Face recognition (DeepFace + Facenet)
- ✅ BLE validation
- ✅ Motion correlation
- ✅ Barometer validation
- ✅ GPS geofencing
- ✅ Sensor fusion scoring

---

## 🔧 Troubleshooting

### Camera Issues:

**Web - Camera Not Working**:
```
1. Check browser permissions (chrome://settings/content/camera)
2. Ensure HTTPS or localhost
3. Try different browser
4. Check if camera is in use by another app
```

**Mobile - Camera Not Working**:
```
1. Grant camera permissions in app settings
2. Test on physical device (not simulator)
3. Check AndroidManifest.xml / Info.plist
4. Restart app
```

### BLE Issues:

**BLE Not Detecting Beacon**:
```
1. Check Bluetooth is enabled
2. Grant location permissions (required for BLE on Android)
3. Ensure beacon is powered on
4. Check beacon UUID matches config
5. Move closer to beacon
6. Check RSSI threshold in config
```

**BLE Permissions Denied**:
```
Android:
1. Settings > Apps > ISAVS > Permissions
2. Enable Bluetooth and Location

iOS:
1. Settings > ISAVS > Bluetooth
2. Enable Bluetooth access
```

---

## 📱 Mobile App Sensor Fusion

The mobile app collects multiple sensor data points:

```typescript
interface SensorData {
  // Camera
  faceImage: string;           // Base64 encoded
  faceQuality: number;          // 0-1 score
  
  // BLE
  bleBeaconDetected: boolean;
  bleRSSI: number;              // Signal strength
  bleDistance: number;          // Calculated distance
  
  // Motion
  motionData: {
    accelerometer: [x, y, z];
    gyroscope: [x, y, z];
    magnetometer: [x, y, z];
  };
  
  // Barometer
  pressure: number;             // hPa
  altitude: number;             // meters
  
  // GPS
  latitude: number;
  longitude: number;
  accuracy: number;
}
```

All this data is sent to backend for validation.

---

## 🎯 Quick Start Guide

### For Web Testing:
```bash
# 1. Start backend
cd backend
python -m uvicorn app.main:app --reload --host 0.0.0.0 --port 8000

# 2. Start frontend
cd frontend
npm run dev

# 3. Test camera
# Open: http://localhost:5173/kiosk?session=<session_id>
# Click "Capture Face"
# Allow camera permissions
# Capture and submit
```

### For Mobile Testing:
```bash
# 1. Install dependencies
cd mobile
npm install

# 2. Run on Android
npx react-native run-android

# 3. Run on iOS
npx react-native run-ios

# 4. Test camera + BLE
# Navigate to verification screen
# Grant all permissions
# Position face in guide
# Check BLE status indicator
# Submit verification
```

---

## 📚 Documentation Files

- **Camera (Web)**: `frontend/src/components/WebcamCapture.tsx`
- **Camera (Mobile)**: `mobile/src/components/FaceVerificationCamera.tsx`
- **BLE Scanner**: `mobile/src/services/BLEScanner.ts`
- **BLE Beacon Manager**: `mobile/src/services/BeaconManager.ts`
- **BLE Hook**: `mobile/src/hooks/useBLEProximity.ts`
- **Sensor Validation**: `backend/app/services/sensor_validation_service.py`
- **Mobile Setup**: `mobile/SENSOR_LIBRARIES_SETUP.md`

---

## ✅ Summary

### Camera: ✅ WORKING
- Web: Fully functional webcam capture
- Mobile: Advanced camera with quality checks

### BLE: ✅ WORKING
- Scanning: Real-time beacon detection
- Validation: RSSI-based proximity check
- Optional: Works without beacon for testing

### Integration: ✅ COMPLETE
- All sensors feed into verification pipeline
- Backend validates all data points
- Sensor fusion scoring system
- Comprehensive anti-spoofing

---

**Status**: Camera and BLE are both fully implemented and working! 🎉

**Need Help?**
- Camera not working? Check permissions and browser/device settings
- BLE not detecting? Ensure beacon is configured and permissions granted
- Questions? Check the documentation files listed above
