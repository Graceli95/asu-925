"""
User model for the Songs API application
"""

from datetime import datetime
from typing import Optional, Dict, Any
from dataclasses import dataclass, field
from bson import ObjectId


# The @dataclass decorator automatically generates special methods for the class,
# such as __init__, __repr__, __eq__, and others, based on the class attributes.
# This simplifies the creation of classes that are primarily used to store data.
@dataclass
# This code defines a User data model using Python's dataclass.
# The User class represents a user entity with fields for username, email, optional first and last names,
# timestamps for creation, update, and last login, an active status flag, and an optional database ID.
class User:
    """User entity model"""
    username: str
    email: str
    first_name: Optional[str] = None
    last_name: Optional[str] = None
    created_at: datetime = field(default_factory=datetime.now)
    updated_at: Optional[datetime] = None
    last_login: Optional[datetime] = None
    is_active: bool = True
    _id: Optional[ObjectId] = None
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert user to dictionary for database storage"""
        data = {
            "username": self.username,
            "email": self.email,
            "first_name": self.first_name,
            "last_name": self.last_name,
            "created_at": self.created_at,
            "is_active": self.is_active
        }
        
        if self.updated_at:
            data["updated_at"] = self.updated_at
        
        if self.last_login:
            data["last_login"] = self.last_login
            
        if self._id:
            data["_id"] = self._id
            
        return data
    
    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'User':
        """Create User instance from dictionary (e.g., from database)"""
        return cls(
            username=data.get("username", ""),
            email=data.get("email", ""),
            first_name=data.get("first_name"),
            last_name=data.get("last_name"),
            created_at=data.get("created_at", datetime.now()),
            updated_at=data.get("updated_at"),
            last_login=data.get("last_login"),
            is_active=data.get("is_active", True),
            _id=data.get("_id")
        )
    
    def update(self, **kwargs) -> None:
        """Update user fields and set updated_at timestamp"""
        for key, value in kwargs.items():
            if hasattr(self, key) and value is not None:
                setattr(self, key, value)
        self.updated_at = datetime.now()
    
    def get_full_name(self) -> str:
        """Get user's full name"""
        if self.first_name and self.last_name:
            return f"{self.first_name} {self.last_name}"
        elif self.first_name:
            return self.first_name
        elif self.last_name:
            return self.last_name
        return self.username
    
    def update_last_login(self) -> None:
        """Update the last login timestamp"""
        self.last_login = datetime.now()
    
    def deactivate(self) -> None:
        """Deactivate the user account"""
        self.is_active = False
        self.updated_at = datetime.now()
    
    def activate(self) -> None:
        """Activate the user account"""
        self.is_active = True
        self.updated_at = datetime.now()
    
    def __str__(self) -> str:
        """String representation of the user"""
        full_name = self.get_full_name()
        if full_name != self.username:
            return f"{self.username} ({full_name})"
        return self.username
    
    def __repr__(self) -> str:
        """Detailed representation of the user"""
        return (f"User(username='{self.username}', email='{self.email}', "
                f"first_name='{self.first_name}', last_name='{self.last_name}', "
                f"is_active={self.is_active})")
    
    def to_response(self) -> Dict[str, Any]:
        """Convert user to API response format"""
        return {
            "id": str(self._id) if self._id else None,
            "username": self.username,
            "email": self.email,
            "first_name": self.first_name,
            "last_name": self.last_name,
            "full_name": self.get_full_name(),
            "created_at": self.created_at,
            "updated_at": self.updated_at,
            "last_login": self.last_login,
            "is_active": self.is_active
        }

