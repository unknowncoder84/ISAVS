"""
Authentication Service
Handles user authentication and authorization with Supabase
"""
from typing import Optional, Dict
from supabase import create_client, Client
from app.core.config import settings
from app.db.supabase_client import get_supabase
import logging

logger = logging.getLogger(__name__)


class AuthService:
    """Service for authentication operations"""
    
    def __init__(self):
        self.supabase: Client = get_supabase()
    
    async def verify_token(self, token: str) -> Dict:
        """
        Verify Supabase JWT token and extract user info
        
        Args:
            token: JWT token from Supabase Auth
            
        Returns:
            Dict with user info from token
            
        Raises:
            Exception if token is invalid
        """
        try:
            # Get user from Supabase using the token
            user_response = self.supabase.auth.get_user(token)
            
            if not user_response or not user_response.user:
                raise Exception("Invalid token")
            
            user = user_response.user
            
            return {
                "supabase_user_id": user.id,
                "email": user.email,
                "email_verified": user.email_confirmed_at is not None
            }
            
        except Exception as e:
            logger.error(f"Token verification failed: {str(e)}")
            raise Exception(f"Token verification failed: {str(e)}")
    
    async def get_user_by_supabase_id(self, supabase_id: str) -> Optional[Dict]:
        """
        Get user from database by Supabase user ID
        
        Args:
            supabase_id: Supabase user UUID
            
        Returns:
            User dict or None if not found
        """
        try:
            response = self.supabase.table("users").select("*").eq("supabase_user_id", supabase_id).execute()
            
            if response.data and len(response.data) > 0:
                return response.data[0]
            return None
            
        except Exception as e:
            logger.error(f"Error fetching user by Supabase ID: {str(e)}")
            return None
    
    async def get_user_by_email(self, email: str) -> Optional[Dict]:
        """
        Get user from database by email
        
        Args:
            email: User email
            
        Returns:
            User dict or None if not found
        """
        try:
            response = self.supabase.table("users").select("*").eq("email", email).execute()
            
            if response.data and len(response.data) > 0:
                return response.data[0]
            return None
            
        except Exception as e:
            logger.error(f"Error fetching user by email: {str(e)}")
            return None
    
    async def create_user(self, email: str, name: str, role: str, supabase_id: str) -> Dict:
        """
        Create new user in database
        
        Args:
            email: User email
            name: User name
            role: User role ('admin', 'teacher', 'student')
            supabase_id: Supabase user UUID
            
        Returns:
            Created user dict
        """
        try:
            user_data = {
                "email": email,
                "name": name,
                "role": role,
                "supabase_user_id": supabase_id
            }
            
            response = self.supabase.table("users").insert(user_data).execute()
            
            if response.data and len(response.data) > 0:
                return response.data[0]
            else:
                raise Exception("Failed to create user")
                
        except Exception as e:
            logger.error(f"Error creating user: {str(e)}")
            raise Exception(f"Failed to create user: {str(e)}")
    
    async def update_user_supabase_id(self, user_id: int, supabase_id: str) -> Dict:
        """
        Update user's Supabase ID (for existing users)
        
        Args:
            user_id: User ID in database
            supabase_id: Supabase user UUID
            
        Returns:
            Updated user dict
        """
        try:
            response = self.supabase.table("users").update({
                "supabase_user_id": supabase_id
            }).eq("id", user_id).execute()
            
            if response.data and len(response.data) > 0:
                return response.data[0]
            else:
                raise Exception("Failed to update user")
                
        except Exception as e:
            logger.error(f"Error updating user Supabase ID: {str(e)}")
            raise Exception(f"Failed to update user: {str(e)}")
    
    async def get_user_role(self, user_id: int) -> str:
        """
        Get user role
        
        Args:
            user_id: User ID in database
            
        Returns:
            User role string
        """
        try:
            response = self.supabase.table("users").select("role").eq("id", user_id).execute()
            
            if response.data and len(response.data) > 0:
                return response.data[0]["role"]
            else:
                raise Exception("User not found")
                
        except Exception as e:
            logger.error(f"Error fetching user role: {str(e)}")
            raise Exception(f"Failed to get user role: {str(e)}")


# Singleton instance
_auth_service = None

def get_auth_service() -> AuthService:
    """Get singleton auth service instance"""
    global _auth_service
    if _auth_service is None:
        _auth_service = AuthService()
    return _auth_service
