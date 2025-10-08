"""
Database layer for song operations using Beanie ODM
Handles MongoDB operations for songs only
"""

from typing import List, Optional
from datetime import datetime
from src.model.song import Song


class SongDatabase:
    """Pure data access layer for song operations using Beanie"""
    
    def __init__(self):
        """Initialize the database layer"""
        pass  # Beanie handles connection through global initialization
    
    async def add_song(self, title: str, artist: str, user: str, genre: str = None, year: int = None) -> Optional[Song]:
        """Add song to database using Beanie"""
        try:
            song = Song(
                title=title,
                artist=artist,
                user=user,
                genre=genre,
                year=year,
                created_at=datetime.now()
            )
            await song.insert()
            return song
        except Exception as e:
            print(f"Error adding song: {e}")
            return None
    
    async def get_songs(self, user: str = None) -> List[Song]:
        """Get songs from database using Beanie"""
        try:
            if user:
                return await Song.find({"user": user}).to_list()
            else:
                return await Song.find_all().to_list()
        except Exception as e:
            print(f"Error getting songs: {e}")
            return []
    
    async def get_song_by_id(self, song_id: str, user: str) -> Optional[Song]:
        """Get song by ID using Beanie"""
        try:
            from bson import ObjectId
            return await Song.find_one({"_id": ObjectId(song_id), "user": user})
        except Exception as e:
            print(f"Error getting song by ID: {e}")
            return None
    
    async def update_song(self, song_id: str, user: str, **updates) -> bool:
        """Update song using Beanie"""
        try:
            from bson import ObjectId
            song = await Song.find_one({"_id": ObjectId(song_id), "user": user})
            
            if song:
                for key, value in updates.items():
                    if hasattr(song, key) and value is not None:
                        setattr(song, key, value)
                song.updated_at = datetime.now()
                await song.save()
                return True
            return False
        except Exception as e:
            print(f"Error updating song: {e}")
            return False
    
    async def delete_song(self, song_id: str, user: str) -> bool:
        """Delete song using Beanie"""
        try:
            from bson import ObjectId
            song = await Song.find_one({"_id": ObjectId(song_id), "user": user})
            
            if song:
                await song.delete()
                return True
            return False
        except Exception as e:
            print(f"Error deleting song: {e}")
            return False
    
    async def search_songs(self, query: str, user: str) -> List[Song]:
        """Search songs using Beanie"""
        try:
            from beanie.operators import Regex
            return await Song.find(
                Song.user == user,
                (Regex(Song.title, query, options="i")) | (Regex(Song.artist, query, options="i"))
            ).to_list()
        except Exception as e:
            print(f"Error searching songs: {e}")
            return []
    
    async def find_duplicate_song(self, title: str, artist: str, user: str) -> Optional[Song]:
        """Find duplicate song using Beanie"""
        try:
            return await Song.find_one(
                Song.title == title,
                Song.artist == artist,
                Song.user == user
            )
        except Exception as e:
            print(f"Error finding duplicate song: {e}")
            return None
    
    async def play_song(self, song_id: str, user: str) -> bool:
        """Mark a song as played (placeholder for future implementation)"""
        # For now, just return True as playing doesn't require database changes
        # In the future, this could update a play_count or last_played timestamp
        return True