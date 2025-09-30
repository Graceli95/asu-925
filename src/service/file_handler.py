"""
File handling operations for the Songs CLI application
Handles creation and management of song files in the assets directory
"""

import os
import re
from typing import Optional
from model import Song


class SongFileHandler:
    """Handles file operations for song data export"""
    
    def __init__(self, assets_dir: str = "assets"):
        """Initialize the file handler with assets directory path"""
        self.assets_dir = assets_dir
        self._ensure_assets_directory()
    
    def _ensure_assets_directory(self) -> None:
        """Ensure the assets directory exists"""
        if not os.path.exists(self.assets_dir):
            os.makedirs(self.assets_dir)
    
    def _sanitize_filename(self, filename: str) -> str:
        """
        Sanitize filename by removing invalid characters
        
        Args:
            filename: The original filename
            
        Returns:
            str: Sanitized filename safe for filesystem use
        """
        # Replace invalid characters with underscores
        sanitized = re.sub(r'[<>:"/\\|?*]', '_', filename)
        # Remove multiple consecutive underscores
        sanitized = re.sub(r'_+', '_', sanitized)
        # Remove leading/trailing underscores and spaces
        sanitized = sanitized.strip('_ ')
        return sanitized
    
    def _format_song_content(self, song: Song) -> str:
        """
        Format song data for file content
        
        Args:
            song: Song object containing the song data
            
        Returns:
            str: Formatted content for the file
        """
        content = "Song Information\n"
        content += "================\n\n"
        content += f"Title: {song.title}\n"
        content += f"Artist: {song.artist}\n"
        content += f"User: {song.user}\n"
        
        if song.genre:
            content += f"Genre: {song.genre}\n"
        else:
            content += "Genre: Not specified\n"
            
        if song.year:
            content += f"Year: {song.year}\n"
        else:
            content += "Year: Not specified\n"
            
        content += f"Added: {song.created_at.strftime('%Y-%m-%d %H:%M:%S')}\n"
        
        if song.updated_at:
            content += f"Last Updated: {song.updated_at.strftime('%Y-%m-%d %H:%M:%S')}\n"
        
        if song._id:
            content += f"Database ID: {str(song._id)}\n"
        
        return content
    
    def create_song_file(self, song: Song) -> bool:
        """
        Create a .txt file for the song in the assets directory
        
        Args:
            song: Song object containing the song data
            
        Returns:
            bool: True if file was created successfully, False otherwise
        """
        try:
            # Create filename in format "artist - title.txt"
            filename = f"{song.artist} - {song.title}.txt"
            sanitized_filename = self._sanitize_filename(filename)
            filepath = os.path.join(self.assets_dir, sanitized_filename)
            
            # Create file content
            content = self._format_song_content(song)
            
            # Write file
            with open(filepath, 'w', encoding='utf-8') as f:
                f.write(content)
            
            return True
        except Exception as e:
            print(f"Error creating song file: {e}")
            return False
    
    def get_file_path(self, song: Song) -> str:
        """
        Get the expected file path for a song
        
        Args:
            song: Song object
            
        Returns:
            str: Expected file path for the song
        """
        filename = f"{song.artist} - {song.title}.txt"
        sanitized_filename = self._sanitize_filename(filename)
        return os.path.join(self.assets_dir, sanitized_filename)
    
    def delete_song_file(self, song: Song) -> bool:
        """
        Delete the file associated with a song
        
        Args:
            song: Song object
            
        Returns:
            bool: True if file was deleted or didn't exist, False if deletion failed
        """
        try:
            filepath = self.get_file_path(song)
            if os.path.exists(filepath):
                os.remove(filepath)
            return True
        except Exception as e:
            print(f"Error deleting song file: {e}")
            return False
