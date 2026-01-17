/**
 * Sensor Status Manager
 * Tracks status of all sensors and determines verification readiness
 */
import {SensorStatus} from '../types';

export interface SensorReadiness {
  ble: SensorStatus;
  gps: SensorStatus;
  barometer: SensorStatus;
  motion: SensorStatus;
  camera: SensorStatus;
  allReady: boolean;
  readySensors: string[];
  failedSensors: string[];
}

export type SensorType = 'ble' | 'gps' | 'barometer' | 'motion' | 'camera';

export class SensorStatusManager {
  private sensorStatuses: Map<SensorType, SensorStatus> = new Map();
  private listeners: Set<(readiness: SensorReadiness) => void> = new Set();

  constructor() {
    // Initialize all sensors as IDLE
    this.sensorStatuses.set('ble', SensorStatus.IDLE);
    this.sensorStatuses.set('gps', SensorStatus.IDLE);
    this.sensorStatuses.set('barometer', SensorStatus.IDLE);
    this.sensorStatuses.set('motion', SensorStatus.IDLE);
    this.sensorStatuses.set('camera', SensorStatus.IDLE);
  }

  /**
   * Update status for a specific sensor
   */
  updateSensorStatus(sensor: SensorType, status: SensorStatus): void {
    const previousStatus = this.sensorStatuses.get(sensor);
    
    if (previousStatus !== status) {
      this.sensorStatuses.set(sensor, status);
      console.log(`[SensorStatus] ${sensor} status changed: ${previousStatus} -> ${status}`);
      
      // Notify listeners
      this.notifyListeners();
    }
  }

  /**
   * Get status for a specific sensor
   */
  getSensorStatus(sensor: SensorType): SensorStatus {
    return this.sensorStatuses.get(sensor) || SensorStatus.IDLE;
  }

  /**
   * Get overall sensor readiness
   */
  getSensorReadiness(): SensorReadiness {
    const ble = this.sensorStatuses.get('ble') || SensorStatus.IDLE;
    const gps = this.sensorStatuses.get('gps') || SensorStatus.IDLE;
    const barometer = this.sensorStatuses.get('barometer') || SensorStatus.IDLE;
    const motion = this.sensorStatuses.get('motion') || SensorStatus.IDLE;
    const camera = this.sensorStatuses.get('camera') || SensorStatus.IDLE;

    const readySensors: string[] = [];
    const failedSensors: string[] = [];

    // Check each sensor
    if (ble === SensorStatus.READY) readySensors.push('ble');
    else if (ble === SensorStatus.FAILED || ble === SensorStatus.UNAVAILABLE) failedSensors.push('ble');

    if (gps === SensorStatus.READY) readySensors.push('gps');
    else if (gps === SensorStatus.FAILED || gps === SensorStatus.UNAVAILABLE) failedSensors.push('gps');

    if (barometer === SensorStatus.READY) readySensors.push('barometer');
    else if (barometer === SensorStatus.FAILED || barometer === SensorStatus.UNAVAILABLE) failedSensors.push('barometer');

    if (motion === SensorStatus.READY) readySensors.push('motion');
    else if (motion === SensorStatus.FAILED || motion === SensorStatus.UNAVAILABLE) failedSensors.push('motion');

    if (camera === SensorStatus.READY) readySensors.push('camera');
    else if (camera === SensorStatus.FAILED || camera === SensorStatus.UNAVAILABLE) failedSensors.push('camera');

    // All critical sensors must be ready (BLE, GPS, Camera)
    // Barometer and Motion can be optional with fallbacks
    const criticalReady = 
      ble === SensorStatus.READY &&
      gps === SensorStatus.READY &&
      camera === SensorStatus.READY;

    // At least one liveness method (motion or barometer)
    const livenessReady = 
      motion === SensorStatus.READY || 
      barometer === SensorStatus.READY;

    const allReady = criticalReady && livenessReady;

    return {
      ble,
      gps,
      barometer,
      motion,
      camera,
      allReady,
      readySensors,
      failedSensors,
    };
  }

  /**
   * Check if verification can proceed
   */
  canVerify(): boolean {
    return this.getSensorReadiness().allReady;
  }

  /**
   * Get human-readable status message
   */
  getStatusMessage(): string {
    const readiness = this.getSensorReadiness();

    if (readiness.allReady) {
      return 'All sensors ready - You can verify attendance';
    }

    const messages: string[] = [];

    if (readiness.ble !== SensorStatus.READY) {
      messages.push('Waiting for classroom beacon...');
    }

    if (readiness.gps !== SensorStatus.READY) {
      messages.push('Acquiring GPS location...');
    }

    if (readiness.camera !== SensorStatus.READY) {
      messages.push('Initializing camera...');
    }

    if (readiness.motion !== SensorStatus.READY && readiness.barometer !== SensorStatus.READY) {
      messages.push('Waiting for motion sensors...');
    }

    if (readiness.failedSensors.length > 0) {
      messages.push(`Failed sensors: ${readiness.failedSensors.join(', ')}`);
    }

    return messages.join(' | ');
  }

  /**
   * Subscribe to sensor status changes
   */
  onSensorStatusChange(callback: (readiness: SensorReadiness) => void): () => void {
    this.listeners.add(callback);

    // Return unsubscribe function
    return () => {
      this.listeners.delete(callback);
    };
  }

  /**
   * Notify all listeners of status change
   */
  private notifyListeners(): void {
    const readiness = this.getSensorReadiness();
    this.listeners.forEach(listener => {
      try {
        listener(readiness);
      } catch (error) {
        console.error('[SensorStatus] Listener error:', error);
      }
    });
  }

  /**
   * Reset all sensors to IDLE
   */
  reset(): void {
    this.sensorStatuses.set('ble', SensorStatus.IDLE);
    this.sensorStatuses.set('gps', SensorStatus.IDLE);
    this.sensorStatuses.set('barometer', SensorStatus.IDLE);
    this.sensorStatuses.set('motion', SensorStatus.IDLE);
    this.sensorStatuses.set('camera', SensorStatus.IDLE);
    this.notifyListeners();
  }

  /**
   * Get sensor count by status
   */
  getSensorCounts(): {ready: number; searching: number; failed: number; total: number} {
    let ready = 0;
    let searching = 0;
    let failed = 0;

    this.sensorStatuses.forEach(status => {
      if (status === SensorStatus.READY) ready++;
      else if (status === SensorStatus.SEARCHING) searching++;
      else if (status === SensorStatus.FAILED || status === SensorStatus.UNAVAILABLE) failed++;
    });

    return {ready, searching, failed, total: this.sensorStatuses.size};
  }
}

// Singleton instance
let sensorStatusManager: SensorStatusManager | null = null;

export const getSensorStatusManager = (): SensorStatusManager => {
  if (!sensorStatusManager) {
    sensorStatusManager = new SensorStatusManager();
  }
  return sensorStatusManager;
};

export default getSensorStatusManager;
