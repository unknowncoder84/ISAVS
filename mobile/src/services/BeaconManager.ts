/**
 * Beacon Manager Service (Teacher App)
 * Broadcasts BLE beacon signal for classroom proximity detection
 */
import BleManager from 'react-native-ble-manager';
import {NativeEventEmitter, NativeModules, Platform} from 'react-native';
import {SensorStatus} from '../types';

const BleManagerModule = NativeModules.BleManager;
const bleManagerEmitter = new NativeEventEmitter(BleManagerModule);

export interface BeaconStatus {
  isActive: boolean;
  sessionUUID: string;
  beaconUUID: string;
  startTime: number;
  connectedStudents: number;
}

export class BeaconManager {
  private isActive: boolean = false;
  private sessionUUID: string = '';
  private beaconUUID: string = '';
  private startTime: number = 0;
  private status: SensorStatus = SensorStatus.IDLE;
  private connectedStudents: Set<string> = new Set();

  constructor() {
    this.initialize();
  }

  /**
   * Initialize BLE Manager for peripheral mode
   */
  async initialize(): Promise<void> {
    try {
      await BleManager.start({showAlert: false});
      console.log('[Beacon] Manager initialized');
      this.status = SensorStatus.IDLE;
    } catch (error) {
      console.error('[Beacon] Initialization error:', error);
      this.status = SensorStatus.FAILED;
      throw error;
    }
  }

  /**
   * Start broadcasting BLE beacon
   * @param sessionUUID - Unique session identifier from backend
   */
  async startBeacon(sessionUUID: string): Promise<BeaconStatus> {
    if (this.isActive) {
      console.log('[Beacon] Already broadcasting');
      return this.getBeaconStatus();
    }

    try {
      this.sessionUUID = sessionUUID;
      this.beaconUUID = this.generateBeaconUUID();
      this.startTime = Date.now();
      this.status = SensorStatus.READY;

      if (Platform.OS === 'android') {
        await this.startAndroidBeacon();
      } else {
        await this.startIOSBeacon();
      }

      this.isActive = true;
      console.log(`[Beacon] Broadcasting started - Session: ${sessionUUID}, Beacon: ${this.beaconUUID}`);

      return this.getBeaconStatus();
    } catch (error) {
      console.error('[Beacon] Start error:', error);
      this.status = SensorStatus.FAILED;
      throw error;
    }
  }

  /**
   * Start beacon on Android
   */
  private async startAndroidBeacon(): Promise<void> {
    try {
      // Android BLE peripheral mode
      await BleManager.enableBluetooth();
      
      // Start advertising with session UUID
      // Note: react-native-ble-manager doesn't support peripheral mode directly
      // You may need to use a native module or react-native-ble-advertiser
      console.log('[Beacon] Android beacon started (requires native implementation)');
      
      // TODO: Implement native Android BLE advertising
      // For now, log a warning
      console.warn('[Beacon] Android peripheral mode requires native implementation');
    } catch (error) {
      console.error('[Beacon] Android beacon error:', error);
      throw error;
    }
  }

  /**
   * Start beacon on iOS
   */
  private async startIOSBeacon(): Promise<void> {
    try {
      // iOS BLE peripheral mode
      // Note: react-native-ble-manager doesn't support peripheral mode directly
      // You may need to use CoreBluetooth native module
      console.log('[Beacon] iOS beacon started (requires native implementation)');
      
      // TODO: Implement native iOS BLE advertising
      // For now, log a warning
      console.warn('[Beacon] iOS peripheral mode requires native implementation');
    } catch (error) {
      console.error('[Beacon] iOS beacon error:', error);
      throw error;
    }
  }

  /**
   * Stop broadcasting BLE beacon
   */
  async stopBeacon(): Promise<void> {
    if (!this.isActive) {
      console.log('[Beacon] Not broadcasting');
      return;
    }

    try {
      if (Platform.OS === 'android') {
        await this.stopAndroidBeacon();
      } else {
        await this.stopIOSBeacon();
      }

      this.isActive = false;
      this.status = SensorStatus.IDLE;
      this.connectedStudents.clear();
      console.log('[Beacon] Broadcasting stopped');
    } catch (error) {
      console.error('[Beacon] Stop error:', error);
      throw error;
    }
  }

  /**
   * Stop Android beacon
   */
  private async stopAndroidBeacon(): Promise<void> {
    // TODO: Implement native Android BLE advertising stop
    console.log('[Beacon] Android beacon stopped');
  }

  /**
   * Stop iOS beacon
   */
  private async stopIOSBeacon(): Promise<void> {
    // TODO: Implement native iOS BLE advertising stop
    console.log('[Beacon] iOS beacon stopped');
  }

  /**
   * Generate unique beacon UUID
   */
  private generateBeaconUUID(): string {
    // Generate UUID v4
    return 'xxxxxxxx-xxxx-4xxx-yxxx-xxxxxxxxxxxx'.replace(/[xy]/g, (c) => {
      const r = (Math.random() * 16) | 0;
      const v = c === 'x' ? r : (r & 0x3) | 0x8;
      return v.toString(16);
    });
  }

  /**
   * Get current beacon status
   */
  getBeaconStatus(): BeaconStatus {
    return {
      isActive: this.isActive,
      sessionUUID: this.sessionUUID,
      beaconUUID: this.beaconUUID,
      startTime: this.startTime,
      connectedStudents: this.connectedStudents.size,
    };
  }

  /**
   * Register student detection
   * @param studentId - Student identifier
   */
  registerStudent(studentId: string): void {
    this.connectedStudents.add(studentId);
    console.log(`[Beacon] Student registered: ${studentId} (Total: ${this.connectedStudents.size})`);
  }

  /**
   * Get beacon UUID for session
   */
  getBeaconUUID(): string {
    return this.beaconUUID;
  }

  /**
   * Get session UUID
   */
  getSessionUUID(): string {
    return this.sessionUUID;
  }

  /**
   * Check if beacon is active
   */
  isBeaconActive(): boolean {
    return this.isActive;
  }

  /**
   * Get beacon uptime in seconds
   */
  getUptime(): number {
    if (!this.isActive) return 0;
    return Math.floor((Date.now() - this.startTime) / 1000);
  }

  /**
   * Clean up
   */
  async cleanup(): Promise<void> {
    if (this.isActive) {
      await this.stopBeacon();
    }
    this.connectedStudents.clear();
  }
}

// Singleton instance
let beaconManager: BeaconManager | null = null;

export const getBeaconManager = (): BeaconManager => {
  if (!beaconManager) {
    beaconManager = new BeaconManager();
  }
  return beaconManager;
};

export default getBeaconManager;
