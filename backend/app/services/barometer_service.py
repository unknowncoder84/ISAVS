"""
Barometer Service
Validates barometric pressure to detect floor-level differences.
"""
from typing import Tuple, Optional
from dataclasses import dataclass


@dataclass
class PressureValidationResult:
    """Result of pressure validation"""
    passed: bool
    pressure_difference_hpa: float
    altitude_difference_meters: float
    message: str


class BarometerService:
    """
    Service for barometric pressure validation and altitude estimation.
    
    Features:
    - Pressure-to-altitude conversion using barometric formula
    - Floor-level detection (0.5 hPa threshold ≈ 4 meters)
    - Pressure difference validation
    
    Physics:
    - At sea level: ΔH ≈ -8.5 * ΔP (meters per hPa)
    - 1 floor ≈ 3-4 meters ≈ 0.35-0.47 hPa
    - Threshold: 0.5 hPa allows same floor + measurement error
    """
    
    # Constants
    PRESSURE_TO_ALTITUDE_FACTOR = -8.5  # meters per hPa at sea level
    DEFAULT_THRESHOLD_HPA = 0.5  # hPa
    
    # Valid pressure range (hPa)
    MIN_VALID_PRESSURE = 900.0  # Below this is unrealistic (extreme altitude)
    MAX_VALID_PRESSURE = 1100.0  # Above this is unrealistic (below sea level)
    
    def __init__(self):
        """Initialize barometer service"""
        pass
    
    def pressure_to_altitude(
        self,
        pressure_hpa: float,
        reference_pressure_hpa: float = 1013.25
    ) -> float:
        """
        Convert barometric pressure to altitude using simplified barometric formula.
        
        Simplified formula (valid for small altitude differences):
        ΔH ≈ -8.5 * ΔP (meters)
        
        Full barometric formula:
        H = 44330 * (1 - (P/P0)^0.1903)
        
        Args:
            pressure_hpa: Current pressure in hPa
            reference_pressure_hpa: Reference pressure (default: sea level 1013.25 hPa)
        
        Returns:
            Altitude in meters relative to reference
        """
        # Use full barometric formula for accuracy
        altitude = 44330 * (1 - (pressure_hpa / reference_pressure_hpa) ** 0.1903)
        return altitude
    
    def calculate_altitude_difference(
        self,
        pressure1_hpa: float,
        pressure2_hpa: float
    ) -> float:
        """
        Calculate altitude difference between two pressure readings.
        
        Uses simplified formula: ΔH ≈ -8.5 * ΔP
        
        Args:
            pressure1_hpa: First pressure reading
            pressure2_hpa: Second pressure reading
        
        Returns:
            Altitude difference in meters (positive if pressure1 is higher altitude)
        """
        pressure_diff = pressure1_hpa - pressure2_hpa
        altitude_diff = self.PRESSURE_TO_ALTITUDE_FACTOR * pressure_diff
        return altitude_diff
    
    def estimate_floor_difference(
        self,
        altitude_difference_meters: float,
        floor_height_meters: float = 3.5
    ) -> int:
        """
        Estimate floor difference from altitude difference.
        
        Args:
            altitude_difference_meters: Altitude difference
            floor_height_meters: Average floor height (default 3.5m)
        
        Returns:
            Estimated number of floors difference
        """
        return round(abs(altitude_difference_meters) / floor_height_meters)
    
    def validate_pressure(
        self,
        pressure_hpa: float
    ) -> Tuple[bool, str]:
        """
        Validate that pressure reading is within realistic range.
        
        Args:
            pressure_hpa: Pressure reading in hPa
        
        Returns:
            (is_valid, message)
        """
        if pressure_hpa < self.MIN_VALID_PRESSURE:
            return False, f"Pressure too low: {pressure_hpa} hPa (min {self.MIN_VALID_PRESSURE})"
        
        if pressure_hpa > self.MAX_VALID_PRESSURE:
            return False, f"Pressure too high: {pressure_hpa} hPa (max {self.MAX_VALID_PRESSURE})"
        
        return True, "Pressure valid"
    
    def validate_pressure_difference(
        self,
        student_pressure_hpa: float,
        teacher_pressure_hpa: float,
        threshold_hpa: Optional[float] = None
    ) -> PressureValidationResult:
        """
        Validate that student and teacher are on the same floor.
        
        Args:
            student_pressure_hpa: Student's barometric pressure
            teacher_pressure_hpa: Teacher's barometric pressure (classroom)
            threshold_hpa: Maximum allowed pressure difference (default 0.5 hPa)
        
        Returns:
            PressureValidationResult with validation details
        """
        if threshold_hpa is None:
            threshold_hpa = self.DEFAULT_THRESHOLD_HPA
        
        # Validate student pressure
        student_valid, student_msg = self.validate_pressure(student_pressure_hpa)
        if not student_valid:
            return PressureValidationResult(
                passed=False,
                pressure_difference_hpa=0.0,
                altitude_difference_meters=0.0,
                message=f"Invalid student pressure: {student_msg}"
            )
        
        # Validate teacher pressure
        teacher_valid, teacher_msg = self.validate_pressure(teacher_pressure_hpa)
        if not teacher_valid:
            return PressureValidationResult(
                passed=False,
                pressure_difference_hpa=0.0,
                altitude_difference_meters=0.0,
                message=f"Invalid teacher pressure: {teacher_msg}"
            )
        
        # Calculate pressure difference (absolute value)
        pressure_diff = abs(student_pressure_hpa - teacher_pressure_hpa)
        
        # Calculate altitude difference
        altitude_diff = self.calculate_altitude_difference(
            student_pressure_hpa,
            teacher_pressure_hpa
        )
        
        # Estimate floor difference
        floor_diff = self.estimate_floor_difference(abs(altitude_diff))
        
        # Validate threshold
        passed = pressure_diff <= threshold_hpa
        
        if passed:
            message = (
                f"Barometric pressure verified "
                f"(Δ{pressure_diff:.2f} hPa, ~{abs(altitude_diff):.1f}m altitude diff)"
            )
        else:
            message = (
                f"Pressure mismatch - different floor detected "
                f"(Δ{pressure_diff:.2f} hPa > {threshold_hpa} hPa, "
                f"~{abs(altitude_diff):.1f}m, ~{floor_diff} floors)"
            )
        
        return PressureValidationResult(
            passed=passed,
            pressure_difference_hpa=pressure_diff,
            altitude_difference_meters=abs(altitude_diff),
            message=message
        )


# Singleton instance
_barometer_service: Optional[BarometerService] = None


def get_barometer_service() -> BarometerService:
    """Get or create barometer service instance."""
    global _barometer_service
    if _barometer_service is None:
        _barometer_service = BarometerService()
    return _barometer_service
