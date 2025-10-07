"""
Song service layer for the Songs API application
Handles business logic and coordinates between API and data layers using Beanie ODM
"""

from typing import List, Optional, Dict, Any
from datetime import datetime
from src.db.song_db import SongDatabase
from src.model import Song


class SongService:
    """Service layer for song operations with Beanie ODM"""
    
    def __init__(self, database: SongDatabase):
        """Initialize the service with a Beanie database instance"""
        self.db = database
    
    async def add_song(self, title: str, artist: str, user: str, genre: Optional[str] = None, year: Optional[int] = None) -> Dict[str, Any]:
        """
        Add a new song
        
        Returns:
            Dict with 'success' boolean and 'message' string
        """
        # Business logic validation
        if not title.strip():
            return {"success": False, "message": "Title cannot be empty"}
        
        if not artist.strip():
            return {"success": False, "message": "Artist cannot be empty"}
        
        current_year = datetime.now().year
        if year is not None and year > current_year:
            return {"success": False, "message": f"Year cannot be in the future (current year: {current_year})"}
        
        # Business logic: check for duplicates
        existing_song = await self.db.find_duplicate_song(title.strip(), artist.strip(), user)
        if existing_song:
            return {"success": False, "message": "Song already exists"}
        
        # Delegate to database layer
        created_song = await self.db.add_song(title.strip(), artist.strip(), user, genre, year)
        
        if created_song:
            return {"success": True, "message": f"Song '{title}' by '{artist}' added successfully."}
        else:
            return {"success": False, "message": "Failed to add song"}
    
    async def get_songs(self, user: Optional[str] = None) -> List[Song]:
        """Get songs, optionally filtered by user"""
        return await self.db.get_songs(user)
    
    async def get_song_by_id(self, song_id: str, user: str) -> Optional[Song]:
        """Get a specific song by ID"""
        return await self.db.get_song_by_id(song_id, user)
    
    async def search_songs(self, query: str, user: Optional[str] = None) -> Dict[str, Any]:
        """
        Search songs by title or artist
        
        Returns:
            Dict with 'success' boolean, 'results' list, and 'message' string
        """
        if not query.strip():
            return {"success": False, "results": [], "message": "Search query cannot be empty"}
        
        if len(query.strip()) < 2:
            return {"success": False, "results": [], "message": "Search query must be at least 2 characters"}
        
        results = await self.db.search_songs(query.strip(), user)
        
        return {
            "success": True,
            "results": results,
            "message": f"Found {len(results)} song(s) matching '{query}'"
        }
    
    async def update_song(self, song_id: str, user: str, **updates) -> Dict[str, Any]:
        """
        Update a song
        
        Returns:
            Dict with 'success' boolean and 'message' string
        """
        # Validate that song exists and belongs to user
        song = await self.get_song_by_id(song_id, user)
        if not song:
            return {"success": False, "message": "Song not found or you don't have permission to update it"}
        
        # Business logic validation
        if 'title' in updates and not updates['title'].strip():
            return {"success": False, "message": "Title cannot be empty"}
        
        if 'artist' in updates and not updates['artist'].strip():
            return {"success": False, "message": "Artist cannot be empty"}
        
        if 'year' in updates and updates['year'] is not None:
            current_year = datetime.now().year
            if updates['year'] > current_year:
                return {"success": False, "message": f"Year cannot be in the future (current year: {current_year})"}
        
        # Clean up string fields
        cleaned_updates = {}
        for key, value in updates.items():
            if key in ['title', 'artist', 'genre'] and isinstance(value, str):
                cleaned_updates[key] = value.strip()
            else:
                cleaned_updates[key] = value
        
        # Delegate to database layer
        success = await self.db.update_song(song_id, user, **cleaned_updates)
        
        if success:
            return {"success": True, "message": "Song updated successfully"}
        else:
            return {"success": False, "message": "Failed to update song"}
    
    async def delete_song(self, song_id: str, user: str) -> Dict[str, Any]:
        """
        Delete a song
        
        Returns:
            Dict with 'success' boolean, 'message' string, and 'song' object if found
        """
        # Validate that song exists and belongs to user
        song = await self.get_song_by_id(song_id, user)
        if not song:
            return {"success": False, "message": "Song not found or you don't have permission to delete it"}
        
        # Delegate to database layer
        success = await self.db.delete_song(song_id, user)
        
        if success:
            return {
                "success": True,
                "message": f"Song '{song.title}' by '{song.artist}' deleted successfully",
                "song": song
            }
        else:
            return {"success": False, "message": "Failed to delete song"}
    
    async def play_song(self, song_id: str, user: str) -> Dict[str, Any]:
        """
        Mark a song as played
        
        Returns:
            Dict with 'success' boolean, 'message' string, and 'song' object if found
        """
        # Validate that song exists and belongs to user
        song = await self.get_song_by_id(song_id, user)
        if not song:
            return {"success": False, "message": "Song not found or you don't have permission to play it"}
        
        # For now, just return success (no database update needed for playing)
        return {
            "success": True,
            "message": f"Now playing: '{song.title}' by '{song.artist}'",
            "song": song
        }
    
    async def get_user_stats(self, user: str) -> Dict[str, Any]:
        """
        Get statistics for a user's song collection
        
        Returns:
            Dict with user statistics
        """
        songs = await self.get_songs(user)
        
        if not songs:
            return {
                "total_songs": 0,
                "genres": {},
                "years": {},
                "artists": {}
            }
        
        # Calculate statistics
        genres = {}
        years = {}
        artists = {}
        
        for song in songs:
            # Genre stats
            genre = song.genre or "Unknown"
            genres[genre] = genres.get(genre, 0) + 1
            
            # Year stats
            year = song.year or "Unknown"
            years[year] = years.get(year, 0) + 1
            
            # Artist stats
            artist = song.artist
            artists[artist] = artists.get(artist, 0) + 1
        
        return {
            "total_songs": len(songs),
            "genres": dict(sorted(genres.items(), key=lambda x: x[1], reverse=True)),
            "years": dict(sorted(years.items(), key=lambda x: x[1], reverse=True)),
            "artists": dict(sorted(artists.items(), key=lambda x: x[1], reverse=True))
        }
