/**
 * Camera Service
 * High-performance camera capture for face verification and motion correlation
 */
import {Camera, useCameraDevices, CameraDevice} from 'react-native-vision-camera';
import {SensorStatus} from '../types';

export class CameraService {
  private camera: Camera | null = null;
  private status: SensorStatus = SensorStatus.IDLE;
  private capturedFrames: string[] = [];
  private frameTimestamps: number[] = [];

  /**
   * Initialize camera
   */
  async initialize(): Promise<void> {
    try {
      // Request camera permission
      const permission = await Camera.requestCameraPermission();
      
      if (permission === 'denied') {
        this.status = SensorStatus.UNAVAILABLE;
        throw new Error('Camera permission denied');
      }

      this.status = SensorStatus.IDLE;
      console.log('[Camera] Initialized');
    } catch (error) {
      console.error('[Camera] Initialization error:', error);
      this.status = SensorStatus.FAILED;
      throw error;
    }
  }

  /**
   * Capture multiple frames over a duration
   * @param count - Number of frames to capture
   * @param duration - Duration in milliseconds
   * @returns Array of base64 encoded frames
   */
  async captureFrames(count: number = 10, duration: number = 2000): Promise<{frames: string[]; timestamps: number[]}> {
    if (!this.camera) {
      throw new Error('Camera not initialized');
    }

    try {
      this.status = SensorStatus.SEARCHING;
      this.capturedFrames = [];
      this.frameTimestamps = [];

      const interval = duration / count;
      console.log('[Camera] Capturing', count, 'frames over', duration, 'ms (interval:', interval, 'ms)');

      for (let i = 0; i < count; i++) {
        try {
          const timestamp = Date.now();
          
          // Take photo
          const photo = await this.camera.takePhoto({
            qualityPrioritization: 'speed',
            flash: 'off',
            enableShutterSound: false,
          });

          // Convert to base64
          const base64 = await this.photoToBase64(photo.path);
          
          this.capturedFrames.push(base64);
          this.frameTimestamps.push(timestamp);

          console.log(`[Camera] Frame ${i + 1}/${count} captured at ${timestamp}`);

          // Wait for next frame (except for last frame)
          if (i < count - 1) {
            await new Promise(resolve => setTimeout(resolve, interval));
          }
        } catch (error) {
          console.error(`[Camera] Frame ${i + 1} capture error:`, error);
        }
      }

      this.status = SensorStatus.READY;
      console.log('[Camera] Capture complete:', this.capturedFrames.length, 'frames');

      return {
        frames: this.capturedFrames,
        timestamps: this.frameTimestamps,
      };
    } catch (error) {
      console.error('[Camera] Capture frames error:', error);
      this.status = SensorStatus.FAILED;
      throw error;
    }
  }

  /**
   * Capture a single frame
   */
  async captureSingleFrame(): Promise<{frame: string; timestamp: number}> {
    if (!this.camera) {
      throw new Error('Camera not initialized');
    }

    try {
      const timestamp = Date.now();
      
      const photo = await this.camera.takePhoto({
        qualityPrioritization: 'balanced',
        flash: 'off',
        enableShutterSound: false,
      });

      const base64 = await this.photoToBase64(photo.path);

      console.log('[Camera] Single frame captured');

      return {frame: base64, timestamp};
    } catch (error) {
      console.error('[Camera] Single frame capture error:', error);
      throw error;
    }
  }

  /**
   * Convert photo path to base64
   */
  private async photoToBase64(path: string): Promise<string> {
    try {
      const RNFS = require('react-native-fs');
      const base64 = await RNFS.readFile(path, 'base64');
      
      // Delete temporary file
      await RNFS.unlink(path);
      
      return base64;
    } catch (error) {
      console.error('[Camera] Photo to base64 error:', error);
      throw error;
    }
  }

  /**
   * Get frame timestamps
   */
  getFrameTimestamps(): number[] {
    return this.frameTimestamps;
  }

  /**
   * Validate timestamp monotonicity
   * Ensures timestamps are strictly increasing
   */
  validateTimestampMonotonicity(timestamps: number[]): boolean {
    for (let i = 1; i < timestamps.length; i++) {
      if (timestamps[i] <= timestamps[i - 1]) {
        console.warn('[Camera] Timestamp monotonicity violation at index', i);
        return false;
      }
    }
    return true;
  }

  /**
   * Compress frames for transmission
   * Reduces quality to minimize data size
   */
  async compressFrames(frames: string[]): Promise<string[]> {
    // TODO: Implement frame compression
    // For now, return frames as-is
    console.log('[Camera] Compression not implemented, returning original frames');
    return frames;
  }

  /**
   * Set camera reference
   */
  setCameraRef(camera: Camera): void {
    this.camera = camera;
  }

  /**
   * Get available camera devices
   */
  static async getAvailableDevices(): Promise<CameraDevice[]> {
    try {
      const devices = await Camera.getAvailableCameraDevices();
      console.log('[Camera] Available devices:', devices.length);
      return devices;
    } catch (error) {
      console.error('[Camera] Get devices error:', error);
      return [];
    }
  }

  /**
   * Get front camera device
   */
  static getFrontCamera(devices: CameraDevice[]): CameraDevice | undefined {
    return devices.find(device => device.position === 'front');
  }

  /**
   * Check camera permission
   */
  static async checkPermission(): Promise<boolean> {
    try {
      const permission = await Camera.getCameraPermissionStatus();
      return permission === 'authorized';
    } catch (error) {
      console.error('[Camera] Check permission error:', error);
      return false;
    }
  }

  /**
   * Request camera permission
   */
  static async requestPermission(): Promise<boolean> {
    try {
      const permission = await Camera.requestCameraPermission();
      return permission === 'authorized';
    } catch (error) {
      console.error('[Camera] Request permission error:', error);
      return false;
    }
  }

  /**
   * Get current status
   */
  getStatus(): SensorStatus {
    return this.status;
  }

  /**
   * Get captured frames count
   */
  getFramesCount(): number {
    return this.capturedFrames.length;
  }

  /**
   * Clear captured frames
   */
  clearFrames(): void {
    this.capturedFrames = [];
    this.frameTimestamps = [];
  }

  /**
   * Clean up
   */
  cleanup(): void {
    this.clearFrames();
    this.camera = null;
    this.status = SensorStatus.IDLE;
  }
}

// Singleton instance
let cameraService: CameraService | null = null;

export const getCameraService = (): CameraService => {
  if (!cameraService) {
    cameraService = new CameraService();
  }
  return cameraService;
};

export default getCameraService;
