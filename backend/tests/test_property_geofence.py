"""
Property-Based Tests for Geofence Service
Tests Haversine formula correctness and geofence radius enforcement
"""
import pytest
from hypothesis import given, strategies as st, assume
from hypothesis import settings
import math
from app.services.geofence_service import GeofenceService


# **Feature: isavs, Property 12: Haversine formula calculates GPS distance**
# **Validates: Requirements 4A.3**


@given(
    lat1=st.floats(min_value=-90, max_value=90, allow_nan=False, allow_infinity=False),
    lon1=st.floats(min_value=-180, max_value=180, allow_nan=False, allow_infinity=False),
    lat2=st.floats(min_value=-90, max_value=90, allow_nan=False, allow_infinity=False),
    lon2=st.floats(min_value=-180, max_value=180, allow_nan=False, allow_infinity=False)
)
@settings(max_examples=100)
def test_haversine_distance_is_non_negative(lat1, lon1, lat2, lon2):
    """
    Property: For any two valid GPS coordinates, the Haversine distance
    SHALL be non-negative.
    """
    distance = GeofenceService.calculate_distance(lat1, lon1, lat2, lon2)
    assert distance >= 0, f"Distance should be non-negative, got {distance}"


@given(
    lat=st.floats(min_value=-90, max_value=90, allow_nan=False, allow_infinity=False),
    lon=st.floats(min_value=-180, max_value=180, allow_nan=False, allow_infinity=False)
)
@settings(max_examples=100)
def test_haversine_same_point_is_zero(lat, lon):
    """
    Property: For any GPS coordinate, the distance from that point to itself
    SHALL be zero (or very close to zero due to floating point precision).
    """
    distance = GeofenceService.calculate_distance(lat, lon, lat, lon)
    assert distance < 0.01, f"Distance to same point should be ~0, got {distance}"


@given(
    lat1=st.floats(min_value=-89, max_value=89, allow_nan=False, allow_infinity=False),
    lon1=st.floats(min_value=-179, max_value=179, allow_nan=False, allow_infinity=False),
    lat2=st.floats(min_value=-89, max_value=89, allow_nan=False, allow_infinity=False),
    lon2=st.floats(min_value=-179, max_value=179, allow_nan=False, allow_infinity=False)
)
@settings(max_examples=100)
def test_haversine_symmetry(lat1, lon1, lat2, lon2):
    """
    Property: For any two GPS coordinates, the distance from A to B
    SHALL equal the distance from B to A (symmetry property).
    """
    distance_ab = GeofenceService.calculate_distance(lat1, lon1, lat2, lon2)
    distance_ba = GeofenceService.calculate_distance(lat2, lon2, lat1, lon1)
    
    # Allow small floating point differences
    assert abs(distance_ab - distance_ba) < 0.01, \
        f"Distance should be symmetric: {distance_ab} vs {distance_ba}"


def test_haversine_known_distances():
    """
    Test Haversine formula with known real-world distances.
    These are specific examples to validate correctness.
    """
    # New York to Los Angeles (approx 3936 km)
    ny_lat, ny_lon = 40.7128, -74.0060
    la_lat, la_lon = 34.0522, -118.2437
    distance = GeofenceService.calculate_distance(ny_lat, ny_lon, la_lat, la_lon)
    # Allow 1% error margin
    assert 3900000 < distance < 3970000, f"NY-LA distance should be ~3936km, got {distance/1000}km"
    
    # London to Paris (approx 344 km)
    london_lat, london_lon = 51.5074, -0.1278
    paris_lat, paris_lon = 48.8566, 2.3522
    distance = GeofenceService.calculate_distance(london_lat, london_lon, paris_lat, paris_lon)
    assert 340000 < distance < 350000, f"London-Paris distance should be ~344km, got {distance/1000}km"
    
    # Very short distance (100 meters apart, approximately)
    lat1, lon1 = 40.7128, -74.0060
    lat2, lon2 = 40.7138, -74.0060  # ~0.001 degree latitude ≈ 111 meters
    distance = GeofenceService.calculate_distance(lat1, lon1, lat2, lon2)
    assert 100 < distance < 120, f"Short distance should be ~111m, got {distance}m"


# **Feature: isavs, Property 13: Geofence radius is 50 meters**
# **Validates: Requirements 4A.4**


@given(
    classroom_lat=st.floats(min_value=-89, max_value=89, allow_nan=False, allow_infinity=False),
    classroom_lon=st.floats(min_value=-179, max_value=179, allow_nan=False, allow_infinity=False),
    offset_meters=st.floats(min_value=0, max_value=100, allow_nan=False, allow_infinity=False)
)
@settings(max_examples=100)
def test_geofence_radius_enforcement(classroom_lat, classroom_lon, offset_meters):
    """
    Property: For any classroom location and distance offset,
    if the distance is <= 50 meters, is_within_geofence SHALL return True,
    if the distance is > 50 meters, is_within_geofence SHALL return False.
    """
    # Calculate student position offset_meters away (approximately)
    # Using simple latitude offset (1 degree ≈ 111km)
    lat_offset = offset_meters / 111000
    student_lat = classroom_lat + lat_offset
    student_lon = classroom_lon
    
    is_within, distance = GeofenceService.is_within_geofence(
        student_lat, student_lon,
        classroom_lat, classroom_lon,
        radius_meters=50
    )
    
    # Verify the logic
    if distance <= 50:
        assert is_within, f"Should be within geofence at {distance}m"
    else:
        assert not is_within, f"Should be outside geofence at {distance}m"


@given(
    classroom_lat=st.floats(min_value=-89, max_value=89, allow_nan=False, allow_infinity=False),
    classroom_lon=st.floats(min_value=-179, max_value=179, allow_nan=False, allow_infinity=False)
)
@settings(max_examples=100)
def test_geofence_at_exact_location(classroom_lat, classroom_lon):
    """
    Property: For any classroom location, a student at the exact same
    coordinates SHALL always be within the geofence.
    """
    is_within, distance = GeofenceService.is_within_geofence(
        classroom_lat, classroom_lon,
        classroom_lat, classroom_lon,
        radius_meters=50
    )
    
    assert is_within, f"Student at exact classroom location should be within geofence"
    assert distance < 0.01, f"Distance should be ~0 at same location, got {distance}m"


def test_geofence_boundary_cases():
    """
    Test geofence at exact boundary (50 meters).
    """
    classroom_lat, classroom_lon = 40.7128, -74.0060
    
    # Student approximately 49 meters away (using latitude offset)
    lat_offset_49m = 49 / 111000
    student_lat = classroom_lat + lat_offset_49m
    student_lon = classroom_lon
    
    is_within, distance = GeofenceService.is_within_geofence(
        student_lat, student_lon,
        classroom_lat, classroom_lon,
        radius_meters=50
    )
    
    # At ~49m, should be within
    assert is_within, f"Student at ~49m should be within geofence (distance: {distance}m)"
    
    # Student 60 meters away
    lat_offset_60m = 60 / 111000
    student_lat = classroom_lat + lat_offset_60m
    
    is_within, distance = GeofenceService.is_within_geofence(
        student_lat, student_lon,
        classroom_lat, classroom_lon,
        radius_meters=50
    )
    
    # At 60m, should be outside
    assert not is_within, f"Student at ~60m should be outside geofence (distance: {distance}m)"


@given(
    lat=st.floats(min_value=-180, max_value=180, allow_nan=False, allow_infinity=False),
    lon=st.floats(min_value=-360, max_value=360, allow_nan=False, allow_infinity=False)
)
@settings(max_examples=100)
def test_coordinate_validation(lat, lon):
    """
    Property: For any coordinates, validate_coordinates SHALL return True
    only if lat is in [-90, 90] and lon is in [-180, 180].
    """
    is_valid = GeofenceService.validate_coordinates(lat, lon)
    
    expected_valid = (-90 <= lat <= 90) and (-180 <= lon <= 180)
    
    assert is_valid == expected_valid, \
        f"Validation mismatch for ({lat}, {lon}): got {is_valid}, expected {expected_valid}"


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
