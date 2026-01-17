"""
Property-Based Tests for Motion-Image Correlation
Tests Property 9: Motion-image correlation threshold
Validates Requirements: 5.3, 5.4
"""
import pytest
import numpy as np
from hypothesis import given, strategies as st, assume, settings

from app.services.motion_image_correlator import (
    get_motion_image_correlator,
    MotionData
)


# ============== Property 9: Motion-Image Correlation Threshold ==============

@given(
    correlation=st.floats(min_value=-1.0, max_value=1.0, allow_nan=False, allow_infinity=False)
)
def test_property_correlation_threshold_enforcement(correlation):
    """
    Property 9: Motion-image correlation threshold enforcement
    
    For any correlation coefficient:
    - If correlation >= 0.7 → liveness passes
    - If correlation < 0.7 → liveness fails
    
    Validates:
    - Requirement 5.3: Correlation threshold of 0.7
    - Requirement 5.4: Liveness detection accuracy
    """
    correlator = get_motion_image_correlator()
    
    result = correlator.validate_motion_correlation(correlation)
    
    # Property: Threshold enforcement
    if correlation >= 0.7:
        assert result.passed, f"Correlation {correlation} >= 0.7 should pass"
        assert result.anomaly_type is None
    else:
        assert not result.passed, f"Correlation {correlation} < 0.7 should fail"
        assert result.anomaly_type == "motion_correlation_violation"
    
    assert result.value == correlation
    assert result.threshold == 0.7


@given(correlation=st.floats(min_value=-1.0, max_value=1.0, allow_nan=False, allow_infinity=False))
def test_property_correlation_monotonicity(correlation):
    """
    Property: Correlation validation is monotonic
    
    If correlation1 > correlation2 and correlation1 passes, then correlation2 should fail
    (or both pass if correlation2 >= 0.7)
    """
    correlator = get_motion_image_correlator()
    
    result = correlator.validate_motion_correlation(correlation)
    
    # If this correlation passes, any higher correlation should also pass
    if result.passed and correlation < 1.0:
        higher_correlation = min(correlation + 0.1, 1.0)
        higher_result = correlator.validate_motion_correlation(higher_correlation)
        assert higher_result.passed, \
            f"Higher correlation {higher_correlation} should pass if {correlation} passes"


@given(
    n_samples=st.integers(min_value=10, max_value=100),
    noise_level=st.floats(min_value=0.0, max_value=0.5)
)
@settings(deadline=1000)  # Allow more time for computation
def test_property_perfect_correlation(n_samples, noise_level):
    """
    Property: Perfect correlation (r=1.0) should always pass
    
    When motion and optical flow are identical (or nearly identical), correlation should be ~1.0
    """
    correlator = get_motion_image_correlator()
    
    # Generate identical signals with small noise
    signal = np.random.rand(n_samples)
    flow = signal + np.random.normal(0, noise_level, n_samples)
    motion = signal + np.random.normal(0, noise_level, n_samples)
    
    correlation, p_value = correlator.calculate_correlation(
        flow.tolist(),
        motion.tolist()
    )
    
    # Property: High correlation should pass
    if correlation >= 0.7:
        result = correlator.validate_motion_correlation(correlation)
        assert result.passed, f"High correlation {correlation} should pass"


@given(
    n_samples=st.integers(min_value=10, max_value=100)
)
@settings(deadline=1000)
def test_property_zero_correlation(n_samples):
    """
    Property: Zero correlation (r≈0) should fail
    
    When motion and optical flow are uncorrelated, correlation should be ~0 and fail
    """
    correlator = get_motion_image_correlator()
    
    # Generate uncorrelated signals
    flow = np.random.rand(n_samples).tolist()
    motion = np.random.rand(n_samples).tolist()
    
    correlation, p_value = correlator.calculate_correlation(flow, motion)
    
    # Property: Low correlation should fail
    if abs(correlation) < 0.7:
        result = correlator.validate_motion_correlation(correlation)
        assert not result.passed, f"Low correlation {correlation} should fail"


@given(correlation=st.floats(min_value=0.69, max_value=0.71))
def test_property_correlation_boundary_behavior(correlation):
    """
    Property: Boundary behavior at 0.7 threshold
    
    Values very close to 0.7 should behave consistently with the threshold rule.
    """
    correlator = get_motion_image_correlator()
    
    result = correlator.validate_motion_correlation(correlation)
    
    # Property: Strict threshold enforcement
    if correlation >= 0.7:
        assert result.passed, f"Correlation {correlation} >= 0.7 should pass"
    else:
        assert not result.passed, f"Correlation {correlation} < 0.7 should fail"


@given(
    n_samples=st.integers(min_value=10, max_value=50),
    scale_factor=st.floats(min_value=0.1, max_value=10.0)
)
@settings(deadline=1000)
def test_property_correlation_scale_invariance(n_samples, scale_factor):
    """
    Property: Correlation is scale-invariant
    
    Scaling both signals by the same factor should not change correlation.
    """
    correlator = get_motion_image_correlator()
    
    # Generate correlated signals
    base_signal = np.random.rand(n_samples)
    flow = base_signal + np.random.normal(0, 0.1, n_samples)
    motion = base_signal + np.random.normal(0, 0.1, n_samples)
    
    # Calculate original correlation
    corr1, _ = correlator.calculate_correlation(flow.tolist(), motion.tolist())
    
    # Scale both signals
    flow_scaled = flow * scale_factor
    motion_scaled = motion * scale_factor
    
    # Calculate scaled correlation
    corr2, _ = correlator.calculate_correlation(
        flow_scaled.tolist(),
        motion_scaled.tolist()
    )
    
    # Property: Correlation should be approximately the same
    assert abs(corr1 - corr2) < 0.01, \
        f"Correlation should be scale-invariant: {corr1} vs {corr2}"


# ============== Edge Cases ==============

def test_correlation_exact_threshold():
    """Test exact threshold value 0.7"""
    correlator = get_motion_image_correlator()
    
    # Exactly at threshold should pass (>= 0.7)
    result = correlator.validate_motion_correlation(0.7)
    assert result.passed, "Correlation exactly at 0.7 should pass"


def test_correlation_perfect():
    """Test perfect correlation (r=1.0)"""
    correlator = get_motion_image_correlator()
    
    result = correlator.validate_motion_correlation(1.0)
    assert result.passed, "Perfect correlation should pass"


def test_correlation_negative():
    """Test negative correlation (anti-correlated)"""
    correlator = get_motion_image_correlator()
    
    result = correlator.validate_motion_correlation(-0.8)
    assert not result.passed, "Negative correlation should fail"


def test_correlation_invalid_range():
    """Test invalid correlation values outside [-1, 1]"""
    correlator = get_motion_image_correlator()
    
    # Test > 1
    result = correlator.validate_motion_correlation(1.5)
    assert not result.passed, "Correlation > 1 should fail"
    assert result.anomaly_type == "invalid_correlation_value"
    
    # Test < -1
    result = correlator.validate_motion_correlation(-1.5)
    assert not result.passed, "Correlation < -1 should fail"
    assert result.anomaly_type == "invalid_correlation_value"


def test_calculate_correlation_insufficient_samples():
    """Test correlation calculation with insufficient samples"""
    correlator = get_motion_image_correlator()
    
    # Less than MIN_SAMPLES (10)
    flow = [1.0, 2.0, 3.0]
    motion = [1.1, 2.1, 3.1]
    
    with pytest.raises(ValueError, match="Need at least 10 samples"):
        correlator.calculate_correlation(flow, motion)


def test_calculate_correlation_mismatched_length():
    """Test correlation calculation with mismatched array lengths"""
    correlator = get_motion_image_correlator()
    
    flow = [1.0] * 20
    motion = [1.0] * 15
    
    with pytest.raises(ValueError, match="same length"):
        correlator.calculate_correlation(flow, motion)


def test_motion_magnitude_calculation():
    """Test motion magnitude calculation from accelerometer and gyroscope"""
    correlator = get_motion_image_correlator()
    
    motion_data = MotionData(
        timestamps=[0.0, 0.02, 0.04],
        accelerometer_x=[1.0, 2.0, 3.0],
        accelerometer_y=[0.5, 1.0, 1.5],
        accelerometer_z=[0.2, 0.4, 0.6],
        gyroscope_x=[0.1, 0.2, 0.3],
        gyroscope_y=[0.05, 0.1, 0.15],
        gyroscope_z=[0.02, 0.04, 0.06]
    )
    
    magnitudes, timestamps = correlator.calculate_motion_magnitude(motion_data)
    
    assert len(magnitudes) == 3
    assert len(timestamps) == 3
    assert all(m > 0 for m in magnitudes), "All magnitudes should be positive"


def test_timestamp_alignment():
    """Test timestamp alignment with tolerance"""
    correlator = get_motion_image_correlator()
    
    # Flow timestamps
    flow_magnitudes = [1.0, 2.0, 3.0]
    flow_timestamps = [0.0, 0.02, 0.04]
    
    # Motion timestamps (slightly offset)
    motion_magnitudes = [1.1, 2.1, 3.1, 4.1]
    motion_timestamps = [0.001, 0.021, 0.041, 0.061]  # Within 20ms tolerance
    
    aligned_flow, aligned_motion = correlator.align_timestamps(
        flow_magnitudes, flow_timestamps,
        motion_magnitudes, motion_timestamps
    )
    
    assert len(aligned_flow) == len(aligned_motion)
    assert len(aligned_flow) == 3, "Should align 3 samples within tolerance"


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
