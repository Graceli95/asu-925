"""
Song model for the Songs CLI application
"""

from datetime import datetime
from typing import Optional, Dict, Any
from dataclasses import dataclass, field
from bson import ObjectId


@dataclass
class Song:
    """Song entity model"""
    title: str
    artist: str
    user: str
    genre: Optional[str] = None
    year: Optional[int] = None
    created_at: datetime = field(default_factory=datetime.now)
    updated_at: Optional[datetime] = None
    _id: Optional[ObjectId] = None
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert song to dictionary for database storage"""
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
            
        if self._id:
            data["_id"] = self._id
            
        return data
    
    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'Song':
        """Create Song instance from dictionary (e.g., from database)"""
        return cls(
            title=data.get("title", ""),
            artist=data.get("artist", ""),
            user=data.get("user", ""),
            genre=data.get("genre"),
            year=data.get("year"),
            created_at=data.get("created_at", datetime.now()),
            updated_at=data.get("updated_at"),
            _id=data.get("_id")
        )
    
    def update(self, **kwargs) -> None:
        """Update song fields and set updated_at timestamp"""
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
        """Convert song to API response format"""
        return {
            "id": str(self._id) if self._id else None,
            "title": self.title,
            "artist": self.artist,
            "user": self.user,
            "genre": self.genre,
            "year": self.year,
            "created_at": self.created_at,
            "updated_at": self.updated_at
        }