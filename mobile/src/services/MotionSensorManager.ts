/**
 * Motion Sensor Manager
 * Manages accelerometer and gyroscope data collection for liveness detection
 */
import {accelerometer, gyroscope, SensorData} from 'react-native-sensors';
import {Subscription} from 'rxjs';
import {MotionData, AccelerometerData, GyroscopeData, SensorStatus} from '../types';
import {TIMING} from '../constants/config';

export class MotionSensorManager {
  private accelerometerSubscription: Subscription | null = null;
  private gyroscopeSubscription: Subscription | null = null;
  private accelerometerData: AccelerometerData[] = [];
  private gyroscopeData: GyroscopeData[] = [];
  private isRecording: boolean = false;
  private startTime: number = 0;
  private status: SensorStatus = SensorStatus.IDLE;
  private targetSamples: number = 100; // 2 seconds at 50Hz

  /**
   * Start recording motion data
   * @param duration - Duration in milliseconds (default: 2000ms)
   */
  async startRecording(duration: number = 2000): Promise<void> {
    if (this.isRecording) {
      console.log('[Motion] Already recording');
      return;
    }

    try {
      this.status = SensorStatus.SEARCHING;
      this.accelerometerData = [];
      this.gyroscopeData = [];
      this.startTime = Date.now();
      this.isRecording = true;

      console.log('[Motion] Starting recording for', duration, 'ms');

      // Subscribe to accelerometer at 50Hz (20ms interval)
      this.accelerometerSubscription = accelerometer.subscribe(
        (data: SensorData) => {
          if (this.isRecording) {
            this.accelerometerData.push({
              x: data.x,
              y: data.y,
              z: data.z,
              timestamp: data.timestamp || Date.now(),
            });
          }
        },
        (error: any) => {
          console.error('[Motion] Accelerometer error:', error);
          this.status = SensorStatus.FAILED;
        }
      );

      // Subscribe to gyroscope at 50Hz (20ms interval)
      this.gyroscopeSubscription = gyroscope.subscribe(
        (data: SensorData) => {
          if (this.isRecording) {
            this.gyroscopeData.push({
              x: data.x,
              y: data.y,
              z: data.z,
              timestamp: data.timestamp || Date.now(),
            });
          }
        },
        (error: any) => {
          console.error('[Motion] Gyroscope error:', error);
          this.status = SensorStatus.FAILED;
        }
      );

      // Auto-stop after duration
      setTimeout(() => {
        if (this.isRecording) {
          this.stopRecording();
        }
      }, duration);

      this.status = SensorStatus.READY;
    } catch (error) {
      console.error('[Motion] Start recording error:', error);
      this.status = SensorStatus.FAILED;
      throw error;
    }
  }

  /**
   * Stop recording and return collected data
   */
  stopRecording(): MotionData {
    if (!this.isRecording) {
      console.log('[Motion] Not recording');
      return this.getEmptyMotionData();
    }

    try {
      // Unsubscribe from sensors
      if (this.accelerometerSubscription) {
        this.accelerometerSubscription.unsubscribe();
        this.accelerometerSubscription = null;
      }

      if (this.gyroscopeSubscription) {
        this.gyroscopeSubscription.unsubscribe();
        this.gyroscopeSubscription = null;
      }

      this.isRecording = false;
      const endTime = Date.now();

      // Calculate sampling rate
      const duration = (endTime - this.startTime) / 1000; // seconds
      const samplingRate = this.accelerometerData.length / duration;

      console.log('[Motion] Recording stopped:', {
        accelerometerSamples: this.accelerometerData.length,
        gyroscopeSamples: this.gyroscopeData.length,
        duration: duration.toFixed(2),
        samplingRate: samplingRate.toFixed(1),
      });

      const motionData: MotionData = {
        accelerometer: this.accelerometerData,
        gyroscope: this.gyroscopeData,
        startTime: this.startTime,
        endTime,
      };

      this.status = SensorStatus.IDLE;
      return motionData;
    } catch (error) {
      console.error('[Motion] Stop recording error:', error);
      this.status = SensorStatus.FAILED;
      return this.getEmptyMotionData();
    }
  }

  /**
   * Detect nod motion (vertical head movement)
   * Checks for z-axis acceleration > 0.5 m/s²
   */
  detectNod(data: AccelerometerData[]): boolean {
    if (data.length < 10) {
      return false;
    }

    try {
      // Calculate z-axis acceleration changes
      let maxZChange = 0;

      for (let i = 1; i < data.length; i++) {
        const zChange = Math.abs(data[i].z - data[i - 1].z);
        if (zChange > maxZChange) {
          maxZChange = zChange;
        }
      }

      const nodDetected = maxZChange > 0.5;
      console.log('[Motion] Nod detection:', {
        maxZChange: maxZChange.toFixed(3),
        threshold: 0.5,
        detected: nodDetected,
      });

      return nodDetected;
    } catch (error) {
      console.error('[Motion] Nod detection error:', error);
      return false;
    }
  }

  /**
   * Detect shake motion (horizontal head rotation)
   * Checks for y-axis angular velocity > 0.3 rad/s
   */
  detectShake(data: GyroscopeData[]): boolean {
    if (data.length < 10) {
      return false;
    }

    try {
      // Find maximum y-axis angular velocity
      let maxYVelocity = 0;

      for (const sample of data) {
        const yVelocity = Math.abs(sample.y);
        if (yVelocity > maxYVelocity) {
          maxYVelocity = yVelocity;
        }
      }

      const shakeDetected = maxYVelocity > 0.3;
      console.log('[Motion] Shake detection:', {
        maxYVelocity: maxYVelocity.toFixed(3),
        threshold: 0.3,
        detected: shakeDetected,
      });

      return shakeDetected;
    } catch (error) {
      console.error('[Motion] Shake detection error:', error);
      return false;
    }
  }

  /**
   * Get current sampling rate
   */
  getSamplingRate(): number {
    if (!this.isRecording || this.accelerometerData.length < 2) {
      return 0;
    }

    const duration = (Date.now() - this.startTime) / 1000; // seconds
    return this.accelerometerData.length / duration;
  }

  /**
   * Get recording progress (0-1)
   */
  getProgress(): number {
    if (!this.isRecording) {
      return 0;
    }

    return Math.min(this.accelerometerData.length / this.targetSamples, 1);
  }

  /**
   * Check if sufficient motion detected
   */
  hasSufficientMotion(): boolean {
    const nodDetected = this.detectNod(this.accelerometerData);
    const shakeDetected = this.detectShake(this.gyroscopeData);
    return nodDetected || shakeDetected;
  }

  /**
   * Get current status
   */
  getStatus(): SensorStatus {
    return this.status;
  }

  /**
   * Check if sensors are available
   */
  async checkAvailability(): Promise<{accelerometer: boolean; gyroscope: boolean}> {
    try {
      // Try to subscribe briefly to check availability
      let accelAvailable = false;
      let gyroAvailable = false;

      const accelSub = accelerometer.subscribe(
        () => {
          accelAvailable = true;
        },
        () => {
          accelAvailable = false;
        }
      );

      const gyroSub = gyroscope.subscribe(
        () => {
          gyroAvailable = true;
        },
        () => {
          gyroAvailable = false;
        }
      );

      // Wait briefly
      await new Promise(resolve => setTimeout(resolve, 100));

      // Unsubscribe
      accelSub.unsubscribe();
      gyroSub.unsubscribe();

      return {accelerometer: accelAvailable, gyroscope: gyroAvailable};
    } catch (error) {
      console.error('[Motion] Availability check error:', error);
      return {accelerometer: false, gyroscope: false};
    }
  }

  /**
   * Get empty motion data
   */
  private getEmptyMotionData(): MotionData {
    return {
      accelerometer: [],
      gyroscope: [],
      startTime: 0,
      endTime: 0,
    };
  }

  /**
   * Clean up
   */
  cleanup(): void {
    if (this.isRecording) {
      this.stopRecording();
    }
    this.accelerometerData = [];
    this.gyroscopeData = [];
    this.status = SensorStatus.IDLE;
  }
}

// Singleton instance
let motionSensorManager: MotionSensorManager | null = null;

export const getMotionSensorManager = (): MotionSensorManager => {
  if (!motionSensorManager) {
    motionSensorManager = new MotionSensorManager();
  }
  return motionSensorManager;
};

export default getMotionSensorManager;
