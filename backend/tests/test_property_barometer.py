"""
Property-Based Tests for Barometric Pressure Validation
Tests Property 13: Barometric pressure threshold
Validates Requirements: 7.4
"""
import pytest
from hypothesis import given, strategies as st, assume

from app.services.barometer_service import get_barometer_service


# ============== Property 13: Barometric Pressure Threshold ==============

@given(
    student_pressure=st.floats(min_value=950, max_value=1050),
    teacher_pressure=st.floats(min_value=950, max_value=1050)
)
def test_property_pressure_threshold_enforcement(student_pressure, teacher_pressure):
    """
    Property 13: Barometric pressure threshold enforcement
    
    For any pressure readings:
    - If |student_pressure - teacher_pressure| <= 0.5 hPa → validation passes
    - If |student_pressure - teacher_pressure| > 0.5 hPa → validation fails
    
    Validates:
    - Requirement 7.4: Pressure difference threshold of 0.5 hPa
    """
    service = get_barometer_service()
    
    result = service.validate_pressure_difference(student_pressure, teacher_pressure)
    
    pressure_diff = abs(student_pressure - teacher_pressure)
    
    # Property: Threshold enforcement
    if pressure_diff <= 0.5:
        assert result.passed, \
            f"Pressure diff {pressure_diff:.2f} <= 0.5 hPa should pass"
        assert result.pressure_difference_hpa == pytest.approx(pressure_diff, abs=0.01)
    else:
        assert not result.passed, \
            f"Pressure diff {pressure_diff:.2f} > 0.5 hPa should fail"


@given(
    base_pressure=st.floats(min_value=950, max_value=1050),
    offset=st.floats(min_value=-10, max_value=10)
)
def test_property_pressure_symmetry(base_pressure, offset):
    """
    Property: Pressure validation is symmetric
    
    validate(P1, P2) should give same result as validate(P2, P1)
    """
    assume(900 <= base_pressure + offset <= 1100)  # Keep both pressures valid
    
    service = get_barometer_service()
    
    result1 = service.validate_pressure_difference(base_pressure, base_pressure + offset)
    result2 = service.validate_pressure_difference(base_pressure + offset, base_pressure)
    
    # Property: Symmetric validation
    assert result1.passed == result2.passed, "Validation should be symmetric"
    assert result1.pressure_difference_hpa == pytest.approx(
        result2.pressure_difference_hpa, abs=0.01
    )


@given(
    pressure1=st.floats(min_value=950, max_value=1050),
    pressure2=st.floats(min_value=950, max_value=1050)
)
def test_property_pressure_altitude_relationship(pressure1, pressure2):
    """
    Property: Altitude difference is inversely related to pressure difference
    
    Higher pressure → lower altitude
    Lower pressure → higher altitude
    """
    service = get_barometer_service()
    
    altitude_diff = service.calculate_altitude_difference(pressure1, pressure2)
    
    # Property: Inverse relationship
    if pressure1 > pressure2:
        # pressure1 is higher → altitude1 is lower → negative altitude diff
        assert altitude_diff < 0, \
            f"Higher pressure should give negative altitude diff: {altitude_diff}"
    elif pressure1 < pressure2:
        # pressure1 is lower → altitude1 is higher → positive altitude diff
        assert altitude_diff > 0, \
            f"Lower pressure should give positive altitude diff: {altitude_diff}"
    else:
        # Equal pressure → zero altitude diff
        assert abs(altitude_diff) < 0.1, \
            f"Equal pressure should give zero altitude diff: {altitude_diff}"


@given(
    student_pressure=st.floats(min_value=950, max_value=1050),
    teacher_pressure=st.floats(min_value=950, max_value=1050)
)
def test_property_pressure_floor_estimation(student_pressure, teacher_pressure):
    """
    Property: Floor difference estimation is reasonable
    
    - 0.5 hPa ≈ 4 meters ≈ 1 floor
    - 1.0 hPa ≈ 8 meters ≈ 2 floors
    """
    service = get_barometer_service()
    
    result = service.validate_pressure_difference(student_pressure, teacher_pressure)
    
    altitude_diff = result.altitude_difference_meters
    floor_diff = service.estimate_floor_difference(altitude_diff)
    
    # Property: Floor estimation is reasonable
    expected_floors = round(altitude_diff / 3.5)  # 3.5m per floor
    assert abs(floor_diff - expected_floors) <= 1, \
        f"Floor estimation should be reasonable: {floor_diff} vs {expected_floors}"


@given(pressure_diff=st.floats(min_value=0.49, max_value=0.51))
def test_property_pressure_boundary_behavior(pressure_diff):
    """
    Property: Boundary behavior at 0.5 hPa threshold
    
    Values very close to 0.5 should behave consistently with the threshold rule.
    """
    service = get_barometer_service()
    
    base_pressure = 1013.25  # Sea level
    student_pressure = base_pressure + pressure_diff
    
    result = service.validate_pressure_difference(student_pressure, base_pressure)
    
    # Property: Strict threshold enforcement
    if pressure_diff <= 0.5:
        assert result.passed, f"Pressure diff {pressure_diff} <= 0.5 should pass"
    else:
        assert not result.passed, f"Pressure diff {pressure_diff} > 0.5 should fail"


@given(
    pressure=st.floats(min_value=950, max_value=1050),
    offset1=st.floats(min_value=0, max_value=0.5),
    offset2=st.floats(min_value=0.5, max_value=2.0)
)
def test_property_pressure_monotonicity(pressure, offset1, offset2):
    """
    Property: Pressure validation is monotonic
    
    If offset1 < offset2 and offset1 passes, then offset2 should fail
    """
    assume(900 <= pressure + offset2 <= 1100)  # Keep valid
    
    service = get_barometer_service()
    
    result1 = service.validate_pressure_difference(pressure, pressure + offset1)
    result2 = service.validate_pressure_difference(pressure, pressure + offset2)
    
    # Property: Monotonicity
    if result1.passed and offset1 < offset2:
        assert not result2.passed or offset2 <= 0.5, \
            f"Larger offset {offset2} should fail if smaller offset {offset1} passes"


# ============== Edge Cases ==============

def test_pressure_exact_threshold():
    """Test exact threshold value 0.5 hPa"""
    service = get_barometer_service()
    
    # Exactly at threshold should pass (<= 0.5)
    result = service.validate_pressure_difference(1013.25, 1013.75)
    assert result.passed, "Pressure diff exactly at 0.5 hPa should pass"


def test_pressure_same_floor():
    """Test same floor (zero pressure difference)"""
    service = get_barometer_service()
    
    result = service.validate_pressure_difference(1013.25, 1013.25)
    assert result.passed, "Same pressure should pass"
    assert result.pressure_difference_hpa == 0.0


def test_pressure_different_floor():
    """Test different floor (large pressure difference)"""
    service = get_barometer_service()
    
    # 1 hPa ≈ 8 meters ≈ 2 floors
    result = service.validate_pressure_difference(1013.25, 1014.25)
    assert not result.passed, "Different floor should fail"
    assert result.pressure_difference_hpa == pytest.approx(1.0, abs=0.01)


def test_pressure_invalid_student():
    """Test invalid student pressure (out of range)"""
    service = get_barometer_service()
    
    # Too low
    result = service.validate_pressure_difference(800.0, 1013.25)
    assert not result.passed, "Invalid student pressure should fail"
    assert "Invalid student pressure" in result.message
    
    # Too high
    result = service.validate_pressure_difference(1200.0, 1013.25)
    assert not result.passed, "Invalid student pressure should fail"


def test_pressure_invalid_teacher():
    """Test invalid teacher pressure (out of range)"""
    service = get_barometer_service()
    
    # Too low
    result = service.validate_pressure_difference(1013.25, 800.0)
    assert not result.passed, "Invalid teacher pressure should fail"
    assert "Invalid teacher pressure" in result.message


def test_pressure_to_altitude_conversion():
    """Test pressure to altitude conversion"""
    service = get_barometer_service()
    
    # Sea level
    altitude = service.pressure_to_altitude(1013.25, 1013.25)
    assert abs(altitude) < 1.0, "Sea level should give ~0 altitude"
    
    # Higher altitude (lower pressure)
    altitude = service.pressure_to_altitude(900.0, 1013.25)
    assert altitude > 0, "Lower pressure should give positive altitude"
    
    # Lower altitude (higher pressure)
    altitude = service.pressure_to_altitude(1050.0, 1013.25)
    assert altitude < 0, "Higher pressure should give negative altitude"


def test_altitude_difference_calculation():
    """Test altitude difference calculation"""
    service = get_barometer_service()
    
    # 1 hPa difference
    altitude_diff = service.calculate_altitude_difference(1013.25, 1014.25)
    
    # Should be approximately -8.5 meters (simplified formula)
    assert -10 < altitude_diff < -7, \
        f"1 hPa should give ~-8.5m altitude diff, got {altitude_diff}"


def test_floor_difference_estimation():
    """Test floor difference estimation"""
    service = get_barometer_service()
    
    # 1 floor ≈ 3.5 meters
    floor_diff = service.estimate_floor_difference(3.5)
    assert floor_diff == 1, "3.5m should be 1 floor"
    
    # 2 floors ≈ 7 meters
    floor_diff = service.estimate_floor_difference(7.0)
    assert floor_diff == 2, "7m should be 2 floors"
    
    # Same floor
    floor_diff = service.estimate_floor_difference(1.0)
    assert floor_diff == 0, "1m should be 0 floors (same floor)"


def test_validate_pressure_range():
    """Test pressure validation range"""
    service = get_barometer_service()
    
    # Valid pressures
    valid, msg = service.validate_pressure(1013.25)
    assert valid, "Normal pressure should be valid"
    
    valid, msg = service.validate_pressure(950.0)
    assert valid, "950 hPa should be valid"
    
    valid, msg = service.validate_pressure(1050.0)
    assert valid, "1050 hPa should be valid"
    
    # Invalid pressures
    valid, msg = service.validate_pressure(800.0)
    assert not valid, "800 hPa should be invalid"
    
    valid, msg = service.validate_pressure(1200.0)
    assert not valid, "1200 hPa should be invalid"


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
