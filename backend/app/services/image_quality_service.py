"""
Image Quality Service
Analyzes image quality for face recognition suitability.
"""
from typing import List, Optional
import numpy as np

try:
    import cv2
    CV2_AVAILABLE = True
except ImportError:
    CV2_AVAILABLE = False

from app.models.domain import QualityResult


class ImageQualityService:
    """Service for analyzing image quality."""
    
    # Quality thresholds
    MIN_CONTRAST = 30.0
    MIN_BRIGHTNESS = 40.0
    MAX_BRIGHTNESS = 220.0
    MIN_SHARPNESS = 50.0
    
    def __init__(
        self,
        min_contrast: float = None,
        min_brightness: float = None,
        max_brightness: float = None
    ):
        self.min_contrast = min_contrast or self.MIN_CONTRAST
        self.min_brightness = min_brightness or self.MIN_BRIGHTNESS
        self.max_brightness = max_brightness or self.MAX_BRIGHTNESS
    
    def analyze_brightness(self, image: np.ndarray) -> float:
        """
        Analyze image brightness.
        Returns average brightness value (0-255).
        """
        if not CV2_AVAILABLE:
            return 128.0  # Mock value
        
        try:
            if len(image.shape) == 3:
                gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
            else:
                gray = image
            
            return float(np.mean(gray))
        except Exception:
            return 128.0
    
    def analyze_contrast(self, image: np.ndarray) -> float:
        """
        Analyze image contrast using standard deviation.
        Returns contrast value.
        """
        if not CV2_AVAILABLE:
            return 50.0  # Mock value
        
        try:
            if len(image.shape) == 3:
                gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
            else:
                gray = image
            
            return float(np.std(gray))
        except Exception:
            return 50.0
    
    def analyze_sharpness(self, image: np.ndarray) -> float:
        """
        Analyze image sharpness using Laplacian variance.
        Higher values indicate sharper images.
        """
        if not CV2_AVAILABLE:
            return 100.0  # Mock value
        
        try:
            if len(image.shape) == 3:
                gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
            else:
                gray = image
            
            laplacian = cv2.Laplacian(gray, cv2.CV_64F)
            return float(laplacian.var())
        except Exception:
            return 100.0
    
    def check_quality_threshold(self, image: np.ndarray) -> QualityResult:
        """
        Check if image meets minimum quality requirements.
        
        Args:
            image: Input image as numpy array
            
        Returns:
            QualityResult with analysis details
        """
        brightness = self.analyze_brightness(image)
        contrast = self.analyze_contrast(image)
        sharpness = self.analyze_sharpness(image)
        
        issues: List[str] = []
        suggestions: List[str] = []
        
        # Check brightness
        if brightness < self.min_brightness:
            issues.append("low_brightness")
            suggestions.append("Move to a brighter area or turn on more lights")
        elif brightness > self.max_brightness:
            issues.append("high_brightness")
            suggestions.append("Reduce lighting or move away from direct light source")
        
        # Check contrast
        if contrast < self.min_contrast:
            issues.append("low_contrast")
            suggestions.append("Improve lighting conditions for better contrast")
        
        # Check sharpness
        if sharpness < self.MIN_SHARPNESS:
            issues.append("blurry")
            suggestions.append("Hold the camera steady and ensure face is in focus")
        
        acceptable = len(issues) == 0
        
        return QualityResult(
            acceptable=acceptable,
            contrast=contrast,
            brightness=brightness,
            issues=issues,
            suggestions=suggestions
        )
    
    def get_improvement_suggestions(self, issues: List[str]) -> List[str]:
        """
        Generate user-friendly suggestions based on detected issues.
        """
        suggestion_map = {
            "low_brightness": "The image is too dark. Please move to a well-lit area.",
            "high_brightness": "The image is overexposed. Please reduce direct lighting.",
            "low_contrast": "Low contrast detected. Ensure even lighting on your face.",
            "blurry": "The image is blurry. Please hold still and ensure camera focus.",
        }
        
        return [suggestion_map.get(issue, f"Issue detected: {issue}") for issue in issues]
    
    def is_low_light(self, image: np.ndarray) -> bool:
        """Check if image has low light conditions."""
        brightness = self.analyze_brightness(image)
        contrast = self.analyze_contrast(image)
        return brightness < self.min_brightness or contrast < self.min_contrast


# Singleton instance
_quality_service: Optional[ImageQualityService] = None


def get_image_quality_service() -> ImageQualityService:
    """Get or create image quality service instance."""
    global _quality_service
    if _quality_service is None:
        _quality_service = ImageQualityService()
    return _quality_service
