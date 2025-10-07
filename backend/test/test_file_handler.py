"""
Tests for the file handler module
"""

import os
import pytest
import tempfile
from datetime import datetime
from bson import ObjectId
from service.file_handler import SongFileHandler
from model import Song


class TestSongFileHandler:
    """Test the song file handler"""
    
    @pytest.fixture
    def temp_assets_dir(self):
        """Create a temporary assets directory for testing"""
        with tempfile.TemporaryDirectory() as temp_dir:
            yield temp_dir
    
    @pytest.fixture
    def file_handler(self, temp_assets_dir):
        """Create a file handler with temporary directory"""
        return SongFileHandler(temp_assets_dir)
    
    @pytest.fixture
    def sample_song(self):
        """Create a sample song for testing"""
        return Song(
            title="Test Song",
            artist="Test Artist",
            user="TestUser",
            genre="Rock",
            year=2020,
            created_at=datetime(2023, 1, 1, 12, 0, 0),
            _id=ObjectId()
        )
    
    def test_assets_directory_creation(self, temp_assets_dir):
        """Test that assets directory is created if it doesn't exist"""
        assets_path = os.path.join(temp_assets_dir, "new_assets")
        assert not os.path.exists(assets_path)
        
        # Create file handler with non-existent directory
        handler = SongFileHandler(assets_path)
        
        # Directory should now exist
        assert os.path.exists(assets_path)
    
    def test_filename_sanitization(self, file_handler):
        """Test filename sanitization removes invalid characters"""
        test_cases = [
            ("normal filename", "normal filename"),
            ("file/with\\bad:chars", "file_with_bad_chars"),
            ("file*with?special|chars", "file_with_special_chars"),
            ("file<with>quotes\"", "file_with_quotes"),
            ("   leading_trailing___   ", "leading_trailing"),
            ("multiple___underscores", "multiple_underscores")
        ]
        
        for input_filename, expected in test_cases:
            result = file_handler._sanitize_filename(input_filename)
            assert result == expected
    
    def test_create_song_file_success(self, file_handler, sample_song, temp_assets_dir):
        """Test successful file creation"""
        result = file_handler.create_song_file(sample_song)
        assert result is True
        
        # Verify file exists
        expected_path = os.path.join(temp_assets_dir, "Test Artist - Test Song.txt")
        assert os.path.exists(expected_path)
        
        # Verify file contents
        with open(expected_path, 'r', encoding='utf-8') as f:
            content = f.read()
        
        assert "Title: Test Song" in content
        assert "Artist: Test Artist" in content
        assert "User: TestUser" in content
        assert "Genre: Rock" in content
        assert "Year: 2020" in content
        assert "Added: 2023-01-01 12:00:00" in content
    
    def test_create_song_file_with_special_characters(self, file_handler, temp_assets_dir):
        """Test file creation with special characters in song data"""
        song = Song(
            title="Song/With*Special?Chars",
            artist="Artist:With|Bad\\Chars",
            user="TestUser",
            genre="Pop",
            year=2021,
            created_at=datetime.now(),
            _id=ObjectId()
        )
        
        result = file_handler.create_song_file(song)
        assert result is True
        
        # File should be created with sanitized name
        expected_path = os.path.join(temp_assets_dir, "Artist_With_Bad_Chars - Song_With_Special_Chars.txt")
        assert os.path.exists(expected_path)
        
        # But content should preserve original characters
        with open(expected_path, 'r', encoding='utf-8') as f:
            content = f.read()
        
        assert "Title: Song/With*Special?Chars" in content
        assert "Artist: Artist:With|Bad\\Chars" in content
    
    def test_get_file_path(self, file_handler, sample_song, temp_assets_dir):
        """Test getting the expected file path for a song"""
        expected_path = os.path.join(temp_assets_dir, "Test Artist - Test Song.txt")
        actual_path = file_handler.get_file_path(sample_song)
        assert actual_path == expected_path
    
    def test_delete_song_file_existing(self, file_handler, sample_song, temp_assets_dir):
        """Test deleting an existing song file"""
        # Create the file first
        file_handler.create_song_file(sample_song)
        file_path = file_handler.get_file_path(sample_song)
        assert os.path.exists(file_path)
        
        # Delete the file
        result = file_handler.delete_song_file(sample_song)
        assert result is True
        assert not os.path.exists(file_path)
    
    def test_delete_song_file_nonexistent(self, file_handler, sample_song):
        """Test deleting a non-existent song file (should succeed)"""
        file_path = file_handler.get_file_path(sample_song)
        assert not os.path.exists(file_path)
        
        # Should succeed even if file doesn't exist
        result = file_handler.delete_song_file(sample_song)
        assert result is True
    
    def test_format_song_content_complete(self, file_handler):
        """Test formatting content for a song with all fields"""
        song = Song(
            title="Complete Song",
            artist="Complete Artist",
            user="CompleteUser",
            genre="Jazz",
            year=2022,
            created_at=datetime(2023, 1, 15, 10, 30, 0),
            updated_at=datetime(2023, 1, 16, 11, 30, 0),
            _id=ObjectId("507f1f77bcf86cd799439011")
        )
        
        content = file_handler._format_song_content(song)
        
        expected_lines = [
            "Song Information",
            "================",
            "Title: Complete Song",
            "Artist: Complete Artist",
            "User: CompleteUser",
            "Genre: Jazz",
            "Year: 2022",
            "Added: 2023-01-15 10:30:00",
            "Last Updated: 2023-01-16 11:30:00",
            "Database ID: 507f1f77bcf86cd799439011"
        ]
        
        for line in expected_lines:
            assert line in content
    
    def test_format_song_content_minimal(self, file_handler):
        """Test formatting content for a song with minimal fields"""
        song = Song(
            title="Minimal Song",
            artist="Minimal Artist",
            user="MinimalUser",
            created_at=datetime(2023, 1, 15, 10, 30, 0)
        )
        
        content = file_handler._format_song_content(song)
        
        assert "Title: Minimal Song" in content
        assert "Artist: Minimal Artist" in content
        assert "User: MinimalUser" in content
        assert "Genre: Not specified" in content
        assert "Year: Not specified" in content
        assert "Added: 2023-01-15 10:30:00" in content
        assert "Last Updated:" not in content  # Should not be present
