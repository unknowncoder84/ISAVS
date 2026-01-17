/**
 * Barometer Service (Mobile App)
 * Measures atmospheric pressure for floor-level verification
 */
import Barometer from 'react-native-barometer';
import {PressureData, SensorStatus} from '../types';

export class BarometerService {
  private isMonitoring: boolean = false;
  private currentPressure: number = 0;
  private status: SensorStatus = SensorStatus.IDLE;
  private listeners: Set<(pressure: number) => void> = new Set();

  /**
   * Get current barometric pressure
   */
  async getCurrentPressure(): Promise<number> {
    try {
      const pressure = await Barometer.getPressure();
      this.currentPressure = pressure;
      this.status = SensorStatus.READY;
      console.log('[Barometer] Current pressure:', pressure.toFixed(2), 'hPa');
      return pressure;
    } catch (error) {
      console.error('[Barometer] Get pressure error:', error);
      this.status = SensorStatus.UNAVAILABLE;
      throw error;
    }
  }

  /**
   * Start monitoring pressure changes
   * @param interval - Update interval in milliseconds
   */
  startMonitoring(interval: number = 1000): void {
    if (this.isMonitoring) {
      console.log('[Barometer] Already monitoring');
      return;
    }

    try {
      this.isMonitoring = true;
      this.status = SensorStatus.SEARCHING;

      // Poll pressure at interval
      const monitorInterval = setInterval(async () => {
        if (!this.isMonitoring) {
          clearInterval(monitorInterval);
          return;
        }

        try {
          const pressure = await this.getCurrentPressure();
          this.notifyListeners(pressure);
        } catch (error) {
          console.error('[Barometer] Monitoring error:', error);
          this.status = SensorStatus.FAILED;
        }
      }, interval);

      console.log('[Barometer] Monitoring started');
    } catch (error) {
      console.error('[Barometer] Start monitoring error:', error);
      this.status = SensorStatus.FAILED;
      throw error;
    }
  }

  /**
   * Stop monitoring pressure changes
   */
  stopMonitoring(): void {
    this.isMonitoring = false;
    this.status = SensorStatus.IDLE;
    console.log('[Barometer] Monitoring stopped');
  }

  /**
   * Subscribe to pressure changes
   */
  onPressureChange(callback: (pressure: number) => void): () => void {
    this.listeners.add(callback);

    // Return unsubscribe function
    return () => {
      this.listeners.delete(callback);
    };
  }

  /**
   * Notify all listeners of pressure change
   */
  private notifyListeners(pressure: number): void {
    this.listeners.forEach(listener => {
      try {
        listener(pressure);
      } catch (error) {
        console.error('[Barometer] Listener error:', error);
      }
    });
  }

  /**
   * Convert pressure to estimated altitude
   * Formula: h ≈ 44330 * (1 - (P/P0)^0.1903)
   * where P0 = 1013.25 hPa (sea level pressure)
   */
  pressureToAltitude(pressure: number, seaLevelPressure: number = 1013.25): number {
    const altitude = 44330 * (1 - Math.pow(pressure / seaLevelPressure, 0.1903));
    return altitude;
  }

  /**
   * Calculate altitude difference from pressure difference
   * Simplified: ΔH ≈ -8.5 * ΔP (meters per hPa)
   */
  pressureDifferenceToAltitude(pressureDiff: number): number {
    return -8.5 * pressureDiff;
  }

  /**
   * Get pressure data with timestamp
   */
  async getPressureData(): Promise<PressureData> {
    const pressure = await this.getCurrentPressure();
    const altitude = this.pressureToAltitude(pressure);

    return {
      pressure,
      altitude,
      timestamp: Date.now(),
    };
  }

  /**
   * Check if barometer is available
   */
  async checkAvailability(): Promise<boolean> {
    try {
      await this.getCurrentPressure();
      return true;
    } catch (error) {
      console.error('[Barometer] Availability check failed:', error);
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
   * Get last known pressure
   */
  getLastPressure(): number {
    return this.currentPressure;
  }

  /**
   * Clean up
   */
  cleanup(): void {
    this.stopMonitoring();
    this.listeners.clear();
    this.currentPressure = 0;
    this.status = SensorStatus.IDLE;
  }
}

// Singleton instance
let barometerService: BarometerService | null = null;

export const getBarometerService = (): BarometerService => {
  if (!barometerService) {
    barometerService = new BarometerService();
  }
  return barometerService;
};

export default getBarometerService;
