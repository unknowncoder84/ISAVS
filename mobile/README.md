# ISAVS Mobile - Sensor Fusion Attendance System

React Native mobile application for 8-factor biometric attendance verification with hardware sensor integration.

## 🎯 Features

- **8-Factor Authentication**:
  1. Face Recognition (0.6 threshold)
  2. ID Card Verification
  3. OTP (4-digit, 5-min TTL)
  4. GPS Geofence (50m radius)
  5. BLE Proximity (RSSI > -70 dBm)
  6. Barometric Pressure (0.5 hPa threshold)
  7. Motion-Image Correlation (0.7 correlation)
  8. Emotion Detection (Smile-to-verify)

- **Hardware Sensors**:
  - Bluetooth Low Energy (BLE) for proximity detection
  - Accelerometer + Gyroscope for motion tracking
  - Barometer for floor-level detection
  - GPS for geofencing
  - Camera for face verification and optical flow

## 📦 Installation

### Prerequisites
- Node.js >= 18
- React Native CLI
- Xcode (for iOS)
- Android Studio (for Android)

### Setup

```bash
# Install dependencies
npm install

# iOS: Install pods
cd ios && pod install && cd ..

# Run on Android
npm run android

# Run on iOS
npm run ios
```

## 🔧 Configuration

### Backend API URL

Update `src/constants/config.ts`:

```typescript
export const APP_CONFIG: AppConfig = {
  apiBaseUrl: 'http://your-backend-url:8000',
  // ...
};
```

### Sensor Libraries

See `SENSOR_LIBRARIES_SETUP.md` for detailed installation instructions.

## 📱 Permissions

### iOS (Info.plist)
- Bluetooth
- Location (When In Use & Always)
- Camera
- Motion

### Android (AndroidManifest.xml)
- Bluetooth & Bluetooth Admin
- Location (Fine & Coarse)
- Camera
- Internet

See template files in `ios/` and `android/` directories.

## 🏗️ Project Structure

```
mobile/
├── src/
│   ├── components/      # React components
│   ├── services/        # Business logic
│   │   └── api.ts      # API client
│   ├── hooks/           # Custom hooks
│   ├── types/           # TypeScript types
│   │   └── index.ts    # Type definitions
│   ├── screens/         # Screen components
│   ├── navigation/      # Navigation config
│   ├── utils/           # Utilities
│   └── constants/       # Configuration
│       └── config.ts   # App config
├── android/             # Android native
├── ios/                 # iOS native
├── App.tsx             # Root component
└── package.json
```

## 🧪 Testing

```bash
# Run tests
npm test

# Run with coverage
npm test -- --coverage
```

## 🚀 Build

### Android
```bash
cd android
./gradlew assembleRelease
```

### iOS
```bash
cd ios
xcodebuild -workspace ISAVSMobile.xcworkspace -scheme ISAVSMobile -configuration Release
```

## 📊 Sensor Thresholds

| Sensor | Threshold | Description |
|--------|-----------|-------------|
| BLE RSSI | -70 dBm | Proximity detection |
| GPS | 50 meters | Geofence radius |
| Barometer | 0.5 hPa | Floor-level detection |
| Motion Correlation | 0.7 | Liveness detection |
| Face Confidence | 0.6 | Face recognition |

## 🔍 Troubleshooting

### BLE not working
- Check Bluetooth permission
- On Android, location permission is required for BLE

### Camera not working
- Check camera permission
- Ensure device has camera

### Barometer unavailable
- Not all devices have barometer sensors
- Implement fallback to GPS-only mode

### Build errors
```bash
# Clean and rebuild
npm start -- --reset-cache
cd android && ./gradlew clean && cd ..
cd ios && rm -rf Pods Podfile.lock && pod install && cd ..
```

## 📚 Documentation

- [Phase 1 Backend Complete](../PHASE_1_BACKEND_COMPLETE.md)
- [Phase 2 Getting Started](../PHASE_2_GETTING_STARTED.md)
- [Sensor Libraries Setup](./SENSOR_LIBRARIES_SETUP.md)
- [Quick Reference](../QUICK_REFERENCE_SENSOR_FUSION.md)

## 🎓 Development Status

**Phase 2: React Native Project Setup** ✅
- [x] 2.1 Initialize React Native project
- [ ] 2.2 Install sensor libraries (See SENSOR_LIBRARIES_SETUP.md)
- [x] 2.3 Create TypeScript types
- [x] 2.4 Set up API client service

**Next**: Phase 3 - BLE Proximity Module

## 📞 Support

For issues or questions, refer to:
- Task list: `.kiro/specs/isavs-mobile-sensor-fusion/tasks.md`
- Design doc: `.kiro/specs/isavs-mobile-sensor-fusion/design.md`
- Requirements: `.kiro/specs/isavs-mobile-sensor-fusion/requirements.md`

## 📄 License

Proprietary - ISAVS 2026

---

**Version**: 1.0.0  
**Last Updated**: January 17, 2026  
**Status**: Phase 2 Setup Complete (3/4 tasks)
