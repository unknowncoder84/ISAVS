"""
Motion-Image Correlator Service
Correlates accelerometer/gyroscope motion data with optical flow from camera frames
for liveness detection (anti-spoofing).
"""
from typing import List, Tuple, Optional
import numpy as np
import cv2
from dataclasses import dataclass
from scipy.stats import pearsonr


@dataclass
class MotionData:
    """Motion sensor data from mobile device"""
    timestamps: List[float]  # Unix timestamps in seconds
    accelerometer_x: List[float]  # m/s²
    accelerometer_y: List[float]
    accelerometer_z: List[float]
    gyroscope_x: List[float]  # rad/s
    gyroscope_y: List[float]
    gyroscope_z: List[float]


@dataclass
class FrameData:
    """Camera frame data"""
    timestamps: List[float]  # Unix timestamps in seconds
    frames: List[np.ndarray]  # Grayscale frames


@dataclass
class CorrelationResult:
    """Result of motion-image correlation"""
    correlation_coefficient: float
    p_value: float
    is_live: bool
    message: str
    optical_flow_magnitude: List[float]
    motion_magnitude: List[float]


class MotionImageCorrelator:
    """
    Service for correlating motion sensor data with optical flow from camera frames.
    
    Features:
    - Lucas-Kanade optical flow extraction
    - Pearson correlation coefficient calculation
    - Timestamp alignment (±20ms tolerance)
    - Liveness verification (0.7 correlation threshold)
    
    Anti-spoofing: Detects if someone is holding a photo/video by verifying
    that camera motion matches device motion sensors.
    """
    
    # Thresholds
    CORRELATION_THRESHOLD = 0.7  # Minimum correlation for liveness
    TIMESTAMP_TOLERANCE_MS = 20  # ±20ms tolerance for alignment
    MIN_SAMPLES = 10  # Minimum samples for correlation
    
    # Lucas-Kanade optical flow parameters
    LK_PARAMS = dict(
        winSize=(15, 15),
        maxLevel=2,
        criteria=(cv2.TERM_CRITERIA_EPS | cv2.TERM_CRITERIA_COUNT, 10, 0.03)
    )
    
    # Shi-Tomasi corner detection parameters
    FEATURE_PARAMS = dict(
        maxCorners=100,
        qualityLevel=0.3,
        minDistance=7,
        blockSize=7
    )
    
    def __init__(self):
        """Initialize motion-image correlator"""
        pass
    
    def extract_optical_flow(
        self,
        frames: List[np.ndarray],
        timestamps: List[float]
    ) -> Tuple[List[float], List[float]]:
        """
        Extract optical flow magnitude from consecutive frames using Lucas-Kanade method.
        
        Args:
            frames: List of grayscale frames (numpy arrays)
            timestamps: Frame timestamps in seconds
        
        Returns:
            (flow_magnitudes, flow_timestamps)
            - flow_magnitudes: List of average optical flow magnitudes
            - flow_timestamps: Timestamps for each flow measurement (midpoint between frames)
        """
        if len(frames) < 2:
            raise ValueError("Need at least 2 frames for optical flow")
        
        flow_magnitudes = []
        flow_timestamps = []
        
        for i in range(len(frames) - 1):
            prev_frame = frames[i]
            next_frame = frames[i + 1]
            
            # Convert to grayscale if needed
            if len(prev_frame.shape) == 3:
                prev_gray = cv2.cvtColor(prev_frame, cv2.COLOR_BGR2GRAY)
            else:
                prev_gray = prev_frame
            
            if len(next_frame.shape) == 3:
                next_gray = cv2.cvtColor(next_frame, cv2.COLOR_BGR2GRAY)
            else:
                next_gray = next_frame
            
            # Detect features in first frame using Shi-Tomasi corner detection
            p0 = cv2.goodFeaturesToTrack(prev_gray, mask=None, **self.FEATURE_PARAMS)
            
            if p0 is None or len(p0) == 0:
                # No features detected, use zero flow
                flow_magnitudes.append(0.0)
                flow_timestamps.append((timestamps[i] + timestamps[i + 1]) / 2)
                continue
            
            # Calculate optical flow using Lucas-Kanade method
            p1, status, err = cv2.calcOpticalFlowPyrLK(
                prev_gray, next_gray, p0, None, **self.LK_PARAMS
            )
            
            if p1 is None:
                flow_magnitudes.append(0.0)
                flow_timestamps.append((timestamps[i] + timestamps[i + 1]) / 2)
                continue
            
            # Select good points
            good_new = p1[status == 1]
            good_old = p0[status == 1]
            
            if len(good_new) == 0:
                flow_magnitudes.append(0.0)
                flow_timestamps.append((timestamps[i] + timestamps[i + 1]) / 2)
                continue
            
            # Calculate flow vectors
            flow_vectors = good_new - good_old
            
            # Calculate magnitude of each flow vector
            magnitudes = np.sqrt(flow_vectors[:, 0]**2 + flow_vectors[:, 1]**2)
            
            # Average magnitude across all tracked points
            avg_magnitude = np.mean(magnitudes)
            
            flow_magnitudes.append(float(avg_magnitude))
            
            # Timestamp is midpoint between frames
            flow_timestamps.append((timestamps[i] + timestamps[i + 1]) / 2)
        
        return flow_magnitudes, flow_timestamps
    
    def calculate_motion_magnitude(
        self,
        motion_data: MotionData
    ) -> Tuple[List[float], List[float]]:
        """
        Calculate motion magnitude from accelerometer and gyroscope data.
        
        Combines linear acceleration and angular velocity into a single magnitude metric.
        
        Args:
            motion_data: MotionData object with sensor readings
        
        Returns:
            (motion_magnitudes, timestamps)
        """
        if len(motion_data.timestamps) == 0:
            raise ValueError("Motion data is empty")
        
        motion_magnitudes = []
        
        for i in range(len(motion_data.timestamps)):
            # Calculate linear acceleration magnitude (m/s²)
            accel_mag = np.sqrt(
                motion_data.accelerometer_x[i]**2 +
                motion_data.accelerometer_y[i]**2 +
                motion_data.accelerometer_z[i]**2
            )
            
            # Calculate angular velocity magnitude (rad/s)
            gyro_mag = np.sqrt(
                motion_data.gyroscope_x[i]**2 +
                motion_data.gyroscope_y[i]**2 +
                motion_data.gyroscope_z[i]**2
            )
            
            # Combine both (weighted sum)
            # Weight gyroscope more heavily as it's more relevant for camera motion
            combined_magnitude = 0.3 * accel_mag + 0.7 * gyro_mag
            
            motion_magnitudes.append(float(combined_magnitude))
        
        return motion_magnitudes, motion_data.timestamps
    
    def align_timestamps(
        self,
        flow_magnitudes: List[float],
        flow_timestamps: List[float],
        motion_magnitudes: List[float],
        motion_timestamps: List[float]
    ) -> Tuple[List[float], List[float]]:
        """
        Align optical flow and motion data by timestamps.
        
        For each flow timestamp, finds the closest motion sample within tolerance.
        
        Args:
            flow_magnitudes: Optical flow magnitudes
            flow_timestamps: Flow timestamps
            motion_magnitudes: Motion magnitudes
            motion_timestamps: Motion timestamps
        
        Returns:
            (aligned_flow, aligned_motion) - Lists of same length with aligned samples
        """
        aligned_flow = []
        aligned_motion = []
        
        tolerance_sec = self.TIMESTAMP_TOLERANCE_MS / 1000.0
        
        for i, flow_ts in enumerate(flow_timestamps):
            # Find closest motion sample
            time_diffs = [abs(flow_ts - motion_ts) for motion_ts in motion_timestamps]
            min_diff_idx = np.argmin(time_diffs)
            min_diff = time_diffs[min_diff_idx]
            
            # Check if within tolerance
            if min_diff <= tolerance_sec:
                aligned_flow.append(flow_magnitudes[i])
                aligned_motion.append(motion_magnitudes[min_diff_idx])
        
        return aligned_flow, aligned_motion
    
    def calculate_correlation(
        self,
        flow_magnitudes: List[float],
        motion_magnitudes: List[float]
    ) -> Tuple[float, float]:
        """
        Calculate Pearson correlation coefficient between optical flow and motion.
        
        Args:
            flow_magnitudes: Aligned optical flow magnitudes
            motion_magnitudes: Aligned motion magnitudes
        
        Returns:
            (correlation_coefficient, p_value)
        """
        if len(flow_magnitudes) < self.MIN_SAMPLES:
            raise ValueError(f"Need at least {self.MIN_SAMPLES} samples for correlation")
        
        if len(flow_magnitudes) != len(motion_magnitudes):
            raise ValueError("Flow and motion arrays must have same length")
        
        # Calculate Pearson correlation
        correlation, p_value = pearsonr(flow_magnitudes, motion_magnitudes)
        
        return float(correlation), float(p_value)
    
    def verify_liveness(
        self,
        frames: List[np.ndarray],
        frame_timestamps: List[float],
        motion_data: MotionData,
        threshold: Optional[float] = None
    ) -> CorrelationResult:
        """
        Verify liveness by correlating optical flow with motion sensor data.
        
        Args:
            frames: List of camera frames
            frame_timestamps: Frame timestamps
            motion_data: Motion sensor data
            threshold: Correlation threshold (default 0.7)
        
        Returns:
            CorrelationResult with verification details
        """
        if threshold is None:
            threshold = self.CORRELATION_THRESHOLD
        
        try:
            # Step 1: Extract optical flow
            flow_magnitudes, flow_timestamps = self.extract_optical_flow(
                frames, frame_timestamps
            )
            
            # Step 2: Calculate motion magnitude
            motion_magnitudes, motion_timestamps = self.calculate_motion_magnitude(
                motion_data
            )
            
            # Step 3: Align timestamps
            aligned_flow, aligned_motion = self.align_timestamps(
                flow_magnitudes, flow_timestamps,
                motion_magnitudes, motion_timestamps
            )
            
            if len(aligned_flow) < self.MIN_SAMPLES:
                return CorrelationResult(
                    correlation_coefficient=0.0,
                    p_value=1.0,
                    is_live=False,
                    message=f"Insufficient aligned samples: {len(aligned_flow)} < {self.MIN_SAMPLES}",
                    optical_flow_magnitude=flow_magnitudes,
                    motion_magnitude=motion_magnitudes
                )
            
            # Step 4: Calculate correlation
            correlation, p_value = self.calculate_correlation(
                aligned_flow, aligned_motion
            )
            
            # Step 5: Determine liveness
            is_live = correlation >= threshold
            
            if is_live:
                message = f"Liveness verified (r={correlation:.3f}, p={p_value:.4f})"
            else:
                message = f"Motion-image mismatch detected (r={correlation:.3f} < {threshold})"
            
            return CorrelationResult(
                correlation_coefficient=correlation,
                p_value=p_value,
                is_live=is_live,
                message=message,
                optical_flow_magnitude=flow_magnitudes,
                motion_magnitude=motion_magnitudes
            )
            
        except Exception as e:
            return CorrelationResult(
                correlation_coefficient=0.0,
                p_value=1.0,
                is_live=False,
                message=f"Correlation failed: {str(e)}",
                optical_flow_magnitude=[],
                motion_magnitude=[]
            )


# Singleton instance
_motion_image_correlator: Optional[MotionImageCorrelator] = None


def get_motion_image_correlator() -> MotionImageCorrelator:
    """Get or create motion-image correlator instance."""
    global _motion_image_correlator
    if _motion_image_correlator is None:
        _motion_image_correlator = MotionImageCorrelator()
    return _motion_image_correlator
