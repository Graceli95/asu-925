"""
User model for the Songs API application
Using Pydantic BaseModel for validation and serialization
"""

from datetime import datetime
from typing import Optional, Dict, Any
from pydantic import BaseModel, Field, field_validator, ConfigDict
from bson import ObjectId
from passlib.context import CryptContext


# Password hashing context
pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

class User(BaseModel):
    """
    User entity model with Pydantic validation and password hashing
    
    Attributes:
        username: Unique username (required)
        email: User email address (required)
        password_hash: Hashed password (required)
        first_name: User's first name (optional)
        last_name: User's last name (optional)
        created_at: Timestamp when user was created
        updated_at: Timestamp when user was last updated
        last_login: Timestamp of last login
        is_active: Whether user account is active
        id: MongoDB ObjectId
    """
    
    # Configure Pydantic model
    model_config = ConfigDict(
        arbitrary_types_allowed=True,  # Allow ObjectId type
        populate_by_name=True,  # Allow population by field name or alias
        str_strip_whitespace=True,  # Strip whitespace from strings
        validate_assignment=True,  # Validate on attribute assignment
        json_encoders={
            ObjectId: str,  # Convert ObjectId to string in JSON
            datetime: lambda v: v.isoformat()  # ISO format for datetime
        }
    )
    
    # Fields with validation
    username: str = Field(
        ...,
        min_length=3,
        max_length=32,
        description="Unique username",
        examples=["john_doe"],
        validation_alias="user_name"
    )
    
    email: str = Field(
        ...,
        description="User email address",
        examples=["john@example.com"],
        validation_alias="email_address"
    )
    
    password_hash: str = Field(
        ...,
        description="Hashed password",
        exclude=True  # Never include in API responses
    )
    
    first_name: Optional[str] = Field(
        default=None,
        max_length=50,
        description="User's first name",
        examples=["John"],
        validation_alias="firstname"
    )
    
    last_name: Optional[str] = Field(
        default=None,
        max_length=50,
        description="User's last name",
        examples=["Doe"],
        validation_alias="lastname"
    )
    
    created_at: datetime = Field(
        default_factory=datetime.now,
        description="Timestamp when user was created",
        validation_alias="date_created"
    )
    
    updated_at: Optional[datetime] = Field(
        default=None,
        description="Timestamp when user was last updated",
        validation_alias="date_updated"
    )
    
    last_login: Optional[datetime] = Field(
        default=None,
        description="Timestamp of last login",
        validation_alias="last_login_date"
    )
    
    is_active: bool = Field(
        default=True,
        description="Whether user account is active"
    )
    
    id: Optional[ObjectId] = Field(
        default=None,
        alias="_id",  # Serialization alias: stores as "_id" in MongoDB
        description="MongoDB ObjectId"
    )
    
    # Validators
    @field_validator('username', 'email')
    @classmethod
    def validate_not_empty(cls, v: str) -> str:
        """Ensure required string fields are not empty or only whitespace"""
        if not v or not v.strip():
            raise ValueError('Field cannot be empty or only whitespace')
        return v.strip()
    
    @field_validator('email')
    @classmethod
    def validate_email(cls, v: str) -> str:
        """Basic email validation"""
        if '@' not in v or '.' not in v.split('@')[-1]:
            raise ValueError('Invalid email format')
        return v.lower().strip()
    
    @field_validator('first_name', 'last_name')
    @classmethod
    def validate_names(cls, v: Optional[str]) -> Optional[str]:
        """Clean up name fields"""
        if v is not None and v.strip():
            return v.strip()
        return None
    
    # Password methods
    @staticmethod
    def hash_password(password: str) -> str:
        """Hash a password using bcrypt"""
        return pwd_context.hash(password)
    
    def verify_password(self, password: str) -> bool:
        """Verify a password against the stored hash"""
        return pwd_context.verify(password, self.password_hash)
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert user to dictionary for database storage"""
        data = {
            "username": self.username,
            "email": self.email,
            "password_hash": self.password_hash,
            "first_name": self.first_name,
            "last_name": self.last_name,
            "created_at": self.created_at,
            "is_active": self.is_active
        }
        
        if self.updated_at:
            data["updated_at"] = self.updated_at
        
        if self.last_login:
            data["last_login"] = self.last_login
            
        if self.id:
            data["_id"] = self.id
            
        return data
    
    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'User':
        """Create User instance from dictionary (e.g., from database)"""
        return cls(
            username=data.get("username", ""),
            email=data.get("email", ""),
            password_hash=data.get("password_hash", ""),
            first_name=data.get("first_name"),
            last_name=data.get("last_name"),
            created_at=data.get("created_at", datetime.now()),
            updated_at=data.get("updated_at"),
            last_login=data.get("last_login"),
            is_active=data.get("is_active", True),
            id=data.get("_id")  # MongoDB uses _id, map to our 'id' field
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
        """Convert user to API response format (excludes password_hash)"""
        return {
            "id": str(self.id) if self.id else None,
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

