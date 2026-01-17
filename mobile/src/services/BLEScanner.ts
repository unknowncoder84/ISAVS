/**
 * BLE Scanner Service (Student App)
 * Scans for classroom beacons and measures RSSI for proximity detection
 */
import BleManager, {Peripheral} from 'react-native-ble-manager';
import {NativeEventEmitter, NativeModules, Platform} from 'react-native';
import {BeaconData, SensorStatus} from '../types';
import {APP_CONFIG, TIMING} from '../constants/config';

const BleManagerModule = NativeModules.BleManager;
const bleManagerEmitter = new NativeEventEmitter(BleManagerModule);

export class BLEScanner {
  private isScanning: boolean = false;
  private detectedBeacons: Map<string, BeaconData> = new Map();
  private rssiHistory: Map<string, number[]> = new Map();
  private scanListener: any = null;
  private status: SensorStatus = SensorStatus.IDLE;

  constructor() {
    this.initialize();
  }

  /**
   * Initialize BLE Manager
   */
  async initialize(): Promise<void> {
    try {
      await BleManager.start({showAlert: false});
      console.log('[BLE] Manager initialized');
      
      // Check if Bluetooth is enabled
      const isEnabled = await this.checkBluetoothEnabled();
      if (!isEnabled) {
        this.status = SensorStatus.UNAVAILABLE;
        throw new Error('Bluetooth is not enabled');
      }
      
      this.status = SensorStatus.IDLE;
    } catch (error) {
      console.error('[BLE] Initialization error:', error);
      this.status = SensorStatus.FAILED;
      throw error;
    }
  }

  /**
   * Check if Bluetooth is enabled
   */
  async checkBluetoothEnabled(): Promise<boolean> {
    try {
      if (Platform.OS === 'android') {
        return await BleManager.checkState();
      }
      // iOS always returns true if permission granted
      return true;
    } catch (error) {
      console.error('[BLE] Check state error:', error);
      return false;
    }
  }

  /**
   * Request Bluetooth permissions
   */
  async requestPermissions(): Promise<boolean> {
    try {
      if (Platform.OS === 'android') {
        // Android 12+ requires BLUETOOTH_SCAN permission
        const {PermissionsAndroid} = require('react-native');
        const granted = await PermissionsAndroid.requestMultiple([
          PermissionsAndroid.PERMISSIONS.BLUETOOTH_SCAN,
          PermissionsAndroid.PERMISSIONS.BLUETOOTH_CONNECT,
          PermissionsAndroid.PERMISSIONS.ACCESS_FINE_LOCATION,
        ]);
        
        return Object.values(granted).every(
          status => status === PermissionsAndroid.RESULTS.GRANTED
        );
      }
      return true; // iOS handles permissions via Info.plist
    } catch (error) {
      console.error('[BLE] Permission request error:', error);
      return false;
    }
  }

  /**
   * Start scanning for beacons
   */
  async startScanning(targetUUID?: string): Promise<void> {
    if (this.isScanning) {
      console.log('[BLE] Already scanning');
      return;
    }

    try {
      this.status = SensorStatus.SEARCHING;
      
      // Clear previous data
      this.detectedBeacons.clear();
      this.rssiHistory.clear();

      // Set up listener for discovered peripherals
      this.scanListener = bleManagerEmitter.addListener(
        'BleManagerDiscoverPeripheral',
        (peripheral: Peripheral) => {
          this.handleDiscoveredPeripheral(peripheral, targetUUID);
        }
      );

      // Start scanning
      await BleManager.scan(
        [], // Service UUIDs (empty = scan all)
        TIMING.BLE_SCAN_DURATION_MS / 1000, // Duration in seconds
        true // Allow duplicates for RSSI updates
      );

      this.isScanning = true;
      console.log('[BLE] Scanning started');

      // Auto-restart scanning after interval
      setTimeout(() => {
        if (this.isScanning) {
          this.restartScanning(targetUUID);
        }
      }, TIMING.BLE_SCAN_DURATION_MS + TIMING.BLE_SCAN_INTERVAL_MS);

    } catch (error) {
      console.error('[BLE] Start scanning error:', error);
      this.status = SensorStatus.FAILED;
      throw error;
    }
  }

  /**
   * Restart scanning (for continuous monitoring)
   */
  private async restartScanning(targetUUID?: string): Promise<void> {
    try {
      await BleManager.stopScan();
      await new Promise(resolve => setTimeout(resolve, 100)); // Small delay
      await this.startScanning(targetUUID);
    } catch (error) {
      console.error('[BLE] Restart scanning error:', error);
    }
  }

  /**
   * Stop scanning
   */
  async stopScanning(): Promise<void> {
    try {
      if (this.scanListener) {
        this.scanListener.remove();
        this.scanListener = null;
      }

      await BleManager.stopScan();
      this.isScanning = false;
      this.status = SensorStatus.IDLE;
      console.log('[BLE] Scanning stopped');
    } catch (error) {
      console.error('[BLE] Stop scanning error:', error);
    }
  }

  /**
   * Handle discovered peripheral
   */
  private handleDiscoveredPeripheral(
    peripheral: Peripheral,
    targetUUID?: string
  ): void {
    const {id, name, rssi, advertising} = peripheral;

    // Filter by target UUID if specified
    if (targetUUID) {
      const hasTargetUUID = 
        advertising?.serviceUUIDs?.includes(targetUUID) ||
        name?.includes(targetUUID) ||
        id === targetUUID;

      if (!hasTargetUUID) {
        return;
      }
    }

    // Filter by beacon name pattern (ISAVS classroom beacons)
    if (name && !name.includes('ISAVS') && !name.includes('CLASSROOM')) {
      return;
    }

    // Store RSSI for averaging
    if (!this.rssiHistory.has(id)) {
      this.rssiHistory.set(id, []);
    }
    const history = this.rssiHistory.get(id)!;
    history.push(rssi);

    // Keep only last 10 readings for 3-second average
    if (history.length > 10) {
      history.shift();
    }

    // Calculate average RSSI
    const avgRSSI = history.reduce((sum, val) => sum + val, 0) / history.length;

    // Calculate distance
    const distance = this.calculateDistance(avgRSSI);

    // Update beacon data
    const beaconData: BeaconData = {
      uuid: id,
      rssi: avgRSSI,
      distance,
      name: name || 'Unknown Beacon',
    };

    this.detectedBeacons.set(id, beaconData);

    // Update status
    if (avgRSSI > APP_CONFIG.bleRSSIThreshold) {
      this.status = SensorStatus.READY;
    }

    console.log(`[BLE] Beacon detected: ${name} (${id}), RSSI: ${avgRSSI.toFixed(1)} dBm, Distance: ${distance.toFixed(1)}m`);
  }

  /**
   * Get RSSI for a specific beacon (with 3-second averaging)
   */
  getRSSI(beaconUUID: string): number | null {
    const beacon = this.detectedBeacons.get(beaconUUID);
    return beacon ? beacon.rssi : null;
  }

  /**
   * Get all detected beacons
   */
  getDetectedBeacons(): BeaconData[] {
    return Array.from(this.detectedBeacons.values());
  }

  /**
   * Get closest beacon
   */
  getClosestBeacon(): BeaconData | null {
    const beacons = this.getDetectedBeacons();
    if (beacons.length === 0) return null;

    return beacons.reduce((closest, current) => 
      current.rssi > closest.rssi ? current : closest
    );
  }

  /**
   * Calculate estimated distance from RSSI using log-distance path loss model
   * Formula: d = 10^((TxPower - RSSI) / (10 * n))
   * 
   * @param rssi - Received Signal Strength Indicator in dBm
   * @returns Estimated distance in meters
   */
  calculateDistance(rssi: number): number {
    const txPower = -59; // Measured power at 1 meter (typical for BLE)
    const pathLossExponent = 2; // Free space path loss exponent

    const distance = Math.pow(10, (txPower - rssi) / (10 * pathLossExponent));
    return Math.max(0, distance); // Ensure non-negative
  }

  /**
   * Check if within proximity threshold
   */
  isWithinProximity(beaconUUID?: string): boolean {
    if (beaconUUID) {
      const rssi = this.getRSSI(beaconUUID);
      return rssi !== null && rssi > APP_CONFIG.bleRSSIThreshold;
    }

    // Check any beacon
    const closest = this.getClosestBeacon();
    return closest !== null && closest.rssi > APP_CONFIG.bleRSSIThreshold;
  }

  /**
   * Get current status
   */
  getStatus(): SensorStatus {
    return this.status;
  }

  /**
   * Clean up
   */
  async cleanup(): Promise<void> {
    await this.stopScanning();
    this.detectedBeacons.clear();
    this.rssiHistory.clear();
  }
}

// Singleton instance
let bleScanner: BLEScanner | null = null;

export const getBLEScanner = (): BLEScanner => {
  if (!bleScanner) {
    bleScanner = new BLEScanner();
  }
  return bleScanner;
};

export default getBLEScanner;
