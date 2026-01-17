# Requirements Document

## Introduction

The Intelligent Student Attendance Verification System (ISAVS) is a full-stack EdTech application designed for secure, tamper-resistant student attendance using Multi-Factor Verification. The system combines Face Recognition, ID Validation, and Simulated Biometrics to prevent proxy attendance and ensure accurate attendance tracking. The application follows a privacy-first approach by storing only facial embeddings rather than raw images.

## Glossary

- **ISAVS**: Intelligent Student Attendance Verification System - the main application
- **Facial Embedding**: A 128-dimensional numerical vector representing unique facial features
- **Cosine Similarity**: A metric used to measure similarity between two vectors
- **Liveness Detection**: A technique to verify that a live person is present (not a photo or video)
- **Blink Detection**: A liveness check method that detects eye blinks to confirm a live subject using MediaPipe Tasks API
- **Three-Factor Verification**: Authentication requiring Face Recognition, ID Validation, and OTP Verification
- **Geofencing**: Location-based verification ensuring students are within 50 meters of the classroom
- **Haversine Formula**: Mathematical formula for calculating distance between two GPS coordinates on Earth's surface
- **CLAHE**: Contrast Limited Adaptive Histogram Equalization - image preprocessing technique for improving recognition in uneven lighting
- **Centroid Embedding**: The mean (average) of multiple facial embeddings, computed from 10 frames to improve recognition accuracy
- **MediaPipe Tasks API**: Modern Google MediaPipe library using vision.FaceLandmarker for face detection
- **Proxy Attendance**: Fraudulent attendance where one person marks attendance for another
- **Anomaly**: A suspicious or failed verification attempt requiring review
- **Kiosk View**: The student-facing interface for attendance verification
- **Faculty Dashboard**: The administrative interface for monitoring attendance and anomalies
- **Three-Strike Policy**: A security measure that locks sessions after three consecutive failed attempts
- **OTP (One-Time Password)**: A unique random 4-digit code generated per student for each attendance session
- **TTL (Time-To-Live)**: The duration (60 seconds) for which an OTP remains valid
- **Class Session**: An attendance-taking period initiated by faculty for a specific class
- **Identity Mismatch Anomaly**: A logged event when OTP is correct but face recognition similarity is below threshold

## Requirements

### Requirement 1: Student Enrollment

**User Story:** As an administrator, I want to enroll students with their facial data and ID information, so that the system can verify their identity during attendance.

#### Acceptance Criteria

1. WHEN an administrator initiates enrollment THEN the ISAVS SHALL capture 10 frames from the live video feed
2. WHEN the ISAVS processes enrollment frames THEN the ISAVS SHALL apply CLAHE (Contrast Limited Adaptive Histogram Equalization) and grayscale conversion to each frame before face detection
3. WHEN the ISAVS extracts embeddings from 10 frames THEN the ISAVS SHALL compute the mean (centroid) of all 128-dimensional embeddings and store the centroid vector in the database
4. WHEN the ISAVS processes facial images for enrollment THEN the ISAVS SHALL discard all raw image frames after extracting the centroid embedding
5. WHEN a student with a duplicate student ID card number is submitted for enrollment THEN the ISAVS SHALL reject the enrollment and return an error message
6. WHEN the facial image quality is insufficient for embedding extraction THEN the ISAVS SHALL reject the enrollment and provide feedback about image quality requirements
7. WHEN enrollment succeeds THEN the ISAVS SHALL store the student record with ID, name, student ID card number, and centroid facial embedding vector

### Requirement 2: Face Recognition Verification (Factor 1)

**User Story:** As a student, I want to verify my identity through facial recognition, so that I can securely mark my attendance.

#### Acceptance Criteria

1. WHEN the ISAVS captures a live video frame THEN the ISAVS SHALL apply CLAHE and grayscale conversion to ensure recognition works in uneven lighting conditions
2. WHEN the ISAVS processes preprocessed frames THEN the ISAVS SHALL use MediaPipe Tasks API (vision.FaceLandmarker) with the face_landmarker.task model file for face detection
3. WHEN the ISAVS detects faces THEN the ISAVS SHALL extract 128-dimensional facial embeddings using the face_recognition library
4. WHEN comparing a captured facial embedding against stored centroid embeddings THEN the ISAVS SHALL use Cosine Similarity with a threshold of 0.6 to determine a match
5. WHEN a face is detected THEN the ISAVS SHALL perform a liveness check using blink detection before proceeding with verification
6. WHEN the liveness check fails THEN the ISAVS SHALL reject the verification attempt and log the failure reason
7. WHEN no face is detected in the captured frame THEN the ISAVS SHALL prompt the user to position their face within the camera view

### Requirement 3: ID Validation (Factor 2)

**User Story:** As a student, I want to enter my College ID for verification, so that the system can confirm my identity alongside facial recognition.

#### Acceptance Criteria

1. WHEN a student enters their College ID THEN the ISAVS SHALL validate the ID format against the expected pattern
2. WHEN a valid College ID is submitted THEN the ISAVS SHALL verify the ID exists in the student database
3. WHEN an invalid or non-existent College ID is submitted THEN the ISAVS SHALL reject the verification and display an appropriate error message
4. WHEN the submitted College ID does not match the face recognition result THEN the ISAVS SHALL flag the attempt as a potential proxy and log an anomaly

### Requirement 4: Individualized OTP Verification (Factor 3)

**User Story:** As a student, I want to receive a unique OTP for my attendance verification, so that the system has an additional time-bound verification factor.

#### Acceptance Criteria

1. WHEN a faculty member starts an attendance session for a class THEN the ISAVS SHALL generate a unique random 4-digit OTP for each enrolled student in that class
2. WHEN OTPs are generated for a class session THEN the ISAVS SHALL store the student-OTP mappings in cache with a 60-second TTL
3. WHEN a student submits their OTP THEN the ISAVS SHALL verify the OTP matches the one assigned to that specific student ID
4. WHEN an OTP expires (after 60 seconds) THEN the ISAVS SHALL reject verification attempts using that OTP
5. WHEN a student requests OTP resend THEN the ISAVS SHALL generate a new OTP with fresh 60-second TTL, limited to 2 resend attempts per session

### Requirement 4A: Geofencing Verification

**User Story:** As a system administrator, I want to verify that students are physically present in the classroom, so that remote proxy attendance is prevented.

#### Acceptance Criteria

1. WHEN a faculty member starts an attendance session THEN the ISAVS SHALL store the classroom GPS coordinates (latitude and longitude) with the session
2. WHEN a student submits verification THEN the ISAVS SHALL capture the student's current GPS coordinates using the Geolocation API
3. WHEN the ISAVS receives student GPS coordinates THEN the ISAVS SHALL calculate the distance between student location and classroom location using the Haversine formula
4. WHEN the calculated distance exceeds 50 meters THEN the ISAVS SHALL reject the verification attempt and log a geofence violation anomaly
5. WHEN the student's device denies location access THEN the ISAVS SHALL reject the verification attempt and provide feedback about location requirements

### Requirement 5: Three-Factor Verification Pipeline

**User Story:** As a system administrator, I want all three verification factors plus geofencing to pass before attendance is marked, so that the system maintains high security against proxy attendance.

#### Acceptance Criteria

1. WHEN all verification factors (Face with similarity >= 0.6, ID, OTP, Geofence within 50m) return positive verification THEN the ISAVS SHALL mark the attendance as verified and store the record
2. WHEN any of the verification factors fails THEN the ISAVS SHALL reject the attendance attempt and provide specific feedback about which factor failed
3. WHEN attendance is successfully verified THEN the ISAVS SHALL record the student ID, timestamp, GPS coordinates, and verification status in the Attendance table
4. WHEN a verification attempt fails THEN the ISAVS SHALL log the attempt details in the Anomalies table with the failure reason and timestamp
5. WHEN the OTP is correct but face recognition similarity is below 0.6 THEN the ISAVS SHALL log an "Identity Mismatch Anomaly" and reject the verification
6. WHEN the OTP and face are correct but geofence check fails THEN the ISAVS SHALL log a "Geofence Violation Anomaly" and reject the verification

### Requirement 6: Attendance Recording and Reporting

**User Story:** As a faculty member, I want to view attendance reports and statistics, so that I can monitor student attendance patterns.

#### Acceptance Criteria

1. WHEN a faculty member requests attendance reports THEN the ISAVS SHALL return attendance percentages for each student
2. WHEN generating reports THEN the ISAVS SHALL flag "Proxy Alerts" where the submitted ID did not match the face recognition result
3. WHEN a faculty member searches attendance by date THEN the ISAVS SHALL return all attendance records for the specified date
4. WHEN displaying real-time check-ins THEN the Faculty Dashboard SHALL show student name, timestamp, and verification status

### Requirement 7: Anomaly Detection and Handling

**User Story:** As a faculty member, I want to be alerted about suspicious verification attempts, so that I can investigate potential fraud.

#### Acceptance Criteria

1. WHEN a verification attempt fails THEN the ISAVS SHALL record the failure in the Anomalies table with student ID (if known), failure reason, and timestamp
2. WHEN a student has three consecutive failed biometric matches THEN the ISAVS SHALL lock the session and log an anomaly for manual faculty review
3. WHEN a session is locked due to the Three-Strike Policy THEN the ISAVS SHALL require faculty intervention to unlock
4. WHEN viewing the Anomaly Alert tab THEN the Faculty Dashboard SHALL display repeated failed attempts grouped by student

### Requirement 8: Environment Quality Handling

**User Story:** As a student, I want to receive feedback about environmental conditions, so that I can adjust for successful verification.

#### Acceptance Criteria

1. WHEN the captured image has low contrast indicating poor lighting THEN the ISAVS SHALL display a "Low Light" warning to the user
2. WHEN environmental conditions are unsuitable for verification THEN the ISAVS SHALL provide specific guidance on how to improve conditions
3. WHEN image quality falls below the minimum threshold THEN the ISAVS SHALL prevent verification attempts until conditions improve

### Requirement 9: Kiosk User Interface

**User Story:** As a student, I want a clear and intuitive interface for attendance verification, so that I can complete the process efficiently.

#### Acceptance Criteria

1. WHEN the Kiosk View loads THEN the Frontend SHALL display a live webcam feed with a green bounding box when a face is detected
2. WHEN a face is detected in the webcam feed THEN the Frontend SHALL display the green bounding box around the detected face in real-time
3. WHEN verification is in progress THEN the Frontend SHALL display clear status indicators for each of the verification factors
4. WHEN verification completes THEN the Frontend SHALL display a success or failure message with appropriate visual feedback
5. WHEN an OTP is active THEN the Frontend SHALL display a 30-second circular countdown timer showing remaining time
6. WHEN the countdown timer reaches zero THEN the Frontend SHALL disable the OTP input and show a "Resend OTP" button
7. WHEN a student clicks "Resend OTP" THEN the Frontend SHALL request a new OTP if resend attempts remain (maximum 2 resends)
8. WHEN the Kiosk View loads THEN the Frontend SHALL request geolocation permission and display the permission status

### Requirement 10: Faculty Dashboard Interface

**User Story:** As a faculty member, I want a comprehensive dashboard to monitor attendance in real-time, so that I can manage student attendance effectively.

#### Acceptance Criteria

1. WHEN the Faculty Dashboard loads THEN the Frontend SHALL establish a WebSocket connection for real-time updates
2. WHEN a student successfully verifies attendance THEN the Dashboard SHALL update immediately via WebSocket without requiring a page refresh
3. WHEN a biometric mismatch occurs (correct OTP but failed face) THEN the Dashboard SHALL highlight the entry in red
4. WHEN the Anomaly Alert tab is selected THEN the Dashboard SHALL display all logged anomalies with details for review
5. WHEN a faculty member uses the date search feature THEN the Dashboard SHALL filter and display attendance records for the selected date

### Requirement 11: API Endpoints

**User Story:** As a developer, I want well-defined API endpoints, so that the frontend can communicate effectively with the backend.

#### Acceptance Criteria

1. WHEN a POST request is made to /enroll with student details THEN the ISAVS SHALL capture 10 frames, compute centroid embedding, and return success or error status
2. WHEN a POST request is made to /verify with verification data (face image, student ID, OTP, GPS coordinates) THEN the ISAVS SHALL run the matching logic including geofence check and return the verification result
3. WHEN a GET request is made to /reports THEN the ISAVS SHALL return attendance percentages and anomaly alerts
4. WHEN any API request fails validation THEN the ISAVS SHALL return appropriate HTTP status codes and error messages
5. WHEN a POST request is made to /session/start with class_id and classroom GPS coordinates THEN the ISAVS SHALL generate unique 4-digit OTPs for all students in that class and store the geofence center point
6. WHEN a POST request is made to /otp/resend with student_id THEN the ISAVS SHALL generate a new OTP if resend attempts remain
7. WHEN a WebSocket connection is established to /ws/dashboard THEN the ISAVS SHALL push real-time attendance updates to connected clients

### Requirement 12: Data Privacy and Security

**User Story:** As a system administrator, I want the system to follow privacy-first principles, so that student biometric data is protected.

#### Acceptance Criteria

1. WHEN processing facial images THEN the ISAVS SHALL extract embeddings and immediately discard raw image data
2. WHEN storing facial embeddings THEN the ISAVS SHALL store only the 128-dimensional vector without any reversible image data
3. WHEN transmitting biometric data THEN the ISAVS SHALL use secure communication channels
4. WHEN OTPs are generated THEN the ISAVS SHALL store them securely in cache and never expose other students' OTPs

### Requirement 13: Concurrency and Performance

**User Story:** As a system administrator, I want the system to handle concurrent verification requests, so that multiple students can verify attendance simultaneously.

#### Acceptance Criteria

1. WHEN 50 or more students submit verification requests simultaneously THEN the ISAVS SHALL process all requests within the 60-second OTP window
2. WHEN multiple verification requests arrive concurrently THEN the ISAVS SHALL maintain data consistency and prevent race conditions
3. WHEN the OTP cache is accessed concurrently THEN the ISAVS SHALL use thread-safe operations to prevent data corruption
4. WHEN high load is detected THEN the ISAVS SHALL queue requests appropriately without dropping valid submissions