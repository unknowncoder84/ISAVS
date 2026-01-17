/**
 * Verification Screen (Student App)
 * Main screen for sensor-fused attendance verification
 */
import React, {useState, useEffect} from 'react';
import {
  View,
  Text,
  StyleSheet,
  TouchableOpacity,
  ScrollView,
  Alert,
  ActivityIndicator,
} from 'react-native';
import {useBLEProximity} from '../hooks/useBLEProximity';
import {BLEStatusIndicator} from '../components/BLEStatusIndicator';
import {LocationStatusIndicator} from '../components/LocationStatusIndicator';
import {MotionPrompt} from '../components/MotionPrompt';
import {FaceVerificationCamera} from '../components/FaceVerificationCamera';
import {getSensorStatusManager} from '../services/SensorStatusManager';
import {getVerificationService} from '../services/VerificationService';
import {getMotionSensorManager} from '../services/MotionSensorManager';
import {getEnhancedGeolocationService} from '../services/EnhancedGeolocationService';
import {getCameraService} from '../services/CameraService';
import {SensorStatus, LocationData, PressureData, MotionData} from '../types';
import {APP_CONFIG} from '../constants/config';

interface VerificationScreenProps {
  studentId: string;
  sessionId: string;
  onVerificationComplete: (success: boolean, result: any) => void;
}

export const VerificationScreen: React.FC<VerificationScreenProps> = ({
  studentId,
  sessionId,
  onVerificationComplete,
}) => {
  const [isVerifying, setIsVerifying] = useState(false);
  const [otp, setOTP] = useState('');
  const [faceImage, setFaceImage] = useState<string | null>(null);

  // BLE Proximity
  const {
    isReady: bleReady,
    status: bleStatus,
    rssi,
    distance,
    beaconData,
    startScanning,
    stopScanning,
    retry: retryBLE,
  } = useBLEProximity();

  // Sensor Status Manager
  const statusManager = getSensorStatusManager();
  const [sensorReadiness, setSensorReadiness] = useState(statusManager.getSensorReadiness());

  // Services
  const verificationService = getVerificationService();
  const motionManager = getMotionSensorManager();
  const geoService = getEnhancedGeolocationService();
  const cameraService = getCameraService();

  // Sensor Data State
  const [locationData, setLocationData] = useState<LocationData | null>(null);
  const [pressureData, setPressureData] = useState<PressureData | null>(null);
  const [motionData, setMotionData] = useState<MotionData | null>(null);
  const [videoFrames, setVideoFrames] = useState<string[]>([]);
  const [frameTimestamps, setFrameTimestamps] = useState<number[]>([]);
  
  // UI State
  const [showMotionPrompt, setShowMotionPrompt] = useState(false);
  const [showCamera, setShowCamera] = useState(false);
  const [motionProgress, setMotionProgress] = useState(0);

  /**
   * Initialize sensors on mount
   */
  useEffect(() => {
    initializeSensors();

    // Subscribe to sensor status changes
    const unsubscribe = statusManager.onSensorStatusChange(readiness => {
      setSensorReadiness(readiness);
    });

    return () => {
      unsubscribe();
      cleanup();
    };
  }, []);

  /**
   * Update BLE status in manager
   */
  useEffect(() => {
    statusManager.updateSensorStatus('ble', bleStatus);
  }, [bleStatus]);

  /**
   * Initialize all sensors
   */
  const initializeSensors = async () => {
    try {
      // Start BLE scanning
      await startScanning();

      // Initialize GPS + Barometer
      initializeLocation();

      // Initialize Motion sensors
      initializeMotion();

      // Initialize Camera
      initializeCamera();

      console.log('[Verification] Sensors initialized');
    } catch (error) {
      console.error('[Verification] Initialization error:', error);
      Alert.alert('Error', 'Failed to initialize sensors');
    }
  };

  /**
   * Initialize GPS and Barometer
   */
  const initializeLocation = async () => {
    try {
      statusManager.updateSensorStatus('gps', SensorStatus.SEARCHING);
      statusManager.updateSensorStatus('barometer', SensorStatus.SEARCHING);

      const location = await geoService.getCurrentLocation();
      
      if (location) {
        setLocationData(location.location);
        setPressureData(location.pressure);
        statusManager.updateSensorStatus('gps', SensorStatus.READY);
        statusManager.updateSensorStatus('barometer', SensorStatus.READY);
        console.log('[Verification] Location acquired:', location);
      } else {
        statusManager.updateSensorStatus('gps', SensorStatus.FAILED);
        statusManager.updateSensorStatus('barometer', SensorStatus.FAILED);
      }
    } catch (error) {
      console.error('[Verification] Location error:', error);
      statusManager.updateSensorStatus('gps', SensorStatus.FAILED);
      statusManager.updateSensorStatus('barometer', SensorStatus.FAILED);
    }
  };

  /**
   * Initialize Motion sensors
   */
  const initializeMotion = async () => {
    try {
      statusManager.updateSensorStatus('motion', SensorStatus.SEARCHING);
      
      const available = await motionManager.checkAvailability();
      if (available) {
        statusManager.updateSensorStatus('motion', SensorStatus.READY);
        console.log('[Verification] Motion sensors ready');
      } else {
        statusManager.updateSensorStatus('motion', SensorStatus.UNAVAILABLE);
      }
    } catch (error) {
      console.error('[Verification] Motion error:', error);
      statusManager.updateSensorStatus('motion', SensorStatus.FAILED);
    }
  };

  /**
   * Initialize Camera
   */
  const initializeCamera = async () => {
    try {
      statusManager.updateSensorStatus('camera', SensorStatus.SEARCHING);
      
      // Camera service doesn't have checkPermission, just mark as ready
      statusManager.updateSensorStatus('camera', SensorStatus.READY);
      console.log('[Verification] Camera ready');
    } catch (error) {
      console.error('[Verification] Camera error:', error);
      statusManager.updateSensorStatus('camera', SensorStatus.FAILED);
    }
  };

  /**
   * Cleanup sensors
   */
  const cleanup = async () => {
    await stopScanning();
    motionManager.stopRecording();
    geoService.stopWatching();
    statusManager.reset();
  };

  /**
   * Handle verification button press
   */
  const handleVerify = async () => {
    if (!sensorReadiness.allReady) {
      Alert.alert('Not Ready', statusManager.getStatusMessage());
      return;
    }

    if (!beaconData) {
      Alert.alert('Error', 'Beacon data not available');
      return;
    }

    setIsVerifying(true);

    try {
      // Step 1: Collect motion data
      console.log('[Verification] Starting motion collection...');
      setShowMotionPrompt(true);
      
      const collectedMotionData = await collectMotionData();
      setMotionData(collectedMotionData);
      setShowMotionPrompt(false);

      // Step 2: Capture video frames
      console.log('[Verification] Capturing video frames...');
      setShowCamera(true);
      
      const {frames, timestamps} = await collectVideoFrames();
      setVideoFrames(frames);
      setFrameTimestamps(timestamps);
      setShowCamera(false);

      // Step 3: Validate sensor data
      const validation = verificationService.validateSensorData(
        beaconData,
        locationData,
        pressureData,
        collectedMotionData,
        frames
      );

      if (!validation.valid) {
        Alert.alert('Validation Error', validation.errors.join('\n'));
        setIsVerifying(false);
        return;
      }

      // Step 4: Submit verification
      console.log('[Verification] Submitting verification...');
      const result = await verificationService.submitVerification(
        studentId,
        sessionId,
        otp,
        faceImage || '',
        beaconData,
        locationData!,
        pressureData!,
        collectedMotionData,
        frames,
        timestamps
      );

      console.log('[Verification] Result:', result);

      // Navigate to result screen
      onVerificationComplete(result.success, result);
    } catch (error: any) {
      console.error('[Verification] Error:', error);
      Alert.alert('Verification Failed', error.message || 'Unknown error');
      onVerificationComplete(false, null);
    } finally {
      setIsVerifying(false);
      setShowMotionPrompt(false);
      setShowCamera(false);
    }
  };

  /**
   * Collect motion sensor data
   */
  const collectMotionData = async (): Promise<MotionData> => {
    try {
      // Start recording for 2 seconds
      await motionManager.startRecording(2000);
      
      // Wait for recording to complete
      await new Promise(resolve => setTimeout(resolve, 2100));
      
      // Get the collected data
      const data = motionManager.stopRecording();
      
      console.log('[Verification] Motion data collected:', {
        accelerometerSamples: data.accelerometer.length,
        gyroscopeSamples: data.gyroscope.length,
      });
      
      return data;
    } catch (error) {
      console.error('[Verification] Motion collection error:', error);
      throw new Error('Failed to collect motion data');
    }
  };

  /**
   * Collect video frames
   */
  const collectVideoFrames = async (): Promise<{frames: string[]; timestamps: number[]}> => {
    try {
      const result = await cameraService.captureFrames(10, 2000);
      console.log('[Verification] Video frames captured:', result.frames.length);
      return result;
    } catch (error) {
      console.error('[Verification] Frame capture error:', error);
      throw new Error('Failed to capture video frames');
    }
  };

  /**
   * Get button color based on readiness
   */
  const getButtonColor = (): string => {
    if (isVerifying) return '#9CA3AF';
    return sensorReadiness.allReady ? '#10B981' : '#D1D5DB';
  };

  /**
   * Get button text
   */
  const getButtonText = (): string => {
    if (isVerifying) return 'Verifying...';
    if (sensorReadiness.allReady) return 'Verify Attendance';
    return 'Waiting for Sensors...';
  };

  return (
    <ScrollView style={styles.container}>
      <View style={styles.content}>
        <Text style={styles.title}>Attendance Verification</Text>
        <Text style={styles.subtitle}>Session: {sessionId}</Text>

        {/* Sensor Status Summary */}
        <View style={styles.statusSummary}>
          <Text style={styles.statusTitle}>Sensor Status</Text>
          <Text style={styles.statusMessage}>{statusManager.getStatusMessage()}</Text>
          
          <View style={styles.statusGrid}>
            <SensorStatusBadge label="BLE" status={sensorReadiness.ble} />
            <SensorStatusBadge label="GPS" status={sensorReadiness.gps} />
            <SensorStatusBadge label="Barometer" status={sensorReadiness.barometer} />
            <SensorStatusBadge label="Motion" status={sensorReadiness.motion} />
            <SensorStatusBadge label="Camera" status={sensorReadiness.camera} />
          </View>
        </View>

        {/* BLE Status Indicator */}
        <BLEStatusIndicator
          status={bleStatus}
          rssi={rssi}
          distance={distance}
          threshold={APP_CONFIG.bleRSSIThreshold}
        />

        {/* GPS + Barometer Status Indicator */}
        {locationData && pressureData && (
          <LocationStatusIndicator
            gpsStatus={sensorReadiness.gps}
            barometerStatus={sensorReadiness.barometer}
            location={locationData}
            pressure={pressureData}
            distanceFromClassroom={null} // TODO: Calculate from session location
          />
        )}

        {/* Motion Prompt (shown during collection) */}
        {showMotionPrompt && (
          <MotionPrompt
            status={sensorReadiness.motion}
            progress={motionProgress / 100}
            motionDetected={motionProgress > 50}
            samplingRate={50}
          />
        )}

        {/* Camera Preview (shown during capture) */}
        {showCamera && (
          <FaceVerificationCamera
            onFramesCaptured={(frames, timestamps) => {
              setVideoFrames(frames);
              setFrameTimestamps(timestamps);
              setShowCamera(false);
            }}
            isCapturing={true}
            frameCount={10}
            captureDuration={2000}
          />
        )}

        {/* Verify Button */}
        <TouchableOpacity
          style={[styles.verifyButton, {backgroundColor: getButtonColor()}]}
          onPress={handleVerify}
          disabled={!sensorReadiness.allReady || isVerifying}>
          {isVerifying ? (
            <ActivityIndicator color="#FFFFFF" />
          ) : (
            <Text style={styles.verifyButtonText}>{getButtonText()}</Text>
          )}
        </TouchableOpacity>

        {/* Retry Button */}
        {sensorReadiness.failedSensors.length > 0 && (
          <TouchableOpacity style={styles.retryButton} onPress={retryBLE}>
            <Text style={styles.retryButtonText}>Retry Sensors</Text>
          </TouchableOpacity>
        )}
      </View>
    </ScrollView>
  );
};

/**
 * Sensor Status Badge Component
 */
const SensorStatusBadge: React.FC<{label: string; status: SensorStatus}> = ({label, status}) => {
  const getColor = () => {
    switch (status) {
      case SensorStatus.READY:
        return '#10B981';
      case SensorStatus.SEARCHING:
        return '#F59E0B';
      case SensorStatus.FAILED:
      case SensorStatus.UNAVAILABLE:
        return '#EF4444';
      default:
        return '#9CA3AF';
    }
  };

  const getIcon = () => {
    switch (status) {
      case SensorStatus.READY:
        return '✓';
      case SensorStatus.SEARCHING:
        return '⋯';
      case SensorStatus.FAILED:
      case SensorStatus.UNAVAILABLE:
        return '✗';
      default:
        return '○';
    }
  };

  return (
    <View style={[styles.badge, {borderColor: getColor()}]}>
      <Text style={[styles.badgeIcon, {color: getColor()}]}>{getIcon()}</Text>
      <Text style={styles.badgeLabel}>{label}</Text>
    </View>
  );
};

const styles = StyleSheet.create({
  container: {
    flex: 1,
    backgroundColor: '#F9FAFB',
  },
  content: {
    padding: 16,
  },
  title: {
    fontSize: 24,
    fontWeight: 'bold',
    color: '#1F2937',
    marginBottom: 4,
  },
  subtitle: {
    fontSize: 14,
    color: '#6B7280',
    marginBottom: 24,
  },
  statusSummary: {
    backgroundColor: '#FFFFFF',
    borderRadius: 12,
    padding: 16,
    marginBottom: 16,
    shadowColor: '#000',
    shadowOffset: {width: 0, height: 2},
    shadowOpacity: 0.1,
    shadowRadius: 4,
    elevation: 3,
  },
  statusTitle: {
    fontSize: 16,
    fontWeight: '600',
    color: '#1F2937',
    marginBottom: 8,
  },
  statusMessage: {
    fontSize: 14,
    color: '#6B7280',
    marginBottom: 16,
  },
  statusGrid: {
    flexDirection: 'row',
    flexWrap: 'wrap',
    gap: 8,
  },
  badge: {
    flexDirection: 'row',
    alignItems: 'center',
    borderWidth: 2,
    borderRadius: 8,
    paddingHorizontal: 12,
    paddingVertical: 6,
    backgroundColor: '#FFFFFF',
  },
  badgeIcon: {
    fontSize: 16,
    fontWeight: 'bold',
    marginRight: 6,
  },
  badgeLabel: {
    fontSize: 12,
    fontWeight: '600',
    color: '#1F2937',
  },
  verifyButton: {
    borderRadius: 12,
    paddingVertical: 16,
    alignItems: 'center',
    marginTop: 24,
    shadowColor: '#000',
    shadowOffset: {width: 0, height: 2},
    shadowOpacity: 0.1,
    shadowRadius: 4,
    elevation: 3,
  },
  verifyButtonText: {
    fontSize: 18,
    fontWeight: 'bold',
    color: '#FFFFFF',
  },
  retryButton: {
    borderRadius: 12,
    paddingVertical: 12,
    alignItems: 'center',
    marginTop: 12,
    borderWidth: 2,
    borderColor: '#3B82F6',
    backgroundColor: '#FFFFFF',
  },
  retryButtonText: {
    fontSize: 16,
    fontWeight: '600',
    color: '#3B82F6',
  },
});

export default VerificationScreen;
