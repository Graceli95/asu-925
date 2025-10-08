"""
Pydantic schemas for request/response validation in the FastAPI application
"""

from pydantic import BaseModel, Field, field_validator
from typing import Optional
from datetime import datetime


class SongCreate(BaseModel):
    """Schema for creating a new song"""
    title: str = Field(..., min_length=1, description="Song title")
    artist: str = Field(..., min_length=1, description="Artist name")
    genre: Optional[str] = Field(None, description="Music genre")
    year: Optional[int] = Field(None, ge=1000, le=9999, description="Release year")
    
    @field_validator('title', 'artist')
    @classmethod
    def validate_not_empty(cls, v: str) -> str:
        if not v.strip():
            raise ValueError("Field cannot be empty or only whitespace")
        return v.strip()
    
    @field_validator('genre')
    @classmethod
    def validate_genre(cls, v: Optional[str]) -> Optional[str]:
        if v is not None and not v.strip():
            return None
        return v.strip() if v else None


class SongUpdate(BaseModel):
    """Schema for updating an existing song"""
    title: Optional[str] = Field(None, min_length=1, description="Song title")
    artist: Optional[str] = Field(None, min_length=1, description="Artist name")
    genre: Optional[str] = Field(None, description="Music genre")
    year: Optional[int] = Field(None, ge=1000, le=9999, description="Release year")
    
    @field_validator('title', 'artist')
    @classmethod
    def validate_not_empty(cls, v: Optional[str]) -> Optional[str]:
        if v is not None and not v.strip():
            raise ValueError("Field cannot be empty or only whitespace")
        return v.strip() if v else None
    
    @field_validator('genre')
    @classmethod
    def validate_genre(cls, v: Optional[str]) -> Optional[str]:
        if v is not None and not v.strip():
            return None
        return v.strip() if v else None


class SongResponse(BaseModel):
    """Schema for song response"""
    id: str = Field(..., description="Song ID")
    title: str
    artist: str
    user: str
    genre: Optional[str] = None
    year: Optional[int] = None
    created_at: datetime
    updated_at: Optional[datetime] = None
    
    class Config:
        from_attributes = True


class SongListResponse(BaseModel):
    """Schema for list of songs response"""
    songs: list[SongResponse]
    count: int


class SearchResponse(BaseModel):
    """Schema for search results"""
    results: list[SongResponse]
    count: int
    message: str


class MessageResponse(BaseModel):
    """Generic message response"""
    message: str
    success: bool = True


class ErrorResponse(BaseModel):
    """Error response schema"""
    detail: str
    success: bool = False


class UserStatsResponse(BaseModel):
    """Schema for user statistics response"""
    user: str
    total_songs: int
    genres: dict[str, int]
    years: dict[str, int]
    artists: dict[str, int]


# Authentication Schemas
class UserRegister(BaseModel):
    """Schema for user registration"""
    username: str = Field(..., min_length=3, max_length=32, description="Username")
    email: str = Field(..., description="Email address")
    password: str = Field(..., min_length=8, description="Password")
    first_name: Optional[str] = Field(None, max_length=50, description="First name")
    last_name: Optional[str] = Field(None, max_length=50, description="Last name")
    
    @field_validator('username', 'email', 'password')
    @classmethod
    def validate_not_empty(cls, v: str) -> str:
        if not v.strip():
            raise ValueError("Field cannot be empty or only whitespace")
        return v.strip()
    
    @field_validator('email')
    @classmethod
    def validate_email(cls, v: str) -> str:
        if '@' not in v or '.' not in v.split('@')[-1]:
            raise ValueError('Invalid email format')
        return v.lower().strip()
    
    @field_validator('password')
    @classmethod
    def validate_password(cls, v: str) -> str:
        if len(v) < 8:
            raise ValueError('Password must be at least 8 characters long')
        if not any(c.isupper() for c in v):
            raise ValueError('Password must contain at least one uppercase letter')
        if not any(c.islower() for c in v):
            raise ValueError('Password must contain at least one lowercase letter')
        if not any(c.isdigit() for c in v):
            raise ValueError('Password must contain at least one digit')
        return v


class UserLogin(BaseModel):
    """Schema for user login"""
    username: str = Field(..., description="Username or email")
    password: str = Field(..., description="Password")
    
    @field_validator('username', 'password')
    @classmethod
    def validate_not_empty(cls, v: str) -> str:
        if not v.strip():
            raise ValueError("Field cannot be empty or only whitespace")
        return v.strip()


class Token(BaseModel):
    """Schema for JWT token response"""
    access_token: str = Field(..., description="JWT access token")
    token_type: str = Field(default="bearer", description="Token type")
    expires_in: int = Field(..., description="Token expiration time in seconds")
    refresh_token: Optional[str] = Field(None, description="Refresh token for obtaining new access tokens")


class RefreshTokenRequest(BaseModel):
    """Schema for refresh token request"""
    refresh_token: str = Field(..., description="Refresh token to exchange for new access token")


class TokenData(BaseModel):
    """Schema for JWT token payload data"""
    username: Optional[str] = None
    user_id: Optional[str] = None
    type: Optional[str] = None  # For distinguishing access vs refresh tokens
    version: Optional[int] = 0  # For refresh token versioning, default to 0


class UserUpdate(BaseModel):
    """Schema for updating user information"""
    email: Optional[str] = Field(None, description="Email address")
    first_name: Optional[str] = Field(None, max_length=50, description="First name")
    last_name: Optional[str] = Field(None, max_length=50, description="Last name")
    
    @field_validator('email')
    @classmethod
    def validate_email(cls, v: Optional[str]) -> Optional[str]:
        if v is not None:
            if '@' not in v or '.' not in v.split('@')[-1]:
                raise ValueError('Invalid email format')
            return v.lower().strip()
        return v
    
    @field_validator('first_name', 'last_name')
    @classmethod
    def validate_names(cls, v: Optional[str]) -> Optional[str]:
        if v is not None and not v.strip():
            return None
        return v.strip() if v else None


class UserResponse(BaseModel):
    """Schema for user response (excludes password)"""
    id: str = Field(..., description="User ID")
    username: str
    email: str
    first_name: Optional[str] = None
    last_name: Optional[str] = None
    full_name: str
    created_at: datetime
    updated_at: Optional[datetime] = None
    last_login: Optional[datetime] = None
    is_active: bool
    
    class Config:
        from_attributes = True
