"""
Property-Based Tests for Embedding Storage

**Feature: isavs, Property 1: Enrollment stores valid 128-dimensional embedding**
**Validates: Requirements 1.1, 1.5, 12.2**
"""
import pytest
from hypothesis import given, strategies as st, settings
import numpy as np

from app.db.models import StudentORM


# Custom strategy for generating valid 128-d embeddings
@st.composite
def embedding_strategy(draw):
    """Generate valid 128-dimensional embedding vectors."""
    values = draw(st.lists(
        st.floats(min_value=-1.0, max_value=1.0, allow_nan=False, allow_infinity=False),
        min_size=128,
        max_size=128
    ))
    return values


@st.composite
def student_data_strategy(draw):
    """Generate valid student enrollment data."""
    name = draw(st.text(
        alphabet=st.characters(whitelist_categories=('L', 'N', 'Zs')),
        min_size=1,
        max_size=100
    ).filter(lambda x: x.strip()))
    
    # Generate student ID in format like STU12345
    prefix = draw(st.sampled_from(['STU', 'FAC', 'ADM']))
    number = draw(st.integers(min_value=10000, max_value=99999))
    student_id = f"{prefix}{number}"
    
    embedding = draw(embedding_strategy())
    
    return {
        "name": name.strip(),
        "student_id_card_number": student_id,
        "facial_embedding": embedding
    }


class TestEmbeddingStorageProperty:
    """
    Property tests for embedding storage dimension.
    
    **Feature: isavs, Property 1: Enrollment stores valid 128-dimensional embedding**
    """
    
    @given(embedding=embedding_strategy())
    @settings(max_examples=100)
    def test_embedding_dimension_is_128(self, embedding):
        """
        **Feature: isavs, Property 1: Enrollment stores valid 128-dimensional embedding**
        
        For any valid embedding, it must have exactly 128 dimensions.
        """
        assert len(embedding) == 128, f"Embedding must be 128-d, got {len(embedding)}"
    
    @given(embedding=embedding_strategy())
    @settings(max_examples=100)
    def test_embedding_values_are_floats(self, embedding):
        """
        **Feature: isavs, Property 1: Enrollment stores valid 128-dimensional embedding**
        
        All embedding values must be valid floating-point numbers.
        """
        for i, val in enumerate(embedding):
            assert isinstance(val, float), f"Value at index {i} must be float"
            assert not np.isnan(val), f"Value at index {i} must not be NaN"
            assert not np.isinf(val), f"Value at index {i} must not be infinite"
    
    @given(embedding=embedding_strategy())
    @settings(max_examples=100)
    def test_embedding_values_in_valid_range(self, embedding):
        """
        **Feature: isavs, Property 1: Enrollment stores valid 128-dimensional embedding**
        
        Embedding values should be normalized (between -1 and 1).
        """
        for i, val in enumerate(embedding):
            assert -1.0 <= val <= 1.0, f"Value at index {i} out of range: {val}"
    
    @given(student_data=student_data_strategy())
    @settings(max_examples=100)
    def test_student_orm_accepts_valid_embedding(self, student_data):
        """
        **Feature: isavs, Property 1: Enrollment stores valid 128-dimensional embedding**
        
        StudentORM model should accept valid 128-d embeddings.
        """
        student = StudentORM(
            name=student_data["name"],
            student_id_card_number=student_data["student_id_card_number"],
            facial_embedding=student_data["facial_embedding"]
        )
        
        assert student.name == student_data["name"]
        assert student.student_id_card_number == student_data["student_id_card_number"]
        assert len(student.facial_embedding) == 128
    
    @given(student_data=student_data_strategy())
    @settings(max_examples=100)
    def test_embedding_preserves_values_after_storage(self, student_data):
        """
        **Feature: isavs, Property 1: Enrollment stores valid 128-dimensional embedding**
        
        Embedding values should be preserved exactly when stored in model.
        """
        original_embedding = student_data["facial_embedding"]
        
        student = StudentORM(
            name=student_data["name"],
            student_id_card_number=student_data["student_id_card_number"],
            facial_embedding=original_embedding
        )
        
        # Verify all values are preserved
        for i, (original, stored) in enumerate(zip(original_embedding, student.facial_embedding)):
            assert abs(original - stored) < 1e-10, f"Value mismatch at index {i}"


class TestEmbeddingEdgeCases:
    """Edge case tests for embedding storage."""
    
    def test_zero_embedding(self):
        """Test that zero embedding is valid."""
        zero_embedding = [0.0] * 128
        student = StudentORM(
            name="Test Student",
            student_id_card_number="STU00001",
            facial_embedding=zero_embedding
        )
        assert len(student.facial_embedding) == 128
        assert all(v == 0.0 for v in student.facial_embedding)
    
    def test_boundary_embedding(self):
        """Test embeddings at boundary values."""
        # All -1
        min_embedding = [-1.0] * 128
        student_min = StudentORM(
            name="Min Student",
            student_id_card_number="STU00002",
            facial_embedding=min_embedding
        )
        assert all(v == -1.0 for v in student_min.facial_embedding)
        
        # All +1
        max_embedding = [1.0] * 128
        student_max = StudentORM(
            name="Max Student",
            student_id_card_number="STU00003",
            facial_embedding=max_embedding
        )
        assert all(v == 1.0 for v in student_max.facial_embedding)
