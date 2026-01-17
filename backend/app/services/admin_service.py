"""
Admin Service
Handles admin operations for managing teachers and students
"""
from typing import List, Dict, Optional
from app.db.supabase_client import get_supabase
from app.services.auth_service import get_auth_service
import logging

logger = logging.getLogger(__name__)


class AdminService:
    """Service for admin operations"""
    
    def __init__(self):
        self.supabase = get_supabase()
        self.auth_service = get_auth_service()
    
    # ==================== Teacher Management ====================
    
    async def list_teachers(self) -> List[Dict]:
        """
        List all teachers with their user information
        
        Returns:
            List of teacher dicts with user info
        """
        try:
            # Join teachers with users table
            response = self.supabase.table("teachers").select(
                "*, users!inner(id, email, name, role, created_at)"
            ).execute()
            
            teachers = []
            for teacher in response.data:
                teachers.append({
                    "id": teacher["id"],
                    "user_id": teacher["user_id"],
                    "email": teacher["users"]["email"],
                    "name": teacher["users"]["name"],
                    "department": teacher.get("department"),
                    "active": teacher.get("active", True),
                    "created_at": teacher["created_at"]
                })
            
            return teachers
            
        except Exception as e:
            logger.error(f"Error listing teachers: {str(e)}")
            raise Exception(f"Failed to list teachers: {str(e)}")
    
    async def create_teacher(self, email: str, name: str, department: Optional[str] = None) -> Dict:
        """
        Create new teacher account
        
        Args:
            email: Teacher email
            name: Teacher name
            department: Teacher department (optional)
            
        Returns:
            Created teacher dict
        """
        try:
            # Check if user already exists
            existing_user = await self.auth_service.get_user_by_email(email)
            
            if existing_user:
                # Check if already a teacher
                teacher_response = self.supabase.table("teachers").select("*").eq("user_id", existing_user["id"]).execute()
                if teacher_response.data and len(teacher_response.data) > 0:
                    raise Exception("Teacher already exists")
                
                # User exists but not a teacher - update role
                self.supabase.table("users").update({"role": "teacher"}).eq("id", existing_user["id"]).execute()
                user_id = existing_user["id"]
            else:
                # Create new user
                user = await self.auth_service.create_user(
                    email=email,
                    name=name,
                    role="teacher",
                    supabase_id=None  # Will be set on first login
                )
                user_id = user["id"]
            
            # Create teacher record
            teacher_data = {
                "user_id": user_id,
                "department": department,
                "active": True
            }
            
            teacher_response = self.supabase.table("teachers").insert(teacher_data).execute()
            
            if not teacher_response.data or len(teacher_response.data) == 0:
                raise Exception("Failed to create teacher record")
            
            # Get full teacher info
            teachers = await self.list_teachers()
            created_teacher = next((t for t in teachers if t["user_id"] == user_id), None)
            
            return created_teacher
            
        except Exception as e:
            logger.error(f"Error creating teacher: {str(e)}")
            raise Exception(f"Failed to create teacher: {str(e)}")
    
    async def update_teacher(self, teacher_id: int, department: Optional[str] = None, active: Optional[bool] = None) -> Dict:
        """
        Update teacher details
        
        Args:
            teacher_id: Teacher ID
            department: New department (optional)
            active: Active status (optional)
            
        Returns:
            Updated teacher dict
        """
        try:
            update_data = {}
            if department is not None:
                update_data["department"] = department
            if active is not None:
                update_data["active"] = active
            
            if not update_data:
                raise Exception("No fields to update")
            
            response = self.supabase.table("teachers").update(update_data).eq("id", teacher_id).execute()
            
            if not response.data or len(response.data) == 0:
                raise Exception("Teacher not found")
            
            # Get full teacher info
            teachers = await self.list_teachers()
            updated_teacher = next((t for t in teachers if t["id"] == teacher_id), None)
            
            return updated_teacher
            
        except Exception as e:
            logger.error(f"Error updating teacher: {str(e)}")
            raise Exception(f"Failed to update teacher: {str(e)}")
    
    async def deactivate_teacher(self, teacher_id: int) -> bool:
        """
        Deactivate teacher account
        
        Args:
            teacher_id: Teacher ID
            
        Returns:
            True if successful
        """
        try:
            response = self.supabase.table("teachers").update({"active": False}).eq("id", teacher_id).execute()
            
            if not response.data or len(response.data) == 0:
                raise Exception("Teacher not found")
            
            return True
            
        except Exception as e:
            logger.error(f"Error deactivating teacher: {str(e)}")
            raise Exception(f"Failed to deactivate teacher: {str(e)}")
    
    # ==================== Student Management ====================
    
    async def list_pending_students(self) -> List[Dict]:
        """
        List all students with pending approval status
        
        Returns:
            List of pending student dicts
        """
        try:
            response = self.supabase.table("students").select(
                "*, users(email)"
            ).eq("approval_status", "pending").execute()
            
            students = []
            for student in response.data:
                students.append({
                    "id": student["id"],
                    "name": student["name"],
                    "student_id_card_number": student["student_id_card_number"],
                    "email": student.get("users", {}).get("email") if student.get("users") else None,
                    "face_image_base64": student.get("face_image_base64"),
                    "created_at": student["created_at"],
                    "approval_status": student["approval_status"]
                })
            
            return students
            
        except Exception as e:
            logger.error(f"Error listing pending students: {str(e)}")
            raise Exception(f"Failed to list pending students: {str(e)}")
    
    async def approve_student(self, student_id: int, admin_id: int) -> Dict:
        """
        Approve student registration
        
        Args:
            student_id: Student ID
            admin_id: Admin user ID who approved
            
        Returns:
            Updated student dict
        """
        try:
            update_data = {
                "approval_status": "approved",
                "approved_by": admin_id,
                "approved_at": "now()"
            }
            
            response = self.supabase.table("students").update(update_data).eq("id", student_id).execute()
            
            if not response.data or len(response.data) == 0:
                raise Exception("Student not found")
            
            return response.data[0]
            
        except Exception as e:
            logger.error(f"Error approving student: {str(e)}")
            raise Exception(f"Failed to approve student: {str(e)}")
    
    async def reject_student(self, student_id: int, admin_id: int, reason: str) -> Dict:
        """
        Reject student registration
        
        Args:
            student_id: Student ID
            admin_id: Admin user ID who rejected
            reason: Rejection reason
            
        Returns:
            Updated student dict
        """
        try:
            update_data = {
                "approval_status": "rejected",
                "approved_by": admin_id,
                "approved_at": "now()",
                "rejection_reason": reason
            }
            
            response = self.supabase.table("students").update(update_data).eq("id", student_id).execute()
            
            if not response.data or len(response.data) == 0:
                raise Exception("Student not found")
            
            return response.data[0]
            
        except Exception as e:
            logger.error(f"Error rejecting student: {str(e)}")
            raise Exception(f"Failed to reject student: {str(e)}")


# Singleton instance
_admin_service = None

def get_admin_service() -> AdminService:
    """Get singleton admin service instance"""
    global _admin_service
    if _admin_service is None:
        _admin_service = AdminService()
    return _admin_service
