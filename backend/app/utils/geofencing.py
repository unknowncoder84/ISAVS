"""
ISAVS 2026 - Robust Geofencing Utilities
Implements Haversine formula with fallback verification
"""

import math
from typing import Tuple, Dict, Optional
from datetime import datetime


class GeofencingService:
    """
    Robust geofencing service with GPS and WiFi fallback verification
    """
    
    # Configuration (can be overridden from database)
    MAX_DISTANCE_METERS = 100  # Increased from 50m to account for indoor GPS drift
    GPS_FAILURE_THRESHOLD = 2
    EARTH_RADIUS_KM = 6371.0
    
    @staticmethod
    def haversine_distance(
        lat1: float, 
        lon1: float, 
        lat2: float, 
        lon2: float
    ) -> float:
        """
        Calculate the great circle distance between two points on Earth
        using the Haversine formula.
        
        Args:
            lat1: Latitude of point 1 (degrees)
            lon1: Longitude of point 1 (degrees)
            lat2: Latitude of point 2 (degrees)
            lon2: Longitude of point 2 (degrees)
            
        Returns:
            Distance in meters
            
        Formula:
            a = sin²(Δφ/2) + cos φ1 ⋅ cos φ2 ⋅ sin²(Δλ/2)
            c = 2 ⋅ atan2(√a, √(1−a))
            d = R ⋅ c
        """
        # Convert degrees to radians
        lat1_rad = math.radians(lat1)
        lon1_rad = math.radians(lon1)
        lat2_rad = math.radians(lat2)
        lon2_rad = math.radians(lon2)
        
        # Differences
        dlat = lat2_rad - lat1_rad
        dlon = lon2_rad - lon1_rad
        
        # Haversine formula
        a = (
            math.sin(dlat / 2) ** 2 +
            math.cos(lat1_rad) * math.cos(lat2_rad) * math.sin(dlon / 2) ** 2
        )
        c = 2 * math.atan2(math.sqrt(a), math.sqrt(1 - a))
        
        # Distance in meters
        distance_meters = GeofencingService.EARTH_RADIUS_KM * c * 1000
        
        return round(distance_meters, 2)
    
    @staticmethod
    def verify_geofence(
        student_lat: float,
        student_lon: float,
        teacher_lat: float,
        teacher_lon: float,
        max_distance: Optional[float] = None
    ) -> Dict[str, any]:
        """
        Verify if student is within geofence of teacher location.
        
        Args:
            student_lat: Student's latitude
            student_lon: Student's longitude
            teacher_lat: Teacher's latitude
            teacher_lon: Teacher's longitude
            max_distance: Maximum allowed distance (default: 100m)
            
        Returns:
            Dict with verification result:
            {
                'verified': bool,
                'distance_meters': float,
                'max_distance': float,
                'message': str
            }
        """
        if max_distance is None:
            max_distance = GeofencingService.MAX_DISTANCE_METERS
        
        # Calculate distance
        distance = GeofencingService.haversine_distance(
            student_lat, student_lon,
            teacher_lat, teacher_lon
        )
        
        # Verify within threshold
        verified = distance <= max_distance
        
        return {
            'verified': verified,
            'distance_meters': distance,
            'max_distance': max_distance,
            'message': (
                f'Student is {distance:.2f}m from teacher (limit: {max_distance}m)'
                if verified
                else f'Student is too far: {distance:.2f}m (limit: {max_distance}m)'
            )
        }
    
    @staticmethod
    def verify_with_accuracy(
        student_lat: float,
        student_lon: float,
        teacher_lat: float,
        teacher_lon: float,
        gps_accuracy: float,
        max_distance: Optional[float] = None
    ) -> Dict[str, any]:
        """
        Verify geofence with GPS accuracy consideration.
        
        If GPS accuracy is poor (>50m), add it to the threshold.
        
        Args:
            student_lat: Student's latitude
            student_lon: Student's longitude
            teacher_lat: Teacher's latitude
            teacher_lon: Teacher's longitude
            gps_accuracy: GPS accuracy in meters from device
            max_distance: Maximum allowed distance
            
        Returns:
            Dict with verification result including accuracy info
        """
        if max_distance is None:
            max_distance = GeofencingService.MAX_DISTANCE_METERS
        
        # Adjust threshold if GPS accuracy is poor
        adjusted_distance = max_distance
        if gps_accuracy > 50:
            adjusted_distance = max_distance + (gps_accuracy - 50)
        
        result = GeofencingService.verify_geofence(
            student_lat, student_lon,
            teacher_lat, teacher_lon,
            adjusted_distance
        )
        
        result['gps_accuracy'] = gps_accuracy
        result['threshold_adjusted'] = adjusted_distance != max_distance
        
        return result
    
    @staticmethod
    def check_wifi_fallback(
        wifi_ssid: str,
        whitelisted_ssids: list
    ) -> Dict[str, any]:
        """
        Check if WiFi SSID is in the college network whitelist.
        
        Args:
            wifi_ssid: WiFi SSID from student device
            whitelisted_ssids: List of approved college WiFi SSIDs
            
        Returns:
            Dict with verification result:
            {
                'verified': bool,
                'ssid': str,
                'method': 'wifi',
                'message': str
            }
        """
        verified = wifi_ssid in whitelisted_ssids
        
        return {
            'verified': verified,
            'ssid': wifi_ssid,
            'method': 'wifi',
            'message': (
                f'WiFi verification successful: {wifi_ssid}'
                if verified
                else f'WiFi SSID not recognized: {wifi_ssid}'
            )
        }
    
    @staticmethod
    def verify_location(
        student_lat: Optional[float],
        student_lon: Optional[float],
        teacher_lat: float,
        teacher_lon: float,
        gps_accuracy: Optional[float],
        gps_failure_count: int,
        wifi_ssid: Optional[str],
        whitelisted_ssids: list,
        max_distance: Optional[float] = None
    ) -> Dict[str, any]:
        """
        Comprehensive location verification with GPS and WiFi fallback.
        
        Logic:
        1. Try GPS verification first
        2. If GPS fails twice, allow WiFi fallback
        3. Return verification result with method used
        
        Args:
            student_lat: Student's latitude (None if GPS failed)
            student_lon: Student's longitude (None if GPS failed)
            teacher_lat: Teacher's latitude
            teacher_lon: Teacher's longitude
            gps_accuracy: GPS accuracy in meters
            gps_failure_count: Number of previous GPS failures
            wifi_ssid: WiFi SSID from student device
            whitelisted_ssids: List of approved college WiFi SSIDs
            max_distance: Maximum allowed distance for GPS
            
        Returns:
            Dict with comprehensive verification result
        """
        # Try GPS verification first
        if student_lat is not None and student_lon is not None:
            if gps_accuracy is not None:
                result = GeofencingService.verify_with_accuracy(
                    student_lat, student_lon,
                    teacher_lat, teacher_lon,
                    gps_accuracy, max_distance
                )
            else:
                result = GeofencingService.verify_geofence(
                    student_lat, student_lon,
                    teacher_lat, teacher_lon,
                    max_distance
                )
            
            result['method'] = 'gps'
            result['gps_failure_count'] = gps_failure_count
            return result
        
        # GPS failed - check if WiFi fallback is allowed
        if gps_failure_count >= GeofencingService.GPS_FAILURE_THRESHOLD:
            if wifi_ssid:
                result = GeofencingService.check_wifi_fallback(
                    wifi_ssid, whitelisted_ssids
                )
                result['gps_failure_count'] = gps_failure_count
                result['fallback_used'] = True
                return result
            else:
                return {
                    'verified': False,
                    'method': 'none',
                    'gps_failure_count': gps_failure_count,
                    'message': 'GPS failed and no WiFi SSID provided for fallback'
                }
        else:
            return {
                'verified': False,
                'method': 'gps',
                'gps_failure_count': gps_failure_count,
                'message': f'GPS verification failed ({gps_failure_count}/{GeofencingService.GPS_FAILURE_THRESHOLD} attempts)'
            }


# Convenience functions for direct use
def calculate_distance(lat1: float, lon1: float, lat2: float, lon2: float) -> float:
    """
    Calculate distance between two GPS coordinates using Haversine formula.
    
    Returns:
        Distance in meters
    """
    return GeofencingService.haversine_distance(lat1, lon1, lat2, lon2)


def verify_student_location(
    student_coords: Tuple[float, float],
    teacher_coords: Tuple[float, float],
    max_distance: float = 100
) -> bool:
    """
    Simple verification if student is within range of teacher.
    
    Args:
        student_coords: (latitude, longitude) of student
        teacher_coords: (latitude, longitude) of teacher
        max_distance: Maximum allowed distance in meters (default: 100m)
        
    Returns:
        True if student is within range, False otherwise
    """
    result = GeofencingService.verify_geofence(
        student_coords[0], student_coords[1],
        teacher_coords[0], teacher_coords[1],
        max_distance
    )
    return result['verified']


# Example usage and testing
if __name__ == "__main__":
    # Test coordinates (example: college campus)
    teacher_location = (28.6139, 77.2090)  # Delhi, India
    student_location_near = (28.6145, 77.2095)  # ~70m away
    student_location_far = (28.6200, 77.2150)  # ~800m away
    
    print("=== Geofencing Tests ===\n")
    
    # Test 1: Student nearby
    distance1 = calculate_distance(
        teacher_location[0], teacher_location[1],
        student_location_near[0], student_location_near[1]
    )
    print(f"Test 1 - Student nearby: {distance1:.2f}m")
    
    # Test 2: Student far away
    distance2 = calculate_distance(
        teacher_location[0], teacher_location[1],
        student_location_far[0], student_location_far[1]
    )
    print(f"Test 2 - Student far: {distance2:.2f}m")
    
    # Test 3: Verification with accuracy
    result = GeofencingService.verify_with_accuracy(
        student_location_near[0], student_location_near[1],
        teacher_location[0], teacher_location[1],
        gps_accuracy=30.0
    )
    print(f"\nTest 3 - With accuracy: {result}")
    
    # Test 4: WiFi fallback
    whitelisted = ['College-WiFi', 'College-Student']
    wifi_result = GeofencingService.check_wifi_fallback(
        'College-WiFi', whitelisted
    )
    print(f"\nTest 4 - WiFi fallback: {wifi_result}")
    
    # Test 5: Comprehensive verification
    comprehensive = GeofencingService.verify_location(
        None, None,  # GPS failed
        teacher_location[0], teacher_location[1],
        None, 2,  # 2 GPS failures
        'College-WiFi', whitelisted
    )
    print(f"\nTest 5 - Comprehensive (WiFi fallback): {comprehensive}")
