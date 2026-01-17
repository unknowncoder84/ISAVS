# 🚀 Quick Start: Testing ISAVS Mobile

**Status**: Ready for npm install and device testing  
**Time Required**: 2-3 hours

---

## ⚡ Quick Commands

### 1. Install Dependencies (10 min)
```bash
cd mobile
npm install react-native-ble-manager react-native-sensors react-native-barometer react-native-vision-camera @react-native-community/geolocation react-native-permissions react-native-fs
cd ios && pod install && cd ..
```

### 2. Run on Device (5 min)

**iOS**:
```bash
npx react-native run-ios --device
```

**Android**:
```bash
npx react-native run-android
```

---

## ✅ Testing Checklist

### Sensor Initialization (30 sec)
- [ ] BLE: "Searching for Classroom Signal..."
- [ ] GPS: "Acquiring GPS..."
- [ ] Barometer: "Reading Pressure..."
- [ ] Motion: "Checking Sensors..."
- [ ] Camera: "Checking Permission..."

### Sensor Ready (5-10 sec)
- [ ] BLE: "Classroom Detected ✓" (green)
- [ ] GPS: "Location Verified ✓" (green)
- [ ] Barometer: "Pressure Verified ✓" (green)
- [ ] Motion: "Ready ✓" (green)
- [ ] Camera: "Ready ✓" (green)

### Verify Button
- [ ] Button turns green when all sensors ready
- [ ] Button shows "Verify Attendance"

### Motion Collection (2 sec)
- [ ] Motion prompt appears
- [ ] "Nod your head gently" message
- [ ] Progress bar fills 0-100%
- [ ] Checkmark when complete

### Camera Capture (2 sec)
- [ ] Camera preview appears
- [ ] Face guide overlay visible
- [ ] Frame count: 1/10, 2/10, ... 10/10
- [ ] Preview closes automatically

### Submission
- [ ] "Verifying..." message
- [ ] Loading indicator
- [ ] Result screen appears

### Result Screen
- [ ] Overall status: Success ✓ or Failed ✗
- [ ] 8 factors displayed:
  - [ ] Face Match
  - [ ] Student ID
  - [ ] OTP
  - [ ] BLE Proximity
  - [ ] GPS Location
  - [ ] Barometer
  - [ ] Motion Liveness
  - [ ] Emotion

---

## 🐛 Common Issues

### Issue: BLE not detecting beacon
**Solution**: 
1. Ensure teacher app is running and broadcasting
2. Check Bluetooth is enabled
3. Grant location permission (Android requirement)

### Issue: GPS not acquiring
**Solution**:
1. Go outdoors or near window
2. Wait 30-60 seconds
3. Check location permission granted

### Issue: Barometer shows "Unavailable"
**Solution**: 
- Not all devices have barometer
- This is expected, system will use GPS-only fallback

### Issue: Motion sensors not ready
**Solution**:
1. Check motion permission (iOS)
2. Restart app
3. Check device has accelerometer/gyroscope

### Issue: Camera permission denied
**Solution**:
1. Go to Settings → App → Permissions
2. Enable Camera permission
3. Restart app

---

## 📊 Expected Values

### BLE
- **RSSI**: -40 to -70 dBm (closer = higher)
- **Distance**: 0.5 to 5 meters
- **Threshold**: -70 dBm

### GPS
- **Accuracy**: < 20 meters
- **Distance from classroom**: < 50 meters

### Barometer
- **Pressure**: 950-1050 hPa (typical)
- **Threshold**: ±0.5 hPa from classroom

### Motion
- **Samples**: 100 (50 accel + 50 gyro)
- **Duration**: 2 seconds
- **Sampling rate**: ~50 Hz

### Camera
- **Frames**: 10
- **Duration**: 2 seconds
- **Interval**: ~200ms

---

## 🎯 Success Criteria

### Minimum Working Test
- [x] All sensors initialize
- [x] At least 3 sensors show "Ready"
- [x] Verify button enables
- [x] Motion collection completes
- [x] Camera capture completes
- [x] Submission succeeds
- [x] Result screen displays

### Full Working Test
- [x] All 5 sensors show "Ready"
- [x] BLE detects classroom beacon
- [x] GPS within 50m of classroom
- [x] Barometer within 0.5 hPa
- [x] Motion data collected (100 samples)
- [x] Camera captures 10 frames
- [x] Backend validates all factors
- [x] Result shows 8/8 factors passed

---

## 📱 Device Requirements

### Minimum
- iOS 13+ or Android 8+
- Bluetooth 4.0+ (BLE)
- GPS
- Accelerometer + Gyroscope
- Camera

### Recommended
- iOS 15+ or Android 11+
- Bluetooth 5.0+
- High-accuracy GPS
- Barometer sensor
- Front camera with face detection

---

## 🔧 Debug Mode

### Enable Debug Logging
```typescript
// In VerificationScreen.tsx
const DEBUG = true;

if (DEBUG) {
  console.log('[Verification] Sensor data:', {
    ble: beaconData,
    gps: locationData,
    pressure: pressureData,
    motion: motionData,
    frames: videoFrames.length,
  });
}
```

### View Motion Visualizer
```typescript
// Add to VerificationScreen
import {MotionVisualizer} from '../components/MotionVisualizer';

// In render
{DEBUG && <MotionVisualizer />}
```

---

## 📞 Quick Reference

### File Locations
- **Main Screen**: `mobile/src/screens/VerificationScreen.tsx`
- **Services**: `mobile/src/services/`
- **Components**: `mobile/src/components/`
- **Types**: `mobile/src/types/index.ts`
- **Config**: `mobile/src/constants/config.ts`

### Key Services
```typescript
import {getBLEScanner} from './services/BLEScanner';
import {getMotionSensorManager} from './services/MotionSensorManager';
import {getEnhancedGeolocationService} from './services/EnhancedGeolocationService';
import {getCameraService} from './services/CameraService';
import {getVerificationService} from './services/VerificationService';
```

### Configuration
```typescript
// mobile/src/constants/config.ts
export const APP_CONFIG = {
  bleRSSIThreshold: -70,        // dBm
  geofenceRadius: 50,           // meters
  barometerThreshold: 0.5,      // hPa
  motionSamplingRate: 50,       // Hz
  motionDuration: 2000,         // ms
  frameCaptureCount: 10,        // frames
  frameCaptureInterval: 200,    // ms
};
```

---

## ✅ Next Steps After Testing

### If Tests Pass
1. Implement Teacher app (Phase 8)
2. Add error handling (Phase 9)
3. Add offline support (Phase 10)
4. Polish UI (Phase 11)

### If Tests Fail
1. Check console logs
2. Verify permissions granted
3. Check sensor availability
4. Test individual sensors
5. Review error messages

---

## 🎉 You're Ready!

**Command to start**:
```bash
cd mobile && npm install
```

**Then**: Build, deploy, and test!

---

**Good luck! 🚀**
