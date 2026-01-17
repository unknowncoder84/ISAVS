"""
Liveness Detection Service
Detects eye blinks to verify live person presence.
"""
from typing import List, Optional, Tuple
import numpy as np

try:
    import cv2
    import mediapipe as mp
    MEDIAPIPE_AVAILABLE = True
except ImportError:
    MEDIAPIPE_AVAILABLE = False

from app.models.domain import LivenessResult


class LivenessService:
    """Service for liveness detection using blink detection."""
    
    # Eye landmark indices for MediaPipe Face Mesh
    LEFT_EYE_INDICES = [362, 385, 387, 263, 373, 380]
    RIGHT_EYE_INDICES = [33, 160, 158, 133, 153, 144]
    
    def __init__(
        self,
        ear_threshold: float = 0.25,
        consecutive_frames: int = 2
    ):
        """
        Initialize liveness service.
        
        Args:
            ear_threshold: Eye Aspect Ratio threshold for blink detection
            consecutive_frames: Number of consecutive frames with closed eyes to detect blink
        """
        self.ear_threshold = ear_threshold
        self.consecutive_frames = consecutive_frames
        self._face_mesh = None
        
        if MEDIAPIPE_AVAILABLE:
            self._init_face_mesh()
    
    def _init_face_mesh(self):
        """Initialize MediaPipe Face Mesh."""
        mp_face_mesh = mp.solutions.face_mesh
        self._face_mesh = mp_face_mesh.FaceMesh(
            max_num_faces=1,
            refine_landmarks=True,
            min_detection_confidence=0.5,
            min_tracking_confidence=0.5
        )
    
    def calculate_eye_aspect_ratio(self, eye_landmarks: np.ndarray) -> float:
        """
        Calculate Eye Aspect Ratio (EAR) for blink detection.
        
        EAR = (||p2-p6|| + ||p3-p5||) / (2 * ||p1-p4||)
        
        Args:
            eye_landmarks: 6 landmark points for one eye
            
        Returns:
            Eye aspect ratio value
        """
        if len(eye_landmarks) != 6:
            return 1.0  # Return open eye value if invalid
        
        # Vertical distances
        v1 = np.linalg.norm(eye_landmarks[1] - eye_landmarks[5])
        v2 = np.linalg.norm(eye_landmarks[2] - eye_landmarks[4])
        
        # Horizontal distance
        h = np.linalg.norm(eye_landmarks[0] - eye_landmarks[3])
        
        if h == 0:
            return 1.0
        
        ear = (v1 + v2) / (2.0 * h)
        return float(ear)
    
    def _get_eye_landmarks(
        self, 
        landmarks, 
        indices: List[int],
        image_width: int,
        image_height: int
    ) -> np.ndarray:
        """Extract eye landmarks from face mesh results."""
        points = []
        for idx in indices:
            lm = landmarks[idx]
            x = lm.x * image_width
            y = lm.y * image_height
            points.append([x, y])
        return np.array(points)
    
    def detect_blink_in_frame(self, image: np.ndarray) -> Tuple[bool, float, float]:
        """
        Detect if eyes are closed (potential blink) in a single frame.
        
        Returns:
            Tuple of (eyes_closed, left_ear, right_ear)
        """
        if not MEDIAPIPE_AVAILABLE or self._face_mesh is None:
            # Mock response for testing
            return False, 0.3, 0.3
        
        try:
            # Convert to RGB if needed
            if len(image.shape) == 3 and image.shape[2] == 3:
                rgb_image = cv2.cvtColor(image, cv2.COLOR_BGR2RGB)
            else:
                rgb_image = image
            
            results = self._face_mesh.process(rgb_image)
            
            if not results.multi_face_landmarks:
                return False, 0.0, 0.0
            
            landmarks = results.multi_face_landmarks[0].landmark
            h, w = image.shape[:2]
            
            # Get eye landmarks
            left_eye = self._get_eye_landmarks(landmarks, self.LEFT_EYE_INDICES, w, h)
            right_eye = self._get_eye_landmarks(landmarks, self.RIGHT_EYE_INDICES, w, h)
            
            # Calculate EAR for both eyes
            left_ear = self.calculate_eye_aspect_ratio(left_eye)
            right_ear = self.calculate_eye_aspect_ratio(right_eye)
            
            # Average EAR
            avg_ear = (left_ear + right_ear) / 2.0
            
            # Eyes are closed if EAR is below threshold
            eyes_closed = avg_ear < self.ear_threshold
            
            return eyes_closed, left_ear, right_ear
            
        except Exception:
            return False, 0.0, 0.0
    
    def detect_blink(self, frames: List[np.ndarray]) -> bool:
        """
        Detect eye blink across multiple frames.
        
        A blink is detected when eyes are closed for consecutive frames
        and then open again.
        
        Args:
            frames: List of image frames (numpy arrays)
            
        Returns:
            True if blink detected, False otherwise
        """
        if len(frames) < self.consecutive_frames + 1:
            return False
        
        closed_count = 0
        was_open = False
        blink_detected = False
        
        for frame in frames:
            eyes_closed, _, _ = self.detect_blink_in_frame(frame)
            
            if not eyes_closed:
                if closed_count >= self.consecutive_frames:
                    # Eyes were closed and now open = blink
                    blink_detected = True
                was_open = True
                closed_count = 0
            else:
                if was_open:
                    closed_count += 1
        
        return blink_detected
    
    def check_liveness(self, frames: List[np.ndarray]) -> LivenessResult:
        """
        Perform complete liveness check on a sequence of frames.
        
        Args:
            frames: List of image frames for liveness detection
            
        Returns:
            LivenessResult with detection status
        """
        if not frames:
            return LivenessResult(
                is_live=False,
                blink_detected=False,
                confidence=0.0,
                message="No frames provided for liveness check"
            )
        
        blink_detected = self.detect_blink(frames)
        
        # Calculate confidence based on frame quality and detection
        confidence = 0.9 if blink_detected else 0.1
        
        return LivenessResult(
            is_live=blink_detected,
            blink_detected=blink_detected,
            confidence=confidence,
            message="Liveness verified" if blink_detected else "No blink detected - please blink naturally"
        )
    
    def close(self):
        """Release resources."""
        if self._face_mesh:
            self._face_mesh.close()


# Singleton instance
_liveness_service: Optional[LivenessService] = None


def get_liveness_service() -> LivenessService:
    """Get or create liveness service instance."""
    global _liveness_service
    if _liveness_service is None:
        _liveness_service = LivenessService()
    return _liveness_service
