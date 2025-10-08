"""
Dependency injection for FastAPI application with Beanie ODM
Provides database and service instances for route handlers
"""

from typing import Generator
from src.db.song_db import SongDatabase
from src.db.user_db import UserDatabase
from src.service.song_service import SongService
from src.service.auth_service import AuthService
from src.service.user_service import UserService

# Singleton database instances
_song_db_instance = None
_user_db_instance = None

def get_song_database() -> SongDatabase:
    """
    Get or create Beanie song database instance (singleton pattern)
    This ensures only one database connection is created and reused
    across all requests, avoiding connection overhead.
    Returns:
        SongDatabase: Singleton database instance
    """
    global _song_db_instance
    if _song_db_instance is None:
        _song_db_instance = SongDatabase()
    return _song_db_instance

def get_user_database() -> UserDatabase:
    """
    Get or create Beanie user database instance (singleton pattern)
    Returns:
        UserDatabase: Singleton database instance
    """
    global _user_db_instance
    if _user_db_instance is None:
        _user_db_instance = UserDatabase()
    return _user_db_instance

def get_song_service() -> Generator[SongService, None, None]:
    """
    Dependency injection for SongService with Beanie
    Provides a SongService instance with Beanie database dependency.
    Using generator pattern allows for cleanup if needed in the future.
    Yields:
        SongService: Service instance with Beanie database connection
    """
    db = get_song_database()
    service = SongService(db)
    try:
        yield service
    finally:
        # Cleanup can be added here if needed
        pass

def get_auth_service() -> Generator[AuthService, None, None]:
    """
    Dependency injection for AuthService
    Provides an AuthService instance with UserDatabase dependency.
    """
    user_db = get_user_database()
    service = AuthService(user_db)
    try:
        yield service
    finally:
        # Cleanup can be added here if needed
        pass

def get_user_service() -> Generator[UserService, None, None]:
    """
    Dependency injection for UserService
    Provides a UserService instance with UserDatabase dependency.
    """
    user_db = get_user_database()
    service = UserService(user_db)
    try:
        yield service
    finally:
        # Cleanup can be added here if needed
        pass

# Legacy compatibility - keep old function name for existing code
def get_database() -> SongDatabase:
    """Legacy function name for backward compatibility"""
    return get_song_database()
