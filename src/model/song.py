"""
Song model for the Songs API application
Using Pydantic BaseModel for validation and serialization
"""

from datetime import datetime
from typing import Optional, Dict, Any
from pydantic import BaseModel, Field, field_validator, ConfigDict
from bson import ObjectId


class Song(BaseModel):
    """
    Song entity model with Pydantic validation
    
    Attributes:
        title: Song title (required)
        artist: Artist name (required)
        user: Username who owns the song (required)
        genre: Music genre (optional)
        year: Release year (optional)
        created_at: Timestamp when song was created
        updated_at: Timestamp when song was last updated
        _id: MongoDB ObjectId
    """
    
    # Configure Pydantic model
    # ConfigDict is a utility from Pydantic v2+ that allows you to configure model behavior.
    # It replaces the old inner 'class Config' from Pydantic v1.
    # Here, it is used to set options such as allowing arbitrary types (like ObjectId),
    # enabling population by field name or alias, stripping whitespace from strings,
    # validating assignments, and customizing JSON encoding for ObjectId and datetime.
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
    
    # Fields with validation and aliases
    title: str = Field(
        # The ... (Ellipsis) is used in Pydantic's Field to indicate that this field is required.
        # In this context, it tells Pydantic that 'title' must be provided when creating a Song instance.
        # Without the ellipsis, the field would be considered optional or would require a default value.
        ...,
        min_length=1,
        max_length=200,
        description="Song title",
        examples=["Bohemian Rhapsody"],
        validation_alias="song_title"  # Alias for input: "song_title" or "title"
    )
    
    artist: str = Field(
        ...,
        min_length=1,
        max_length=200,
        description="Artist name",
        examples=["Queen"],
        validation_alias="artist_name"  # Alias for input: "artist_name" or "artist"
    )
    
    user: str = Field(
        ...,
        min_length=1,
        max_length=32,
        description="Username who owns the song",
        examples=["john_doe"],
        validation_alias="username"  # Alias for input: "username" or "user"
    )
    
    genre: Optional[str] = Field(
        default=None,
        max_length=50,
        description="Music genre",
        examples=["Rock", "Pop", "Jazz"],
        validation_alias="music_genre"  # Alias for input: "music_genre" or "genre"
    )
    
    year: Optional[int] = Field(
        default=None,
        ge=1000,
        le=datetime.now().year,
        description="Release year",
        examples=[1975, datetime.now().year],
        validation_alias="release_year"  # Alias for input: "release_year" or "year"
    )
    
    created_at: datetime = Field(
        default_factory=datetime.now,
        description="Timestamp when song was created",
        validation_alias="date_created"  # Alias for input: "date_created" or "created_at"
    )
    
    updated_at: Optional[datetime] = Field(
        default=None,
        description="Timestamp when song was last updated",
        validation_alias="date_updated"  # Alias for input: "date_updated" or "updated_at"
    )
    
    id: Optional[ObjectId] = Field(
        default=None,
        alias="_id",  # Serialization alias: stores as "_id" in MongoDB
        description="MongoDB ObjectId"
    )
    
    # Validators
    @field_validator('title', 'artist', 'user')
    @classmethod
    def validate_not_empty(cls, v: str) -> str:
        """Ensure required string fields are not empty or only whitespace"""
        if not v or not v.strip():
            raise ValueError('Field cannot be empty or only whitespace')
        return v.strip()
    
    @field_validator('genre')
    @classmethod
    def validate_genre(cls, v: Optional[str]) -> Optional[str]:
        """Clean up genre field"""
        if v is not None and v.strip():
            return v.strip()
        return None
    
    @field_validator('year')
    @classmethod
    def validate_year_not_future(cls, v: Optional[int]) -> Optional[int]:
        """Ensure year is not in the future"""
        if v is not None and v > datetime.now().year:
            raise ValueError(f'Year cannot be in the future (current year: {datetime.now().year})')
        return v
    
    # Methods
    def to_dict(self) -> Dict[str, Any]:
        """
        Convert song to dictionary for database storage
        
        Returns:
            Dictionary representation suitable for MongoDB
        """
        data = {
            "title": self.title,
            "artist": self.artist,
            "user": self.user,
            "genre": self.genre,
            "year": self.year,
            "created_at": self.created_at
        }
        
        if self.updated_at:
            data["updated_at"] = self.updated_at
            
        if self.id:
            data["_id"] = self.id
            
        return data
    
    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'Song':
        """
        Create Song instance from dictionary (e.g., from database)
        
        Args:
            data: Dictionary containing song data
            
        Returns:
            Song instance
        """
        return cls(
            title=data.get("title", ""),
            artist=data.get("artist", ""),
            user=data.get("user", ""),
            genre=data.get("genre"),
            year=data.get("year"),
            created_at=data.get("created_at", datetime.now()),
            updated_at=data.get("updated_at"),
            id=data.get("_id")  # MongoDB uses _id, map to our 'id' field
        )
    
    def update_fields(self, **kwargs) -> None:
        """
        Update song fields and set updated_at timestamp
        
        Args:
            **kwargs: Fields to update with their new values
        """
        for key, value in kwargs.items():
            if hasattr(self, key) and value is not None:
                setattr(self, key, value)
        self.updated_at = datetime.now()
    
    def __str__(self) -> str:
        """String representation of the song"""
        year_str = f" ({self.year})" if self.year else ""
        genre_str = f" [{self.genre}]" if self.genre else ""
        return f"{self.title} by {self.artist}{year_str}{genre_str}"
    
    def __repr__(self) -> str:
        """Detailed representation of the song"""
        return (f"Song(title='{self.title}', artist='{self.artist}', "
                f"user='{self.user}', genre='{self.genre}', year={self.year})")
    
    def to_response(self) -> Dict[str, Any]:
        """
        Convert song to API response format
        
        Returns:
            Dictionary formatted for API responses
        """
        return {
            "id": str(self.id) if self.id else None,
            "title": self.title,
            "artist": self.artist,
            "user": self.user,
            "genre": self.genre,
            "year": self.year,
            "created_at": self.created_at,
            "updated_at": self.updated_at
        }
