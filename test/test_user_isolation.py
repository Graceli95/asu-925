"""
Tests for user isolation functionality
"""

import pytest
from model import Song


class TestUserIsolation:
    """Test that users can only access their own data"""
    
    def test_user_isolation(self, test_db, test_user, test_user2):
        """Test that users can only access their own data"""
        # Add songs for both users
        test_db.add_song("User1 Song", "Artist", test_user, "Rock", 2020)
        test_db.add_song("User2 Song", "Artist", test_user2, "Pop", 2021)
        
        # User1 should only see their songs
        user1_songs = test_db.get_songs(test_user)
        assert len(user1_songs) == 1
        assert user1_songs[0].title == "User1 Song"
        
        # User2 should only see their songs
        user2_songs = test_db.get_songs(test_user2)
        assert len(user2_songs) == 1
        assert user2_songs[0].title == "User2 Song"
        
        # User isolation verified - no history tracking
