# 🚀 Phase 2 Complete - Quick Start Guide

**Status**: Phase 2 is 75% complete (3/4 tasks done)  
**Next**: Install sensor libraries, then proceed to Phase 3

---

## ✅ What's Done

1. ✅ **React Native project initialized** (`mobile/` directory)
2. ✅ **TypeScript types created** (`mobile/src/types/index.ts`)
3. ✅ **API client service ready** (`mobile/src/services/api.ts`)
4. ⏳ **Sensor libraries** (instructions provided, needs manual install)

---

## 📦 Complete Task 2.2: Install Sensor Libraries

### Quick Install
```bash
cd mobile

# Install all sensor libraries
npm install \
  react-native-ble-manager \
  react-native-sensors \
  react-native-barometer \
  react-native-vision-camera \
  @react-native-community/geolocation \
  react-native-permissions \
  babel-plugin-module-resolver

# iOS: Install pods
cd ios && pod install && cd ..

# Test build
npm run android  # or npm run ios
```

### Configure Permissions

**iOS**: Copy `mobile/ios/Info.plist.template` content to your `Info.plist`

**Android**: Copy `mobile/android/app/src/main/AndroidManifest.xml.template` content to your `AndroidManifest.xml`

**Full instructions**: See `mobile/SENSOR_LIBRARIES_SETUP.md`

---

## 🎯 Phase 3 Preview: BLE Proximity Module

Once Task 2.2 is complete, you'll implement:

### Task 3.1: BLEScanner Service (Student App)
```typescript
// mobile/src/services/BLEScanner.ts
class BLEScanner {
  async startScanning(): Promise<void>
  async stopScanning(): Promise<void>
  async getRSSI(beaconUUID: string): Promise<number>
  getEstimatedDistance(rssi: number): number
}
```

### Task 3.2: BeaconManager Service (Teacher App)
```typescript
// mobile/src/services/BeaconManager.ts
class BeaconManager {
  async startBeacon(sessionUUID: string): Promise<void>
  async stopBeacon(): Promise<void>
  getBeaconStatus(): BeaconStatus
}
```

### Task 3.3: BLEStatusIndicator Component
```typescript
// mobile/src/components/BLEStatusIndicator.tsx
<BLEStatusIndicator
  rssi={-65}
  threshold={-70}
  distance={5.2}
  status="ready"
/>
```

---

## 📁 Project Structure

```
mobile/
├── src/
│   ├── types/
│   │   └── index.ts           ✅ Complete
│   ├── services/
│   │   ├── api.ts             ✅ Complete
│   │   ├── BLEScanner.ts      📋 Phase 3
│   │   ├── BeaconManager.ts   📋 Phase 3
│   │   └── ...                📋 Future phases
│   ├── components/
│   │   ├── BLEStatusIndicator.tsx  📋 Phase 3
│   │   └── ...                📋 Future phases
│   └── constants/
│       └── config.ts          ✅ Complete
├── App.tsx                    ✅ Complete
├── package.json               ✅ Complete
└── README.md                  ✅ Complete
```

---

## 🔧 Configuration

### Update Backend URL

Edit `mobile/src/constants/config.ts`:

```typescript
export const APP_CONFIG: AppConfig = {
  apiBaseUrl: 'http://YOUR_BACKEND_IP:8000',  // ← Change this
  // ...
};
```

### Test API Connection

```typescript
import apiClient from './src/services/api';

// Test health check
const isHealthy = await apiClient.healthCheck();
console.log('Backend healthy:', isHealthy);

// Test OTP fetch
const otp = await apiClient.getOTP('session-id', 'student-id');
console.log('OTP:', otp);
```

---

## 📊 Progress Tracker

### Phase 1: Backend ✅ (100%)
- [x] SensorValidationService
- [x] MotionImageCorrelator
- [x] BarometerService
- [x] Database migration
- [x] Property-based tests

### Phase 2: React Native Setup ⏳ (75%)
- [x] Project initialization
- [ ] Sensor libraries ← **YOU ARE HERE**
- [x] TypeScript types
- [x] API client

### Phase 3: BLE Module 📋 (0%)
- [ ] BLEScanner service
- [ ] BeaconManager service
- [ ] BLEStatusIndicator component
- [ ] RSSI-based button control
- [ ] Property tests
- [ ] Unit tests

---

## 🐛 Common Issues

### Issue: npm install fails
```bash
# Clear cache
npm cache clean --force
rm -rf node_modules package-lock.json
npm install
```

### Issue: iOS build fails
```bash
cd ios
rm -rf Pods Podfile.lock
pod install
cd ..
```

### Issue: Android build fails
```bash
cd android
./gradlew clean
cd ..
```

---

## 📚 Documentation

- **Setup Guide**: `mobile/SENSOR_LIBRARIES_SETUP.md`
- **Project README**: `mobile/README.md`
- **Phase 1 Complete**: `PHASE_1_BACKEND_COMPLETE.md`
- **Phase 2 Complete**: `PHASE_2_SETUP_COMPLETE.md`
- **Quick Reference**: `QUICK_REFERENCE_SENSOR_FUSION.md`

---

## ✅ Checklist

Before moving to Phase 3:

- [ ] Sensor libraries installed (`npm install`)
- [ ] iOS permissions configured (Info.plist)
- [ ] Android permissions configured (AndroidManifest.xml)
- [ ] iOS pods installed (`pod install`)
- [ ] App builds successfully
- [ ] Backend URL configured
- [ ] API connection tested

---

## 🚀 Next Command

```bash
cd mobile
npm install react-native-ble-manager react-native-sensors react-native-barometer react-native-vision-camera @react-native-community/geolocation react-native-permissions babel-plugin-module-resolver
cd ios && pod install && cd ..
npm run android
```

---

**Ready to complete Phase 2 and start Phase 3!** 🎉
