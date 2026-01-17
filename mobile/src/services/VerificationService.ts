/**
 * Verification Service
 * Handles sensor data collection and submission to backend
 */
import {api} from './api';
import {
  SensorVerificationRequest,
  SensorVerificationResponse,
  MotionData,
  LocationData,
  PressureData,
  BeaconData,
} from '../types';

export class VerificationService {
  /**
   * Submit verification request with all sensor data
   */
  async submitVerification(
    studentId: string,
    sessionId: string,
    otp: string,
    faceImage: string,
    beaconData: BeaconData,
    locationData: LocationData,
    pressureData: PressureData,
    motionData: MotionData,
    videoFrames: string[],
    frameTimestamps: number[]
  ): Promise<SensorVerificationResponse> {
    try {
      const request: SensorVerificationRequest = {
        student_id: studentId,
        session_id: sessionId,
        otp,
        face_image: faceImage,
        
        // BLE Data
        ble_rssi: beaconData.rssi,
        ble_beacon_uuid: beaconData.uuid,
        ble_distance: beaconData.distance,
        
        // Motion Data
        accelerometer_data: motionData.accelerometer,
        gyroscope_data: motionData.gyroscope,
        motion_start_time: motionData.startTime,
        motion_end_time: motionData.endTime,
        
        // Location Data
        gps_latitude: locationData.latitude,
        gps_longitude: locationData.longitude,
        gps_accuracy: locationData.accuracy,
        barometric_pressure: pressureData.pressure,
        
        // Video Frames
        video_frames: videoFrames,
        frame_timestamps: frameTimestamps,
      };

      console.log('[Verification] Submitting request:', {
        studentId,
        sessionId,
        rssi: beaconData.rssi,
        distance: beaconData.distance,
        pressure: pressureData.pressure,
        motionSamples: motionData.accelerometer.length,
        frames: videoFrames.length,
      });

      const response = await api.post<SensorVerificationResponse>(
        '/verify',
        request
      );

      console.log('[Verification] Response:', response.data);
      return response.data;
    } catch (error: any) {
      console.error('[Verification] Submission error:', error);
      
      // Extract error message from response
      const errorMessage = error.response?.data?.message || error.message || 'Verification failed';
      
      throw new Error(errorMessage);
    }
  }

  /**
   * Validate sensor data completeness before submission
   */
  validateSensorData(
    beaconData: BeaconData | null,
    locationData: LocationData | null,
    pressureData: PressureData | null,
    motionData: MotionData | null,
    videoFrames: string[]
  ): {valid: boolean; errors: string[]} {
    const errors: string[] = [];

    // Validate BLE data
    if (!beaconData) {
      errors.push('BLE beacon data is missing');
    } else if (beaconData.rssi === 0) {
      errors.push('Invalid RSSI value');
    }

    // Validate GPS data
    if (!locationData) {
      errors.push('GPS location data is missing');
    } else if (locationData.latitude === 0 && locationData.longitude === 0) {
      errors.push('Invalid GPS coordinates');
    }

    // Validate pressure data
    if (!pressureData) {
      errors.push('Barometric pressure data is missing');
    } else if (pressureData.pressure === 0) {
      errors.push('Invalid pressure reading');
    }

    // Validate motion data
    if (!motionData) {
      errors.push('Motion sensor data is missing');
    } else {
      if (motionData.accelerometer.length === 0) {
        errors.push('No accelerometer data collected');
      }
      if (motionData.gyroscope.length === 0) {
        errors.push('No gyroscope data collected');
      }
      if (motionData.accelerometer.length < 50) {
        errors.push('Insufficient accelerometer samples (need at least 50)');
      }
    }

    // Validate video frames
    if (videoFrames.length === 0) {
      errors.push('No video frames captured');
    } else if (videoFrames.length < 5) {
      errors.push('Insufficient video frames (need at least 5)');
    }

    return {
      valid: errors.length === 0,
      errors,
    };
  }

  /**
   * Get verification status
   */
  async getVerificationStatus(
    studentId: string,
    sessionId: string
  ): Promise<{verified: boolean; timestamp: string}> {
    try {
      const response = await api.get(`/verification-status`, {
        params: {student_id: studentId, session_id: sessionId},
      });
      return response.data;
    } catch (error) {
      console.error('[Verification] Status check error:', error);
      throw error;
    }
  }
}

// Singleton instance
let verificationService: VerificationService | null = null;

export const getVerificationService = (): VerificationService => {
  if (!verificationService) {
    verificationService = new VerificationService();
  }
  return verificationService;
};

export default getVerificationService;
