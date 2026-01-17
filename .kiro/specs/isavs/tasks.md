# Implementation Plan

- [x] 1. Set up project structure and dependencies

  - [x] 1.1 Create backend directory structure (app/api, app/services, app/models, app/db)
    - Set up FastAPI project with proper module organization
    - Create __init__.py files for all packages
    - _Requirements: 11.1, 11.2, 11.3_

  - [x] 1.2 Create requirements.txt with all Python dependencies
    - Include FastAPI, uvicorn, SQLAlchemy, face_recognition, opencv-python, mediapipe (Tasks API), numpy, hypothesis, pytest, redis, asyncio, python-socketio
    - Ensure mediapipe version supports Tasks API (vision.FaceLandmarker)
    - _Requirements: 11.1_

  - [x] 1.3 Create frontend directory structure with React + Tailwind
    - Initialize React app with TypeScript
    - Configure Tailwind CSS
    - Create component folders (components, hooks, services, types)
    - Install socket.io-client for WebSocket support
    - _Requirements: 9.1, 10.1_

  - [x] 1.4 Set up PostgreSQL database schema
    - Create migration script with Students, Classes, ClassEnrollments, AttendanceSessions (with GPS fields), Attendance (with GPS fields), Anomalies (with geofence_violation type), OTPResendTracking, VerificationSessions tables
    - Add indexes for performance
    - _Requirements: 1.1, 5.3, 7.1, 4.1, 4A.1_

  - [x] 1.5 Download face_landmarker.task model file


    - Download MediaPipe face_landmarker.task model from official source
    - Place in backend root directory
    - _Requirements: 2.2_



- [ ] 2. Implement preprocessing and core data models

  - [x] 2.1 Create PreprocessingService class



    - Implement CLAHE (Contrast Limited Adaptive Histogram Equalization) function
    - Implement grayscale conversion
    - Implement preprocess_frame pipeline method
    - _Requirements: 1.2, 2.1_

  - [x] 2.2 Write property test for CLAHE preprocessing


    - **Property 2: CLAHE preprocessing applied to all frames**
    - **Validates: Requirements 1.2, 2.1**

  - [x] 2.3 Create Pydantic models for API request/response
    - Implement EnrollRequest (without face_image), EnrollResponse (with frames_captured, centroid_computed)
    - Implement VerifyRequest (with latitude, longitude), VerifyResponse (with geofence_verified, distance_meters)
    - Implement StartSessionRequest (with classroom_latitude, classroom_longitude), StartSessionResponse (with geofence_center)
    - Implement WebSocketMessage model
    - _Requirements: 11.1, 11.2, 11.5, 11.7_

  - [x] 2.4 Implement SQLAlchemy ORM models
    - Update AttendanceSession with classroom_latitude, classroom_longitude fields
    - Update Attendance with student_latitude, student_longitude, distance_meters fields
    - Update Anomaly with geofence_violation type and distance_meters field
    - _Requirements: 4A.1, 5.3, 5.6_

  - [x] 2.5 Create database connection and session management
    - Implement async database connection pool
    - Create dependency injection for database sessions
    - _Requirements: 11.1_

- [ ] 3. Implement Face Recognition Service with MediaPipe Tasks API

  - [x] 3.1 Create FaceRecognitionService class with MediaPipe Tasks API


    - Load face_landmarker.task model using vision.FaceLandmarker
    - Implement face detection using MediaPipe Tasks API
    - Implement 128-d embedding extraction using face_recognition library
    - _Requirements: 2.2, 2.3_

  - [x] 3.2 Implement extract_centroid_embedding method

    - Accept 10 frames as input
    - Extract embedding from each frame
    - Compute mean (centroid) of all valid embeddings
    - Require minimum 5 valid frames
    - _Requirements: 1.3_

  - [x] 3.3 Write property test for centroid computation


    - **Property 3: Centroid is mean of embeddings**
    - **Validates: Requirements 1.3**

  - [x] 3.4 Implement cosine similarity comparison
    - Create embedding comparison function with 0.6 threshold
    - _Requirements: 2.4**

  - [x] 3.5 Write property test for cosine similarity threshold


    - **Property 10: Cosine similarity threshold is 0.6**
    - **Validates: Requirements 2.4**

  - [x] 3.6 Implement find_matching_student method
    - Query database for all centroid embeddings
    - Return best match above 0.6 threshold
    - _Requirements: 2.4_

  - [x] 3.7 Write property test for embedding dimensions


    - **Property 9: Face embeddings are always 128-dimensional**
    - **Validates: Requirements 2.3**

- [x] 4. Implement Liveness Detection Service
  - [x] 4.1 Create LivenessService class with Mediapipe
    - Initialize face mesh detector
    - Implement eye landmark extraction
    - _Requirements: 2.3_
  - [x] 4.2 Implement blink detection algorithm
    - Calculate Eye Aspect Ratio (EAR)
    - Detect blink across consecutive frames
    - _Requirements: 2.3, 2.4_
  - [x] 4.3 Implement check_liveness method
    - Require blink detection within timeout
    - Return liveness result with confidence
    - _Requirements: 2.3, 2.4_
  - [ ] 4.4 Write property test for liveness check ordering
    - **Property 7: Liveness check precedes verification**
    - **Validates: Requirements 2.3, 2.4**

- [x] 4B. Implement Emotion-based Liveness Detection (2026 Standard)
  - [x] 4B.1 Create EmotionService class with DeepFace
    - Initialize DeepFace for emotion detection
    - Support 7 emotions: Happy, Sad, Angry, Surprise, Fear, Disgust, Neutral
    - _Requirements: 2.3, 2.5_
  - [x] 4B.2 Implement smile detection (check_smile method)
    - Detect "happy" emotion with 0.7 confidence threshold
    - Return is_smiling, confidence, and all emotions
    - _Requirements: 2.3, 2.5_
  - [x] 4B.3 Implement emotion feedback messages
    - Generate user-friendly feedback for each emotion
    - Guide users to smile for verification
    - _Requirements: 8.2, 9.8_
  - [x] 4B.4 Integrate emotion check into verification endpoint
    - Add emotion check before face recognition
    - Reject verification if not smiling
    - Store emotion data in attendance records
    - _Requirements: 5.1, 5.2, 5.3_
  - [x] 4B.5 Create database migration for emotion tracking
    - Add emotion_detected and emotion_confidence columns to attendance table
    - Add embedding_dimension and embedding_model columns to students table
    - _Requirements: 1.1, 5.3_
  - [x] 4B.6 Update configuration for emotion settings
    - Add REQUIRE_SMILE and SMILE_CONFIDENCE_THRESHOLD to config
    - Default to enabled with 0.7 threshold
    - _Requirements: 11.1, 13.4_

- [x] 5. Implement Image Quality Service
  - [x] 5.1 Create ImageQualityService class
    - Implement contrast analysis using OpenCV
    - Implement brightness analysis
    - _Requirements: 8.1, 8.2_
  - [x] 5.2 Implement quality threshold checking
    - Define minimum contrast/brightness thresholds
    - Return quality result with specific issues
    - _Requirements: 8.3, 1.6_
  - [x] 5.3 Implement improvement suggestions generator
    - Map quality issues to user-friendly suggestions
    - _Requirements: 8.2_
  - [ ] 5.4 Write property test for image quality validation
    - **Property 6: Image quality validation with feedback**
    - **Validates: Requirements 1.6, 8.1, 8.2, 8.3**

- [ ] 5A. Implement Geofence Service
  - [x] 5A.1 Create GeofenceService class


    - Implement Haversine formula for GPS distance calculation
    - Set GEOFENCE_RADIUS_METERS constant to 50
    - _Requirements: 4A.3_

  - [x] 5A.2 Implement calculate_distance method

    - Use Haversine formula with Earth radius 6371000 meters
    - Return distance in meters
    - _Requirements: 4A.3_

  - [x] 5A.3 Write property test for Haversine formula


    - **Property 12: Haversine formula calculates GPS distance**
    - **Validates: Requirements 4A.3**

  - [x] 5A.4 Implement verify_location method

    - Calculate distance between student and classroom coordinates
    - Return GeofenceResult with within_geofence boolean and distance
    - _Requirements: 4A.4_

  - [x] 5A.5 Write property test for geofence radius enforcement

    - **Property 13: Geofence radius is 50 meters**
    - **Validates: Requirements 4A.4**
    
- [ ] 6. Checkpoint - Ensure all tests pass
  - Ensure all tests pass, ask the user if questions arise.

- [ ] 7. Implement Verification Pipeline with Geofencing
  - [ ] 7.1 Create VerificationPipeline class
    - Inject FaceRecognitionService, LivenessService, ImageQualityService, PreprocessingService, GeofenceService, OTPService
    - _Requirements: 5.1, 5.2_

  - [ ] 7.2 Implement verify_face method (Factor 1)
    - Apply CLAHE preprocessing to frames
    - Check image quality first
    - Perform liveness check
    - Extract and compare embeddings with 0.6 threshold
    - _Requirements: 2.1, 2.4, 2.5, 8.1_

  - [ ] 7.3 Write property test for liveness check ordering
    - **Property 11: Liveness check precedes verification**
    - **Validates: Requirements 2.5, 2.6**

  - [x] 7.4 Implement verify_id method (Factor 2)
    - Validate ID format with regex
    - Check ID exists in database
    - Compare with face match result for proxy detection
    - _Requirements: 3.1, 3.2, 3.3, 3.4_

  - [x] 7.5 Implement verify_otp method (Factor 3)
    - Validate OTP against cached value for student
    - Check TTL expiration
    - _Requirements: 4.3, 4.4_

  - [x] 7.6 Implement verify_geofence method (Factor 4)


    - Call GeofenceService to calculate distance
    - Check if distance <= 50 meters
    - Return GeofenceVerificationResult
    - _Requirements: 4A.2, 4A.4_

  - [x] 7.7 Implement run_full_verification method


    - Execute all four factors: Face, ID, OTP, Geofence
    - Log Identity Mismatch Anomaly if OTP correct but face < 0.6
    - Log Geofence Violation Anomaly if OTP+Face correct but distance > 50m
    - Aggregate results and determine final status
    - _Requirements: 5.1, 5.2, 5.5, 5.6_

  - [ ] 7.8 Write property test for all factors passing
    - **Property 16: All factors must pass for verified attendance**
    - **Validates: Requirements 5.1, 5.3**

  - [ ] 7.9 Write property test for identity mismatch anomaly
    - **Property 18: Identity mismatch anomaly logging**
    - **Validates: Requirements 5.5**

  - [ ] 7.10 Write property test for geofence violation anomaly
    - **Property 19: Geofence violation anomaly logging**
    - **Validates: Requirements 5.6**

- [x] 8. Implement OTP Service
  - [x] 8.1 Create OTPService class with cache backend
    - Initialize Redis or in-memory dict cache
    - Configure 60-second TTL for OTPs
    - _Requirements: 4.2, 13.3_
  - [x] 8.2 Implement generate_class_otps method
    - Generate unique 4-digit OTPs for all students in class
    - Ensure no duplicate OTPs within same session
    - Store in cache with TTL
    - _Requirements: 4.1, 4.2_
  - [x] 8.3 Implement verify_otp method
    - Check OTP matches stored value for student
    - Validate TTL not expired
    - _Requirements: 4.3, 4.4_
  - [x] 8.4 Implement resend_otp method
    - Check resend attempts remaining (max 2)
    - Generate new OTP with fresh TTL
    - Update resend tracking
    - _Requirements: 4.5_
  - [ ] 8.5 Write property test for OTP uniqueness
    - **Property 22: OTP generation uniqueness per student**
    - **Validates: Requirements 4.1**
  - [ ] 8.6 Write property test for OTP TTL
    - **Property 23: OTP TTL enforcement**
    - **Validates: Requirements 4.2, 4.4**
  - [ ] 8.7 Write property test for OTP verification
    - **Property 24: OTP verification correctness**
    - **Validates: Requirements 4.3**

- [x] 9. Implement Anomaly Service
  - [x] 9.1 Create AnomalyService class
    - Implement record_anomaly method
    - Implement record_identity_mismatch method for OTP correct but face < 0.6
    - Implement session failure tracking
    - _Requirements: 7.1, 5.4, 5.5_
  - [x] 9.2 Implement three-strike policy
    - Track consecutive failures per session
    - Lock session after 3 failures
    - _Requirements: 7.2_
  - [x] 9.3 Implement session lock/unlock methods
    - Lock session and log anomaly
    - Unlock with faculty authorization
    - _Requirements: 7.2, 7.3_
  - [ ] 9.4 Write property test for three-strike policy
    - **Property 25: Three-strike policy enforcement**
    - **Validates: Requirements 7.2, 7.3**

- [x] 10. Implement Report Service
  - [x] 10.1 Create ReportService class
    - Implement attendance percentage calculation
    - _Requirements: 6.1_
  - [x] 10.2 Implement proxy alert detection
    - Query anomalies for ID-face mismatches
    - _Requirements: 6.2_
  - [x] 10.3 Implement identity mismatch alert detection
    - Query anomalies where OTP correct but face < 0.6
    - _Requirements: 5.5_
  - [x] 10.4 Implement date filtering for attendance
    - Filter records by date range
    - _Requirements: 6.3_
  - [x] 10.5 Implement anomaly grouping by student
    - Group and sort anomalies for display
    - _Requirements: 7.4_
  - [ ] 10.6 Write property test for attendance percentage
    - **Property 17: Attendance percentage calculation**
    - **Validates: Requirements 6.1**
  - [ ] 10.7 Write property test for date filtering
    - **Property 18: Date filtering returns correct records**
    - **Validates: Requirements 6.3**
  - [ ] 10.8 Write property test for anomaly grouping
    - **Property 20: Anomaly grouping by student**
    - **Validates: Requirements 7.4**

- [ ] 11. Checkpoint - Ensure all tests pass
  - Ensure all tests pass, ask the user if questions arise.

- [ ] 12. Implement API Endpoints with WebSocket Support
  - [ ] 12.1 Create POST /enroll endpoint
    - Capture 10 frames from video stream
    - Apply CLAHE preprocessing to each frame
    - Extract centroid embedding and store student
    - Return success/error response with frames_captured count
    - _Requirements: 11.1, 1.1, 1.2, 1.3_

  - [ ] 12.2 Write property test for centroid enrollment
    - **Property 1: Centroid enrollment captures 10 frames**
    - **Validates: Requirements 1.1**

  - [ ] 12.3 Write property test for raw frames privacy
    - **Property 4: Raw enrollment frames are never persisted**
    - **Validates: Requirements 1.4, 12.1, 12.2**

  - [x] 12.4 Create POST /session/start endpoint
    - Accept class_id, classroom_latitude, classroom_longitude
    - Generate unique OTPs for all students in class
    - Store OTPs in cache with 60s TTL
    - Store classroom GPS coordinates with session
    - Return session info with geofence_center
    - _Requirements: 11.5, 4.1, 4.2, 4A.1_

  - [ ] 12.5 Write property test for session GPS storage
    - **Property 14: Session stores classroom GPS coordinates**
    - **Validates: Requirements 4A.1**

  - [ ] 12.6 Create POST /verify endpoint
    - Accept student_id, otp, face_image, latitude, longitude
    - Apply CLAHE preprocessing to face_image
    - Run verification pipeline with all four factors
    - Record attendance with GPS coordinates or anomaly
    - Push WebSocket update to dashboard
    - _Requirements: 11.2, 5.1, 5.2, 5.5, 5.6_

  - [ ] 12.7 Write property test for verification GPS capture
    - **Property 15: Verification captures student GPS coordinates**
    - **Validates: Requirements 4A.2**

  - [x] 12.8 Create POST /otp/resend endpoint
    - Generate new OTP if resend attempts remain
    - Return new expiration time
    - _Requirements: 11.6, 4.5_

  - [x] 12.9 Create GET /reports endpoint
    - Return attendance statistics
    - Include proxy alerts, identity mismatch alerts, and geofence violations
    - Support date filtering
    - _Requirements: 11.3, 6.1, 6.2, 6.3_

  - [x] 12.10 Create WebSocket endpoint /ws/dashboard



    - Accept WebSocket connections from dashboard clients
    - Maintain list of connected clients
    - Push attendance_update messages on successful verification
    - Push anomaly_alert messages on verification failures
    - _Requirements: 11.7, 10.1, 10.2_

  - [ ] 12.11 Write property test for WebSocket updates
    - **Property 20: WebSocket pushes real-time updates**
    - **Validates: Requirements 10.2, 11.7**

  - [x] 12.12 Implement API error handling middleware
    - Map exceptions to HTTP status codes
    - Return consistent error response format
    - _Requirements: 11.4_

  - [x] 12.13 Implement concurrent request handling
    - Use async/await for non-blocking operations
    - Implement thread-safe cache access
    - _Requirements: 13.1, 13.2, 13.3_

- [ ] 13. Implement Frontend Kiosk View with Geolocation
  - [x] 13.1 Create WebcamCapture component
    - Implement webcam access and frame capture
    - Draw green bounding box on detected face
    - _Requirements: 9.1, 9.2_

  - [ ] 13.2 Update WebcamCapture for 10-frame enrollment
    - Capture 10 frames during enrollment process
    - Display frame count progress
    - _Requirements: 1.1_

  - [x] 13.3 Create CountdownTimer component
    - Implement 30-second circular countdown
    - Trigger onExpire callback when timer reaches zero
    - _Requirements: 9.5, 9.6_

  - [x] 13.4 Create OTPInput component
    - 4-digit OTP input field
    - Auto-focus and validation
    - _Requirements: 4.3, 9.1_

  - [ ] 13.5 Create KioskView component with geolocation
    - Request geolocation permission on load
    - Display permission status
    - Live webcam feed with green bounding box
    - Student ID entry form field
    - OTP input with countdown timer
    - Verification status indicators (Face, ID, OTP, Geofence)
    - Resend OTP button (max 2 attempts)
    - _Requirements: 9.1, 9.3, 9.4, 9.5, 9.6, 9.7, 9.8_

  - [ ] 13.6 Implement geolocation capture in Kiosk
    - Use Geolocation API to get current position
    - Handle permission denial gracefully
    - Include latitude/longitude in verification request
    - _Requirements: 4A.2, 4A.5_

  - [ ] 13.7 Implement verification flow in Kiosk
    - Capture frames for liveness detection
    - Collect student ID, OTP, face image, and GPS coordinates
    - Submit to /verify endpoint
    - Display result feedback with specific factor failures
    - _Requirements: 5.1, 5.2, 9.3, 9.4_

- [ ] 14. Implement Frontend Faculty Dashboard with WebSocket
  - [x] 14.1 Create AttendanceTable component
    - Display real-time check-ins
    - Show student name, timestamp, status
    - Highlight biometric mismatches in red
    - _Requirements: 10.1, 6.4, 10.3_

  - [ ] 14.2 Update AttendanceTable for biometric mismatch highlighting
    - Check isBiometricMismatch flag on records
    - Apply red highlighting CSS for mismatches
    - _Requirements: 10.3_

  - [ ] 14.3 Write property test for biometric mismatch highlighting
    - **Property 21: Biometric mismatch highlighted in red**
    - **Validates: Requirements 10.3**

  - [x] 14.4 Create DateSearch component
    - Date picker for filtering
    - Trigger attendance query on selection
    - _Requirements: 10.2, 6.3_

  - [x] 14.5 Create AnomalyAlertTab component
    - Display anomalies grouped by student
    - Show failure reasons, timestamps, identity mismatch alerts, and geofence violations
    - _Requirements: 10.4, 7.4_

  - [ ] 14.6 Create StartSessionButton component
    - Allow faculty to start attendance session for a class
    - Capture classroom GPS coordinates
    - Display generated OTP count and expiration
    - _Requirements: 11.5, 4.1, 4A.1_

  - [ ] 14.7 Create FacultyDashboard component with WebSocket
    - Tab navigation between attendance and anomalies
    - Establish WebSocket connection to /ws/dashboard on mount
    - Listen for attendance_update and anomaly_alert messages
    - Update state in real-time without polling
    - Close WebSocket on unmount
    - _Requirements: 10.1, 10.2, 10.4, 11.7_

- [ ] 15. Implement API integration and WebSocket client
  - [ ] 15.1 Create API service layer in frontend
    - Implement enroll (with 10-frame capture), verify (with GPS), startSession (with classroom GPS), resendOTP, getReports functions
    - Handle error responses
    - _Requirements: 11.1, 11.2, 11.3, 11.5, 11.6_

  - [ ] 15.2 Implement WebSocket client service
    - Create WebSocket connection manager
    - Handle connection, disconnection, and reconnection
    - Parse and dispatch WebSocket messages
    - _Requirements: 11.7, 10.2_

  - [ ] 15.3 Integrate WebSocket with dashboard state management
    - Update attendance records on attendance_update messages
    - Update anomaly list on anomaly_alert messages
    - Handle connection errors gracefully
    - _Requirements: 10.2, 10.4_

- [ ] 16. Final Checkpoint - Ensure all tests pass
  - Ensure all tests pass, ask the user if questions arise.
