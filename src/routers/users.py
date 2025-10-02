"""
User routes for the FastAPI application
Handles all CRUD operations for users
"""

from fastapi import APIRouter, HTTPException, Query, Path
from typing import Optional

from src.db.songs_db import SongsDatabase
from src.service.song_service import SongService
from src.schemas import MessageResponse, UserStatsResponse

# Create router
router = APIRouter(
    prefix="/users",
    tags=["users"],
    responses={404: {"description": "Not found"}},
)

# Initialize database and service (temporary - using songs service for stats)
db = SongsDatabase()
song_service = SongService(db)

# TODO: Initialize database and service for users when implemented
# from src.db.users_db import UsersDatabase
# from src.service.user_service import UserService
# user_db = UsersDatabase()
# user_service = UserService(user_db)


@router.get("/{username}/stats", response_model=UserStatsResponse)
async def get_user_stats(username: str = Path(..., description="Username")):
    """Get statistics for a user's song collection"""
    stats = song_service.get_user_stats(username)
    
    return UserStatsResponse(
        user=username,
        total_songs=stats["total_songs"],
        genres=stats["genres"],
        years=stats["years"],
        artists=stats["artists"]
    )


@router.get("/{user_id}", response_model=MessageResponse)
async def get_user(user_id: str = Path(..., description="User ID")):
    """Get a specific user by ID (placeholder)"""
    # TODO: Implement user retrieval logic
    return MessageResponse(
        message="User endpoints coming soon!",
        success=True
    )


# Add more user endpoints here as needed:
# - POST /users (create user)
# - GET /users (list users)
# - PUT /users/{user_id} (update user)
# - DELETE /users/{user_id} (delete user)
# - POST /users/{user_id}/login (user login)
# - etc.

