/**
 * Face Verification Camera Component
 * Live camera preview with face detection overlay and frame capture
 */
import React, {useState, useEffect, useRef} from 'react';
import {View, Text, StyleSheet, TouchableOpacity, ActivityIndicator} from 'react';
import {Camera, useCameraDevices, CameraDevice} from 'react-native-vision-camera';
import {getCameraService} from '../services/CameraService';
import {SensorStatus} from '../types';

interface FaceVerificationCameraProps {
  onFramesCaptured: (frames: string[], timestamps: number[]) => void;
  isCapturing: boolean;
  frameCount?: number;
  captureDuration?: number;
}

export const FaceVerificationCamera: React.FC<FaceVerificationCameraProps> = ({
  onFramesCaptured,
  isCapturing,
  frameCount = 10,
  captureDuration = 2000,
}) => {
  const [hasPermission, setHasPermission] = useState(false);
  const [status, setStatus] = useState<SensorStatus>(SensorStatus.IDLE);
  const [capturedCount, setCapture dCount] = useState(0);
  const [device, setDevice] = useState<CameraDevice | null>(null);
  
  const cameraRef = useRef<Camera>(null);
  const cameraService = getCameraService();

  /**
   * Initialize camera on mount
   */
  useEffect(() => {
    initializeCamera();
  }, []);

  /**
   * Start capturing when isCapturing changes
   */
  useEffect(() => {
    if (isCapturing && cameraRef.current) {
      startCapture();
    }
  }, [isCapturing]);

  /**
   * Initialize camera and request permissions
   */
  const initializeCamera = async () => {
    try {
      setStatus(SensorStatus.SEARCHING);

      // Request permission
      const permission = await Camera.requestCameraPermission();
      if (permission === 'denied') {
        setStatus(SensorStatus.UNAVAILABLE);
        setHasPermission(false);
        return;
      }

      setHasPermission(true);

      // Get camera devices
      const devices = await Camera.getAvailableCameraDevices();
      const frontCamera = devices.find(d => d.position === 'front');

      if (!frontCamera) {
        setStatus(SensorStatus.UNAVAILABLE);
        console.error('[FaceCamera] No front camera found');
        return;
      }

      setDevice(frontCamera);
      setStatus(SensorStatus.READY);
      console.log('[FaceCamera] Initialized with front camera');
    } catch (error) {
      console.error('[FaceCamera] Initialization error:', error);
      setStatus(SensorStatus.FAILED);
    }
  };

  /**
   * Start capturing frames
   */
  const startCapture = async () => {
    if (!cameraRef.current) {
      console.error('[FaceCamera] Camera ref not available');
      return;
    }

    try {
      setStatus(SensorStatus.SEARCHING);
      setCapture dCount(0);

      // Set camera reference in service
      cameraService.setCameraRef(cameraRef.current);

      // Capture frames
      const {frames, timestamps} = await cameraService.captureFrames(frameCount, captureDuration);

      setCapture dCount(frames.length);
      setStatus(SensorStatus.READY);

      // Notify parent
      onFramesCaptured(frames, timestamps);

      console.log('[FaceCamera] Capture complete:', frames.length, 'frames');
    } catch (error) {
      console.error('[FaceCamera] Capture error:', error);
      setStatus(SensorStatus.FAILED);
    }
  };

  /**
   * Render camera preview
   */
  if (!hasPermission) {
    return (
      <View style={styles.container}>
        <View style={styles.errorContainer}>
          <Text style={styles.errorText}>Camera permission required</Text>
          <TouchableOpacity style={styles.retryButton} onPress={initializeCamera}>
            <Text style={styles.retryButtonText}>Grant Permission</Text>
          </TouchableOpacity>
        </View>
      </View>
    );
  }

  if (!device) {
    return (
      <View style={styles.container}>
        <View style={styles.errorContainer}>
          <ActivityIndicator size="large" color="#3B82F6" />
          <Text style={styles.loadingText}>Loading camera...</Text>
        </View>
      </View>
    );
  }

  return (
    <View style={styles.container}>
      {/* Camera Preview */}
      <Camera
        ref={cameraRef}
        style={styles.camera}
        device={device}
        isActive={true}
        photo={true}
      />

      {/* Face Detection Overlay */}
      <View style={styles.overlay}>
        <View style={styles.faceGuide}>
          <View style={[styles.corner, styles.topLeft]} />
          <View style={[styles.corner, styles.topRight]} />
          <View style={[styles.corner, styles.bottomLeft]} />
          <View style={[styles.corner, styles.bottomRight]} />
        </View>
      </View>

      {/* Status Overlay */}
      <View style={styles.statusOverlay}>
        {isCapturing && (
          <View style={styles.capturingContainer}>
            <ActivityIndicator size="small" color="#FFFFFF" />
            <Text style={styles.capturingText}>
              Capturing frames... {capturedCount}/{frameCount}
            </Text>
          </View>
        )}

        {!isCapturing && status === SensorStatus.READY && (
          <Text style={styles.readyText}>Position your face in the frame</Text>
        )}
      </View>

      {/* Frame Count Progress */}
      {isCapturing && (
        <View style={styles.progressContainer}>
          <View style={styles.progressBar}>
            <View
              style={[
                styles.progressFill,
                {width: `${(capturedCount / frameCount) * 100}%`},
              ]}
            />
          </View>
        </View>
      )}
    </View>
  );
};

const styles = StyleSheet.create({
  container: {
    width: '100%',
    aspectRatio: 3 / 4,
    backgroundColor: '#000000',
    borderRadius: 12,
    overflow: 'hidden',
    marginVertical: 8,
  },
  camera: {
    flex: 1,
  },
  overlay: {
    ...StyleSheet.absoluteFillObject,
    justifyContent: 'center',
    alignItems: 'center',
  },
  faceGuide: {
    width: 250,
    height: 300,
    position: 'relative',
  },
  corner: {
    position: 'absolute',
    width: 40,
    height: 40,
    borderColor: '#FFFFFF',
    borderWidth: 3,
  },
  topLeft: {
    top: 0,
    left: 0,
    borderRightWidth: 0,
    borderBottomWidth: 0,
  },
  topRight: {
    top: 0,
    right: 0,
    borderLeftWidth: 0,
    borderBottomWidth: 0,
  },
  bottomLeft: {
    bottom: 0,
    left: 0,
    borderRightWidth: 0,
    borderTopWidth: 0,
  },
  bottomRight: {
    bottom: 0,
    right: 0,
    borderLeftWidth: 0,
    borderTopWidth: 0,
  },
  statusOverlay: {
    position: 'absolute',
    top: 16,
    left: 16,
    right: 16,
  },
  capturingContainer: {
    flexDirection: 'row',
    alignItems: 'center',
    backgroundColor: 'rgba(0, 0, 0, 0.7)',
    paddingHorizontal: 16,
    paddingVertical: 8,
    borderRadius: 8,
  },
  capturingText: {
    color: '#FFFFFF',
    fontSize: 14,
    fontWeight: '600',
    marginLeft: 8,
  },
  readyText: {
    color: '#FFFFFF',
    fontSize: 14,
    fontWeight: '600',
    backgroundColor: 'rgba(0, 0, 0, 0.7)',
    paddingHorizontal: 16,
    paddingVertical: 8,
    borderRadius: 8,
    textAlign: 'center',
  },
  progressContainer: {
    position: 'absolute',
    bottom: 16,
    left: 16,
    right: 16,
  },
  progressBar: {
    width: '100%',
    height: 6,
    backgroundColor: 'rgba(255, 255, 255, 0.3)',
    borderRadius: 3,
    overflow: 'hidden',
  },
  progressFill: {
    height: '100%',
    backgroundColor: '#10B981',
    borderRadius: 3,
  },
  errorContainer: {
    flex: 1,
    justifyContent: 'center',
    alignItems: 'center',
    padding: 20,
  },
  errorText: {
    fontSize: 16,
    color: '#EF4444',
    marginBottom: 16,
    textAlign: 'center',
  },
  loadingText: {
    fontSize: 14,
    color: '#6B7280',
    marginTop: 12,
  },
  retryButton: {
    backgroundColor: '#3B82F6',
    paddingHorizontal: 24,
    paddingVertical: 12,
    borderRadius: 8,
  },
  retryButtonText: {
    color: '#FFFFFF',
    fontSize: 14,
    fontWeight: '600',
  },
});

export default FaceVerificationCamera;
