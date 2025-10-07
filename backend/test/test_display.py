"""
Tests for display utility functions
"""

import pytest
from datetime import datetime
from bson import ObjectId
from songs_cli import display_songs
from model import Song


class TestDisplayFunctions:
    """Test display utility functions"""
    
    def test_display_songs_empty(self):
        """Test displaying empty song list"""
        # This should not raise an exception
        display_songs([])
    
    def test_display_songs_with_data(self):
        """Test displaying songs with data"""
        mock_songs = [
            Song(
                title='Test Song',
                artist='Test Artist',
                genre='Rock',
                year=2020,
                user='test_user',
                created_at=datetime.now(),
                _id=ObjectId()
            )
        ]
        
        # This should not raise an exception
        display_songs(mock_songs, "Test Songs")
    
