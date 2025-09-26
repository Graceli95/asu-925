"""
Shared test fixtures and configuration for the Songs CLI test suite
"""

import os
import sys
import pytest
from dotenv import load_dotenv
from pymongo.errors import ServerSelectionTimeoutError

# Add the parent directory to Python path to import our modules
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from db.songs_db import SongsDatabase
from service import SongService

# Load environment variables
load_dotenv()


@pytest.fixture(scope="function")
def test_db():
    """Fixture that provides a clean test database for each test"""
    # Set test database URL and name
    test_db_url = os.getenv('project_db_url', 'mongodb://localhost:27017/songs_test')
    test_db_name = os.getenv('project_db_name', 'songs_test')
    os.environ['project_db_url'] = test_db_url
    os.environ['project_db_name'] = test_db_name
    
    # Initialize test database
    try:
        db = SongsDatabase()
        
        # Clear ALL test data to ensure clean state
        db.songs.delete_many({})
        
        yield db
        
        # Clean up ALL test data after test
        db.songs.delete_many({})
        
    except ServerSelectionTimeoutError:
        pytest.skip("MongoDB not available for testing")


@pytest.fixture
def test_user():
    """Fixture that provides a test user"""
    return "test_user"


@pytest.fixture
def test_user2():
    """Fixture that provides a second test user"""
    return "test_user2"


@pytest.fixture
def sample_song_data():
    """Fixture that provides sample song data for testing"""
    return {
        "title": "Test Song",
        "artist": "Test Artist",
        "genre": "Rock",
        "year": 2023
    }


@pytest.fixture
def multiple_songs_data():
    """Fixture that provides multiple songs data for testing"""
    return [
        ("Song 1", "Artist 1", "Rock", 2020),
        ("Song 2", "Artist 2", "Pop", 2021),
        ("Song 3", "Artist 3", "Jazz", 2022)
    ]


@pytest.fixture
def song_service(test_db):
    """Fixture that provides a SongService instance"""
    return SongService(test_db)
