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
    user: str = Field(..., min_length=1, description="Username")
    genre: Optional[str] = Field(None, description="Music genre")
    year: Optional[int] = Field(None, ge=1000, le=9999, description="Release year")
    
    @field_validator('title', 'artist', 'user')
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
