"""
Pydantic schemas for the Songs API
Defines request and response models for API endpoints
"""

from datetime import datetime
from typing import List, Optional, Dict, Any
from pydantic import BaseModel, Field, validator
from bson import ObjectId


class PyObjectId(ObjectId):
    """Custom ObjectId type for Pydantic"""
    @classmethod
    def __get_validators__(cls):
        yield cls.validate

    @classmethod
    def validate(cls, v):
        if not ObjectId.is_valid(v):
            raise ValueError("Invalid ObjectId")
        return ObjectId(v)

    @classmethod
    def __modify_schema__(cls, field_schema):
        field_schema.update(type="string")


class SongBase(BaseModel):
    """Base song model with common fields"""
    title: str = Field(..., min_length=1, max_length=200, description="Song title")
    artist: str = Field(..., min_length=1, max_length=200, description="Artist name")
    genre: Optional[str] = Field(None, max_length=100, description="Song genre")
    year: Optional[int] = Field(None, ge=1800, le=2100, description="Release year")

    @validator('title', 'artist')
    def validate_string_fields(cls, v):
        if not v or not v.strip():
            raise ValueError('Field cannot be empty or whitespace only')
        return v.strip()

    @validator('year')
    def validate_year(cls, v):
        if v is not None:
            current_year = datetime.now().year
            if v > current_year:
                raise ValueError(f'Year cannot be in the future (current year: {current_year})')
        return v


class SongCreate(SongBase):
    """Schema for creating a new song"""
    user: str = Field(..., min_length=1, max_length=100, description="Username")


class SongUpdate(BaseModel):
    """Schema for updating a song"""
    title: Optional[str] = Field(None, min_length=1, max_length=200)
    artist: Optional[str] = Field(None, min_length=1, max_length=200)
    genre: Optional[str] = Field(None, max_length=100)
    year: Optional[int] = Field(None, ge=1800, le=2100)

    @validator('title', 'artist')
    def validate_string_fields(cls, v):
        if v is not None and (not v or not v.strip()):
            raise ValueError('Field cannot be empty or whitespace only')
        return v.strip() if v else v

    @validator('year')
    def validate_year(cls, v):
        if v is not None:
            current_year = datetime.now().year
            if v > current_year:
                raise ValueError(f'Year cannot be in the future (current year: {current_year})')
        return v


class SongResponse(SongBase):
    """Schema for song response"""
    id: PyObjectId = Field(alias="_id")
    user: str = Field(..., description="Username")
    created_at: datetime = Field(..., description="Creation timestamp")
    updated_at: Optional[datetime] = Field(None, description="Last update timestamp")

    @classmethod
    def from_orm(cls, song):
        """Create SongResponse from Song model"""
        return cls(
            _id=song._id,
            title=song.title,
            artist=song.artist,
            user=song.user,
            genre=song.genre,
            year=song.year,
            created_at=song.created_at,
            updated_at=song.updated_at
        )

    class Config:
        allow_population_by_field_name = True
        arbitrary_types_allowed = True
        json_encoders = {ObjectId: str}


class SongSearchResponse(BaseModel):
    """Schema for search results response"""
    success: bool = Field(..., description="Whether the search was successful")
    results: List[SongResponse] = Field(..., description="List of matching songs")
    message: str = Field(..., description="Search result message")
    total_count: int = Field(..., description="Total number of results")


class PlaySongResponse(BaseModel):
    """Schema for play song response"""
    success: bool = Field(..., description="Whether the operation was successful")
    message: str = Field(..., description="Response message")
    song: Optional[SongResponse] = Field(None, description="Song that was played")


class UserStatsResponse(BaseModel):
    """Schema for user statistics response"""
    total_songs: int = Field(..., description="Total number of songs")
    genres: Dict[str, int] = Field(..., description="Genre distribution")
    years: Dict[str, int] = Field(..., description="Year distribution")
    artists: Dict[str, int] = Field(..., description="Artist distribution")


class ErrorResponse(BaseModel):
    """Schema for error responses"""
    detail: str = Field(..., description="Error message")
    error_code: Optional[str] = Field(None, description="Error code")
    timestamp: datetime = Field(default_factory=datetime.now, description="Error timestamp")


class SuccessResponse(BaseModel):
    """Schema for success responses"""
    success: bool = Field(True, description="Operation success status")
    message: str = Field(..., description="Success message")
    data: Optional[Dict[str, Any]] = Field(None, description="Additional data")
