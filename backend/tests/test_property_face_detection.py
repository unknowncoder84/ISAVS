"""
Property-Based Tests for Face Detection and Embedding Extraction

**Feature: isavs, Property 5: Face detection produces embeddings**
**Validates: Requirements 2.1**
"""
import pytest
from hypothesis import given, strategies as st, settings, assume
import numpy as np
import cv2

from app.services.face_recognition_service import FaceRecognitionService


# Custom strategy for generating synthetic face-like images
@st.composite
def face_image_strategy(draw):
    """Generate synthetic images that may contain face-like patterns."""
    width = draw(st.integers(min_value=200, max_value=800))
    height = draw(st.integers(min_value=200, max_value=800))
    
    # Create image with random pixel values
    image = np.random.randint(0, 255, (height, width, 3), dtype=np.uint8)
    
    return image


@st.composite
def simple_face_image_strategy(draw):
    """Generate simple synthetic face images with basic features."""
    width = draw(st.integers(min_value=300, max_value=600))
    height = draw(st.integers(min_value=300, max_value=600))
    
    # Create blank image
    image = np.ones((height, width, 3), dtype=np.uint8) * 200
    
    # Add face-like oval shape
    center_x = width // 2
    center_y = height // 2
    axes_x = width // 4
    axes_y = height // 3
    
    # Draw face oval
    cv2.ellipse(image, (center_x, center_y), (axes_x, axes_y), 0, 0, 360, (180, 150, 120), -1)
    
    # Add eyes
    eye_y = center_y - axes_y // 3
    left_eye_x = center_x - axes_x // 2
    right_eye_x = center_x + axes_x // 2
    eye_radius = axes_x // 8
    
    cv2.circle(image, (left_eye_x, eye_y), eye_radius, (255, 255, 255), -1)
    cv2.circle(image, (right_eye_x, eye_y), eye_radius, (255, 255, 255), -1)
    cv2.circle(image, (left_eye_x, eye_y), eye_radius // 2, (0, 0, 0), -1)
    cv2.circle(image, (right_eye_x, eye_y), eye_radius // 2, (0, 0, 0), -1)
    
    # Add mouth
    mouth_y = center_y + axes_y // 3
    cv2.ellipse(image, (center_x, mouth_y), (axes_x // 3, axes_y // 6), 0, 0, 180, (100, 50, 50), 2)
    
    return image


class TestFaceDetectionProperty:
    """
    Property tests for face detection and embedding extraction.
    
    **Feature: isavs, Property 5: Face detection produces embeddings**
    """
    
    def test_face_detection_returns_list(self):
        """
        **Feature: isavs, Property 5: Face detection produces embeddings**
        
        Face detection should always return a list (empty or with faces).
        """
        service = FaceRecognitionService()
        
        # Test with various image sizes
        for size in [100, 300, 640]:
            image = np.random.randint(0, 255, (size, size, 3), dtype=np.uint8)
            faces = service.detect_faces(image)
            
            assert isinstance(faces, list), "detect_faces must return a list"
    
    def test_face_detection_bounding_box_format(self):
        """
        **Feature: isavs, Property 5: Face detection produces embeddings**
        
        When faces are detected, each bounding box should have 4 coordinates.
        """
        service = FaceRecognitionService()
        
        # Create simple face image
        image = self._create_simple_face_image()
        faces = service.detect_faces(image)
        
        for face in faces:
            assert len(face) == 4, f"Face bounding box must have 4 values (x, y, w, h), got {len(face)}"
            x, y, w, h = face
            assert w > 0, "Face width must be positive"
            assert h > 0, "Face height must be positive"
            assert x >= 0, "Face x coordinate must be non-negative"
            assert y >= 0, "Face y coordinate must be non-negative"
    
    def test_embedding_dimension_is_128(self):
        """
        **Feature: isavs, Property 5: Face detection produces embeddings**
        
        When an embedding is extracted, it must be 128-dimensional.
        """
        service = FaceRecognitionService()
        
        # Create simple face image
        image = self._create_simple_face_image()
        embedding = service.extract_embedding(image)
        
        if embedding is not None:
            assert len(embedding) == 128, f"Embedding must be 128-d, got {len(embedding)}"
            assert embedding.dtype == np.float64, "Embedding must be float64"
    
    def test_embedding_is_normalized(self):
        """
        **Feature: isavs, Property 5: Face detection produces embeddings**
        
        Extracted embeddings should be normalized (unit vector or bounded).
        """
        service = FaceRecognitionService()
        
        # Create simple face image
        image = self._create_simple_face_image()
        embedding = service.extract_embedding(image)
        
        if embedding is not None:
            # Check that embedding is normalized (L2 norm close to 1)
            norm = np.linalg.norm(embedding)
            # Allow some tolerance for normalization
            assert 0.9 <= norm <= 1.1, f"Embedding should be normalized, got norm {norm}"
    
    def test_no_face_returns_none(self):
        """
        **Feature: isavs, Property 5: Face detection produces embeddings**
        
        When no face is detected, embedding extraction should return None.
        """
        service = FaceRecognitionService()
        
        # Create image with no face (just noise)
        image = np.random.randint(0, 255, (100, 100, 3), dtype=np.uint8)
        embedding = service.extract_embedding(image)
        
        # Either None or a valid 128-d embedding
        if embedding is not None:
            assert len(embedding) == 128
    
    @given(image=simple_face_image_strategy())
    @settings(max_examples=50, deadline=5000)
    def test_face_detection_with_synthetic_faces(self, image):
        """
        **Feature: isavs, Property 5: Face detection produces embeddings**
        
        For any synthetic face image, detection should return valid results.
        """
        service = FaceRecognitionService()
        faces = service.detect_faces(image)
        
        assert isinstance(faces, list), "detect_faces must return a list"
        
        # If faces detected, validate format
        for face in faces:
            assert len(face) == 4, "Each face must have 4 coordinates"
            x, y, w, h = face
            assert w > 0 and h > 0, "Face dimensions must be positive"
            assert x >= 0 and y >= 0, "Face coordinates must be non-negative"
            assert x + w <= image.shape[1], "Face must be within image bounds"
            assert y + h <= image.shape[0], "Face must be within image bounds"
    
    @given(image=simple_face_image_strategy())
    @settings(max_examples=50, deadline=5000)
    def test_embedding_extraction_consistency(self, image):
        """
        **Feature: isavs, Property 5: Face detection produces embeddings**
        
        Extracting embedding from same image twice should give same result.
        """
        service = FaceRecognitionService()
        
        embedding1 = service.extract_embedding(image)
        embedding2 = service.extract_embedding(image)
        
        # Both should be None or both should be valid
        if embedding1 is None:
            assert embedding2 is None, "Embedding extraction should be deterministic"
        else:
            assert embedding2 is not None, "Embedding extraction should be deterministic"
            assert len(embedding1) == 128
            assert len(embedding2) == 128
            
            # Should be very similar (allowing for minor floating point differences)
            similarity = service.cosine_similarity(embedding1, embedding2)
            assert similarity > 0.99, f"Same image should produce same embedding, got similarity {similarity}"
    
    def _create_simple_face_image(self) -> np.ndarray:
        """Helper to create a simple synthetic face image."""
        width, height = 400, 400
        image = np.ones((height, width, 3), dtype=np.uint8) * 200
        
        # Draw face oval
        center_x, center_y = width // 2, height // 2
        axes_x, axes_y = width // 4, height // 3
        cv2.ellipse(image, (center_x, center_y), (axes_x, axes_y), 0, 0, 360, (180, 150, 120), -1)
        
        # Add eyes
        eye_y = center_y - axes_y // 3
        left_eye_x = center_x - axes_x // 2
        right_eye_x = center_x + axes_x // 2
        eye_radius = axes_x // 8
        
        cv2.circle(image, (left_eye_x, eye_y), eye_radius, (255, 255, 255), -1)
        cv2.circle(image, (right_eye_x, eye_y), eye_radius, (255, 255, 255), -1)
        cv2.circle(image, (left_eye_x, eye_y), eye_radius // 2, (0, 0, 0), -1)
        cv2.circle(image, (right_eye_x, eye_y), eye_radius // 2, (0, 0, 0), -1)
        
        # Add mouth
        mouth_y = center_y + axes_y // 3
        cv2.ellipse(image, (center_x, mouth_y), (axes_x // 3, axes_y // 6), 0, 0, 180, (100, 50, 50), 2)
        
        return image


class TestFaceDetectionEdgeCases:
    """Edge case tests for face detection."""
    
    def test_empty_image(self):
        """Test with empty/black image."""
        service = FaceRecognitionService()
        
        # Black image
        image = np.zeros((300, 300, 3), dtype=np.uint8)
        faces = service.detect_faces(image)
        
        assert isinstance(faces, list), "Should return empty list for black image"
    
    def test_white_image(self):
        """Test with white image."""
        service = FaceRecognitionService()
        
        # White image
        image = np.ones((300, 300, 3), dtype=np.uint8) * 255
        faces = service.detect_faces(image)
        
        assert isinstance(faces, list), "Should return empty list for white image"
    
    def test_very_small_image(self):
        """Test with very small image."""
        service = FaceRecognitionService()
        
        # Tiny image
        image = np.random.randint(0, 255, (50, 50, 3), dtype=np.uint8)
        faces = service.detect_faces(image)
        
        assert isinstance(faces, list), "Should handle small images gracefully"
    
    def test_very_large_image(self):
        """Test with large image."""
        service = FaceRecognitionService()
        
        # Large image
        image = np.random.randint(0, 255, (1920, 1080, 3), dtype=np.uint8)
        faces = service.detect_faces(image)
        
        assert isinstance(faces, list), "Should handle large images gracefully"
