"""
Emotion Detection Service for Liveness Verification
Uses DeepFace for emotion recognition (smile detection)
"""
import numpy as np
import cv2
from typing import Optional, Dict, Tuple
import os

# Suppress warnings
os.environ['TF_CPP_MIN_LOG_LEVEL'] = '3'

try:
    from deepface import DeepFace
    DEEPFACE_AVAILABLE = True
except ImportError:
    DEEPFACE_AVAILABLE = False
    print("⚠️ DeepFace not available for emotion detection")


class EmotionService:
    """
    Emotion Detection Service for Liveness Verification.
    
    Features:
    - Detect 7 emotions: Happy, Sad, Angry, Surprise, Fear, Disgust, Neutral
    - Smile-to-verify liveness check
    - Confidence thresholds
    - Fallback to neutral if detection fails
    """
    
    # Emotion labels
    EMOTIONS = ['angry', 'disgust', 'fear', 'happy', 'sad', 'surprise', 'neutral']
    
    def __init__(self, smile_threshold: float = 0.7):
        """
        Initialize emotion service.
        
        Args:
            smile_threshold: Minimum confidence for "happy" emotion (default 0.7)
        """
        self.smile_threshold = smile_threshold
        self.available = DEEPFACE_AVAILABLE
    
    def is_available(self) -> bool:
        """Check if emotion detection is available."""
        return self.available
    
    def detect_emotion(self, image: np.ndarray) -> Optional[Dict[str, float]]:
        """
        Detect emotion from face image.
        
        Args:
            image: BGR image (OpenCV format)
        
        Returns:
            Dictionary with emotion probabilities
            Example: {'happy': 0.85, 'neutral': 0.10, 'sad': 0.05, ...}
        """
        if not self.is_available():
            print("⚠️ DeepFace not available for emotion detection")
            return None
        
        try:
            # Convert to RGB (DeepFace expects RGB)
            rgb_image = cv2.cvtColor(image, cv2.COLOR_BGR2RGB)
            
            # Analyze emotion using DeepFace
            result = DeepFace.analyze(
                img_path=rgb_image,
                actions=['emotion'],
                enforce_detection=False,  # Don't fail if face not detected
                detector_backend='opencv',
                silent=True
            )
            
            # Handle both single face and multiple faces
            if isinstance(result, list):
                if len(result) == 0:
                    print("⚠️ No face detected for emotion analysis")
                    return None
                result = result[0]  # Use first face
            
            # Extract emotion probabilities
            emotions = result.get('emotion', {})
            
            # Normalize to ensure sum = 1.0
            total = sum(emotions.values())
            if total > 0:
                emotions = {k: v / total for k, v in emotions.items()}
            
            return emotions
            
        except Exception as e:
            print(f"❌ Emotion detection error: {e}")
            return None
    
    def check_smile(self, image: np.ndarray) -> Tuple[bool, float, Dict[str, float]]:
        """
        Check if person is smiling (for liveness detection).
        
        Args:
            image: BGR image (OpenCV format)
        
        Returns:
            (is_smiling, happy_confidence, all_emotions)
        """
        emotions = self.detect_emotion(image)
        
        if emotions is None:
            # Return neutral if detection fails
            return False, 0.0, {'neutral': 1.0}
        
        # Get "happy" emotion score
        happy_score = emotions.get('happy', 0.0)
        
        # Check if above threshold
        is_smiling = happy_score >= self.smile_threshold
        
        return is_smiling, happy_score, emotions
    
    def get_dominant_emotion(self, emotions: Dict[str, float]) -> Tuple[str, float]:
        """
        Get the dominant emotion from emotion dictionary.
        
        Args:
            emotions: Dictionary of emotion probabilities
        
        Returns:
            (emotion_name, confidence)
        """
        if not emotions:
            return 'neutral', 0.0
        
        # Find emotion with highest probability
        dominant = max(emotions.items(), key=lambda x: x[1])
        
        return dominant[0], dominant[1]
    
    def is_positive_emotion(self, emotions: Dict[str, float]) -> bool:
        """
        Check if detected emotion is positive (happy or surprise).
        
        Args:
            emotions: Dictionary of emotion probabilities
        
        Returns:
            True if positive emotion detected
        """
        if not emotions:
            return False
        
        positive_score = emotions.get('happy', 0.0) + emotions.get('surprise', 0.0)
        
        return positive_score >= self.smile_threshold
    
    def format_emotion_feedback(self, emotions: Dict[str, float]) -> str:
        """
        Format emotion detection results for user feedback.
        
        Args:
            emotions: Dictionary of emotion probabilities
        
        Returns:
            Human-readable feedback string
        """
        if not emotions:
            return "No emotion detected"
        
        dominant, confidence = self.get_dominant_emotion(emotions)
        
        # Create feedback message
        if dominant == 'happy':
            if confidence >= self.smile_threshold:
                return f"😊 Great smile! ({confidence:.0%} confidence)"
            else:
                return f"🙂 Almost there! Smile a bit more ({confidence:.0%})"
        elif dominant == 'neutral':
            return "😐 Please smile for verification"
        elif dominant == 'sad':
            return "😔 Cheer up! We need a smile"
        elif dominant == 'angry':
            return "😠 Relax and smile please"
        elif dominant == 'surprise':
            return f"😲 Surprised? That works too! ({confidence:.0%})"
        else:
            return f"Detected: {dominant} ({confidence:.0%})"


# Singleton instance
_emotion_service: Optional[EmotionService] = None


def get_emotion_service() -> EmotionService:
    """Get or create emotion service instance."""
    global _emotion_service
    if _emotion_service is None:
        _emotion_service = EmotionService()
    return _emotion_service
