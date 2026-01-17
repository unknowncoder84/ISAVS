# Sensor Libraries Setup Guide

This guide covers Task 2.2: Install sensor libraries for ISAVS Mobile.

## 📦 Installation Commands

Run these commands in the `mobile/` directory:

```bash
# Core sensor libraries
npm install react-native-ble-manager
npm install react-native-sensors
npm install react-native-barometer
npm install react-native-vision-camera
npm install @react-native-community/geolocation

# Additional dependencies
npm install react-native-permissions
npm install babel-plugin-module-resolver

# iOS only: Install pods
cd ios && pod install && cd ..
```

## 📱 iOS Configuration

### Info.plist Permissions

Add to `ios/ISAVSMobile/Info.plist`:

```xml
<!-- Bluetooth -->
<key>NSBluetoothAlwaysUsageDescription</key>
<string>We need Bluetooth to detect classroom proximity for attendance verification</string>
<key>NSBluetoothPeripheralUsageDescription</key>
<string>We need Bluetooth to broadcast classroom beacon (Teacher app)</string>

<!-- Location -->
<key>NSLocationWhenInUseUsageDescription</key>
<string>We need your location to verify you are in the classroom</string>
<key>NSLocationAlwaysUsageDescription</key>
<string>We need your location to verify classroom attendance</string>
<key>NSLocationAlwaysAndWhenInUseUsageDescription</key>
<string>We need your location to verify classroom attendance</string>

<!-- Camera -->
<key>NSCameraUsageDescription</key>
<string>We need camera access for face verification and liveness detection</string>

<!-- Motion -->
<key>NSMotionUsageDescription</key>
<string>We need motion sensors for liveness detection</string>
```

### Podfile Configuration

Ensure `ios/Podfile` includes:

```ruby
platform :ios, '13.0'

target 'ISAVSMobile' do
  config = use_native_modules!

  use_react_native!(
    :path => config[:reactNativePath],
    :hermes_enabled => true
  )

  # Permissions
  permissions_path = '../node_modules/react-native-permissions/ios'
  pod 'Permission-BluetoothPeripheral', :path => "#{permissions_path}/BluetoothPeripheral"
  pod 'Permission-Camera', :path => "#{permissions_path}/Camera"
  pod 'Permission-LocationWhenInUse', :path => "#{permissions_path}/LocationWhenInUse"
  pod 'Permission-Motion', :path => "#{permissions_path}/Motion"

  post_install do |installer|
    installer.pods_project.targets.each do |target|
      target.build_configurations.each do |config|
        config.build_settings['IPHONEOS_DEPLOYMENT_TARGET'] = '13.0'
      end
    end
  end
end
```

## 🤖 Android Configuration

### AndroidManifest.xml Permissions

Add to `android/app/src/main/AndroidManifest.xml`:

```xml
<manifest xmlns:android="http://schemas.android.com/apk/res/android">

    <!-- Bluetooth -->
    <uses-permission android:name="android.permission.BLUETOOTH"/>
    <uses-permission android:name="android.permission.BLUETOOTH_ADMIN"/>
    <uses-permission android:name="android.permission.BLUETOOTH_SCAN"
                     android:usesPermissionFlags="neverForLocation" />
    <uses-permission android:name="android.permission.BLUETOOTH_CONNECT"/>
    
    <!-- Location (required for BLE on Android) -->
    <uses-permission android:name="android.permission.ACCESS_FINE_LOCATION"/>
    <uses-permission android:name="android.permission.ACCESS_COARSE_LOCATION"/>
    
    <!-- Camera -->
    <uses-permission android:name="android.permission.CAMERA"/>
    
    <!-- Internet -->
    <uses-permission android:name="android.permission.INTERNET"/>
    
    <!-- Sensors -->
    <uses-feature android:name="android.hardware.sensor.accelerometer" android:required="false"/>
    <uses-feature android:name="android.hardware.sensor.gyroscope" android:required="false"/>
    <uses-feature android:name="android.hardware.sensor.barometer" android:required="false"/>
    <uses-feature android:name="android.hardware.bluetooth_le" android:required="false"/>

    <application>
        <!-- ... -->
    </application>
</manifest>
```

### build.gradle Configuration

Update `android/app/build.gradle`:

```gradle
android {
    compileSdkVersion 34
    
    defaultConfig {
        applicationId "com.isavsmobile"
        minSdkVersion 24
        targetSdkVersion 34
        versionCode 1
        versionName "1.0"
    }
}

dependencies {
    implementation "com.facebook.react:react-native:+"
    
    // BLE
    implementation "com.polidea.rxandroidble2:rxandroidble:1.17.2"
    
    // Camera
    implementation "androidx.camera:camera-camera2:1.3.0"
    implementation "androidx.camera:camera-lifecycle:1.3.0"
    implementation "androidx.camera:camera-view:1.3.0"
}
```

## ✅ Verification

After installation, verify each library:

### Test BLE
```typescript
import BleManager from 'react-native-ble-manager';

BleManager.start({showAlert: false}).then(() => {
  console.log('BLE initialized');
});
```

### Test Motion Sensors
```typescript
import {accelerometer, gyroscope} from 'react-native-sensors';

accelerometer.subscribe(({x, y, z}) => {
  console.log(`Accel: ${x}, ${y}, ${z}`);
});
```

### Test Barometer
```typescript
import Barometer from 'react-native-barometer';

Barometer.getPressure().then((pressure) => {
  console.log(`Pressure: ${pressure} hPa`);
});
```

### Test Camera
```typescript
import {Camera} from 'react-native-vision-camera';

const devices = await Camera.getAvailableCameraDevices();
console.log(`Found ${devices.length} cameras`);
```

### Test GPS
```typescript
import Geolocation from '@react-native-community/geolocation';

Geolocation.getCurrentPosition(
  (position) => {
    console.log(`Location: ${position.coords.latitude}, ${position.coords.longitude}`);
  },
  (error) => console.error(error),
  {enableHighAccuracy: true}
);
```

## 🐛 Common Issues

### Issue: BLE not working on Android
**Solution**: Ensure location permission is granted (required for BLE on Android)

### Issue: Camera not working
**Solution**: Check camera permission in app settings

### Issue: Barometer returns null
**Solution**: Not all devices have barometer sensors. Implement fallback.

### Issue: iOS build fails
**Solution**: Run `cd ios && pod install && cd ..`

## 📚 Documentation Links

- [react-native-ble-manager](https://github.com/innoveit/react-native-ble-manager)
- [react-native-sensors](https://github.com/react-native-sensors/react-native-sensors)
- [react-native-vision-camera](https://github.com/mrousavy/react-native-vision-camera)
- [react-native-permissions](https://github.com/zoontek/react-native-permissions)

## ✅ Task 2.2 Completion Checklist

- [ ] All npm packages installed
- [ ] iOS Info.plist permissions added
- [ ] iOS Podfile configured
- [ ] iOS pods installed
- [ ] Android AndroidManifest.xml permissions added
- [ ] Android build.gradle configured
- [ ] All sensors tested and working
- [ ] No build errors

Once complete, mark Task 2.2 as done in tasks.md!
