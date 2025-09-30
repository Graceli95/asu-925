#!/usr/bin/env python3
"""
Songs Database Module
Handles all database operations for the Songs CLI application
"""

import os
import sys
from datetime import datetime
from typing import Optional, List, Dict, Any
from dotenv import load_dotenv
from pymongo import MongoClient
from pymongo.errors import ServerSelectionTimeoutError, DuplicateKeyError
from bson import ObjectId

# Import models
from src.model import Song

# Load environment variables
load_dotenv()

class SongsDatabase:
    """Database handler for songs operations"""
    
    def __init__(self):
        self.db_url = os.getenv('project_db_url')
        if not self.db_url:
            raise ValueError("project_db_url not found in environment variables")
        
        self.db_name = os.getenv('project_db_name', 'songs')
        
        try:
            self.client = MongoClient(self.db_url)
            self.db = self.client[self.db_name]
            self.songs = self.db.songs
            
            # Create indexes
            self.songs.create_index("title")
            self.songs.create_index("artist")
            self.songs.create_index("user")
            
        except ServerSelectionTimeoutError:
            print("Error: Could not connect to MongoDB. Please check your connection string.")
            sys.exit(1)
    
    def add_song(self, title: str, artist: str, user: str, genre: str = None, year: int = None) -> Optional[Song]:
        """Add a new song to the database and return the created song object"""
        try:
            song = Song(
                title=title,
                artist=artist,
                user=user,
                genre=genre,
                year=year
            )
            
            result = self.songs.insert_one(song.to_dict())
            if result.inserted_id:
                song._id = result.inserted_id
                return song
            return None
        except DuplicateKeyError:
            print(f"Error: Song '{title}' by '{artist}' already exists for user '{user}'")
            return None
    
    def get_songs(self, user: str = None) -> List[Song]:
        """Get all songs, optionally filtered by user"""
        query = {"user": user} if user else {}
        song_dicts = list(self.songs.find(query).sort("created_at", -1))
        return [Song.from_dict(song_dict) for song_dict in song_dicts]
    
    def get_song_by_id(self, song_id: str, user: str) -> Optional[Song]:
        """Get a specific song by ID"""
        try:
            song_dict = self.songs.find_one({"_id": ObjectId(song_id), "user": user})
            return Song.from_dict(song_dict) if song_dict else None
        except:
            return None
    
    def search_songs(self, query: str, user: str = None) -> List[Song]:
        """Search songs by title or artist"""
        search_query = {
            "$or": [
                {"title": {"$regex": query, "$options": "i"}},
                {"artist": {"$regex": query, "$options": "i"}}
            ]
        }
        
        if user:
            search_query["user"] = user
        
        song_dicts = list(self.songs.find(search_query).sort("created_at", -1))
        
        return [Song.from_dict(song_dict) for song_dict in song_dicts]
    
    def update_song(self, song_id: str, user: str, **updates) -> bool:
        """Update a song"""
        try:
            # Remove None values from updates
            updates = {k: v for k, v in updates.items() if v is not None}
            updates["updated_at"] = datetime.now()
            
            result = self.songs.update_one(
                {"_id": ObjectId(song_id), "user": user},
                {"$set": updates}
            )
            
            if result.modified_count > 0:
                return True
            return False
        except:
            return False
    
    def delete_song(self, song_id: str, user: str) -> bool:
        """Delete a song"""
        try:
            song = self.get_song_by_id(song_id, user)
            if not song:
                return False
            
            result = self.songs.delete_one({"_id": ObjectId(song_id), "user": user})
            
            if result.deleted_count > 0:
                return True
            return False
        except:
            return False
    
    def play_song(self, song_id: str, user: str) -> bool:
        """Mark a song as played"""
        song = self.get_song_by_id(song_id, user)
        if song:
            return True
        return False
    
    
    def close(self):
        """Close database connection"""
        if hasattr(self, 'client'):
            self.client.close()
