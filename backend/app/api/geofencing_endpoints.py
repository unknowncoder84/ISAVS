"""
ISAVS 2026 - Geofencing API Endpoints
Handles GPS and WiFi fallback verification
"""

from fastapi import APIRouter, HTTPException, Depends
from pydantic import BaseModel
from typing import Optional
from sqlalchemy.orm import Session
from ..database import get_db
from ..utils.geofencing import GeofencingService
import logging

logger = logging.getLogger(__name__)
router = APIRouter()


class GPSVerificationRequest(BaseModel):
    """GPS verification request model"""
    session_id: str
    student_id: str
    latitude: float
    longitude: float
    accuracy: Optional[float] = None


class WiFiVerificationRequest(BaseModel):
    """WiFi verification request model"""
    session_id: str
    student_id: Optional[str] = None
    wifi_ssid: str


class LocationVerificationRequest(BaseModel):
    """Comprehensive location verification request"""
    session_id: str
    student_id: str
    latitude: Optional[float] = None
    longitude: Optional[float] = None
    accuracy: Optional[float] = None
    gps_failure_count: int = 0
    wifi_ssid: Optional[str] = None


@router.post("/verify-gps")
async def verify_gps_location(
    request: GPSVerificationRequest,
    db: Session = Depends(get_db)
):
    """
    Verify student location using GPS coordinates.
    
    Returns:
        - verified: bool
        - distance_meters: float
        - message: str
    """
    try:
        # Get session from database
        session = db.execute(
            """
            SELECT s.id, s.session_id, 
                   u.id as teacher_id,
                   -- Mock teacher location (in production, store with session)
                   28.6139 as teacher_lat,
                   77.2090 as teacher_lon
            FROM attendance_sessions s
            LEFT JOIN users u ON s.teacher_id = u.id
            WHERE s.session_id = :session_id AND s.status = 'active'
            """,
            {"session_id": request.session_id}
        ).fetchone()
        
        if not session:
            raise HTTPException(status_code=404, detail="Session not found or expired")
        
        # Verify geofence
        if request.accuracy:
            result = GeofencingService.verify_with_accuracy(
                request.latitude,
                request.longitude,
                session.teacher_lat,
                session.teacher_lon,
                request.accuracy
            )
        else:
            result = GeofencingService.verify_geofence(
                request.latitude,
                request.longitude,
                session.teacher_lat,
                session.teacher_lon
            )
        
        logger.info(f"GPS verification for {request.student_id}: {result}")
        
        return {
            "verified": result['verified'],
            "distance_meters": result['distance_meters'],
            "max_distance": result['max_distance'],
            "message": result['message'],
            "method": "gps"
        }
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"GPS verification error: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/verify-wifi")
async def verify_wifi_network(
    request: WiFiVerificationRequest,
    db: Session = Depends(get_db)
):
    """
    Verify student location using WiFi SSID (fallback method).
    
    Returns:
        - verified: bool
        - ssid: str
        - message: str
    """
    try:
        # Get whitelisted WiFi SSIDs from database
        whitelisted = db.execute(
            """
            SELECT ssid FROM wifi_whitelist 
            WHERE is_active = TRUE
            """
        ).fetchall()
        
        whitelisted_ssids = [row.ssid for row in whitelisted]
        
        # Verify WiFi SSID
        result = GeofencingService.check_wifi_fallback(
            request.wifi_ssid,
            whitelisted_ssids
        )
        
        logger.info(f"WiFi verification for SSID '{request.wifi_ssid}': {result}")
        
        return {
            "verified": result['verified'],
            "ssid": result['ssid'],
            "message": result['message'],
            "method": "wifi"
        }
        
    except Exception as e:
        logger.error(f"WiFi verification error: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/verify-location")
async def verify_location_comprehensive(
    request: LocationVerificationRequest,
    db: Session = Depends(get_db)
):
    """
    Comprehensive location verification with GPS and WiFi fallback.
    
    Logic:
    1. Try GPS first if coordinates provided
    2. If GPS fails twice, allow WiFi fallback
    3. Return verification result with method used
    """
    try:
        # Get session and teacher location
        session = db.execute(
            """
            SELECT s.id, s.session_id, 
                   u.id as teacher_id,
                   -- Mock teacher location (in production, store with session)
                   28.6139 as teacher_lat,
                   77.2090 as teacher_lon
            FROM attendance_sessions s
            LEFT JOIN users u ON s.teacher_id = u.id
            WHERE s.session_id = :session_id AND s.status = 'active'
            """,
            {"session_id": request.session_id}
        ).fetchone()
        
        if not session:
            raise HTTPException(status_code=404, detail="Session not found or expired")
        
        # Get whitelisted WiFi SSIDs
        whitelisted = db.execute(
            """
            SELECT ssid FROM wifi_whitelist 
            WHERE is_active = TRUE
            """
        ).fetchall()
        whitelisted_ssids = [row.ssid for row in whitelisted]
        
        # Comprehensive verification
        result = GeofencingService.verify_location(
            request.latitude,
            request.longitude,
            session.teacher_lat,
            session.teacher_lon,
            request.accuracy,
            request.gps_failure_count,
            request.wifi_ssid,
            whitelisted_ssids
        )
        
        logger.info(f"Location verification for {request.student_id}: {result}")
        
        return result
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Location verification error: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/wifi-networks")
async def get_whitelisted_wifi_networks(db: Session = Depends(get_db)):
    """
    Get list of whitelisted WiFi networks.
    
    Returns:
        List of approved WiFi SSIDs
    """
    try:
        networks = db.execute(
            """
            SELECT ssid, location_name, is_active
            FROM wifi_whitelist
            ORDER BY location_name
            """
        ).fetchall()
        
        return {
            "networks": [
                {
                    "ssid": row.ssid,
                    "location": row.location_name,
                    "active": row.is_active
                }
                for row in networks
            ]
        }
        
    except Exception as e:
        logger.error(f"Error fetching WiFi networks: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/geofence-config")
async def get_geofence_configuration(db: Session = Depends(get_db)):
    """
    Get geofencing configuration parameters.
    
    Returns:
        Configuration settings for geofencing
    """
    try:
        config = db.execute(
            """
            SELECT config_key, config_value, description
            FROM geofence_config
            """
        ).fetchall()
        
        return {
            "config": {
                row.config_key: {
                    "value": row.config_value,
                    "description": row.description
                }
                for row in config
            }
        }
        
    except Exception as e:
        logger.error(f"Error fetching geofence config: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))
