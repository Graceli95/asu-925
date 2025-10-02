"""
Routers package for FastAPI application
Contains route handlers organized by resource/model
"""

from .song_router import router as song_router
from .user_router import router as user_router

__all__ = ['song_router', 'user_router']

