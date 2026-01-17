/**
 * BLE Proximity Hook
 * Manages BLE scanning and proximity detection with RSSI-based button control
 */
import {useState, useEffect, useCallback} from 'react';
import {getBLEScanner} from '../services/BLEScanner';
import {BeaconData, SensorStatus} from '../types';
import {APP_CONFIG} from '../constants/config';

interface UseBLEProximityResult {
  isReady: boolean;
  status: SensorStatus;
  rssi: number | null;
  distance: number | null;
  beaconData: BeaconData | null;
  error: string | null;
  startScanning: () => Promise<void>;
  stopScanning: () => Promise<void>;
  retry: () => Promise<void>;
}

export const useBLEProximity = (targetUUID?: string): UseBLEProximityResult => {
  const [isReady, setIsReady] = useState(false);
  const [status, setStatus] = useState<SensorStatus>(SensorStatus.IDLE);
  const [rssi, setRSSI] = useState<number | null>(null);
  const [distance, setDistance] = useState<number | null>(null);
  const [beaconData, setBeaconData] = useState<BeaconData | null>(null);
  const [error, setError] = useState<string | null>(null);

  const scanner = getBLEScanner();

  /**
   * Update proximity state based on detected beacons
   */
  const updateProximityState = useCallback(() => {
    try {
      const closestBeacon = targetUUID
        ? scanner.getDetectedBeacons().find(b => b.uuid === targetUUID)
        : scanner.getClosestBeacon();

      if (closestBeacon) {
        setBeaconData(closestBeacon);
        setRSSI(closestBeacon.rssi);
        setDistance(closestBeacon.distance);

        // Check if within proximity threshold
        const withinRange = closestBeacon.rssi > APP_CONFIG.bleRSSIThreshold;
        setIsReady(withinRange);
        setStatus(withinRange ? SensorStatus.READY : SensorStatus.SEARCHING);
        setError(null);
      } else {
        setBeaconData(null);
        setRSSI(null);
        setDistance(null);
        setIsReady(false);
        setStatus(SensorStatus.SEARCHING);
      }
    } catch (err) {
      console.error('[useBLEProximity] Update error:', err);
      setError(err instanceof Error ? err.message : 'Unknown error');
      setStatus(SensorStatus.FAILED);
    }
  }, [targetUUID, scanner]);

  /**
   * Start BLE scanning
   */
  const startScanning = useCallback(async () => {
    try {
      setStatus(SensorStatus.SEARCHING);
      setError(null);

      // Request permissions
      const hasPermission = await scanner.requestPermissions();
      if (!hasPermission) {
        setError('Bluetooth permission denied');
        setStatus(SensorStatus.UNAVAILABLE);
        return;
      }

      // Check if Bluetooth is enabled
      const isEnabled = await scanner.checkBluetoothEnabled();
      if (!isEnabled) {
        setError('Bluetooth is not enabled');
        setStatus(SensorStatus.UNAVAILABLE);
        return;
      }

      // Start scanning
      await scanner.startScanning(targetUUID);
      console.log('[useBLEProximity] Scanning started');
    } catch (err) {
      console.error('[useBLEProximity] Start scanning error:', err);
      setError(err instanceof Error ? err.message : 'Failed to start scanning');
      setStatus(SensorStatus.FAILED);
    }
  }, [targetUUID, scanner]);

  /**
   * Stop BLE scanning
   */
  const stopScanning = useCallback(async () => {
    try {
      await scanner.stopScanning();
      setStatus(SensorStatus.IDLE);
      setIsReady(false);
      setRSSI(null);
      setDistance(null);
      setBeaconData(null);
      console.log('[useBLEProximity] Scanning stopped');
    } catch (err) {
      console.error('[useBLEProximity] Stop scanning error:', err);
    }
  }, [scanner]);

  /**
   * Retry scanning
   */
  const retry = useCallback(async () => {
    await stopScanning();
    await new Promise(resolve => setTimeout(resolve, 500));
    await startScanning();
  }, [startScanning, stopScanning]);

  /**
   * Set up polling interval to update proximity state
   */
  useEffect(() => {
    if (status === SensorStatus.SEARCHING || status === SensorStatus.READY) {
      const interval = setInterval(() => {
        updateProximityState();
      }, 1000); // Update every second

      return () => clearInterval(interval);
    }
  }, [status, updateProximityState]);

  /**
   * Cleanup on unmount
   */
  useEffect(() => {
    return () => {
      stopScanning();
    };
  }, [stopScanning]);

  return {
    isReady,
    status,
    rssi,
    distance,
    beaconData,
    error,
    startScanning,
    stopScanning,
    retry,
  };
};

export default useBLEProximity;
