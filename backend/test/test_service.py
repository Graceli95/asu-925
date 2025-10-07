"""
Tests for the song service layer
"""

import pytest
from datetime import datetime
from model import Song


class TestSongService:
    """Test the song service layer"""
    
    def test_add_song_success(self, song_service, test_user):
        """Test adding a song through the service layer"""
        result = song_service.add_song("Test Song", "Test Artist", test_user, "Rock", 2023)
        
        assert result["success"] is True
        assert "Test Song" in result["message"]
        assert "Test Artist" in result["message"]
    
    def test_add_song_validation_empty_title(self, song_service, test_user):
        """Test that service validates empty title"""
        result = song_service.add_song("", "Test Artist", test_user)
        
        assert result["success"] is False
        assert "Title cannot be empty" in result["message"]
    
    def test_add_song_validation_empty_artist(self, song_service, test_user):
        """Test that service validates empty artist"""
        result = song_service.add_song("Test Song", "", test_user)
        
        assert result["success"] is False
        assert "Artist cannot be empty" in result["message"]
    
    def test_add_song_validation_future_year(self, song_service, test_user):
        """Test that service validates future years"""
        future_year = datetime.now().year + 1
        result = song_service.add_song("Test Song", "Test Artist", test_user, "Rock", future_year)
        
        assert result["success"] is False
        assert "Year cannot be in the future" in result["message"]
    
    def test_search_songs_empty_query(self, song_service, test_user):
        """Test that service validates empty search query"""
        result = song_service.search_songs("", test_user)
        
        assert result["success"] is False
        assert "Search query cannot be empty" in result["message"]
    
    def test_get_user_stats_empty(self, song_service, test_user):
        """Test user stats with no songs"""
        stats = song_service.get_user_stats(test_user)
        
        assert stats["total_songs"] == 0
        assert stats["genres"] == {}
        assert stats["years"] == {}
        assert stats["artists"] == {}
    
    def test_get_user_stats_with_songs(self, song_service, test_user):
        """Test user stats with songs"""
        # Add some test songs
        song_service.add_song("Song 1", "Artist A", test_user, "Rock", 2020)
        song_service.add_song("Song 2", "Artist A", test_user, "Pop", 2021)
        song_service.add_song("Song 3", "Artist B", test_user, "Rock", 2020)
        
        stats = song_service.get_user_stats(test_user)
        
        assert stats["total_songs"] == 3
        assert stats["genres"]["Rock"] == 2
        assert stats["genres"]["Pop"] == 1
        assert stats["artists"]["Artist A"] == 2
        assert stats["artists"]["Artist B"] == 1
        assert stats["years"][2020] == 2
        assert stats["years"][2021] == 1
    
    def test_add_song_validation_past_years_allowed(self, song_service, test_user):
        """Test that past years are allowed including very old years"""
        # Test various past years including very old ones
        test_years = [1800, 1900, 1950, 2000, datetime.now().year]
        
        for year in test_years:
            result = song_service.add_song(f"Song {year}", "Test Artist", test_user, "Rock", year)
            assert result["success"] is True, f"Year {year} should be valid"
    
    def test_update_song_validation_future_year(self, song_service, test_user):
        """Test that service validates future years in updates"""
        # First add a song
        song_service.add_song("Test Song", "Test Artist", test_user, "Rock", 2020)
        songs = song_service.get_songs(test_user)
        song_id = str(songs[0]._id)
        
        # Try to update with future year
        future_year = datetime.now().year + 1
        result = song_service.update_song(song_id, test_user, year=future_year)
        
        assert result["success"] is False
        assert "Year cannot be in the future" in result["message"]
    
    def test_add_song_creates_file(self, song_service, test_user):
        """Test that adding a song creates a file in the assets folder"""
        import os
        
        result = song_service.add_song("File Test Song", "File Test Artist", test_user, "Rock", 2020)
        
        assert result["success"] is True
        assert "saved to assets folder" in result["message"]
        
        # Check that file was created
        expected_filename = "File Test Artist - File Test Song.txt"
        filepath = os.path.join("assets", expected_filename)
        assert os.path.exists(filepath)
        
        # Check file contents
        with open(filepath, 'r', encoding='utf-8') as f:
            content = f.read()
            
        assert "Title: File Test Song" in content
        assert "Artist: File Test Artist" in content
        assert "User: " + test_user in content
        assert "Genre: Rock" in content
        assert "Year: 2020" in content
        assert "Added: " in content
        
        # Clean up test file
        if os.path.exists(filepath):
            os.remove(filepath)
    
    def test_filename_sanitization(self, song_service, test_user):
        """Test that filenames with special characters are sanitized"""
        import os
        
        result = song_service.add_song("Song/With*Special?Chars", "Artist:With|Bad\\Chars", test_user)
        
        assert result["success"] is True
        assert "saved to assets folder" in result["message"]
        
        # Check that sanitized file was created
        expected_filename = "Artist_With_Bad_Chars - Song_With_Special_Chars.txt"
        filepath = os.path.join("assets", expected_filename)
        assert os.path.exists(filepath)
        
        # Check file contents preserve original characters
        with open(filepath, 'r', encoding='utf-8') as f:
            content = f.read()
            
        assert "Title: Song/With*Special?Chars" in content
        assert "Artist: Artist:With|Bad\\Chars" in content
        
        # Clean up test file
        if os.path.exists(filepath):
            os.remove(filepath)
    
    def test_rollback_on_file_creation_failure(self, song_service, test_user, monkeypatch):
        """Test that database record is rolled back if file creation fails"""
        # Mock the file handler's create_song_file method to always fail
        def mock_create_song_file(song):
            return False
        
        monkeypatch.setattr(song_service.file_handler, 'create_song_file', mock_create_song_file)
        
        # Try to add a song (should fail due to file creation failure)
        result = song_service.add_song("Rollback Test Song", "Rollback Artist", test_user)
        
        assert result["success"] is False
        assert "rolled back" in result["message"]
        
        # Verify no song was left in the database
        songs = song_service.get_songs(test_user)
        assert len(songs) == 0
    
    def test_delete_song_removes_file(self, song_service, test_user):
        """Test that deleting a song also removes its file"""
        import os
        
        # Add a song first
        result = song_service.add_song("Delete Test Song", "Delete Artist", test_user, "Rock", 2020)
        assert result["success"] is True
        
        # Verify file was created
        expected_filename = "Delete Artist - Delete Test Song.txt"
        filepath = os.path.join("assets", expected_filename)
        assert os.path.exists(filepath)
        
        # Get the song ID
        songs = song_service.get_songs(test_user)
        assert len(songs) == 1
        song_id = str(songs[0]._id)
        
        # Delete the song
        delete_result = song_service.delete_song(song_id, test_user)
        assert delete_result["success"] is True
        
        # Verify file was also deleted
        assert not os.path.exists(filepath)
        
        # Verify song was removed from database
        songs = song_service.get_songs(test_user)
        assert len(songs) == 0
