# Design Document: ISAVS Mobile - Sensor Fusion

## Overview

The ISAVS Mobile Sensor Fusion system extends the eximplementation details for adding hardware-level proximity and liveness verification to ISAVS 2026 through a React Native mobile application. The system leverages smartphone sensors (BLE, Accelerometer, Gyroscope, GPS, Barometer) to create a multi-layered, sensor-fused verification system.

### Key Features

- **BLE Proximity Detection**: Teacher beacon broadcasting with RSSI-based distance estimation
- **Motion-Based Liveness**: Accelerometer and gyroscope data correlated with camera optical flow
- **Enhanced Geofencing**: GPS + barometric pressure for 2-stage location verification
- **Sensor Fusion**: Multi-sensor validation with fallback mechanisms
- **Cross-Platform**: React Native for iOS and Android support
- **Real-Time Monitoring**: Live sensor feedback for students and faculty

### Design Goals

1. **Security**: Prevent spoofing through multi-sensor correlation
2. **Usability**: Smooth UX with clear sensor status feedback
3. **Performance**: Optimize battery usage and sensor sampling
4. **Reliability**: Graceful degradation when sensors unavailable
5. **Privacy**: Anonymize and secure sensor data transmission

## Architecture

### System Components

```
┌─────────────────────────────────────────────────────────────┐
│                     ISAVS Mobile System                      │
├─────────────────────────────────────────────────────────────┤
│                                                               │
│  ┌──────────────────┐         ┌──────────────────┐          │
│  │   Teacher App    │         │   Student App    │          │
│  │  (React Native)  │         │  (React Native)  │          │
│  ├──────────────────┤         ├──────────────────┤          │
│  │ - Beacon Manager │         │ - BLE Scanner    │          │
│  │ - Session Control│         │ - Sensor Manager │          │
│  │ - GPS Capture    │         │ - Motion Detector│          │
│  │ - Pressure Sensor│         │ - Camera Capture │          │
│  └────────┬─────────┘         └────────┬─────────┘          │
│           │                            │                     │
│           └────────────┬───────────────┘                     │
│                        │                                     │
│                        ▼                                     │
│           ┌────────────────────────┐                        │
│           │   Backend API (FastAPI)│                        │
│           ├────────────────────────┤                        │
│           │ - Sensor Validation    │                        │
│           │ - Motion Correlation   │                        │
│           │ - Geofence Verification│                        │
│           │ - Anomaly Detection    │                        │
│           └────────────┬───────────┘                        │
│                        │                                     │
│                        ▼                                     │
│           ┌────────────────────────┐                        │
│           │  Supabase Database     │                        │
│           ├────────────────────────┤                        │
│           │ - Sensor Data Storage  │                        │
│           │ - Attendance Records   │                        │
│           │ - Anomaly Logs         │                        │
│           └────────────────────────┘                        │
│                                                               │
└─────────────────────────────────────────────────────────────┘
```

### Technology Stack

**Mobile App (React Native)**
- React Native 0.73+
- TypeScript 5.0+
- react-native-ble-manager (BLE)
- react-native-sensors (Accelerometer, Gyroscope)
- react-native-barometer (Pressure)
- react-native-vision-camera (High-performance camera)
- @react-native-community/geolocation (GPS)

**Backend (FastAPI)**
- Python 3.13+
- FastAPI 0.109+
- NumPy (Sensor data processing)
- SciPy (Correlation calculations)
- OpenCV (Optical flow extraction)

**Database (Supabase)**
- PostgreSQL 15+
- Real-time subscriptions
- Row-level security


## Components and Interfaces

### 1. BLE Beacon Manager (Teacher App)

**Purpose**: Broadcast BLE beacon signal for classroom proximity detection

**Interface**:
```typescript
interface BeaconManager {
  startBeacon(sessionId: string): Promise<BeaconStatus>;
  stopBeacon(): Promise<void>;
  getBeaconStatus(): BeaconStatus;
  onStudentDetected(callback: (studentId: string, rssi: number) => void): void;
}

interface BeaconStatus {
  isActive: boolean;
  sessionId: string;
  uuid: string;
  rssiRange: { min: number; max: number };
  connectedStudents: number;
  batteryLevel: number;
}
```

**Responsibilities**:
- Initialize BLE peripheral mode
- Broadcast beacon with session UUID
- Monitor connected devices
- Track battery usage
- Handle beacon failures

### 2. BLE Scanner (Student App)

**Purpose**: Scan for teacher beacon and measure signal strength

**Interface**:
```typescript
interface BLEScanner {
  startScanning(): Promise<void>;
  stopScanning(): Promise<void>;
  onBeaconDetected(callback: (beacon: BeaconData) => void): void;
  getRSSI(beaconId: string): number;
  getEstimatedDistance(rssi: number): number;
}

interface BeaconData {
  uuid: string;
  sessionId: string;
  rssi: number;
  distance: number;
  timestamp: number;
}
```

**Responsibilities**:
- Scan for BLE beacons
- Measure RSSI values
- Calculate distance using path loss model
- Filter beacons by session ID
- Handle scan errors

### 3. Motion Sensor Manager (Student App)

**Purpose**: Collect accelerometer and gyroscope data for liveness detection

**Interface**:
```typescript
interface MotionSensorManager {
  startRecording(duration: number): Promise<void>;
  stopRecording(): Promise<MotionData>;
  detectNod(data: AccelerometerData[]): boolean;
  detectShake(data: GyroscopeData[]): boolean;
  getSamplingRate(): number;
}

interface MotionData {
  accelerometer: AccelerometerData[];
  gyroscope: GyroscopeData[];
  startTime: number;
  endTime: number;
  samplingRate: number;
}

interface AccelerometerData {
  x: number;
  y: number;
  z: number;
  timestamp: number;
}

interface GyroscopeData {
  x: number;
  y: number;
  z: number;
  timestamp: number;
}
```

**Responsibilities**:
- Record accelerometer data at 50Hz
- Record gyroscope data at 50Hz
- Detect vertical motion (nod)
- Detect horizontal rotation (shake)
- Batch sensor data for processing


### 4. Motion-Image Correlator (Backend)

**Purpose**: Correlate sensor motion with camera optical flow

**Interface**:
```python
class MotionImageCorrelator:
    def extract_optical_flow(self, frames: List[np.ndarray]) -> List[FlowVector]:
        """Extract optical flow from video frames"""
        pass
    
    def calculate_correlation(
        self, 
        motion_data: MotionData, 
        optical_flow: List[FlowVector]
    ) -> float:
        """Calculate correlation coefficient between motion and flow"""
        pass
    
    def verify_liveness(
        self, 
        motion_data: MotionData, 
        frames: List[np.ndarray]
    ) -> LivenessResult:
        """Verify liveness by correlating motion with image flow"""
        pass

class FlowVector:
    x: float
    y: float
    magnitude: float
    timestamp: float

class LivenessResult:
    passed: bool
    correlation: float
    confidence: float
    reason: str
```

**Responsibilities**:
- Extract optical flow from video frames
- Align motion data with frame timestamps
- Calculate Pearson correlation coefficient
- Determine liveness pass/fail (threshold: 0.7)
- Generate failure reasons

### 5. Barometer Service (Mobile App)

**Purpose**: Measure atmospheric pressure for floor-level verification

**Interface**:
```typescript
interface BarometerService {
  getCurrentPressure(): Promise<number>;
  startMonitoring(interval: number): void;
  stopMonitoring(): void;
  onPressureChange(callback: (pressure: number) => void): void;
}

interface PressureData {
  pressure: number; // hPa
  altitude: number; // meters (estimated)
  timestamp: number;
}
```

**Responsibilities**:
- Read barometric pressure sensor
- Convert pressure to altitude estimate
- Monitor pressure changes
- Handle sensor unavailability

### 6. Sensor Validation Service (Backend)

**Purpose**: Validate all sensor data before marking attendance

**Interface**:
```python
class SensorValidationService:
    def validate_ble_proximity(
        self, 
        rssi: float, 
        beacon_uuid: str, 
        session_id: str
    ) -> ValidationResult:
        """Validate BLE proximity data"""
        pass
    
    def validate_motion_liveness(
        self, 
        motion_data: MotionData, 
        frames: List[bytes]
    ) -> ValidationResult:
        """Validate motion-image correlation"""
        pass
    
    def validate_geofence(
        self, 
        student_lat: float, 
        student_lon: float,
        teacher_lat: float, 
        teacher_lon: float
    ) -> ValidationResult:
        """Validate GPS geofence"""
        pass
    
    def validate_barometer(
        self, 
        student_pressure: float, 
        teacher_pressure: float
    ) -> ValidationResult:
        """Validate barometric pressure"""
        pass
    
    def validate_all_sensors(
        self, 
        sensor_data: SensorData
    ) -> MultiSensorValidationResult:
        """Validate all sensors and return combined result"""
        pass

class ValidationResult:
    passed: bool
    value: float
    threshold: float
    message: str
    anomaly_type: Optional[str]

class MultiSensorValidationResult:
    overall_passed: bool
    ble_result: ValidationResult
    motion_result: ValidationResult
    gps_result: ValidationResult
    barometer_result: ValidationResult
    failed_sensors: List[str]
```

**Responsibilities**:
- Validate RSSI threshold (-70dBm)
- Validate motion correlation (0.7)
- Validate GPS distance (50m)
- Validate pressure difference (0.5 hPa)
- Aggregate validation results
- Generate anomaly logs


## Data Models

### Sensor Data Schema

```typescript
// Mobile App Models
interface SensorVerificationRequest {
  student_id: string;
  session_id: string;
  otp: string;
  face_image: string; // base64
  
  // BLE Data
  ble_rssi: number;
  ble_beacon_uuid: string;
  ble_distance: number;
  
  // Motion Data
  accelerometer_data: AccelerometerData[];
  gyroscope_data: GyroscopeData[];
  motion_start_time: number;
  motion_end_time: number;
  
  // Location Data
  gps_latitude: number;
  gps_longitude: number;
  gps_accuracy: number;
  barometric_pressure: number;
  
  // Video Frames (for correlation)
  video_frames: string[]; // base64 encoded frames
  frame_timestamps: number[];
}

interface SensorVerificationResponse {
  success: boolean;
  message: string;
  factors: {
    face_verified: boolean;
    face_confidence: number;
    liveness_passed: boolean;
    id_verified: boolean;
    otp_verified: boolean;
    ble_verified: boolean;
    ble_rssi: number;
    geofence_verified: boolean;
    distance_meters: number;
    barometer_verified: boolean;
    pressure_diff: number;
    motion_verified: boolean;
    motion_correlation: number;
  };
}
```

### Database Schema Extensions

```sql
-- Add sensor columns to attendance table
ALTER TABLE attendance
ADD COLUMN IF NOT EXISTS ble_rssi FLOAT,
ADD COLUMN IF NOT EXISTS ble_distance FLOAT,
ADD COLUMN IF NOT EXISTS barometric_pressure FLOAT,
ADD COLUMN IF NOT EXISTS pressure_difference FLOAT,
ADD COLUMN IF NOT EXISTS motion_correlation FLOAT,
ADD COLUMN IF NOT EXISTS accelerometer_detected BOOLEAN,
ADD COLUMN IF NOT EXISTS gyroscope_detected BOOLEAN,
ADD COLUMN IF NOT EXISTS sensor_collection_duration FLOAT;

-- Add sensor columns to attendance_sessions table
ALTER TABLE attendance_sessions
ADD COLUMN IF NOT EXISTS beacon_uuid VARCHAR(36),
ADD COLUMN IF NOT EXISTS teacher_barometric_pressure FLOAT,
ADD COLUMN IF NOT EXISTS beacon_active BOOLEAN DEFAULT false;

-- Create sensor_anomalies table for detailed logging
CREATE TABLE IF NOT EXISTS sensor_anomalies (
  id SERIAL PRIMARY KEY,
  student_id INTEGER REFERENCES students(id),
  session_id INTEGER REFERENCES attendance_sessions(id),
  anomaly_type VARCHAR(50) NOT NULL,
  sensor_name VARCHAR(50) NOT NULL,
  expected_value FLOAT,
  actual_value FLOAT,
  threshold FLOAT,
  reason TEXT,
  timestamp TIMESTAMP DEFAULT NOW()
);

-- Create indexes for sensor queries
CREATE INDEX IF NOT EXISTS idx_attendance_ble_rssi ON attendance(ble_rssi);
CREATE INDEX IF NOT EXISTS idx_attendance_motion_correlation ON attendance(motion_correlation);
CREATE INDEX IF NOT EXISTS idx_sensor_anomalies_type ON sensor_anomalies(anomaly_type);
CREATE INDEX IF NOT EXISTS idx_sensor_anomalies_sensor ON sensor_anomalies(sensor_name);
```


## Correctness Properties

*A property is a characteristic or behavior that should hold true across all valid executions of a system—essentially, a formal statement about what the system should do. Properties serve as the bridge between human-readable specifications and machine-verifiable correctness guarantees.*

### BLE Proximity Properties

**Property 1: RSSI threshold enforcement**
*For any* verification request with RSSI value, when RSSI <= -70dBm, the system should reject verification with message "Too far from classroom beacon"
**Validates: Requirements 1.4, 1.5, 2.3, 2.4**

**Property 2: RSSI-to-distance conversion**
*For any* RSSI value, the calculated distance using log-distance path loss model should be d = 10^((TxPower - RSSI) / (10 * n)) where n=2 (path loss exponent)
**Validates: Requirements 1.3, 2.1**

**Property 3: Beacon UUID validation**
*For any* verification request, the beacon UUID must match the session's beacon UUID, otherwise verification should fail
**Validates: Requirements 1.1, 10.1, 13.2**

### Motion Liveness Properties

**Property 4: Accelerometer sampling rate**
*For any* motion data collection, the sampling rate should be 50Hz ± 5Hz (20ms ± 2ms intervals between samples)
**Validates: Requirements 3.1, 18.2**

**Property 5: Gyroscope sampling rate**
*For any* motion data collection, the sampling rate should be 50Hz ± 5Hz (20ms ± 2ms intervals between samples)
**Validates: Requirements 4.1, 18.2**

**Property 6: Nod detection threshold**
*For any* accelerometer data sequence, when vertical (z-axis) acceleration change >= 0.5 m/s², the system should detect a nod
**Validates: Requirements 3.3**

**Property 7: Shake detection threshold**
*For any* gyroscope data sequence, when horizontal (y-axis) angular velocity >= 0.3 rad/s, the system should detect a shake
**Validates: Requirements 4.3**

**Property 8: Motion data duration**
*For any* motion data collection, the duration should be exactly 2 seconds (100 samples at 50Hz)
**Validates: Requirements 3.2, 4.2**

**Property 9: Motion-image correlation threshold**
*For any* motion data and video frames, when correlation coefficient >= 0.7, liveness check should pass; when < 0.7, it should fail
**Validates: Requirements 5.3, 5.4**

**Property 10: Frame-motion timestamp alignment**
*For any* motion event at timestamp T, there should exist a video frame with timestamp within ±20ms of T
**Validates: Requirements 3.4, 4.4**

### Geofencing Properties

**Property 11: GPS distance calculation**
*For any* two GPS coordinates, the Haversine distance calculation should satisfy: d = 2 * R * arcsin(sqrt(sin²(Δlat/2) + cos(lat1) * cos(lat2) * sin²(Δlon/2)))
**Validates: Requirements 6.3**

**Property 12: Geofence radius enforcement**
*For any* verification request, when GPS distance > 50 meters, the system should reject verification with message "Outside classroom geofence"
**Validates: Requirements 6.4**

**Property 13: Barometric pressure threshold**
*For any* verification request, when |teacher_pressure - student_pressure| > 0.5 hPa, the system should reject verification with message "Pressure mismatch - different floor detected"
**Validates: Requirements 7.4**

**Property 14: Pressure-to-altitude conversion**
*For any* pressure difference ΔP, the altitude difference should be approximately ΔH ≈ -8.5 * ΔP meters (at sea level)
**Validates: Requirements 7.3**

### Temporal Properties

**Property 15: Timestamp precision**
*For any* sensor reading, the timestamp should have millisecond precision (3 decimal places)
**Validates: Requirements 8.1**

**Property 16: Sensor collection duration**
*For any* verification request, the sensor collection duration (end_time - start_time) should be between 2 and 5 seconds
**Validates: Requirements 8.3**

**Property 17: Timestamp monotonicity**
*For any* sequence of sensor readings, timestamps should be strictly increasing (t[i+1] > t[i])
**Validates: Requirements 8.4**

### Multi-Sensor Fusion Properties

**Property 18: All sensors validated**
*For any* verification request, the system should validate BLE proximity, GPS geofence, barometric pressure, and motion correlation
**Validates: Requirements 9.1**

**Property 19: Sensor failure specificity**
*For any* failed verification, the error message should specify which sensor failed (BLE, GPS, Barometer, or Motion)
**Validates: Requirements 9.3, 13.5**

**Property 20: Sensor data persistence**
*For any* successful verification, all sensor data (RSSI, GPS, pressure, correlation) should be stored in the attendance record
**Validates: Requirements 9.4, 14.1**

### Fallback Properties

**Property 21: BLE fallback to GPS**
*For any* verification request where BLE is unavailable, the system should use GPS-only verification
**Validates: Requirements 15.1**

**Property 22: Motion fallback to emotion**
*For any* verification request where motion sensors are unavailable, the system should use emotion-based liveness (smile detection)
**Validates: Requirements 15.3**

**Property 23: Degraded mode activation**
*For any* verification request where 2 or more sensors fail, the system should activate degraded mode and require faculty override
**Validates: Requirements 15.5**

### UI/UX Properties

**Property 24: Button state based on RSSI**
*For any* RSSI measurement, when RSSI > -70dBm, the verify button should be enabled; when RSSI <= -70dBm, it should be disabled
**Validates: Requirements 1.4, 1.5, 12.4**

**Property 25: Sensor status display**
*For any* sensor state change, the UI should update within 100ms to reflect the new state
**Validates: Requirements 12.1, 12.2, 12.3**

### Security Properties

**Property 26: HTTPS encryption**
*For any* sensor data transmission, the request should use HTTPS with TLS 1.3
**Validates: Requirements 19.1**

**Property 27: GPS anonymization**
*For any* stored GPS coordinates, the precision should be reduced to 10-meter accuracy (4 decimal places)
**Validates: Requirements 19.2**

**Property 28: Data retention**
*For any* sensor data older than 30 days, the raw sensor readings should be deleted
**Validates: Requirements 19.4**


## Error Handling

### Sensor Unavailability

**BLE Unavailable**:
- Fallback to GPS-only verification
- Display warning: "Bluetooth unavailable - using GPS only"
- Log degraded mode event

**GPS Unavailable**:
- Require manual faculty approval
- Display error: "Location services unavailable - contact faculty"
- Block automatic verification

**Barometer Unavailable**:
- Skip pressure validation
- Log warning but continue verification
- Display info: "Pressure sensor unavailable - skipping floor check"

**Motion Sensors Unavailable**:
- Fallback to emotion-based liveness (smile detection)
- Display info: "Motion sensors unavailable - using smile detection"
- Log fallback event

### Permission Errors

**Bluetooth Permission Denied**:
- Display: "Bluetooth permission required for proximity detection"
- Provide "Open Settings" button
- Disable BLE features

**Location Permission Denied**:
- Display: "Location permission required for geofencing"
- Provide "Open Settings" button
- Block verification

**Camera Permission Denied**:
- Display: "Camera permission required for face verification"
- Provide "Open Settings" button
- Block verification

**Motion Sensor Permission Denied** (iOS):
- Display: "Motion permission required for liveness detection"
- Provide "Open Settings" button
- Fallback to emotion liveness

### Validation Errors

**RSSI Too Weak**:
- Error: "Too far from classroom beacon (RSSI: {value}dBm)"
- Suggestion: "Move closer to the classroom"
- Log proximity violation

**GPS Out of Range**:
- Error: "Outside classroom geofence ({distance}m from classroom)"
- Suggestion: "You must be within 50m of the classroom"
- Log geofence violation

**Pressure Mismatch**:
- Error: "Pressure mismatch - different floor detected (Δ{diff}hPa)"
- Suggestion: "Ensure you're on the same floor as the classroom"
- Log floor-level spoofing attempt

**Motion Correlation Failed**:
- Error: "Motion verification failed (correlation: {value})"
- Suggestion: "Please nod or shake your head naturally"
- Log liveness spoofing attempt

### Timeout Errors

**Beacon Not Found**:
- After 10 seconds: "Classroom beacon not found"
- Suggestion: "Ensure faculty has started the session and Bluetooth is enabled"
- Provide "Retry Scan" button

**Motion Timeout**:
- After 5 seconds: "No motion detected"
- Suggestion: "Please nod or shake your head slowly"
- Provide "Retry" button

**GPS Timeout**:
- After 15 seconds: "Unable to acquire GPS location"
- Suggestion: "Move to an area with better GPS signal"
- Provide "Retry" button


## Testing Strategy

### Unit Testing

**Mobile App (Jest + React Native Testing Library)**:
- BLE Scanner: Test RSSI measurement and distance calculation
- Motion Sensor Manager: Test data collection and motion detection
- Barometer Service: Test pressure reading and conversion
- UI Components: Test button states and sensor status display

**Backend (Pytest)**:
- Sensor Validation Service: Test threshold enforcement
- Motion-Image Correlator: Test correlation calculation
- Geofence Service: Test distance and pressure validation
- Anomaly Service: Test sensor-specific anomaly logging

### Property-Based Testing

**Testing Framework**: Hypothesis (Python) for backend, fast-check (TypeScript) for mobile

**Key Properties to Test**:
1. RSSI-to-distance conversion (Property 2)
2. Motion detection thresholds (Properties 6, 7)
3. Correlation coefficient calculation (Property 9)
4. Haversine distance formula (Property 11)
5. Timestamp monotonicity (Property 17)
6. Multi-sensor validation (Property 18)

**Property Test Configuration**:
- Minimum 100 iterations per property
- Generate random sensor values within valid ranges
- Test edge cases (boundary values, extreme conditions)
- Verify invariants hold across all inputs

### Integration Testing

**End-to-End Scenarios**:
1. **Happy Path**: All sensors pass, attendance marked successfully
2. **Weak BLE Signal**: RSSI too weak, verification rejected
3. **Out of Geofence**: GPS distance > 50m, verification rejected
4. **Wrong Floor**: Pressure difference > 0.5 hPa, verification rejected
5. **Motion Spoofing**: Low correlation, liveness failed
6. **Sensor Fallback**: BLE unavailable, GPS-only mode activated
7. **Multiple Failures**: 2+ sensors fail, degraded mode activated

**Mock Data**:
- Mock BLE beacons for testing without physical devices
- Simulated sensor data for automated testing
- GPS coordinate overrides for location testing
- Barometer value overrides for pressure testing

### Performance Testing

**Metrics to Measure**:
- BLE scan latency: < 2 seconds to detect beacon
- Motion data collection: Exactly 2 seconds at 50Hz
- Correlation calculation: < 500ms for 100 samples
- Battery drain: < 5% per verification session
- Memory usage: < 100MB during verification

**Load Testing**:
- 100 concurrent verifications
- 1000 students per session
- Beacon broadcasting for 2 hours
- Sensor data storage for 10,000 records

### Security Testing

**Penetration Testing**:
- Replay attack: Reuse old sensor data
- Spoofing attack: Fake BLE beacon
- Man-in-the-middle: Intercept sensor data
- Sensor manipulation: Fake motion data

**Privacy Testing**:
- GPS anonymization: Verify 10m precision
- Data retention: Verify 30-day deletion
- PII exclusion: Verify no personal data in logs
- Encryption: Verify TLS 1.3 usage

