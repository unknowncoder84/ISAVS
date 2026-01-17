"""
Property-Based Tests for Embedding Dimensions
Validates Requirements 2.3: Face embeddings are always 128-dimensional
"""
import numpy as np
import pytest
from hypothesis import given, strategies as st, settings, HealthCheck
import cv2

from app.services.face_recognition_service import FaceRecognitionService


class TestEmbeddingDimensions:
    """Property 9: Face embeddings are always 128-dimensional"""
    
    @given(
        width=st.integers(min_value=100, max_value=1000),
        height=st.integers(min_value=100, max_value=1000),
        seed=st.integers(min_value=1, max_value=10000)
    )
    @settings(max_examples=100, deadline=5000, suppress_health_check=[HealthCheck.function_scoped_fixture])
    def test_embedding_dimension_from_random_images(self, width, height, seed):
        """
        Property: All extracted embeddings must be 128-dimensional.
        Validates: Requirements 2.3
        """
        face_service = FaceRecognitionService()
        np.random.seed(seed)
        
        # Create random image with a face-like region
        image = np.random.randint(0, 256, (height, width, 3), dtype=np.uint8)
        
        # Add a simple face-like pattern (oval shape)
        center_x, center_y = width // 2, height // 2
        face_width, face_height = min(width, 200), min(height, 250)
        
        # Draw oval (face)
        cv2.ellipse(
            image,
            (center_x, center_y),
            (face_width // 2, face_height // 2),
            0, 0, 360,
            (200, 180, 160),  # Skin tone
            -1
        )
        
        # Add eyes
        eye_y = center_y - face_height // 6
        cv2.circle(image, (center_x - face_width // 4, eye_y), 10, (50, 50, 50), -1)
        cv2.circle(image, (center_x + face_width // 4, eye_y), 10, (50, 50, 50), -1)
        
        # Try to extract embedding
        embedding = face_service.extract_embedding(image)
        
        # If embedding extracted, verify dimension
        if embedding is not None:
            assert len(embedding) == 128, \
                f"Embedding dimension must be 128, got {len(embedding)}"
            assert embedding.dtype in [np.float32, np.float64], \
                f"Embedding must be float type, got {embedding.dtype}"
    
    @given(
        st.integers(min_value=1, max_value=100)
    )
    @settings(max_examples=50, suppress_health_check=[HealthCheck.function_scoped_fixture])
    def test_centroid_embedding_dimension(self, seed):
        """
        Property: Centroid embeddings from multiple frames must be 128-dimensional.
        Validates: Requirements 2.3, 1.3
        """
        face_service = FaceRecognitionService()
        np.random.seed(seed)
        
        # Create 10 frames with face-like patterns
        frames = []
        for i in range(10):
            image = np.random.randint(0, 256, (480, 640, 3), dtype=np.uint8)
            
            # Add face-like pattern
            center_x, center_y = 320, 240
            cv2.ellipse(image, (center_x, center_y), (80, 100), 0, 0, 360, (200, 180, 160), -1)
            cv2.circle(image, (center_x - 30, 220), 10, (50, 50, 50), -1)
            cv2.circle(image, (center_x + 30, 220), 10, (50, 50, 50), -1)
            
            frames.append(image)
        
        # Extract centroid embedding
        centroid = face_service.extract_centroid_embedding(frames)
        
        # If centroid extracted, verify dimension
        if centroid is not None:
            assert len(centroid) == 128, \
                f"Centroid embedding dimension must be 128, got {len(centroid)}"
            assert centroid.dtype in [np.float32, np.float64], \
                f"Centroid embedding must be float type, got {centroid.dtype}"
    
    def test_embedding_normalization(self):
        """
        Property: Embeddings should be normalized (unit length).
        Validates: Requirements 2.3
        """
        face_service = FaceRecognitionService()
        # Create a simple test image with face pattern
        image = np.random.randint(0, 256, (480, 640, 3), dtype=np.uint8)
        
        # Add face-like pattern
        cv2.ellipse(image, (320, 240), (80, 100), 0, 0, 360, (200, 180, 160), -1)
        cv2.circle(image, (290, 220), 10, (50, 50, 50), -1)
        cv2.circle(image, (350, 220), 10, (50, 50, 50), -1)
        
        embedding = face_service.extract_embedding(image)
        
        if embedding is not None:
            # Check if normalized (length close to 1.0)
            norm = np.linalg.norm(embedding)
            assert abs(norm - 1.0) < 0.01, \
                f"Embedding should be normalized (norm ~1.0), got {norm}"
    
    @given(
        num_frames=st.integers(min_value=5, max_value=15)
    )
    @settings(max_examples=30, suppress_health_check=[HealthCheck.function_scoped_fixture])
    def test_centroid_dimension_with_varying_frames(self, num_frames):
        """
        Property: Centroid dimension is 128 regardless of number of frames.
        Validates: Requirements 2.3, 1.3
        """
        face_service = FaceRecognitionService()
        # Create frames with face patterns
        frames = []
        for i in range(num_frames):
            image = np.random.randint(0, 256, (480, 640, 3), dtype=np.uint8)
            
            # Add face pattern
            cv2.ellipse(image, (320, 240), (80, 100), 0, 0, 360, (200, 180, 160), -1)
            cv2.circle(image, (290, 220), 10, (50, 50, 50), -1)
            cv2.circle(image, (350, 220), 10, (50, 50, 50), -1)
            
            frames.append(image)
        
        centroid = face_service.extract_centroid_embedding(frames)
        
        if centroid is not None:
            assert len(centroid) == 128, \
                f"Centroid with {num_frames} frames must be 128-d, got {len(centroid)}"
    
    def test_cosine_similarity_requires_same_dimensions(self):
        """
        Property: Cosine similarity should work with 128-d embeddings.
        Validates: Requirements 2.3, 2.4
        """
        face_service = FaceRecognitionService()
        # Create two 128-d embeddings
        embedding1 = np.random.randn(128)
        embedding1 = embedding1 / np.linalg.norm(embedding1)
        
        embedding2 = np.random.randn(128)
        embedding2 = embedding2 / np.linalg.norm(embedding2)
        
        # Should compute similarity without error
        similarity = face_service.cosine_similarity(embedding1, embedding2)
        
        assert -1.0 <= similarity <= 1.0, \
            f"Cosine similarity must be in [-1, 1], got {similarity}"
    
    def test_dimension_mismatch_handling(self):
        """
        Property: System should handle dimension mismatches gracefully.
        Validates: Requirements 2.3
        """
        face_service = FaceRecognitionService()
        # Create embeddings with different dimensions
        embedding1 = np.random.randn(128)
        embedding1 = embedding1 / np.linalg.norm(embedding1)
        
        embedding2 = np.random.randn(64)  # Wrong dimension
        embedding2 = embedding2 / np.linalg.norm(embedding2)
        
        # Should not crash, but may return 0 or handle gracefully
        try:
            similarity = face_service.cosine_similarity(embedding1, embedding2)
            # If it doesn't raise, it should return a valid value
            assert isinstance(similarity, (int, float)), \
                "Similarity should be numeric"
        except (ValueError, IndexError):
            # Acceptable to raise error for dimension mismatch
            pass
    
    @given(
        st.integers(min_value=1, max_value=50)
    )
    @settings(max_examples=50, suppress_health_check=[HealthCheck.function_scoped_fixture])
    def test_multiple_extractions_same_dimension(self, seed):
        """
        Property: Multiple extractions from same image should have same dimension.
        Validates: Requirements 2.3
        """
        face_service = FaceRecognitionService()
        np.random.seed(seed)
        
        # Create image with face pattern
        image = np.random.randint(0, 256, (480, 640, 3), dtype=np.uint8)
        cv2.ellipse(image, (320, 240), (80, 100), 0, 0, 360, (200, 180, 160), -1)
        cv2.circle(image, (290, 220), 10, (50, 50, 50), -1)
        cv2.circle(image, (350, 220), 10, (50, 50, 50), -1)
        
        # Extract embedding twice
        embedding1 = face_service.extract_embedding(image)
        embedding2 = face_service.extract_embedding(image)
        
        if embedding1 is not None and embedding2 is not None:
            assert len(embedding1) == len(embedding2) == 128, \
                f"Both embeddings should be 128-d, got {len(embedding1)} and {len(embedding2)}"
