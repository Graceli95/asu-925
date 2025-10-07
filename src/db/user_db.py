"""
Database layer for user operations using Beanie ODM
Handles MongoDB operations for users only
"""

from typing import List, Optional
from src.model.user import User


class UserDatabase:
    """Pure data access layer for user operations using Beanie"""
    
    def __init__(self):
        """Initialize the database layer"""
        pass  # Beanie handles connection through global initialization
    
    async def add_user(self, user: User) -> Optional[User]:
        """Add user to database using Beanie"""
        try:
            await user.insert()
            return user
        except Exception as e:
            print(f"Error adding user: {e}")
            return None
    
    async def get_user_by_id(self, user_id: str) -> Optional[User]:
        """Get user by ID using Beanie"""
        try:
            from bson import ObjectId
            return await User.find_one(User.id == ObjectId(user_id))
        except Exception as e:
            print(f"Error getting user by ID: {e}")
            return None
    
    async def get_user_by_username(self, username: str) -> Optional[User]:
        """Get user by username using Beanie"""
        try:
            return await User.find_one(User.username == username)
        except Exception as e:
            print(f"Error getting user by username: {e}")
            return None
    
    async def get_user_by_email(self, email: str) -> Optional[User]:
        """Get user by email using Beanie"""
        try:
            return await User.find_one(User.email == email)
        except Exception as e:
            print(f"Error getting user by email: {e}")
            return None
    
    async def update_user(self, user: User) -> bool:
        """Update user using Beanie"""
        try:
            await user.save()
            return True
        except Exception as e:
            print(f"Error updating user: {e}")
            return False
    
    async def delete_user(self, user_id: str) -> bool:
        """Delete user using Beanie"""
        try:
            from bson import ObjectId
            user = await User.find_one(User.id == ObjectId(user_id))
            
            if user:
                await user.delete()
                return True
            return False
        except Exception as e:
            print(f"Error deleting user: {e}")
            return False
    
    async def get_all_users(self) -> List[User]:
        """Get all users using Beanie"""
        try:
            return await User.find_all().to_list()
        except Exception as e:
            print(f"Error getting all users: {e}")
            return []
    
    async def get_active_users(self) -> List[User]:
        """Get active users using Beanie"""
        try:
            return await User.find(User.is_active == True).to_list()
        except Exception as e:
            print(f"Error getting active users: {e}")
            return []
