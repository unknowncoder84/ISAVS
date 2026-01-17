"""
Robust Preprocessing Pipeline for Face Recognition
Handles lighting variations, alignment, and normalization
UPDATED: MediaPipe Tasks API (2026-compatible) + CLAHE
"""
import cv2
import numpy as np
from typing import Optional, Tuple, List
import mediapipe as mp
from mediapipe.tasks import python
from mediapipe.tasks.python import vision
import os


class FacePreprocessor:
    """
    Production-grade face preprocessing with:
    - CLAHE for lighting normalization (Contrast Limited Adaptive Histogram Equalization)
    - MediaPipe Tasks API for landmark detection (2026-compatible)
    - Affine transformation for alignment
    """
    
    def __init__(self):
        # Path to face landmarker model
        model_path = 'backend/face_landmarker.task'
        
        # Check if model exists
        self.face_landmarker = None
        if not os.path.exists(model_path):
            print(f"⚠️ Face landmarker model not found at {model_path}")
            # Try alternative path
            model_path = 'face_landmarker.task'
            if not os.path.exists(model_path):
                print("⚠️ MediaPipe model not found, will use fallback preprocessing")
                self.face_landmarker = None
            else:
                try:
                    # Initialize MediaPipe Face Landmarker
                    base_options = python.BaseOptions(model_asset_path=model_path)
                    options = vision.FaceLandmarkerOptions(
                        base_options=base_options,
                        output_face_blendshapes=False,
                        output_facial_transformation_matrixes=False,
                        num_faces=1,
                        min_face_detection_confidence=0.5,
                        min_face_presence_confidence=0.5,
                        min_tracking_confidence=0.5
                    )
                    self.face_landmarker = vision.FaceLandmarker.create_from_options(options)
                    print("✓ MediaPipe Face Landmarker initialized")
                except Exception as e:
                    print(f"⚠️ Failed to initialize MediaPipe: {e}")
                    self.face_landmarker = None
        else:
            try:
                # Initialize MediaPipe Face Landmarker (Tasks API - 2026 Standard)
                base_options = python.BaseOptions(model_asset_path=model_path)
                options = vision.FaceLandmarkerOptions(
                    base_options=base_options,
                    output_face_blendshapes=False,
                    output_facial_transformation_matrixes=False,
                    num_faces=1,
                    min_face_detection_confidence=0.5,
                    min_face_presence_confidence=0.5,
                    min_tracking_confidence=0.5
                )
                self.face_landmarker = vision.FaceLandmarker.create_from_options(options)
                print("✓ MediaPipe Face Landmarker initialized")
            except Exception as e:
                print(f"⚠️ Failed to initialize MediaPipe: {e}")
                self.face_landmarker = None
        
        # CLAHE for contrast enhancement (handles uneven lighting)
        self.clahe = cv2.createCLAHE(clipLimit=2.0, tileGridSize=(8, 8))
        
        # Target eye positions for alignment (normalized coordinates)
        self.LEFT_EYE_TARGET = (0.35, 0.35)
        self.RIGHT_EYE_TARGET = (0.65, 0.35)
        self.TARGET_SIZE = (224, 224)  # Standard size for deep learning models
        
        print("✓ FacePreprocessor initialized with CLAHE")
    
    def preprocess(self, image: np.ndarray) -> Optional[np.ndarray]:
        """
        Complete preprocessing pipeline (2026 Standard):
        1. Convert to RGB
        2. Detect landmarks with MediaPipe Tasks API
        3. Align face using eye positions
        4. Convert to grayscale
        5. Apply CLAHE (Contrast Limited Adaptive Histogram Equalization)
        6. Convert back to RGB for face_recognition
        
        Returns: Preprocessed face image or None if face not detected
        """
        if image is None or image.size == 0:
            return None
        
        # Step 1: Convert to RGB (MediaPipe expects RGB)
        if len(image.shape) == 2:
            rgb_image = cv2.cvtColor(image, cv2.COLOR_GRAY2RGB)
        elif image.shape[2] == 4:
            rgb_image = cv2.cvtColor(image, cv2.COLOR_BGRA2RGB)
        else:
            rgb_image = cv2.cvtColor(image, cv2.COLOR_BGR2RGB)
        
        # Step 2: Detect facial landmarks using MediaPipe Tasks API
        landmarks = self._detect_landmarks(rgb_image)
        if landmarks is None:
            print("⚠️ No face landmarks detected")
            # Try without alignment
            return self._preprocess_without_alignment(rgb_image)
        
        # Step 3: Align face using eye positions
        aligned_face = self._align_face(rgb_image, landmarks)
        if aligned_face is None:
            print("⚠️ Face alignment failed, using unaligned")
            return self._preprocess_without_alignment(rgb_image)
        
        # Step 4: Convert to grayscale
        gray_face = cv2.cvtColor(aligned_face, cv2.COLOR_RGB2GRAY)
        
        # Step 5: Apply CLAHE for lighting normalization
        enhanced_face = self.clahe.apply(gray_face)
        
        # Step 6: Convert back to RGB for face_recognition (expects 3 channels)
        final_face = cv2.cvtColor(enhanced_face, cv2.COLOR_GRAY2RGB)
        
        return final_face
    
    def _preprocess_without_alignment(self, rgb_image: np.ndarray) -> np.ndarray:
        """Fallback preprocessing without alignment - always succeeds."""
        try:
            # Resize to target size
            resized = cv2.resize(rgb_image, self.TARGET_SIZE)
            
            # Convert to grayscale
            gray = cv2.cvtColor(resized, cv2.COLOR_RGB2GRAY)
            
            # Apply CLAHE
            enhanced = self.clahe.apply(gray)
            
            # Convert back to RGB
            final = cv2.cvtColor(enhanced, cv2.COLOR_GRAY2RGB)
            
            return final
        except Exception as e:
            print(f"⚠️ Fallback preprocessing error: {e}, returning resized original")
            # Last resort: just resize
            return cv2.resize(rgb_image, self.TARGET_SIZE)
    
    def _detect_landmarks(self, rgb_image: np.ndarray) -> Optional[np.ndarray]:
        """
        Detect facial landmarks using MediaPipe Tasks API.
        Returns: Array of landmark coordinates or None
        """
        # If MediaPipe not available, return None
        if self.face_landmarker is None:
            return None
        
        try:
            # Convert numpy array to MediaPipe Image
            mp_image = mp.Image(image_format=mp.ImageFormat.SRGB, data=rgb_image)
            
            # Detect face landmarks
            detection_result = self.face_landmarker.detect(mp_image)
            
            if not detection_result.face_landmarks or len(detection_result.face_landmarks) == 0:
                return None
            
            # Get first face landmarks
            face_landmarks = detection_result.face_landmarks[0]
            
            # Convert to numpy array
            h, w = rgb_image.shape[:2]
            landmarks = np.array([
                [lm.x * w, lm.y * h] 
                for lm in face_landmarks
            ])
            
            return landmarks
            
        except Exception as e:
            print(f"Landmark detection error: {e}")
            return None
    
    def _align_face(
        self, 
        image: np.ndarray, 
        landmarks: np.ndarray
    ) -> Optional[np.ndarray]:
        """
        Align face using affine transformation based on eye positions.
        Ensures eyes are horizontally aligned and face is centered.
        """
        try:
            # MediaPipe landmark indices for eyes
            LEFT_EYE_IDX = 33   # Left eye center
            RIGHT_EYE_IDX = 263  # Right eye center
            
            # Get eye coordinates
            left_eye = landmarks[LEFT_EYE_IDX]
            right_eye = landmarks[RIGHT_EYE_IDX]
            
            # Calculate eye center and angle
            eye_center = ((left_eye[0] + right_eye[0]) / 2, 
                         (left_eye[1] + right_eye[1]) / 2)
            
            dy = right_eye[1] - left_eye[1]
            dx = right_eye[0] - left_eye[0]
            angle = np.degrees(np.arctan2(dy, dx))
            
            # Calculate scale to match target eye distance
            current_eye_dist = np.sqrt(dx**2 + dy**2)
            target_eye_dist = (self.RIGHT_EYE_TARGET[0] - self.LEFT_EYE_TARGET[0]) * self.TARGET_SIZE[0]
            scale = target_eye_dist / current_eye_dist if current_eye_dist > 0 else 1.0
            
            # Get rotation matrix
            M = cv2.getRotationMatrix2D(eye_center, angle, scale)
            
            # Adjust translation to center face
            target_eye_center = (
                self.TARGET_SIZE[0] * 0.5,
                self.TARGET_SIZE[1] * 0.4  # Slightly above center
            )
            M[0, 2] += target_eye_center[0] - eye_center[0]
            M[1, 2] += target_eye_center[1] - eye_center[1]
            
            # Apply affine transformation
            aligned = cv2.warpAffine(
                image, 
                M, 
                self.TARGET_SIZE,
                flags=cv2.INTER_CUBIC,
                borderMode=cv2.BORDER_REPLICATE
            )
            
            return aligned
            
        except Exception as e:
            print(f"Face alignment error: {e}")
            return None
    
    def preprocess_batch(self, images: List[np.ndarray]) -> List[np.ndarray]:
        """
        Preprocess multiple images (for multi-shot enrollment).
        Returns: List of preprocessed images (skips failed ones)
        """
        preprocessed = []
        for img in images:
            processed = self.preprocess(img)
            if processed is not None:
                preprocessed.append(processed)
        return preprocessed
    
    def quality_check(self, image: np.ndarray) -> Tuple[bool, str]:
        """
        Check if image quality is sufficient for enrollment.
        Returns: (is_good, reason)
        """
        if image is None or image.size == 0:
            return False, "Empty image"
        
        # Check resolution
        h, w = image.shape[:2]
        if h < 100 or w < 100:
            return False, "Image too small (min 100x100)"
        
        # Check brightness
        gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY) if len(image.shape) == 3 else image
        mean_brightness = np.mean(gray)
        if mean_brightness < 40:
            return False, "Image too dark"
        if mean_brightness > 220:
            return False, "Image too bright"
        
        # Check blur (Laplacian variance)
        laplacian_var = cv2.Laplacian(gray, cv2.CV_64F).var()
        if laplacian_var < 100:
            return False, "Image too blurry"
        
        return True, "OK"
    
    def __del__(self):
        """Cleanup MediaPipe resources."""
        if hasattr(self, 'face_landmarker') and self.face_landmarker is not None:
            try:
                self.face_landmarker.close()
            except:
                pass


# Singleton instance
_preprocessor: Optional[FacePreprocessor] = None


def get_preprocessor() -> FacePreprocessor:
    """Get or create preprocessor instance."""
    global _preprocessor
    if _preprocessor is None:
        _preprocessor = FacePreprocessor()
    return _preprocessor
