/**
 * Enhanced Geolocation Service
 * Combines GPS with barometric pressure for enhanced location verification
 */
import Geolocation from '@react-native-community/geolocation';
import {LocationData, PressureData, SensorStatus} from '../types';
import {getBarometerService} from './BarometerService';

export class EnhancedGeolocationService {
  private status: SensorStatus = SensorStatus.IDLE;
  private currentLocation: LocationData | null = null;
  private watchId: number | null = null;

  /**
   * Get current location with pressure reading
   */
  async getCurrentLocation(): Promise<{location: LocationData; pressure: PressureData}> {
    try {
      this.status = SensorStatus.SEARCHING;

      // Get GPS location
      const location = await this.getGPSLocation();

      // Get barometric pressure
      const barometerService = getBarometerService();
      const pressure = await barometerService.getPressureData();

      this.currentLocation = location;
      this.status = SensorStatus.READY;

      console.log('[EnhancedGeo] Location acquired:', {
        lat: location.latitude.toFixed(6),
        lon: location.longitude.toFixed(6),
        accuracy: location.accuracy.toFixed(1),
        pressure: pressure.pressure.toFixed(2),
      });

      return {location, pressure};
    } catch (error) {
      console.error('[EnhancedGeo] Get location error:', error);
      this.status = SensorStatus.FAILED;
      throw error;
    }
  }

  /**
   * Get GPS location
   */
  private getGPSLocation(): Promise<LocationData> {
    return new Promise((resolve, reject) => {
      Geolocation.getCurrentPosition(
        position => {
          const location: LocationData = {
            latitude: position.coords.latitude,
            longitude: position.coords.longitude,
            accuracy: position.coords.accuracy,
            timestamp: position.timestamp,
          };

          // Validate GPS accuracy
          if (location.accuracy > 20) {
            console.warn('[EnhancedGeo] Low GPS accuracy:', location.accuracy, 'm');
          }

          resolve(location);
        },
        error => {
          console.error('[EnhancedGeo] GPS error:', error);
          reject(error);
        },
        {
          enableHighAccuracy: true,
          timeout: 15000,
          maximumAge: 10000,
        }
      );
    });
  }

  /**
   * Start watching location changes
   */
  startWatching(callback: (location: LocationData) => void): void {
    if (this.watchId !== null) {
      console.log('[EnhancedGeo] Already watching');
      return;
    }

    this.watchId = Geolocation.watchPosition(
      position => {
        const location: LocationData = {
          latitude: position.coords.latitude,
          longitude: position.coords.longitude,
          accuracy: position.coords.accuracy,
          timestamp: position.timestamp,
        };

        this.currentLocation = location;
        callback(location);
      },
      error => {
        console.error('[EnhancedGeo] Watch error:', error);
        this.status = SensorStatus.FAILED;
      },
      {
        enableHighAccuracy: true,
        distanceFilter: 10, // Update every 10 meters
        interval: 5000, // Update every 5 seconds
      }
    );

    console.log('[EnhancedGeo] Watching started');
  }

  /**
   * Stop watching location changes
   */
  stopWatching(): void {
    if (this.watchId !== null) {
      Geolocation.clearWatch(this.watchId);
      this.watchId = null;
      console.log('[EnhancedGeo] Watching stopped');
    }
  }

  /**
   * Calculate distance between two GPS coordinates using Haversine formula
   * @returns Distance in meters
   */
  calculateDistance(
    lat1: number,
    lon1: number,
    lat2: number,
    lon2: number
  ): number {
    const R = 6371000; // Earth's radius in meters
    const φ1 = (lat1 * Math.PI) / 180;
    const φ2 = (lat2 * Math.PI) / 180;
    const Δφ = ((lat2 - lat1) * Math.PI) / 180;
    const Δλ = ((lon2 - lon1) * Math.PI) / 180;

    const a =
      Math.sin(Δφ / 2) * Math.sin(Δφ / 2) +
      Math.cos(φ1) * Math.cos(φ2) * Math.sin(Δλ / 2) * Math.sin(Δλ / 2);

    const c = 2 * Math.atan2(Math.sqrt(a), Math.sqrt(1 - a));

    const distance = R * c;
    return distance;
  }

  /**
   * Validate GPS accuracy
   */
  validateAccuracy(location: LocationData, maxAccuracy: number = 20): boolean {
    return location.accuracy <= maxAccuracy;
  }

  /**
   * Request location permission
   */
  async requestPermission(): Promise<boolean> {
    try {
      if (Platform.OS === 'android') {
        const {PermissionsAndroid} = require('react-native');
        const granted = await PermissionsAndroid.request(
          PermissionsAndroid.PERMISSIONS.ACCESS_FINE_LOCATION,
          {
            title: 'Location Permission',
            message: 'This app needs access to your location for attendance verification',
            buttonNeutral: 'Ask Me Later',
            buttonNegative: 'Cancel',
            buttonPositive: 'OK',
          }
        );
        return granted === PermissionsAndroid.RESULTS.GRANTED;
      }
      return true; // iOS handles permissions via Info.plist
    } catch (error) {
      console.error('[EnhancedGeo] Permission request error:', error);
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
   * Get last known location
   */
  getLastLocation(): LocationData | null {
    return this.currentLocation;
  }

  /**
   * Clean up
   */
  cleanup(): void {
    this.stopWatching();
    this.currentLocation = null;
    this.status = SensorStatus.IDLE;
  }
}

// Singleton instance
let enhancedGeolocationService: EnhancedGeolocationService | null = null;

export const getEnhancedGeolocationService = (): EnhancedGeolocationService => {
  if (!enhancedGeolocationService) {
    enhancedGeolocationService = new EnhancedGeolocationService();
  }
  return enhancedGeolocationService;
};

export default getEnhancedGeolocationService;
