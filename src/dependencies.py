"""
Dependency injection for FastAPI application
Provides database and service instances for route handlers
"""

from typing import Generator
from src.db.songs_db import SongsDatabase
from src.service.song_service import SongService

# Singleton database instance
_db_instance = None

def get_database() -> SongsDatabase:
    """
    Get or create database instance (singleton pattern)
    This ensures only one database connection is created and reused
    across all requests, avoiding connection overhead.
    Returns:
        SongsDatabase: Singleton database instance
    """
    global _db_instance
    if _db_instance is None:
        _db_instance = SongsDatabase()
    return _db_instance

def get_song_service() -> Generator[SongService, None, None]:
    """
    Dependency injection for SongService
    Provides a SongService instance with database dependency.
    Using generator pattern allows for cleanup if needed in the future.
    Yields:
        SongService: Service instance with database connection
    """
    db = get_database()
    service = SongService(db)
    try:
        yield service
    finally:
        # Cleanup can be added here if needed
        pass
