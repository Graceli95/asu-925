"""
Service package for Songs CLI application
Contains business logic and service classes
"""

from .song_service import SongService
from .auth_service import AuthService
from .user_service import UserService

__all__ = ['SongService', 'AuthService', 'UserService']
