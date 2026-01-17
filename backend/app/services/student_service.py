"""
Student Service
Handles student-specific operations
"""
from typing import List, Dict, Optional
from datetime import datetime
from app.db.supabase_client import get_supabase
import logging

logger = logging.getLogger(__name__)


class StudentService:
    """Service for student operations"""
    
    def __init__(self):
        self.supabase = get_supabase()
    
    async def get_student_by_user_id(self, user_id: int) -> Optional[Dict]:
        """
        Get student by user ID
        
        Args:
            user_id: User ID
            
        Returns:
            Student dict or None if not found
        """
        try:
            response = self.supabase.table("students").select(
                "*, users(email)"
            ).eq("user_id", user_id).execute()
            
            if response.data and len(response.data) > 0:
                student = response.data[0]
                return {
                    "id": student["id"],
                    "name": student["name"],
                    "student_id_card_number": student["student_id_card_number"],
                    "email": student.get("users", {}).get("email") if student.get("users") else None,
                    "approval_status": student.get("approval_status", "pending"),
                    "created_at": student["created_at"],
                    "approved_at": student.get("approved_at")
                }
            
            return None
            
        except Exception as e:
            logger.error(f"Error fetching student by user ID: {str(e)}")
            return None
    
    async def get_attendance_history(self, student_id: int, start_date: Optional[str] = None, end_date: Optional[str] = None) -> List[Dict]:
        """
        Get student's attendance records
        
        Args:
            student_id: Student ID
            start_date: Optional start date filter (ISO format)
            end_date: Optional end date filter (ISO format)
            
        Returns:
            List of attendance record dicts
        """
        try:
            query = self.supabase.table("attendance").select(
                "*, attendance_sessions(session_id, class_id)"
            ).eq("student_id", student_id)
            
            if start_date:
                query = query.gte("timestamp", start_date)
            if end_date:
                query = query.lte("timestamp", end_date)
            
            query = query.order("timestamp", desc=True)
            response = query.execute()
            
            records = []
            for record in response.data:
                session = record.get("attendance_sessions", {})
                records.append({
                    "id": record["id"],
                    "session_id": record["session_id"],
                    "class_id": session.get("class_id") if session else None,
                    "timestamp": record["timestamp"],
                    "verification_status": record["verification_status"],
                    "face_confidence": record.get("face_confidence"),
                    "otp_verified": record.get("otp_verified", False)
                })
            
            return records
            
        except Exception as e:
            logger.error(f"Error fetching attendance history: {str(e)}")
            raise Exception(f"Failed to fetch attendance history: {str(e)}")
    
    async def get_attendance_stats(self, student_id: int) -> Dict:
        """
        Calculate attendance statistics for student
        
        Args:
            student_id: Student ID
            
        Returns:
            Dict with attendance statistics
        """
        try:
            # Get all attendance records
            attendance_response = self.supabase.table("attendance").select("*").eq("student_id", student_id).execute()
            
            total_attended = len(attendance_response.data)
            verified_count = len([r for r in attendance_response.data if r["verification_status"] == "verified"])
            
            # Get last attendance
            last_attendance = None
            if attendance_response.data:
                sorted_records = sorted(attendance_response.data, key=lambda x: x["timestamp"], reverse=True)
                last_attendance = sorted_records[0]["timestamp"]
            
            # Get total sessions student is enrolled in
            # First get student's classes
            enrollment_response = self.supabase.table("class_enrollments").select("class_id").eq("student_id", student_id).execute()
            
            class_ids = [e["class_id"] for e in enrollment_response.data]
            
            # Count total sessions for those classes
            total_sessions = 0
            if class_ids:
                sessions_response = self.supabase.table("attendance_sessions").select("id").in_("class_id", class_ids).execute()
                total_sessions = len(sessions_response.data)
            
            # Calculate attendance rate
            attendance_rate = (verified_count / total_sessions * 100) if total_sessions > 0 else 0.0
            
            return {
                "total_sessions": total_sessions,
                "attended_sessions": verified_count,
                "attendance_rate": round(attendance_rate, 2),
                "last_attendance": last_attendance
            }
            
        except Exception as e:
            logger.error(f"Error calculating attendance stats: {str(e)}")
            raise Exception(f"Failed to calculate attendance stats: {str(e)}")
    
    async def update_profile(self, student_id: int, name: Optional[str] = None) -> Dict:
        """
        Update student profile (limited fields)
        
        Args:
            student_id: Student ID
            name: New name (optional)
            
        Returns:
            Updated student dict
        """
        try:
            update_data = {}
            if name is not None:
                update_data["name"] = name
            
            if not update_data:
                raise Exception("No fields to update")
            
            response = self.supabase.table("students").update(update_data).eq("id", student_id).execute()
            
            if not response.data or len(response.data) == 0:
                raise Exception("Student not found")
            
            return response.data[0]
            
        except Exception as e:
            logger.error(f"Error updating student profile: {str(e)}")
            raise Exception(f"Failed to update profile: {str(e)}")


# Singleton instance
_student_service = None

def get_student_service() -> StudentService:
    """Get singleton student service instance"""
    global _student_service
    if _student_service is None:
        _student_service = StudentService()
    return _student_service
