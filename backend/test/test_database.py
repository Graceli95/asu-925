"""
Tests for database connection and basic functionality
"""

import pytest
from bson import ObjectId


class TestDatabaseConnection:
    """Test database connection and setup"""
    
    def test_database_connection(self, test_db):
        """Test that database connection works"""
        assert test_db.client is not None
        assert test_db.db is not None
        assert test_db.songs is not None
    
    def test_database_indexes(self, test_db):
        """Test that database indexes are created"""
        # This test verifies that indexes exist (they should be created in setUp)
        # We can verify by checking if queries are fast or by checking index info
        indexes = test_db.songs.list_indexes()
        index_names = [index['name'] for index in indexes]
        
        # Check that our custom indexes exist
        assert 'title_1' in index_names
        assert 'artist_1' in index_names
        assert 'user_1' in index_names
