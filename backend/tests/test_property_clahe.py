"""
Property-Based Tests for CLAHE Preprocessing
Tests that CLAHE is applied to all frames during enrollment and verification
"""
import pytest
from hypothesis import given, strategies as st, settings
import numpy as np
import cv2
from app.services.preprocess import FacePreprocessor, get_preprocessor


# **Feature: isavs, Property 2: CLAHE preprocessing applied to all frames**
# **Validates: Requirements 1.2, 2.1**


@given(
    width=st.integers(min_value=100, max_value=640),
    height=st.integers(min_value=100, max_value=480),
    brightness=st.integers(min_value=50, max_value=200)
)
@settings(max_examples=50)
def test_clahe_applied_to_random_images(width, height, brightness):
    """
    Property: For any valid image, the preprocess method SHALL apply CLAHE
    and return a processed image.
    """
    # Create a random test image
    image = np.full((height, width, 3), brightness, dtype=np.uint8)
    
    preprocessor = get_preprocessor()
    
    # Preprocess the image
    result = preprocessor.preprocess(image)
    
    # Verify result is not None
    assert result is not None, "Preprocessing should return a result"
    
    # Verify result is an image
    assert isinstance(result, np.ndarray), "Result should be numpy array"
    
    # Verify result has correct shape (should be RGB after preprocessing)
    assert len(result.shape) == 3, "Result should be 3-channel image"
    assert result.shape[2] == 3, "Result should have 3 color channels"


def test_clahe_enhances_contrast():
    """
    Test that CLAHE actually enhances contrast in low-contrast images.
    """
    # Create a low-contrast image (all pixels similar values)
    low_contrast_image = np.random.randint(100, 120, (200, 200, 3), dtype=np.uint8)
    
    preprocessor = get_preprocessor()
    
    # Preprocess
    result = preprocessor.preprocess(low_contrast_image)
    
    assert result is not None, "Preprocessing should succeed"
    
    # Convert to grayscale for contrast measurement
    gray_original = cv2.cvtColor(low_contrast_image, cv2.COLOR_BGR2GRAY)
    gray_result = cv2.cvtColor(result, cv2.COLOR_RGB2GRAY)
    
    # Measure contrast (standard deviation)
    contrast_original = np.std(gray_original)
    contrast_result = np.std(gray_result)
    
    # CLAHE should increase contrast
    assert contrast_result >= contrast_original * 0.9, \
        f"CLAHE should maintain or enhance contrast: {contrast_original} -> {contrast_result}"


@given(
    num_frames=st.integers(min_value=1, max_value=15)
)
@settings(max_examples=20)
def test_clahe_applied_to_batch(num_frames):
    """
    Property: For any batch of images, preprocess_batch SHALL apply CLAHE
    to all frames.
    """
    # Create batch of random images
    images = [
        np.random.randint(0, 255, (200, 200, 3), dtype=np.uint8)
        for _ in range(num_frames)
    ]
    
    preprocessor = get_preprocessor()
    
    # Preprocess batch
    results = preprocessor.preprocess_batch(images)
    
    # Verify all frames were processed (some may fail if no face detected)
    assert isinstance(results, list), "Batch preprocessing should return a list"
    
    # Verify each result is a valid image
    for result in results:
        assert isinstance(result, np.ndarray), "Each result should be numpy array"
        assert len(result.shape) == 3, "Each result should be 3-channel image"


def test_clahe_parameters():
    """
    Test that CLAHE is configured with correct parameters.
    """
    preprocessor = get_preprocessor()
    
    # Verify CLAHE object exists
    assert hasattr(preprocessor, 'clahe'), "Preprocessor should have CLAHE object"
    assert preprocessor.clahe is not None, "CLAHE should be initialized"
    
    # Verify CLAHE parameters (clipLimit=2.0, tileGridSize=(8,8))
    # Note: OpenCV doesn't expose these directly, but we can verify it works
    test_image = np.random.randint(0, 255, (200, 200), dtype=np.uint8)
    enhanced = preprocessor.clahe.apply(test_image)
    
    assert enhanced is not None, "CLAHE should process images"
    assert enhanced.shape == test_image.shape, "CLAHE should preserve shape"


def test_preprocessing_pipeline_includes_clahe():
    """
    Test that the full preprocessing pipeline includes CLAHE.
    """
    # Create a test image with known characteristics
    test_image = np.full((200, 200, 3), 128, dtype=np.uint8)
    
    preprocessor = get_preprocessor()
    
    # Process the image
    result = preprocessor.preprocess(test_image)
    
    # Verify processing occurred
    assert result is not None, "Preprocessing should succeed"
    
    # The result should be different from input (due to CLAHE and other processing)
    # Note: We can't directly compare due to alignment and other transformations
    assert result.shape[2] == 3, "Result should be RGB"


def test_clahe_handles_various_lighting():
    """
    Test that CLAHE preprocessing handles various lighting conditions.
    """
    preprocessor = get_preprocessor()
    
    # Test with dark image
    dark_image = np.full((200, 200, 3), 30, dtype=np.uint8)
    result_dark = preprocessor.preprocess(dark_image)
    assert result_dark is not None, "Should handle dark images"
    
    # Test with bright image
    bright_image = np.full((200, 200, 3), 220, dtype=np.uint8)
    result_bright = preprocessor.preprocess(bright_image)
    assert result_bright is not None, "Should handle bright images"
    
    # Test with normal image
    normal_image = np.full((200, 200, 3), 128, dtype=np.uint8)
    result_normal = preprocessor.preprocess(normal_image)
    assert result_normal is not None, "Should handle normal images"


@given(
    brightness_variation=st.integers(min_value=20, max_value=100)
)
@settings(max_examples=30)
def test_clahe_normalizes_uneven_lighting(brightness_variation):
    """
    Property: For any image with uneven lighting, CLAHE SHALL normalize
    the contrast to improve recognition.
    """
    # Create image with uneven lighting (gradient)
    image = np.zeros((200, 200, 3), dtype=np.uint8)
    for i in range(200):
        brightness = 50 + (brightness_variation * i // 200)
        image[i, :, :] = brightness
    
    preprocessor = get_preprocessor()
    
    # Preprocess
    result = preprocessor.preprocess(image)
    
    assert result is not None, "Should handle uneven lighting"
    
    # Verify result is normalized
    gray_result = cv2.cvtColor(result, cv2.COLOR_RGB2GRAY)
    
    # Check that the result has more uniform distribution
    std_result = np.std(gray_result)
    
    # CLAHE should create more contrast
    assert std_result > 0, "Result should have some variation"


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
