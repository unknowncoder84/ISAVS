# Implementation Plan: ISAVS Mobile - Sensor Fusion

## Overview

This implementation plan covers the development of a React Native mobile application with hardware sensor integration for proximity and liveness verification. The plan is organized into phases: Backend Services, Mobile App Core, Sensor Integration, and Testing.

---

- [x] 1. Backend Sensor Services

  - [x] 1.1 Create SensorValidationService class



    - Implement validate_ble_proximity method with -70dBm threshold
    - Implement validate_geofence method using existing GeofenceService
    - Implement validate_barometer method with 0.5 hPa threshold
    - Implement validate_all_sensors method for multi-factor validation
    - _Requirements: 2.2, 2.3, 6.5, 7.3, 11.1_

  - [x] 1.2 Create MotionImageCorrelator class
    - Implement extract_optical_flow using OpenCV Lucas-Kanade method
    - Implement calculate_correlation using Pearson correlation coefficient
    - Implement verify_liveness with 0.7 correlation threshold
    - Handle frame timestamp alignment (±20ms tolerance)
    - _Requirements: 5.1, 5.2, 5.3, 5.4, 5.5_

  - [x] 1.3 Create BarometerService class
    - Implement pressure_to_altitude conversion (ΔH ≈ -8.5 * ΔP)
    - Implement validate_pressure_difference with 0.5 hPa threshold
    - Calculate floor-level difference from pressure
    - _Requirements: 7.1, 7.2, 7.3, 7.4_

  - [x] 1.4 Extend API endpoints for sensor data
    - Update VerifyRequest schema to include sensor data fields
    - Update VerifyResponse schema to include sensor validation results
    - Add sensor data to /verify endpoint processing
    - Store sensor metrics in attendance records
    - _Requirements: 11.1, 11.2, 11.3, 11.5_

  - [x] 1.5 Create database migration for sensor columns
    - Add sensor columns to attendance table (ble_rssi, barometric_pressure, motion_correlation, etc.)
    - Add sensor columns to attendance_sessions table (beacon_uuid, teacher_barometric_pressure)
    - Create sensor_anomalies table for detailed logging
    - Create indexes for sensor queries
    - _Requirements: 11.5, 2.5, 7.5_

  - [x] 1.6 Write property test for RSSI threshold
    - **Property 1: RSSI threshold enforcement**
    - **Validates: Requirements 1.4, 1.5, 2.3, 2.4**

  - [x] 1.7 Write property test for motion correlation
    - **Property 9: Motion-image correlation threshold**
    - **Validates: Requirements 5.3, 5.4**

  - [x] 1.8 Write property test for barometer validation
    - **Property 13: Barometric pressure threshold**
    - **Validates: Requirements 7.4**



- [x] 2. React Native Project Setup

  - [x] 2.1 Initialize React Native project
    - Create new React Native project with TypeScript template
    - Configure iOS and Android build settings
    - Set up folder structure (src/components, src/services, src/hooks, src/types)
    - Install core dependencies (react-navigation, axios, async-storage)
    - _Requirements: 8.1, 13.1_

  - [ ] 2.2 Install sensor libraries (MANUAL STEP REQUIRED)
    - Install react-native-ble-manager for BLE
    - Install react-native-sensors for accelerometer/gyroscope
    - Install react-native-barometer for pressure sensor
    - Install react-native-vision-camera for high-performance camera
    - Install @react-native-community/geolocation for GPS
    - Configure iOS Info.plist and Android AndroidManifest.xml permissions
    - _Requirements: 1.1, 3.1, 4.1, 6.1, 7.1_
    - **See: mobile/SENSOR_LIBRARIES_SETUP.md for instructions**

  - [x] 2.3 Create TypeScript types and interfaces
    - Define SensorVerificationRequest interface
    - Define SensorVerificationResponse interface
    - Define BeaconData, MotionData, PressureData interfaces
    - Define ValidationResult and sensor status types
    - _Requirements: 11.1, 11.2_

  - [x] 2.4 Set up API client service
    - Create axios instance with base URL configuration
    - Implement request/response interceptors
    - Add HTTPS/TLS 1.3 enforcement
    - Implement error handling and retry logic
    - _Requirements: 10.2, 15.1_

- [x] 3. BLE Proximity Module

  - [x] 3.1 Create BLEScanner service (Student App)
    - Initialize BLE manager and request permissions
    - Implement startScanning method with beacon filtering
    - Implement stopScanning method
    - Implement getRSSI method with 3-second averaging
    - Implement getEstimatedDistance using log-distance path loss model
    - _Requirements: 1.3, 1.4, 2.1, 13.4_

  - [x] 3.2 Create BeaconManager service (Teacher App)
    - Initialize BLE peripheral mode
    - Implement startBeacon method with session UUID broadcasting
    - Implement stopBeacon method
    - Implement getBeaconStatus method
    - Handle background beacon broadcasting
    - _Requirements: 1.1, 1.2, 9.1, 9.2, 9.5_

  - [x] 3.3 Create BLEStatusIndicator component
    - Display "Searching for Classroom Signal..." when scanning
    - Display "Classroom Detected ✓" when RSSI > -70dBm
    - Display RSSI value and estimated distance
    - Show animated spinner during scanning
    - _Requirements: 1.5, 1.6, 8.2, 8.3, 14.1_

  - [x] 3.4 Implement RSSI-based button control
    - Enable verify button when RSSI > -70dBm
    - Disable verify button when RSSI <= -70dBm
    - Update button color (green when enabled, gray when disabled)
    - Display proximity message based on RSSI
    - _Requirements: 1.5, 1.6, 8.5, 14.1_

  - [ ] 3.5 Write property test for RSSI-to-distance conversion
    - **Property 2: RSSI-to-distance conversion**
    - **Validates: Requirements 1.3, 2.1**

  - [ ] 3.6 Write unit tests for BLE scanner
    - Test beacon detection and filtering
    - Test RSSI averaging over 3 seconds
    - Test distance calculation accuracy
    - Test permission handling
    - _Requirements: 1.3, 1.4, 13.4_

- [x] 4. Motion Sensor Module

  - [x] 4.1 Create MotionSensorManager service
    - Implement startRecording method with 50Hz sampling rate
    - Implement stopRecording method returning MotionData
    - Implement detectNod method (z-axis acceleration > 0.5 m/s²)
    - Implement detectShake method (y-axis angular velocity > 0.3 rad/s)
    - _Requirements: 3.1, 3.3, 4.1, 4.3, 13.1_

  - [x] 4.2 Create MotionPrompt component
    - Display "Nod your head gently" with animation
    - Show real-time motion detection feedback
    - Display progress bar for 2-second collection
    - Show checkmark when sufficient motion detected
    - _Requirements: 3.2, 8.2, 14.2, 14.3_

  - [x] 4.3 Implement motion data batching
    - Collect exactly 100 samples (2 seconds at 50Hz)
    - Synchronize accelerometer and gyroscope timestamps
    - Validate sampling rate (50Hz ± 5Hz)
    - Compress data for transmission
    - _Requirements: 3.1, 3.4, 4.1, 4.5_

  - [x] 4.4 Create MotionVisualizer component (debug mode)
    - Display real-time accelerometer graph
    - Display real-time gyroscope graph
    - Show detected motion events
    - Display sampling rate and data quality
    - _Requirements: 14.2, 14.3_

  - [ ] 4.5 Write property test for accelerometer sampling rate
    - **Property 4: Accelerometer sampling rate**
    - **Validates: Requirements 3.1, 18.2**

  - [ ] 4.6 Write property test for gyroscope sampling rate
    - **Property 5: Gyroscope sampling rate**
    - **Validates: Requirements 4.1, 18.2**

  - [ ] 4.7 Write property test for nod detection
    - **Property 6: Nod detection threshold**
    - **Validates: Requirements 3.3**

  - [ ] 4.8 Write property test for shake detection
    - **Property 7: Shake detection threshold**
    - **Validates: Requirements 4.3**

- [x] 5. GPS + Barometer Module

  - [x] 5.1 Create BarometerService (Mobile App)
    - Initialize barometer sensor
    - Implement getCurrentPressure method
    - Implement startMonitoring method
    - Handle sensor unavailability gracefully
    - Apply device-specific calibration if available
    - _Requirements: 7.1, 7.2, 13.3_

  - [x] 5.2 Create EnhancedGeolocationService
    - Extend existing geolocation with barometer data
    - Implement getCurrentLocation with pressure reading
    - Validate GPS accuracy (< 20 meters)
    - Handle location permission requests
    - _Requirements: 6.3, 6.4, 14.4_

  - [x] 5.3 Create LocationStatusIndicator component
    - Display "Acquiring GPS..." when searching
    - Display "Location Verified ✓" when GPS acquired
    - Display "Pressure Verified ✓" when barometer ready
    - Show GPS accuracy and distance from classroom
    - _Requirements: 8.4, 14.4_

  - [x] 5.4 Implement dual geofence validation
    - Validate GPS distance <= 50 meters
    - Validate pressure difference <= 0.5 hPa
    - Display specific failure reason (GPS or pressure)
    - Log geofence and barometer violations separately
    - _Requirements: 6.5, 7.4, 7.5, 11.3_

  - [ ] 5.5 Write property test for GPS distance calculation
    - **Property 11: GPS distance calculation**
    - **Validates: Requirements 6.3**

  - [ ] 5.6 Write property test for pressure-to-altitude conversion
    - **Property 14: Pressure-to-altitude conversion**
    - **Validates: Requirements 7.3**

- [x] 6. Camera and Video Capture

  - [x] 6.1 Create CameraService with react-native-vision-camera
    - Initialize camera with high-performance settings
    - Implement captureFrames method (capture 10 frames over 2 seconds)
    - Implement getFrameTimestamps method
    - Compress frames for transmission
    - _Requirements: 5.1, 5.5_

  - [x] 6.2 Create FaceVerificationCamera component
    - Display live camera preview
    - Show face detection overlay
    - Capture frames during motion recording
    - Display frame count progress
    - _Requirements: 5.1, 8.2, 14.2_

  - [x] 6.3 Implement frame-motion synchronization
    - Align frame timestamps with motion data timestamps
    - Ensure ±20ms tolerance for correlation
    - Validate timestamp monotonicity
    - _Requirements: 5.5, 4.5_

  - [ ] 6.4 Write property test for frame-motion alignment
    - **Property 10: Frame-motion timestamp alignment**
    - **Validates: Requirements 3.4, 4.4**

- [x] 7. Sensor Fusion and Verification Flow

  - [x] 7.1 Create SensorStatusManager
    - Track status of all sensors (BLE, GPS, Barometer, Motion, Camera)
    - Implement getSensorReadiness method
    - Implement onSensorStatusChange callback
    - Determine when verify button should be enabled
    - _Requirements: 8.1, 8.5, 11.1_

  - [x] 7.2 Create VerificationScreen (Student App)
    - Display sensor status indicators
    - Show BLE proximity status
    - Show GPS/barometer status
    - Show motion detection prompt
    - Display verify button with dynamic state
    - Integrate all sensor collection (Motion, GPS, Barometer, Camera)
    - _Requirements: 8.1, 8.2, 8.3, 8.4, 8.5, 8.6_

  - [x] 7.3 Implement verification submission flow
    - Collect all sensor data (BLE, GPS, Barometer, Motion, Frames)
    - Validate data completeness before submission
    - Submit SensorVerificationRequest to backend
    - Handle response and display results
    - _Requirements: 11.1, 11.2, 11.3_

  - [x] 7.4 Create VerificationResultScreen
    - Display overall success/failure
    - Show detailed factor breakdown (Face, ID, OTP, BLE, GPS, Barometer, Motion, Emotion)
    - Highlight failed factors in red
    - Display specific failure messages
    - _Requirements: 11.3, 11.4, 14.5_

  - [ ] 7.5 Write property test for multi-sensor validation
    - **Property 18: All sensors validated**
    - **Validates: Requirements 9.1**

  - [ ] 7.6 Write property test for sensor failure specificity
    - **Property 19: Sensor failure specificity**
    - **Validates: Requirements 9.3, 13.5**

- [ ] 8. Teacher App Components

  - [ ] 8.1 Create TeacherSessionScreen
    - Display "Start Session" button
    - Capture classroom GPS coordinates on session start
    - Capture classroom barometric pressure on session start
    - Start BLE beacon broadcasting
    - Display beacon status and connected students count
    - _Requirements: 9.1, 9.2, 6.1, 6.2, 7.2_

  - [ ] 8.2 Create BeaconStatusCard component
    - Display "Beacon Active" with signal icon
    - Show session UUID and beacon UUID
    - Display RSSI range and estimated coverage
    - Show battery level warning if low
    - _Requirements: 9.2, 9.3_

  - [ ] 8.3 Create SessionControlPanel component
    - Display "Stop Session" button
    - Show session duration timer
    - Display real-time student check-ins
    - Show sensor validation statistics
    - _Requirements: 9.4, 9.5_

  - [ ] 8.4 Implement background beacon broadcasting
    - Keep beacon active when app is in background
    - Handle iOS background limitations
    - Display persistent notification on Android
    - _Requirements: 9.5_

- [ ] 9. Error Handling and Fallbacks

  - [ ] 9.1 Implement sensor unavailability handling
    - Detect missing sensors on app launch
    - Display specific error messages for each sensor
    - Implement BLE → GPS fallback
    - Implement Motion → Emotion fallback
    - _Requirements: 13.1, 13.2, 15.1, 15.3_

  - [ ] 9.2 Create PermissionManager service
    - Request Bluetooth permission
    - Request Location permission
    - Request Camera permission
    - Request Motion permission (iOS)
    - Provide "Open Settings" deep links
    - _Requirements: 13.1, 13.2_

  - [ ] 9.3 Create SensorErrorScreen
    - Display missing sensor warnings
    - Show permission denial messages
    - Provide "Retry" and "Open Settings" buttons
    - Explain fallback modes
    - _Requirements: 13.2, 14.1_

  - [ ] 9.4 Implement degraded mode
    - Activate when 2+ sensors fail
    - Require faculty manual approval
    - Log degraded mode events
    - Display warning to student
    - _Requirements: 15.5_

  - [ ] 9.5 Write property test for BLE fallback
    - **Property 21: BLE fallback to GPS**
    - **Validates: Requirements 15.1**

  - [ ] 9.6 Write property test for motion fallback
    - **Property 22: Motion fallback to emotion**
    - **Validates: Requirements 15.3**

- [ ] 10. Offline Support and Caching

  - [ ] 10.1 Create OfflineStorageService
    - Implement cacheVerificationRequest method
    - Implement getCachedRequests method
    - Implement clearCache method
    - Use AsyncStorage for persistence
    - _Requirements: 12.1, 12.2_

  - [ ] 10.2 Implement network connectivity monitoring
    - Detect network status changes
    - Auto-submit cached requests when online
    - Display offline indicator in UI
    - _Requirements: 12.2, 12.3_

  - [ ] 10.3 Create OfflineQueueManager
    - Queue verification requests when offline
    - Retry failed submissions
    - Validate timestamp freshness before submission
    - Handle session expiration
    - _Requirements: 12.2, 12.3, 12.4, 12.5_

  - [ ] 10.4 Write unit tests for offline caching
    - Test cache storage and retrieval
    - Test auto-submission on reconnect
    - Test session expiration handling
    - _Requirements: 12.1, 12.2, 12.3_

- [ ] 11. UI/UX Polish

  - [ ] 11.1 Create SensorStatusBar component
    - Display all sensor statuses in a compact bar
    - Use color coding (green=ready, yellow=searching, red=failed)
    - Show icons for each sensor
    - Animate status changes
    - _Requirements: 8.1, 8.2, 8.3, 8.4_

  - [ ] 11.2 Create ProximityFeedback component
    - Display distance estimate from beacon
    - Show "Move closer" or "Move away" suggestions
    - Animate proximity indicator
    - _Requirements: 14.1, 14.2_

  - [ ] 11.3 Create MotionFeedbackAnimation
    - Show animated head nodding example
    - Display real-time motion detection
    - Show progress bar for motion collection
    - _Requirements: 14.2, 14.3_

  - [ ] 11.4 Implement haptic feedback
    - Vibrate on successful sensor detection
    - Vibrate on verification success/failure
    - Provide tactile feedback for button presses
    - _Requirements: 8.6, 14.5_

  - [ ] 11.5 Write property test for button state
    - **Property 24: Button state based on RSSI**
    - **Validates: Requirements 1.4, 1.5, 12.4**

  - [ ] 11.6 Write property test for UI update latency
    - **Property 25: Sensor status display**
    - **Validates: Requirements 12.1, 12.2, 12.3**

- [ ] 12. Security and Privacy

  - [ ] 12.1 Implement HTTPS/TLS enforcement
    - Configure axios to require TLS 1.3
    - Implement certificate pinning
    - Validate SSL certificates
    - _Requirements: 10.2, 19.1_

  - [ ] 12.2 Implement GPS anonymization
    - Reduce GPS precision to 4 decimal places (10m accuracy)
    - Strip metadata from location data
    - _Requirements: 10.3, 19.2_

  - [ ] 12.3 Implement sensor data encryption
    - Encrypt sensor data before transmission
    - Use AES-256 for local storage
    - Implement secure key management
    - _Requirements: 10.2, 19.1_

  - [ ] 12.4 Create DataRetentionService (Backend)
    - Implement 30-day data retention policy
    - Schedule automatic deletion of old sensor data
    - Retain only aggregated metrics
    - _Requirements: 10.4, 19.4_

  - [ ] 12.5 Write property test for GPS anonymization
    - **Property 27: GPS anonymization**
    - **Validates: Requirements 19.2**

  - [ ] 12.6 Write property test for HTTPS encryption
    - **Property 26: HTTPS encryption**
    - **Validates: Requirements 19.1**

- [ ] 13. Performance Optimization

  - [ ] 13.1 Optimize BLE scanning
    - Implement scan interval optimization (scan 5s, pause 2s)
    - Filter beacons by UUID to reduce processing
    - Batch RSSI measurements for averaging
    - _Requirements: 15.1, 15.2_

  - [ ] 13.2 Optimize motion data collection
    - Use native sensor APIs for better performance
    - Implement data compression before transmission
    - Reduce memory footprint during collection
    - _Requirements: 15.2, 15.3_

  - [ ] 13.3 Optimize battery usage
    - Stop sensors when not in use
    - Use low-power sensor modes
    - Implement adaptive sampling rates
    - Monitor battery drain during verification
    - _Requirements: 15.4_

  - [ ] 13.4 Implement backend processing optimization
    - Use NumPy vectorization for correlation calculation
    - Implement parallel processing for optical flow
    - Cache intermediate results
    - Set 3-second timeout for verification
    - _Requirements: 15.1, 15.2, 15.3, 15.4_

  - [ ] 13.5 Write performance tests
    - Test BLE scan latency (< 2 seconds)
    - Test motion collection duration (exactly 2 seconds)
    - Test correlation calculation (< 500ms)
    - Test battery drain (< 5% per session)
    - _Requirements: 15.1, 15.2, 15.3, 15.4_

- [ ] 14. Integration Testing

  - [ ] 14.1 Create end-to-end test suite
    - Test happy path (all sensors pass)
    - Test weak BLE signal rejection
    - Test out-of-geofence rejection
    - Test wrong floor rejection
    - Test motion spoofing detection
    - Test sensor fallback modes
    - _Requirements: All_

  - [ ] 14.2 Create mock sensor data generators
    - Generate mock BLE beacons
    - Generate mock accelerometer/gyroscope data
    - Generate mock GPS coordinates
    - Generate mock barometer readings
    - _Requirements: Testing_

  - [ ] 14.3 Implement automated UI testing
    - Test sensor status display updates
    - Test button enable/disable logic
    - Test verification flow navigation
    - Test error message display
    - _Requirements: 8.1-8.6, 14.1-14.5_

  - [ ] 14.4 Write property test for timestamp monotonicity
    - **Property 17: Timestamp monotonicity**
    - **Validates: Requirements 8.4**

  - [ ] 14.5 Write property test for sensor data persistence
    - **Property 20: Sensor data persistence**
    - **Validates: Requirements 9.4, 14.1**

- [ ] 15. Documentation and Deployment

  - [ ] 15.1 Create mobile app setup guide
    - Document React Native installation
    - Document iOS/Android build instructions
    - Document sensor library configuration
    - Document permission setup
    - _Requirements: Documentation_

  - [ ] 15.2 Create sensor calibration guide
    - Document RSSI calibration procedure
    - Document barometer calibration
    - Document motion threshold tuning
    - _Requirements: 13.3, 13.4_

  - [ ] 15.3 Create deployment guide
    - Document iOS App Store submission
    - Document Android Play Store submission
    - Document backend API deployment
    - Document database migration
    - _Requirements: Deployment_

  - [ ] 15.4 Create user manual
    - Document student app usage
    - Document teacher app usage
    - Document troubleshooting steps
    - Document sensor requirements
    - _Requirements: Documentation_

- [ ] 16. Final Checkpoint
  - Ensure all tests pass
  - Verify sensor accuracy across devices
  - Test on multiple iOS and Android devices
  - Validate battery usage is acceptable
  - Confirm all security measures are in place
  - Ask the user if questions arise

