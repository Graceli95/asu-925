"""
User service layer for the Songs API application
Handles user management business logic and coordinates between API and data layers
"""

from typing import List, Optional, Dict, Any
from src.schemas import UserResponse, UserUpdate, MessageResponse
from src.model import User
from src.db.user_db import UserDatabase


class UserService:
    """Service layer for user management operations"""
    
    def __init__(self, user_db: UserDatabase):
        """Initialize the service with a user database instance"""
        self.user_db = user_db
    
    async def get_user_by_username(self, username: str) -> Dict[str, Any]:
        """
        Get user by username
        
        Args:
            username: Username to search for
            
        Returns:
            Dict with 'success' boolean, 'user' object if found, and 'message' string
        """
        try:
            user = await self.user_db.get_user_by_username(username)
            if not user:
                return {
                    "success": False,
                    "message": "User not found",
                    "user": None
                }
            
            return {
                "success": True,
                "message": "User found",
                "user": UserResponse(**user.to_response())
            }
            
        except Exception as e:
            return {
                "success": False,
                "message": f"Failed to get user: {str(e)}",
                "user": None
            }
    
    async def get_user_by_email(self, email: str) -> Dict[str, Any]:
        """
        Get user by email
        
        Args:
            email: Email to search for
            
        Returns:
            Dict with 'success' boolean, 'user' object if found, and 'message' string
        """
        try:
            user = await self.user_db.get_user_by_email(email)
            if not user:
                return {
                    "success": False,
                    "message": "User not found",
                    "user": None
                }
            
            return {
                "success": True,
                "message": "User found",
                "user": UserResponse(**user.to_response())
            }
            
        except Exception as e:
            return {
                "success": False,
                "message": f"Failed to get user: {str(e)}",
                "user": None
            }
    
    async def get_all_users(self) -> Dict[str, Any]:
        """
        Get all users
        
        Returns:
            Dict with 'success' boolean, 'users' list, and 'message' string
        """
        try:
            users = await self.user_db.get_all_users()
            
            user_responses = [UserResponse(**user.to_response()) for user in users]
            
            return {
                "success": True,
                "message": f"Found {len(user_responses)} users",
                "users": user_responses
            }
            
        except Exception as e:
            return {
                "success": False,
                "message": f"Failed to get users: {str(e)}",
                "users": []
            }
    
    async def update_user(self, username: str, user_update: UserUpdate) -> Dict[str, Any]:
        """
        Update user information
        
        Args:
            username: Username of the user to update
            user_update: User update data
            
        Returns:
            Dict with 'success' boolean, 'user' object if successful, and 'message' string
        """
        try:
            # Get existing user
            user = await self.user_db.get_user_by_username(username)
            if not user:
                return {
                    "success": False,
                    "message": "User not found",
                    "user": None
                }
            
            # Filter out None values
            updates = user_update.model_dump(exclude_none=True)
            
            if not updates:
                return {
                    "success": False,
                    "message": "No updates provided",
                    "user": None
                }
            
            # Clean up string fields
            cleaned_updates = {}
            for key, value in updates.items():
                if key in ['first_name', 'last_name', 'email'] and isinstance(value, str):
                    cleaned_updates[key] = value.strip()
                else:
                    cleaned_updates[key] = value
            
            # Update user
            success = await self.user_db.update_user(user, **cleaned_updates)
            
            if success:
                # Get updated user
                updated_user = await self.user_db.get_user_by_username(username)
                return {
                    "success": True,
                    "message": "User updated successfully",
                    "user": UserResponse(**updated_user.to_response())
                }
            else:
                return {
                    "success": False,
                    "message": "Failed to update user",
                    "user": None
                }
                
        except Exception as e:
            return {
                "success": False,
                "message": f"Failed to update user: {str(e)}",
                "user": None
            }
    
    async def deactivate_user(self, username: str) -> Dict[str, Any]:
        """
        Deactivate a user account
        
        Args:
            username: Username of the user to deactivate
            
        Returns:
            Dict with 'success' boolean and 'message' string
        """
        try:
            user = await self.user_db.get_user_by_username(username)
            if not user:
                return {
                    "success": False,
                    "message": "User not found"
                }
            
            user.deactivate()
            success = await self.user_db.update_user(user)
            
            if success:
                return {
                    "success": True,
                    "message": f"User '{username}' deactivated successfully"
                }
            else:
                return {
                    "success": False,
                    "message": "Failed to deactivate user"
                }
                
        except Exception as e:
            return {
                "success": False,
                "message": f"Failed to deactivate user: {str(e)}"
            }
    
    async def activate_user(self, username: str) -> Dict[str, Any]:
        """
        Activate a user account
        
        Args:
            username: Username of the user to activate
            
        Returns:
            Dict with 'success' boolean and 'message' string
        """
        try:
            user = await self.user_db.get_user_by_username(username)
            if not user:
                return {
                    "success": False,
                    "message": "User not found"
                }
            
            user.activate()
            success = await self.user_db.update_user(user)
            
            if success:
                return {
                    "success": True,
                    "message": f"User '{username}' activated successfully"
                }
            else:
                return {
                    "success": False,
                    "message": "Failed to activate user"
                }
                
        except Exception as e:
            return {
                "success": False,
                "message": f"Failed to activate user: {str(e)}"
            }
    
    async def delete_user(self, username: str) -> Dict[str, Any]:
        """
        Delete a user account
        
        Args:
            username: Username of the user to delete
            
        Returns:
            Dict with 'success' boolean, 'user' object if found, and 'message' string
        """
        try:
            user = await self.user_db.get_user_by_username(username)
            if not user:
                return {
                    "success": False,
                    "message": "User not found",
                    "user": None
                }
            
            success = await self.user_db.delete_user(username)
            
            if success:
                return {
                    "success": True,
                    "message": f"User '{username}' deleted successfully",
                    "user": UserResponse(**user.to_response())
                }
            else:
                return {
                    "success": False,
                    "message": "Failed to delete user",
                    "user": None
                }
                
        except Exception as e:
            return {
                "success": False,
                "message": f"Failed to delete user: {str(e)}",
                "user": None
            }
    
    async def get_user_stats(self, username: str) -> Dict[str, Any]:
        """
        Get statistics for a user
        
        Args:
            username: Username to get stats for
            
        Returns:
            Dict with user statistics
        """
        try:
            user = await self.user_db.get_user_by_username(username)
            if not user:
                return {
                    "success": False,
                    "message": "User not found",
                    "stats": None
                }
            
            # Basic user stats
            stats = {
                "username": user.username,
                "email": user.email,
                "full_name": user.get_full_name(),
                "is_active": user.is_active,
                "created_at": user.created_at,
                "last_login": user.last_login,
                "account_age_days": (user.created_at - user.created_at).days if user.created_at else 0
            }
            
            return {
                "success": True,
                "message": "User statistics retrieved successfully",
                "stats": stats
            }
            
        except Exception as e:
            return {
                "success": False,
                "message": f"Failed to get user statistics: {str(e)}",
                "stats": None
            }
