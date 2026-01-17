"""
Sensor Validation Service
Validates all sensor data for multi-factor authentication
"""
from typing import Optional, Dict, Any, List
from dataclasses import dataclass
from enum import Enum

from app.services.geofence_service import get_geofence_service


class SensorType(Enum):
    """Sensor types for validation"""
    BLE = "ble"
    GPS = "gps"
    BAROMETER = "barometer"
    MOTION = "motion"
    ACCELEROMETER = "accelerometer"
    GYROSCOPE = "gyroscope"


@dataclass
class ValidationResult:
    """Result of a single sensor validation"""
    passed: bool
    value: float
    threshold: float
    message: str
    anomaly_type: Optional[str] = None
    metadata: Optional[Dict[str, Any]] = None


@dataclass
class MultiSensorValidationResult:
    """Result of multi-sensor validation"""
    overall_passed: bool
    ble_result: Optional[ValidationResult]
    motion_result: Optional[ValidationResult]
    gps_result: Optional[ValidationResult]
    barometer_result: Optional[ValidationResult]
    failed_sensors: List[str]
    total_sensors_checked: int
    passed_sensors_count: int


class SensorValidationService:
    """
    Service for validating sensor data from mobile devices.
    
    Features:
    - BLE proximity validation (RSSI threshold: -70 dBm)
    - GPS geofence validation (50 meter radius)
    - Barometric pressure validation (0.5 hPa threshold)
    - Motion-image correlation validation (0.7 correlation threshold)
    - Multi-sensor aggregation
    """
    
    # Thresholds
    BLE_RSSI_THRESHOLD = -70.0  # dBm (stronger signal = closer proximity)
    BAROMETER_THRESHOLD = 0.5  # hPa (pressure difference)
    MOTION_CORRELATION_THRESHOLD = 0.7  # Correlation coefficient
    GPS_RADIUS_METERS = 50.0  # meters
    
    # Barometric pressure to altitude conversion
    # ΔH ≈ -8.5 * ΔP (meters per hPa at sea level)
    PRESSURE_TO_ALTITUDE_FACTOR = -8.5
    
    def __init__(self):
        """Initialize sensor validation service"""
        self.geofence_service = get_geofence_service()
    
    def validate_ble_proximity(
        self,
        rssi: float,
        beacon_uuid: str,
        session_beacon_uuid: str
    ) -> ValidationResult:
        """
        Validate BLE proximity using RSSI (Received Signal Strength Indicator).
        
        RSSI threshold: -70 dBm
        - Stronger signal (e.g., -50 dBm) = closer proximity
        - Weaker signal (e.g., -90 dBm) = farther away
        
        Args:
            rssi: Received signal strength in dBm
            beacon_uuid: UUID of detected beacon
            session_beacon_uuid: Expected beacon UUID for session
        
        Returns:
            ValidationResult with pass/fail and details
        """
        # Validate beacon UUID matches
        if beacon_uuid != session_beacon_uuid:
            return ValidationResult(
                passed=False,
                value=rssi,
                threshold=self.BLE_RSSI_THRESHOLD,
                message=f"Beacon UUID mismatch: expected {session_beacon_uuid}, got {beacon_uuid}",
                anomaly_type="ble_uuid_mismatch"
            )
        
        # Validate RSSI threshold
        # RSSI is negative, so stronger signal (closer) has higher value (less negative)
        passed = rssi > self.BLE_RSSI_THRESHOLD
        
        if passed:
            # Estimate distance using log-distance path loss model
            # d = 10^((TxPower - RSSI) / (10 * n))
            # Assuming TxPower = -59 dBm, n = 2 (free space)
            tx_power = -59
            path_loss_exponent = 2
            distance = 10 ** ((tx_power - rssi) / (10 * path_loss_exponent))
            
            message = f"BLE proximity verified (RSSI: {rssi:.1f} dBm, ~{distance:.1f}m)"
        else:
            message = f"Too far from classroom beacon (RSSI: {rssi:.1f} dBm < {self.BLE_RSSI_THRESHOLD} dBm)"
        
        return ValidationResult(
            passed=passed,
            value=rssi,
            threshold=self.BLE_RSSI_THRESHOLD,
            message=message,
            anomaly_type="ble_proximity_violation" if not passed else None,
            metadata={"beacon_uuid": beacon_uuid}
        )
    
    def validate_geofence(
        self,
        student_lat: float,
        student_lon: float,
        teacher_lat: float,
        teacher_lon: float,
        radius_meters: Optional[float] = None
    ) -> ValidationResult:
        """
        Validate GPS geofence using Haversine distance formula.
        
        Args:
            student_lat: Student's latitude
            student_lon: Student's longitude
            teacher_lat: Teacher's latitude (classroom)
            teacher_lon: Teacher's longitude (classroom)
            radius_meters: Geofence radius (default 50m)
        
        Returns:
            ValidationResult with pass/fail and distance
        """
        if radius_meters is None:
            radius_meters = self.GPS_RADIUS_METERS
        
        # Validate coordinates
        if not self.geofence_service.validate_coordinates(student_lat, student_lon):
            return ValidationResult(
                passed=False,
                value=0.0,
                threshold=radius_meters,
                message=f"Invalid student coordinates: ({student_lat}, {student_lon})",
                anomaly_type="invalid_gps_coordinates"
            )
        
        if not self.geofence_service.validate_coordinates(teacher_lat, teacher_lon):
            return ValidationResult(
                passed=False,
                value=0.0,
                threshold=radius_meters,
                message=f"Invalid teacher coordinates: ({teacher_lat}, {teacher_lon})",
                anomaly_type="invalid_gps_coordinates"
            )
        
        # Calculate distance
        is_within, distance = self.geofence_service.is_within_geofence(
            student_lat, student_lon,
            teacher_lat, teacher_lon,
            radius_meters
        )
        
        if is_within:
            message = f"GPS geofence verified ({distance:.1f}m from classroom)"
        else:
            message = f"Outside classroom geofence ({distance:.1f}m > {radius_meters:.0f}m)"
        
        return ValidationResult(
            passed=is_within,
            value=distance,
            threshold=radius_meters,
            message=message,
            anomaly_type="geofence_violation" if not is_within else None,
            metadata={
                "student_lat": student_lat,
                "student_lon": student_lon,
                "teacher_lat": teacher_lat,
                "teacher_lon": teacher_lon
            }
        )
    
    def validate_barometer(
        self,
        student_pressure: float,
        teacher_pressure: float,
        threshold_hpa: Optional[float] = None
    ) -> ValidationResult:
        """
        Validate barometric pressure to detect floor-level differences.
        
        Pressure difference threshold: 0.5 hPa
        Altitude difference: ΔH ≈ -8.5 * ΔP meters
        
        Args:
            student_pressure: Student's barometric pressure (hPa)
            teacher_pressure: Teacher's barometric pressure (hPa)
            threshold_hpa: Pressure difference threshold (default 0.5 hPa)
        
        Returns:
            ValidationResult with pass/fail and pressure difference
        """
        if threshold_hpa is None:
            threshold_hpa = self.BAROMETER_THRESHOLD
        
        # Validate pressure values (typical range: 950-1050 hPa)
        if not (900 <= student_pressure <= 1100):
            return ValidationResult(
                passed=False,
                value=0.0,
                threshold=threshold_hpa,
                message=f"Invalid student pressure: {student_pressure} hPa",
                anomaly_type="invalid_barometer_reading"
            )
        
        if not (900 <= teacher_pressure <= 1100):
            return ValidationResult(
                passed=False,
                value=0.0,
                threshold=threshold_hpa,
                message=f"Invalid teacher pressure: {teacher_pressure} hPa",
                anomaly_type="invalid_barometer_reading"
            )
        
        # Calculate pressure difference (absolute value)
        pressure_diff = abs(student_pressure - teacher_pressure)
        
        # Calculate estimated altitude difference
        altitude_diff = self.PRESSURE_TO_ALTITUDE_FACTOR * (student_pressure - teacher_pressure)
        
        passed = pressure_diff <= threshold_hpa
        
        if passed:
            message = f"Barometric pressure verified (Δ{pressure_diff:.2f} hPa, ~{abs(altitude_diff):.1f}m altitude diff)"
        else:
            message = f"Pressure mismatch - different floor detected (Δ{pressure_diff:.2f} hPa > {threshold_hpa} hPa, ~{abs(altitude_diff):.1f}m)"
        
        return ValidationResult(
            passed=passed,
            value=pressure_diff,
            threshold=threshold_hpa,
            message=message,
            anomaly_type="barometer_violation" if not passed else None,
            metadata={
                "student_pressure": student_pressure,
                "teacher_pressure": teacher_pressure,
                "altitude_difference_meters": altitude_diff
            }
        )
    
    def validate_motion_correlation(
        self,
        correlation_coefficient: float,
        threshold: Optional[float] = None
    ) -> ValidationResult:
        """
        Validate motion-image correlation for liveness detection.
        
        Correlation threshold: 0.7
        
        Args:
            correlation_coefficient: Pearson correlation between motion and optical flow
            threshold: Correlation threshold (default 0.7)
        
        Returns:
            ValidationResult with pass/fail
        """
        if threshold is None:
            threshold = self.MOTION_CORRELATION_THRESHOLD
        
        # Validate correlation is in valid range [-1, 1]
        if not (-1.0 <= correlation_coefficient <= 1.0):
            return ValidationResult(
                passed=False,
                value=correlation_coefficient,
                threshold=threshold,
                message=f"Invalid correlation coefficient: {correlation_coefficient}",
                anomaly_type="invalid_correlation_value"
            )
        
        passed = correlation_coefficient >= threshold
        
        if passed:
            message = f"Motion-image correlation verified (r={correlation_coefficient:.3f})"
        else:
            message = f"Motion-image mismatch detected (r={correlation_coefficient:.3f} < {threshold})"
        
        return ValidationResult(
            passed=passed,
            value=correlation_coefficient,
            threshold=threshold,
            message=message,
            anomaly_type="motion_correlation_violation" if not passed else None
        )
    
    def validate_all_sensors(
        self,
        ble_rssi: Optional[float] = None,
        ble_beacon_uuid: Optional[str] = None,
        session_beacon_uuid: Optional[str] = None,
        student_lat: Optional[float] = None,
        student_lon: Optional[float] = None,
        teacher_lat: Optional[float] = None,
        teacher_lon: Optional[float] = None,
        student_pressure: Optional[float] = None,
        teacher_pressure: Optional[float] = None,
        motion_correlation: Optional[float] = None
    ) -> MultiSensorValidationResult:
        """
        Validate all available sensors and aggregate results.
        
        Args:
            ble_rssi: BLE signal strength (optional)
            ble_beacon_uuid: Detected beacon UUID (optional)
            session_beacon_uuid: Expected beacon UUID (optional)
            student_lat: Student GPS latitude (optional)
            student_lon: Student GPS longitude (optional)
            teacher_lat: Teacher GPS latitude (optional)
            teacher_lon: Teacher GPS longitude (optional)
            student_pressure: Student barometric pressure (optional)
            teacher_pressure: Teacher barometric pressure (optional)
            motion_correlation: Motion-image correlation coefficient (optional)
        
        Returns:
            MultiSensorValidationResult with aggregated results
        """
        results = {}
        failed_sensors = []
        total_checked = 0
        passed_count = 0
        
        # Validate BLE if data provided
        if ble_rssi is not None and ble_beacon_uuid and session_beacon_uuid:
            ble_result = self.validate_ble_proximity(ble_rssi, ble_beacon_uuid, session_beacon_uuid)
            results['ble'] = ble_result
            total_checked += 1
            if ble_result.passed:
                passed_count += 1
            else:
                failed_sensors.append("BLE")
        else:
            results['ble'] = None
        
        # Validate GPS if data provided
        if all(v is not None for v in [student_lat, student_lon, teacher_lat, teacher_lon]):
            gps_result = self.validate_geofence(student_lat, student_lon, teacher_lat, teacher_lon)
            results['gps'] = gps_result
            total_checked += 1
            if gps_result.passed:
                passed_count += 1
            else:
                failed_sensors.append("GPS")
        else:
            results['gps'] = None
        
        # Validate barometer if data provided
        if student_pressure is not None and teacher_pressure is not None:
            barometer_result = self.validate_barometer(student_pressure, teacher_pressure)
            results['barometer'] = barometer_result
            total_checked += 1
            if barometer_result.passed:
                passed_count += 1
            else:
                failed_sensors.append("Barometer")
        else:
            results['barometer'] = None
        
        # Validate motion correlation if data provided
        if motion_correlation is not None:
            motion_result = self.validate_motion_correlation(motion_correlation)
            results['motion'] = motion_result
            total_checked += 1
            if motion_result.passed:
                passed_count += 1
            else:
                failed_sensors.append("Motion")
        else:
            results['motion'] = None
        
        # Overall pass requires all checked sensors to pass
        overall_passed = (total_checked > 0) and (passed_count == total_checked)
        
        return MultiSensorValidationResult(
            overall_passed=overall_passed,
            ble_result=results.get('ble'),
            motion_result=results.get('motion'),
            gps_result=results.get('gps'),
            barometer_result=results.get('barometer'),
            failed_sensors=failed_sensors,
            total_sensors_checked=total_checked,
            passed_sensors_count=passed_count
        )


# Singleton instance
_sensor_validation_service: Optional[SensorValidationService] = None


def get_sensor_validation_service() -> SensorValidationService:
    """Get or create sensor validation service instance."""
    global _sensor_validation_service
    if _sensor_validation_service is None:
        _sensor_validation_service = SensorValidationService()
    return _sensor_validation_service

