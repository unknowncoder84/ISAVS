# Requirements Document: ISAVS Mobile - Sensor Fusion

## Introduction

This document specifies the requirements for adding hardware-level proximity and liveness verification to the ISAVS 2026 attendance system through a mobile application. The system will leverage smartphone sensors (BLE, Accelerometer, Gyroscope, GPS, Barometer) to create a multi-layered, sensor-fused verification system that prevents spoofing and ensures physical presence in the classroom.

## Glossary

- **BLE (Bluetooth Low Energy)**: Wireless communication technology for short-range device connectivity
- **RSSI (Received Signal Strength Indicator)**: Measurement of signal power in dBm, used to estimate distance
- **Teacher Beacon**: BLE peripheral device broadcasting classroom presence signal
- **Student App**: React Native mobile application for attendance verification
- **Accelerometer**: Sensor measuring device acceleration in 3D space (x, y, z axes)
- **Gyroscope**: Sensor measuring device rotation rate around 3D axes
- **Barometer**: Sensor measuring atmospheric pressure in hectopascals (hPa)
- **Motion-Image Correlation**: Algorithm verifying that camera movement matches sensor data
- **Sensor Fusion**: Combining data from multiple sensors for enhanced accuracy
- **Backend API**: FastAPI server processing sensor data and verification requests
- **Geofence**: Virtual perimeter defined by GPS coordinates and radius

## Requirements

### Requirement 1: BLE Proximity Detection

**User Story:** As a faculty member, I want to broadcast a classroom beacon signal, so that only students physically present in the classroom can mark attendance.

#### Acceptance Criteria

1. WHEN a faculty member starts an attendance session, THE Backend API SHALL generate a unique BLE beacon UUID for that session
2. WHEN the Teacher App broadcasts the BLE beacon, THE beacon SHALL transmit the session UUID and classroom identifier
3. WHEN the Student App scans for BLE devices, THE Student App SHALL detect all nearby beacons within range
4. WHEN the Student App detects the classroom beacon, THE Student App SHALL measure the RSSI value in dBm
5. WHEN the RSSI value is stronger than -70 dBm, THE Student App SHALL enable the verification button
6. WHEN the RSSI value is weaker than -70 dBm, THE Student App SHALL display "Searching for Classroom Signal..." and disable verification

### Requirement 2: RSSI Distance Validation

**User Story:** As a system administrator, I want to enforce proximity requirements using signal strength, so that students cannot mark attendance from outside the classroom.

#### Acceptance Criteria

1. WHEN the Student App submits verification data, THE Student App SHALL include the measured RSSI value
2. WHEN the Backend API receives RSSI data, THE Backend API SHALL validate that RSSI is stronger than -70 dBm
3. WHEN RSSI is weaker than -70 dBm, THE Backend API SHALL reject the verification with reason "Too far from classroom beacon"
4. WHEN RSSI is stronger than -70 dBm, THE Backend API SHALL proceed with additional verification factors
5. WHEN RSSI validation fails, THE Backend API SHALL log an anomaly with type "ble_proximity_violation"

### Requirement 3: Accelerometer-Based Liveness Detection

**User Story:** As a security administrator, I want to detect device motion during face verification, so that students cannot use static photos or videos for spoofing.

#### Acceptance Criteria

1. WHEN face verification begins, THE Student App SHALL start recording accelerometer data at 50Hz sampling rate
2. WHEN face verification begins, THE Student App SHALL prompt the user to "Nod your head gently"
3. WHEN the user moves the device, THE Student App SHALL capture acceleration values for x, y, and z axes
4. WHEN acceleration data is captured, THE Student App SHALL detect significant motion events with magnitude > 0.5 m/s²
5. WHEN face verification completes, THE Student App SHALL submit accelerometer data with timestamps to the Backend API

### Requirement 4: Gyroscope Motion Tracking

**User Story:** As a security administrator, I want to track device rotation during verification, so that I can correlate camera movement with sensor data.

#### Acceptance Criteria

1. WHEN face verification begins, THE Student App SHALL start recording gyroscope data at 50Hz sampling rate
2. WHEN the device rotates, THE Student App SHALL capture rotation rates for x, y, and z axes in radians per second
3. WHEN rotation data is captured, THE Student App SHALL detect rotation events with magnitude > 0.3 rad/s
4. WHEN face verification completes, THE Student App SHALL submit gyroscope data with timestamps to the Backend API
5. WHEN both accelerometer and gyroscope data are available, THE Student App SHALL synchronize timestamps for correlation

### Requirement 5: Motion-Image Correlation

**User Story:** As a system administrator, I want to verify that camera movement matches sensor motion, so that pre-recorded videos cannot be used for spoofing.

#### Acceptance Criteria

1. WHEN the Backend API receives sensor data and face images, THE Backend API SHALL extract optical flow vectors from consecutive frames
2. WHEN optical flow is calculated, THE Backend API SHALL compute camera motion direction and magnitude
3. WHEN sensor motion data is available, THE Backend API SHALL compute device motion direction and magnitude
4. WHEN both camera and sensor motion are computed, THE Backend API SHALL calculate correlation coefficient between motion vectors
5. WHEN correlation coefficient is above 0.7, THE Backend API SHALL mark liveness check as passed
6. WHEN correlation coefficient is below 0.7, THE Backend API SHALL reject verification with reason "Motion-image mismatch detected"

### Requirement 6: GPS + Barometer Dual Geofencing

**User Story:** As a faculty member, I want to verify student location using both GPS and barometric pressure, so that students on different floors cannot mark attendance.

#### Acceptance Criteria

1. WHEN an attendance session starts, THE Teacher App SHALL capture and store classroom GPS coordinates (latitude, longitude)
2. WHEN an attendance session starts, THE Teacher App SHALL capture and store classroom barometric pressure in hPa
3. WHEN the Student App submits verification, THE Student App SHALL include current GPS coordinates
4. WHEN the Student App submits verification, THE Student App SHALL include current barometric pressure
5. WHEN the Backend API validates location, THE Backend API SHALL verify GPS distance is within 50 meters using Haversine formula

### Requirement 7: Barometric Pressure Validation

**User Story:** As a security administrator, I want to validate floor-level proximity using barometric pressure, so that students on different floors are detected.

#### Acceptance Criteria

1. WHEN the Backend API receives barometric pressure data, THE Backend API SHALL calculate pressure difference between teacher and student devices
2. WHEN pressure difference is calculated, THE Backend API SHALL convert pressure difference to approximate altitude difference using formula: Δh ≈ 8.3 × Δp (meters per hPa)
3. WHEN pressure difference is within 0.5 hPa threshold, THE Backend API SHALL mark barometric check as passed
4. WHEN pressure difference exceeds 0.5 hPa threshold, THE Backend API SHALL reject verification with reason "Different floor detected"
5. WHEN barometric validation fails, THE Backend API SHALL log an anomaly with type "barometer_violation" and include altitude difference

### Requirement 8: Smooth UX with Sensor Status

**User Story:** As a student, I want to see real-time sensor status, so that I know when I can mark attendance.

#### Acceptance Criteria

1. WHEN the Student App launches, THE Student App SHALL display sensor status indicators for BLE, GPS, and Barometer
2. WHEN BLE scanning is active, THE Student App SHALL display "Searching for Classroom Signal..." with animated spinner
3. WHEN classroom beacon is detected with RSSI > -70 dBm, THE Student App SHALL display "Classroom Detected ✓" with green indicator
4. WHEN GPS location is acquired, THE Student App SHALL display "Location Verified ✓" with green indicator
5. WHEN all sensors are ready, THE Student App SHALL enable the "Verify Attendance" button with green background
6. WHEN any sensor fails, THE Student App SHALL keep the button disabled with gray background and show specific failure reason

### Requirement 9: Teacher Beacon Management

**User Story:** As a faculty member, I want to easily start and stop the classroom beacon, so that I can control when students can mark attendance.

#### Acceptance Criteria

1. WHEN the Teacher App starts a session, THE Teacher App SHALL automatically start broadcasting the BLE beacon
2. WHEN the beacon is broadcasting, THE Teacher App SHALL display "Beacon Active" with signal strength indicator
3. WHEN the Teacher App stops the session, THE Teacher App SHALL stop broadcasting the BLE beacon
4. WHEN the beacon stops, THE Teacher App SHALL display "Beacon Stopped" status
5. WHEN the Teacher App is in background, THE Teacher App SHALL continue broadcasting the beacon for session duration

### Requirement 10: Sensor Data Privacy

**User Story:** As a student, I want my sensor data to be used only for verification, so that my privacy is protected.

#### Acceptance Criteria

1. WHEN sensor data is collected, THE Student App SHALL only collect data during active verification attempts
2. WHEN sensor data is transmitted, THE Student App SHALL encrypt data using HTTPS/TLS
3. WHEN the Backend API receives sensor data, THE Backend API SHALL process data in memory without persistent storage
4. WHEN verification completes, THE Backend API SHALL discard raw sensor data and retain only verification results
5. WHEN sensor data is logged, THE Backend API SHALL store only aggregated metrics (RSSI, correlation coefficient) without raw sensor readings

### Requirement 11: Multi-Factor Sensor Verification

**User Story:** As a system administrator, I want to combine all sensor checks with existing verification factors, so that attendance marking requires comprehensive validation.

#### Acceptance Criteria

1. WHEN verification is submitted, THE Backend API SHALL validate all factors: Face, ID, OTP, GPS, Barometer, BLE, Motion-Image Correlation, Emotion
2. WHEN all factors pass, THE Backend API SHALL mark attendance as verified
3. WHEN any factor fails, THE Backend API SHALL reject verification and specify which factor failed
4. WHEN verification fails, THE Backend API SHALL log detailed failure reasons for each failed factor
5. WHEN verification succeeds, THE Backend API SHALL store sensor metrics (RSSI, pressure difference, correlation coefficient) with attendance record

### Requirement 12: Offline Sensor Caching

**User Story:** As a student, I want the app to cache sensor data during network interruptions, so that I can still mark attendance when connectivity is restored.

#### Acceptance Criteria

1. WHEN network connectivity is lost, THE Student App SHALL cache sensor data and verification request locally
2. WHEN network connectivity is restored, THE Student App SHALL automatically submit cached verification requests
3. WHEN cached requests are submitted, THE Student App SHALL include original timestamp and sensor data
4. WHEN the Backend API receives delayed requests, THE Backend API SHALL validate that request timestamp is within session validity period
5. WHEN delayed requests are outside session period, THE Backend API SHALL reject with reason "Session expired"

### Requirement 13: Sensor Calibration and Accuracy

**User Story:** As a system administrator, I want to ensure sensor accuracy across different devices, so that verification is fair for all students.

#### Acceptance Criteria

1. WHEN the Student App initializes sensors, THE Student App SHALL verify that required sensors are available on the device
2. WHEN sensors are unavailable, THE Student App SHALL display error message specifying missing sensors
3. WHEN barometric pressure is read, THE Student App SHALL apply device-specific calibration if available
4. WHEN RSSI is measured, THE Student App SHALL average RSSI values over 3 seconds to reduce noise
5. WHEN sensor readings are anomalous (e.g., pressure = 0), THE Student App SHALL reject the reading and retry

### Requirement 14: Real-Time Sensor Feedback

**User Story:** As a student, I want to see real-time feedback during verification, so that I can adjust my position or movement if needed.

#### Acceptance Criteria

1. WHEN BLE scanning detects weak signal (RSSI < -70 dBm), THE Student App SHALL display "Move closer to classroom" with distance estimate
2. WHEN motion detection is active, THE Student App SHALL display "Nod your head gently" with visual animation
3. WHEN insufficient motion is detected, THE Student App SHALL display "Please move your device slightly"
4. WHEN GPS accuracy is low (> 20 meters), THE Student App SHALL display "Waiting for better GPS signal..."
5. WHEN all sensors are optimal, THE Student App SHALL display "Ready to verify" with green checkmark

### Requirement 15: Backend Sensor Processing

**User Story:** As a backend developer, I want to process sensor data efficiently, so that verification completes within 3 seconds.

#### Acceptance Criteria

1. WHEN sensor data is received, THE Backend API SHALL validate data format and completeness within 100ms
2. WHEN motion-image correlation is computed, THE Backend API SHALL complete processing within 1 second
3. WHEN all sensor checks are performed, THE Backend API SHALL return verification result within 3 seconds total
4. WHEN processing exceeds timeout, THE Backend API SHALL return partial results with timeout warning
5. WHEN sensor processing fails, THE Backend API SHALL log error details and return user-friendly error message

