"""
Property-Based Tests for BLE RSSI Threshold
Tests Property 1: RSSI threshold enforcement
Validates Requirements: 1.4, 1.5, 2.3, 2.4
"""
import pytest
from hypothesis import given, strategies as st, assume

from app.services.sensor_validation_service import get_sensor_validation_service


# ============== Property 1: RSSI Threshold Enforcement ==============

@given(
    rssi=st.floats(min_value=-120, max_value=-20),
    beacon_uuid=st.text(min_size=36, max_size=36),
    session_uuid=st.text(min_size=36, max_size=36)
)
def test_property_rssi_threshold_enforcement(rssi, beacon_uuid, session_uuid):
    """
    Property 1: RSSI threshold enforcement
    
    For any RSSI value:
    - If RSSI > -70 dBm AND beacon UUID matches → validation passes
    - If RSSI <= -70 dBm OR beacon UUID mismatch → validation fails
    
    Validates:
    - Requirement 1.4: RSSI threshold of -70 dBm
    - Requirement 1.5: Beacon UUID matching
    - Requirement 2.3: Proximity validation
    - Requirement 2.4: Signal strength enforcement
    """
    service = get_sensor_validation_service()
    
    # Test with matching UUID
    result_match = service.validate_ble_proximity(rssi, beacon_uuid, beacon_uuid)
    
    # Property: RSSI > -70 with matching UUID should pass
    if rssi > -70:
        assert result_match.passed, f"RSSI {rssi} > -70 with matching UUID should pass"
        assert result_match.value == rssi
        assert result_match.threshold == -70.0
        assert result_match.anomaly_type is None
    else:
        assert not result_match.passed, f"RSSI {rssi} <= -70 should fail"
        assert result_match.anomaly_type == "ble_proximity_violation"
    
    # Test with mismatched UUID
    if beacon_uuid != session_uuid:
        result_mismatch = service.validate_ble_proximity(rssi, beacon_uuid, session_uuid)
        
        # Property: UUID mismatch should always fail
        assert not result_mismatch.passed, "UUID mismatch should always fail"
        assert result_mismatch.anomaly_type == "ble_uuid_mismatch"


@given(rssi=st.floats(min_value=-120, max_value=-20))
def test_property_rssi_monotonicity(rssi):
    """
    Property: RSSI validation is monotonic
    
    If RSSI1 > RSSI2 and RSSI1 passes, then RSSI2 should fail (or both pass if RSSI2 > -70)
    Stronger signal (less negative) should not fail if weaker signal passes.
    """
    service = get_sensor_validation_service()
    uuid = "test-beacon-uuid"
    
    result = service.validate_ble_proximity(rssi, uuid, uuid)
    
    # If this RSSI passes, any stronger signal should also pass
    if result.passed:
        stronger_rssi = rssi + 10  # More positive = stronger signal
        stronger_result = service.validate_ble_proximity(stronger_rssi, uuid, uuid)
        assert stronger_result.passed, f"Stronger RSSI {stronger_rssi} should pass if {rssi} passes"


@given(
    rssi=st.floats(min_value=-120, max_value=-20),
    uuid=st.text(min_size=36, max_size=36)
)
def test_property_rssi_distance_estimation(rssi, uuid):
    """
    Property: Distance estimation is inversely related to RSSI
    
    Stronger signal (higher RSSI) should result in shorter estimated distance.
    """
    service = get_sensor_validation_service()
    
    result = service.validate_ble_proximity(rssi, uuid, uuid)
    
    # Extract distance from metadata if available
    if result.metadata and "estimated_distance" in result.metadata:
        distance = result.metadata["estimated_distance"]
        
        # Test with stronger signal
        stronger_rssi = rssi + 10
        stronger_result = service.validate_ble_proximity(stronger_rssi, uuid, uuid)
        
        if stronger_result.metadata and "estimated_distance" in stronger_result.metadata:
            stronger_distance = stronger_result.metadata["estimated_distance"]
            
            # Property: Stronger signal → shorter distance
            assert stronger_distance < distance, \
                f"Stronger RSSI {stronger_rssi} should have shorter distance than {rssi}"


@given(rssi=st.floats(min_value=-70.1, max_value=-69.9))
def test_property_rssi_boundary_behavior(rssi):
    """
    Property: Boundary behavior at -70 dBm threshold
    
    Values very close to -70 should behave consistently with the threshold rule.
    """
    service = get_sensor_validation_service()
    uuid = "test-beacon-uuid"
    
    result = service.validate_ble_proximity(rssi, uuid, uuid)
    
    # Property: Strict threshold enforcement
    if rssi > -70:
        assert result.passed, f"RSSI {rssi} > -70 should pass"
    else:
        assert not result.passed, f"RSSI {rssi} <= -70 should fail"


@given(
    rssi=st.floats(min_value=-120, max_value=-20),
    uuid1=st.text(min_size=36, max_size=36),
    uuid2=st.text(min_size=36, max_size=36)
)
def test_property_rssi_uuid_independence(rssi, uuid1, uuid2):
    """
    Property: UUID validation is independent of RSSI value
    
    UUID mismatch should fail regardless of RSSI strength.
    """
    assume(uuid1 != uuid2)  # Ensure UUIDs are different
    
    service = get_sensor_validation_service()
    
    result = service.validate_ble_proximity(rssi, uuid1, uuid2)
    
    # Property: UUID mismatch always fails, regardless of RSSI
    assert not result.passed, "UUID mismatch should fail regardless of RSSI"
    assert result.anomaly_type == "ble_uuid_mismatch"


# ============== Edge Cases ==============

def test_rssi_exact_threshold():
    """Test exact threshold value -70 dBm"""
    service = get_sensor_validation_service()
    uuid = "test-beacon-uuid"
    
    # Exactly at threshold should fail (> -70, not >= -70)
    result = service.validate_ble_proximity(-70.0, uuid, uuid)
    assert not result.passed, "RSSI exactly at -70 should fail"


def test_rssi_very_strong_signal():
    """Test very strong signal (close proximity)"""
    service = get_sensor_validation_service()
    uuid = "test-beacon-uuid"
    
    # Very strong signal (e.g., -30 dBm)
    result = service.validate_ble_proximity(-30.0, uuid, uuid)
    assert result.passed, "Very strong signal should pass"


def test_rssi_very_weak_signal():
    """Test very weak signal (far away)"""
    service = get_sensor_validation_service()
    uuid = "test-beacon-uuid"
    
    # Very weak signal (e.g., -100 dBm)
    result = service.validate_ble_proximity(-100.0, uuid, uuid)
    assert not result.passed, "Very weak signal should fail"


def test_rssi_empty_uuid():
    """Test with empty UUID strings"""
    service = get_sensor_validation_service()
    
    result = service.validate_ble_proximity(-50.0, "", "")
    # Should handle gracefully (both empty = match)
    assert result.passed, "Empty UUIDs should match"


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
