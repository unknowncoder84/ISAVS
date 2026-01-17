"""
WebSocket Manager for Real-time Dashboard Updates
Manages WebSocket connections and broadcasts attendance updates
"""
from typing import List, Dict, Any
from fastapi import WebSocket
from datetime import datetime
import json


class ConnectionManager:
    """Manages WebSocket connections for real-time dashboard updates."""
    
    def __init__(self):
        self.active_connections: List[WebSocket] = []
    
    async def connect(self, websocket: WebSocket):
        """Accept and store a new WebSocket connection."""
        await websocket.accept()
        self.active_connections.append(websocket)
        print(f"✓ WebSocket connected. Total connections: {len(self.active_connections)}")
    
    def disconnect(self, websocket: WebSocket):
        """Remove a WebSocket connection."""
        if websocket in self.active_connections:
            self.active_connections.remove(websocket)
            print(f"✓ WebSocket disconnected. Total connections: {len(self.active_connections)}")
    
    async def send_personal_message(self, message: str, websocket: WebSocket):
        """Send a message to a specific WebSocket connection."""
        try:
            await websocket.send_text(message)
        except Exception as e:
            print(f"Error sending personal message: {e}")
            self.disconnect(websocket)
    
    async def broadcast(self, message: str):
        """Broadcast a message to all connected WebSocket clients."""
        disconnected = []
        
        for connection in self.active_connections:
            try:
                await connection.send_text(message)
            except Exception as e:
                print(f"Error broadcasting to connection: {e}")
                disconnected.append(connection)
        
        # Remove disconnected clients
        for connection in disconnected:
            self.disconnect(connection)
    
    async def broadcast_attendance_update(
        self,
        student_id: int,
        student_name: str,
        student_id_card: str,
        verification_status: str,
        face_confidence: float,
        is_biometric_mismatch: bool = False,
        timestamp: datetime = None
    ):
        """
        Broadcast attendance update to all connected dashboard clients.
        
        Args:
            student_id: Student database ID
            student_name: Student's name
            student_id_card: Student's ID card number
            verification_status: 'verified' or 'failed'
            face_confidence: Face recognition confidence score
            is_biometric_mismatch: True if OTP correct but face failed
            timestamp: Verification timestamp
        """
        if timestamp is None:
            timestamp = datetime.utcnow()
        
        message = {
            "type": "attendance_update",
            "data": {
                "student_id": student_id,
                "student_name": student_name,
                "student_id_card": student_id_card,
                "verification_status": verification_status,
                "face_confidence": face_confidence,
                "is_biometric_mismatch": is_biometric_mismatch,
                "timestamp": timestamp.isoformat()
            },
            "timestamp": datetime.utcnow().isoformat()
        }
        
        await self.broadcast(json.dumps(message))
        print(f"📡 Broadcasted attendance update for {student_name}")
    
    async def broadcast_anomaly_alert(
        self,
        student_id: int,
        student_name: str,
        anomaly_type: str,
        reason: str,
        face_confidence: float = None,
        distance_meters: float = None,
        timestamp: datetime = None
    ):
        """
        Broadcast anomaly alert to all connected dashboard clients.
        
        Args:
            student_id: Student database ID
            student_name: Student's name
            anomaly_type: Type of anomaly (identity_mismatch, geofence_violation, etc.)
            reason: Description of the anomaly
            face_confidence: Face recognition confidence (if applicable)
            distance_meters: Distance from classroom (if geofence violation)
            timestamp: Anomaly timestamp
        """
        if timestamp is None:
            timestamp = datetime.utcnow()
        
        message = {
            "type": "anomaly_alert",
            "data": {
                "student_id": student_id,
                "student_name": student_name,
                "anomaly_type": anomaly_type,
                "reason": reason,
                "face_confidence": face_confidence,
                "distance_meters": distance_meters,
                "timestamp": timestamp.isoformat()
            },
            "timestamp": datetime.utcnow().isoformat()
        }
        
        await self.broadcast(json.dumps(message))
        print(f"🚨 Broadcasted anomaly alert for {student_name}: {anomaly_type}")
    
    def get_connection_count(self) -> int:
        """Get the number of active WebSocket connections."""
        return len(self.active_connections)


# Singleton instance
_manager: ConnectionManager = None


def get_connection_manager() -> ConnectionManager:
    """Get or create the WebSocket connection manager instance."""
    global _manager
    if _manager is None:
        _manager = ConnectionManager()
    return _manager
