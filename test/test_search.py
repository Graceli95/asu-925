"""
Tests for song search functionality
"""

import pytest
from model import Song


class TestSongSearch:
    """Test search functionality for songs"""
    
    def test_search_songs_by_title(self, test_db, test_user):
        """Test searching songs by title"""
        test_db.add_song("Bohemian Rhapsody", "Queen", test_user, "Rock", 1975)
        test_db.add_song("We Will Rock You", "Queen", test_user, "Rock", 1977)
        test_db.add_song("Hotel California", "Eagles", test_user, "Rock", 1976)
        
        # Search by title
        results = test_db.search_songs("Bohemian", test_user)
        assert len(results) == 1
        assert results[0].title == "Bohemian Rhapsody"
        
        # Search by artist
        results = test_db.search_songs("Queen", test_user)
        assert len(results) == 2
        titles = [song.title for song in results]
        assert "Bohemian Rhapsody" in titles
        assert "We Will Rock You" in titles
    
    def test_search_songs_case_insensitive(self, test_db, test_user):
        """Test that search is case insensitive"""
        test_db.add_song("Test Song", "Test Artist", test_user, "Rock", 2020)
        
        # Test different case variations
        search_terms = ["test song", "TEST SONG", "Test Song", "test SONG"]
        for term in search_terms:
            results = test_db.search_songs(term, test_user)
            assert len(results) == 1
            assert results[0].title == "Test Song"
    
    def test_search_songs_all_users(self, test_db, test_user, test_user2):
        """Test searching across all users"""
        test_db.add_song("Song 1", "Artist 1", test_user, "Rock", 2020)
        test_db.add_song("Song 2", "Artist 2", test_user2, "Pop", 2021)
        
        # Search without user filter
        results = test_db.search_songs("Song")
        assert len(results) == 2
        
        # Search with user filter
        results = test_db.search_songs("Song", test_user)
        assert len(results) == 1
        assert results[0].title == "Song 1"
