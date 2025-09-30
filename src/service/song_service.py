"""
Song service layer for the Songs CLI application
Handles business logic and coordinates between CLI and data layers
"""

from typing import List, Optional, Dict, Any
from datetime import datetime
from src.db.songs_db import SongsDatabase
from src.model import Song
from src.service.file_handler import SongFileHandler


class SongService:
    """Service layer for song operations"""
    
    def __init__(self, database: SongsDatabase):
        """Initialize the service with a database instance"""
        self.db = database
        self.file_handler = SongFileHandler()
    
    def add_song(self, title: str, artist: str, user: str, genre: Optional[str] = None, year: Optional[int] = None) -> Dict[str, Any]:
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
        
        # Delegate to database layer
        created_song = self.db.add_song(title.strip(), artist.strip(), user, genre, year)
        
        if created_song:
            # Try to create the song file in assets folder
            file_created = self.file_handler.create_song_file(created_song)
            
            if file_created:
                return {"success": True, "message": f"Song '{title}' by '{artist}' added successfully and saved to assets folder"}
            else:
                # File creation failed, rollback the database insertion
                self.db.delete_song(str(created_song._id), user)
                return {"success": False, "message": f"Failed to create song file. Database entry has been rolled back."}
        else:
            return {"success": False, "message": "Failed to add song"}
    
    def get_songs(self, user: Optional[str] = None) -> List[Song]:
        """Get songs, optionally filtered by user"""
        return self.db.get_songs(user)
    
    def get_song_by_id(self, song_id: str, user: str) -> Optional[Song]:
        """Get a specific song by ID"""
        return self.db.get_song_by_id(song_id, user)
    
    def search_songs(self, query: str, user: Optional[str] = None) -> Dict[str, Any]:
        """
        Search songs by title or artist
        
        Returns:
            Dict with 'success' boolean, 'results' list, and 'message' string
        """
        if not query.strip():
            return {"success": False, "results": [], "message": "Search query cannot be empty"}
        
        results = self.db.search_songs(query.strip(), user)
        
        return {
            "success": True,
            "results": results,
            "message": f"Found {len(results)} song(s) matching '{query}'"
        }
    
    def update_song(self, song_id: str, user: str, **updates) -> Dict[str, Any]:
        """
        Update a song
        
        Returns:
            Dict with 'success' boolean and 'message' string
        """
        # Validate that song exists and belongs to user
        song = self.get_song_by_id(song_id, user)
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
        success = self.db.update_song(song_id, user, **cleaned_updates)
        
        if success:
            return {"success": True, "message": "Song updated successfully"}
        else:
            return {"success": False, "message": "Failed to update song"}
    
    def delete_song(self, song_id: str, user: str) -> Dict[str, Any]:
        """
        Delete a song
        
        Returns:
            Dict with 'success' boolean, 'message' string, and 'song' object if found
        """
        # Validate that song exists and belongs to user
        song = self.get_song_by_id(song_id, user)
        if not song:
            return {"success": False, "message": "Song not found or you don't have permission to delete it"}
        
        # Delegate to database layer
        success = self.db.delete_song(song_id, user)
        
        if success:
            # Also delete the associated file
            self.file_handler.delete_song_file(song)
            
            return {
                "success": True,
                "message": f"Song '{song.title}' by '{song.artist}' deleted successfully",
                "song": song
            }
        else:
            return {"success": False, "message": "Failed to delete song"}
    
    def play_song(self, song_id: str, user: str) -> Dict[str, Any]:
        """
        Mark a song as played
        
        Returns:
            Dict with 'success' boolean, 'message' string, and 'song' object if found
        """
        # Validate that song exists and belongs to user
        song = self.get_song_by_id(song_id, user)
        if not song:
            return {"success": False, "message": "Song not found or you don't have permission to play it"}
        
        # Delegate to database layer
        success = self.db.play_song(song_id, user)
        
        if success:
            return {
                "success": True,
                "message": f"Now playing: '{song.title}' by '{song.artist}'",
                "song": song
            }
        else:
            return {"success": False, "message": "Failed to play song"}
    
    def get_user_stats(self, user: str) -> Dict[str, Any]:
        """
        Get statistics for a user's song collection
        
        Returns:
            Dict with user statistics
        """
        songs = self.get_songs(user)
        
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
