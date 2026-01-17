"""
Geofencing Service
Validates student location is within 50 meters of classroom
"""
from math import radians, sin, cos, sqrt, atan2
from typing import Tuple, Optional


class GeofenceService:
    """
    Service for validating student location against classroom coordinates.
    Uses Haversine formula for accurate distance calculation.
    """
    
    EARTH_RADIUS_METERS = 6371000  # Earth radius in meters
    DEFAULT_RADIUS_METERS = 50  # 50 meter radius
    
    @staticmethod
    def calculate_distance(
        lat1: float,
        lon1: float,
        lat2: float,
        lon2: float
    ) -> float:
        """
        Calculate distance between two GPS coordinates using Haversine formula.
        
        Args:
            lat1: Latitude of point 1 (student)
            lon1: Longitude of point 1 (student)
            lat2: Latitude of point 2 (classroom)
            lon2: Longitude of point 2 (classroom)
        
        Returns:
            Distance in meters
        """
        # Convert to radians
        lat1_rad = radians(lat1)
        lon1_rad = radians(lon1)
        lat2_rad = radians(lat2)
        lon2_rad = radians(lon2)
        
        # Haversine formula
        dlat = lat2_rad - lat1_rad
        dlon = lon2_rad - lon1_rad
        
        a = sin(dlat / 2) ** 2 + cos(lat1_rad) * cos(lat2_rad) * sin(dlon / 2) ** 2
        c = 2 * atan2(sqrt(a), sqrt(1 - a))
        
        distance = GeofenceService.EARTH_RADIUS_METERS * c
        
        return distance
    
    @staticmethod
    def is_within_geofence(
        student_lat: float,
        student_lon: float,
        classroom_lat: float,
        classroom_lon: float,
        radius_meters: float = DEFAULT_RADIUS_METERS
    ) -> Tuple[bool, float]:
        """
        Check if student is within geofence radius of classroom.
        
        Args:
            student_lat: Student's latitude
            student_lon: Student's longitude
            classroom_lat: Classroom's latitude
            classroom_lon: Classroom's longitude
            radius_meters: Geofence radius (default 50m)
        
        Returns:
            (is_within_fence, distance_meters)
        """
        distance = GeofenceService.calculate_distance(
            student_lat, student_lon,
            classroom_lat, classroom_lon
        )
        
        is_within = distance <= radius_meters
        
        return is_within, distance
    
    @staticmethod
    def validate_coordinates(lat: float, lon: float) -> bool:
        """
        Validate GPS coordinates are within valid ranges.
        
        Args:
            lat: Latitude (-90 to 90)
            lon: Longitude (-180 to 180)
        
        Returns:
            True if valid, False otherwise
        """
        if not (-90 <= lat <= 90):
            return False
        if not (-180 <= lon <= 180):
            return False
        return True


# Singleton instance
_geofence_service: Optional[GeofenceService] = None


def get_geofence_service() -> GeofenceService:
    """Get or create geofence service instance."""
    global _geofence_service
    if _geofence_service is None:
        _geofence_service = GeofenceService()
    return _geofence_service
