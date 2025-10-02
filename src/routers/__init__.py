"""
Routers package for FastAPI application
Contains route handlers organized by resource/model
"""

from .songs import router as songs_router
from .users import router as users_router

__all__ = ['songs_router', 'users_router']

