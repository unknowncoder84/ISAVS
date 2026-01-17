"""
Property-Based Tests for Cosine Similarity Threshold
Validates Requirements 2.4: Cosine similarity threshold is 0.6
"""
import numpy as np
import pytest
from hypothesis import given, strategies as st, settings, HealthCheck

from app.services.face_recognition_service import FaceRecognitionService


class TestCosineSimilarityThreshold:
    """Property 10: Cosine similarity threshold is 0.6"""
    
    @given(
        similarity=st.floats(min_value=0.6, max_value=1.0, allow_nan=False, allow_infinity=False)
    )
    @settings(max_examples=100, suppress_health_check=[HealthCheck.function_scoped_fixture])
    def test_similarity_above_threshold_matches(self, similarity):
        """
        Property: Embeddings with similarity >= 0.6 should match.
        Validates: Requirements 2.4
        """
        face_service = FaceRecognitionService(similarity_threshold=0.6)
        # Create two embeddings with controlled similarity
        embedding1 = np.random.randn(128)
        embedding1 = embedding1 / np.linalg.norm(embedding1)
        
        # Create embedding2 with desired similarity to embedding1
        # Using formula: embedding2 = similarity * embedding1 + sqrt(1 - similarity^2) * orthogonal
        orthogonal = np.random.randn(128)
        orthogonal = orthogonal - np.dot(orthogonal, embedding1) * embedding1
        orthogonal = orthogonal / np.linalg.norm(orthogonal)
        
        embedding2 = similarity * embedding1 + np.sqrt(1 - similarity**2) * orthogonal
        embedding2 = embedding2 / np.linalg.norm(embedding2)
        
        # Verify actual similarity is close to target
        actual_similarity = face_service.cosine_similarity(embedding1, embedding2)
        assert abs(actual_similarity - similarity) < 0.01, \
            f"Actual similarity {actual_similarity} differs from target {similarity}"
        
        # Test comparison
        is_match, computed_similarity = face_service.compare_embeddings(
            embedding1, embedding2, threshold=0.6
        )
        
        # Should match since similarity >= 0.6
        assert is_match, \
            f"Embeddings with similarity {computed_similarity:.3f} >= 0.6 should match"
        assert computed_similarity >= 0.6, \
            f"Computed similarity {computed_similarity} should be >= 0.6"
    
    @given(
        similarity=st.floats(min_value=0.0, max_value=0.59, allow_nan=False, allow_infinity=False)
    )
    @settings(max_examples=100, suppress_health_check=[HealthCheck.function_scoped_fixture])
    def test_similarity_below_threshold_no_match(self, similarity):
        """
        Property: Embeddings with similarity < 0.6 should not match.
        Validates: Requirements 2.4
        """
        face_service = FaceRecognitionService(similarity_threshold=0.6)
        # Create two embeddings with controlled similarity
        embedding1 = np.random.randn(128)
        embedding1 = embedding1 / np.linalg.norm(embedding1)
        
        # Create embedding2 with desired similarity to embedding1
        orthogonal = np.random.randn(128)
        orthogonal = orthogonal - np.dot(orthogonal, embedding1) * embedding1
        orthogonal = orthogonal / np.linalg.norm(orthogonal)
        
        embedding2 = similarity * embedding1 + np.sqrt(max(0, 1 - similarity**2)) * orthogonal
        embedding2 = embedding2 / np.linalg.norm(embedding2)
        
        # Verify actual similarity is close to target
        actual_similarity = face_service.cosine_similarity(embedding1, embedding2)
        
        # Test comparison
        is_match, computed_similarity = face_service.compare_embeddings(
            embedding1, embedding2, threshold=0.6
        )
        
        # Should not match since similarity < 0.6
        assert not is_match, \
            f"Embeddings with similarity {computed_similarity:.3f} < 0.6 should not match"
    
    @given(
        st.integers(min_value=1, max_value=100)
    )
    @settings(max_examples=50, suppress_health_check=[HealthCheck.function_scoped_fixture])
    def test_threshold_boundary_exact(self, seed):
        """
        Property: Embeddings with similarity exactly 0.6 should match.
        Validates: Requirements 2.4 (boundary condition)
        """
        face_service = FaceRecognitionService(similarity_threshold=0.6)
        np.random.seed(seed)
        
        # Create embeddings with similarity exactly 0.6
        embedding1 = np.random.randn(128)
        embedding1 = embedding1 / np.linalg.norm(embedding1)
        
        # Create embedding2 with similarity 0.6
        similarity = 0.6
        orthogonal = np.random.randn(128)
        orthogonal = orthogonal - np.dot(orthogonal, embedding1) * embedding1
        orthogonal = orthogonal / np.linalg.norm(orthogonal)
        
        embedding2 = similarity * embedding1 + np.sqrt(1 - similarity**2) * orthogonal
        embedding2 = embedding2 / np.linalg.norm(embedding2)
        
        # Test comparison
        is_match, computed_similarity = face_service.compare_embeddings(
            embedding1, embedding2, threshold=0.6
        )
        
        # Should match at boundary (>= 0.6)
        assert is_match, \
            f"Embeddings with similarity {computed_similarity:.3f} at threshold 0.6 should match"
    
    def test_identical_embeddings_match(self):
        """
        Property: Identical embeddings should have similarity 1.0 and match.
        Validates: Requirements 2.4
        """
        face_service = FaceRecognitionService(similarity_threshold=0.6)
        embedding = np.random.randn(128)
        embedding = embedding / np.linalg.norm(embedding)
        
        is_match, similarity = face_service.compare_embeddings(
            embedding, embedding.copy(), threshold=0.6
        )
        
        assert is_match, "Identical embeddings should match"
        assert abs(similarity - 1.0) < 0.001, \
            f"Identical embeddings should have similarity 1.0, got {similarity}"
    
    def test_orthogonal_embeddings_no_match(self):
        """
        Property: Orthogonal embeddings should have similarity ~0.0 and not match.
        Validates: Requirements 2.4
        """
        face_service = FaceRecognitionService(similarity_threshold=0.6)
        # Create two orthogonal embeddings
        embedding1 = np.zeros(128)
        embedding1[0] = 1.0
        
        embedding2 = np.zeros(128)
        embedding2[1] = 1.0
        
        is_match, similarity = face_service.compare_embeddings(
            embedding1, embedding2, threshold=0.6
        )
        
        assert not is_match, "Orthogonal embeddings should not match"
        assert abs(similarity) < 0.001, \
            f"Orthogonal embeddings should have similarity ~0.0, got {similarity}"
    
    @given(
        st.integers(min_value=1, max_value=100)
    )
    @settings(max_examples=50, suppress_health_check=[HealthCheck.function_scoped_fixture])
    def test_threshold_consistency(self, seed):
        """
        Property: Comparison result should be consistent with threshold.
        Validates: Requirements 2.4
        """
        face_service = FaceRecognitionService(similarity_threshold=0.6)
        np.random.seed(seed)
        
        embedding1 = np.random.randn(128)
        embedding1 = embedding1 / np.linalg.norm(embedding1)
        
        embedding2 = np.random.randn(128)
        embedding2 = embedding2 / np.linalg.norm(embedding2)
        
        is_match, similarity = face_service.compare_embeddings(
            embedding1, embedding2, threshold=0.6
        )
        
        # Verify consistency
        if similarity >= 0.6:
            assert is_match, \
                f"Similarity {similarity:.3f} >= 0.6 should result in match"
        else:
            assert not is_match, \
                f"Similarity {similarity:.3f} < 0.6 should not result in match"
    
    def test_service_default_threshold(self):
        """
        Property: FaceRecognitionService should use 0.6 as default threshold from settings.
        Validates: Requirements 2.4
        """
        from app.core.config import settings
        service = FaceRecognitionService()
        assert service.similarity_threshold == settings.FACE_SIMILARITY_THRESHOLD, \
            f"Default threshold should be {settings.FACE_SIMILARITY_THRESHOLD}, got {service.similarity_threshold}"
        assert settings.FACE_SIMILARITY_THRESHOLD == 0.6, \
            f"Settings threshold should be 0.6, got {settings.FACE_SIMILARITY_THRESHOLD}"
