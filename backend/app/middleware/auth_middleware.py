"""
Authentication Middleware
JWT token verification and role-based access control
"""
from fastapi import Request, HTTPException, Depends, status
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from typing import Optional, List
from app.services.auth_service import get_auth_service
import logging

logger = logging.getLogger(__name__)

# HTTP Bearer token scheme
security = HTTPBearer()


async def get_current_user(credentials: HTTPAuthorizationCredentials = Depends(security)) -> dict:
    """
    Dependency to get current authenticated user from JWT token
    
    Args:
        credentials: HTTP Authorization credentials with Bearer token
        
    Returns:
        User dict with id, email, name, role
        
    Raises:
        HTTPException 401 if token is invalid
    """
    try:
        token = credentials.credentials
        auth_service = get_auth_service()
        
        # Verify token with Supabase
        token_data = await auth_service.verify_token(token)
        supabase_id = token_data["supabase_user_id"]
        email = token_data["email"]
        
        # Get user from database
        user = await auth_service.get_user_by_supabase_id(supabase_id)
        
        if not user:
            # User not in our database yet - might be first login
            # Return minimal user info for registration flow
            return {
                "supabase_user_id": supabase_id,
                "email": email,
                "role": None,
                "needs_registration": True
            }
        
        return user
        
    except Exception as e:
        logger.error(f"Authentication failed: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid or expired token",
            headers={"WWW-Authenticate": "Bearer"},
        )


async def require_role(required_roles: List[str]):
    """
    Dependency factory to check if user has required role
    
    Args:
        required_roles: List of allowed roles (e.g., ['admin', 'teacher'])
        
    Returns:
        Dependency function that checks user role
    """
    async def role_checker(current_user: dict = Depends(get_current_user)) -> dict:
        """Check if user has required role"""
        
        # Check if user needs registration
        if current_user.get("needs_registration"):
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="User not registered in system"
            )
        
        user_role = current_user.get("role")
        
        if user_role not in required_roles:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail=f"Insufficient permissions. Required roles: {', '.join(required_roles)}"
            )
        
        return current_user
    
    return role_checker


async def require_admin(current_user: dict = Depends(get_current_user)) -> dict:
    """Dependency to require admin role"""
    if current_user.get("needs_registration"):
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="User not registered in system"
        )
    
    if current_user.get("role") != "admin":
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Admin access required"
        )
    
    return current_user


async def require_teacher_or_admin(current_user: dict = Depends(get_current_user)) -> dict:
    """Dependency to require teacher or admin role"""
    if current_user.get("needs_registration"):
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="User not registered in system"
        )
    
    if current_user.get("role") not in ["teacher", "admin"]:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Teacher or admin access required"
        )
    
    return current_user


async def require_student(current_user: dict = Depends(get_current_user)) -> dict:
    """Dependency to require student role"""
    if current_user.get("needs_registration"):
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="User not registered in system"
        )
    
    if current_user.get("role") != "student":
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Student access required"
        )
    
    return current_user


async def require_approved_student(current_user: dict = Depends(require_student)) -> dict:
    """
    Dependency to require approved student
    Checks if student has approval_status='approved'
    """
    try:
        auth_service = get_auth_service()
        supabase = auth_service.supabase
        
        # Get student record
        response = supabase.table("students").select("*").eq("user_id", current_user["id"]).execute()
        
        if not response.data or len(response.data) == 0:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Student record not found"
            )
        
        student = response.data[0]
        
        if student.get("approval_status") != "approved":
            status_msg = student.get("approval_status", "pending")
            if status_msg == "rejected":
                reason = student.get("rejection_reason", "No reason provided")
                raise HTTPException(
                    status_code=status.HTTP_403_FORBIDDEN,
                    detail=f"Student registration rejected: {reason}"
                )
            else:
                raise HTTPException(
                    status_code=status.HTTP_403_FORBIDDEN,
                    detail="Student registration pending admin approval"
                )
        
        # Add student info to current_user
        current_user["student"] = student
        return current_user
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error checking student approval: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to verify student status"
        )
