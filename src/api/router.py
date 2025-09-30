"""
FastAPI router for songs endpoints
Handles all HTTP routes for song CRUD operations
"""

from fastapi import APIRouter, HTTPException, Query, Path, status
from typing import List, Optional
from datetime import datetime

from src.service.song_service import SongService
from src.api.schemas import (
    SongCreate, SongUpdate, SongResponse, SongSearchResponse,
    UserStatsResponse, PlaySongResponse, SuccessResponse, ErrorResponse
)

# Create router
songs_router = APIRouter()

# This will be injected by the main app
song_service: Optional[SongService] = None

def set_song_service(service: SongService):
    """Set the song service instance"""
    global song_service
    song_service = service


@songs_router.post("/songs", response_model=SongResponse, status_code=status.HTTP_201_CREATED)
async def create_song(song_data: SongCreate):
    """
    Create a new song
    
    - **title**: Song title (required)
    - **artist**: Artist name (required)
    - **user**: Username (required)
    - **genre**: Song genre (optional)
    - **year**: Release year (optional)
    """
    if not song_service:
        raise HTTPException(status_code=500, detail="Service not initialized")
    
    result = song_service.add_song(
        title=song_data.title,
        artist=song_data.artist,
        user=song_data.user,
        genre=song_data.genre,
        year=song_data.year
    )
    
    if not result["success"]:
        raise HTTPException(status_code=400, detail=result["message"])
    
    # Get the created song to return
    songs = song_service.get_songs(song_data.user)
    if songs:
        # Find the most recently created song (should be the one we just added)
        latest_song = max(songs, key=lambda s: s.created_at)
        return SongResponse.from_orm(latest_song)
    
    raise HTTPException(status_code=500, detail="Song created but could not be retrieved")


@songs_router.get("/songs", response_model=List[SongResponse])
async def get_songs(
    user: Optional[str] = Query(None, description="Filter by username"),
    limit: Optional[int] = Query(None, ge=1, le=1000, description="Limit number of results"),
    offset: Optional[int] = Query(0, ge=0, description="Number of results to skip")
):
    """
    Get all songs, optionally filtered by user
    
    - **user**: Filter songs by username (optional)
    - **limit**: Maximum number of songs to return (optional, max 1000)
    - **offset**: Number of songs to skip (optional, for pagination)
    """
    if not song_service:
        raise HTTPException(status_code=500, detail="Service not initialized")
    
    songs = song_service.get_songs(user)
    
    # Apply pagination
    if offset:
        songs = songs[offset:]
    if limit:
        songs = songs[:limit]
    
    return [SongResponse.from_orm(song) for song in songs]


@songs_router.get("/songs/{song_id}", response_model=SongResponse)
async def get_song(
    song_id: str = Path(..., description="Song ID"),
    user: str = Query(..., description="Username")
):
    """
    Get a specific song by ID
    
    - **song_id**: The song's unique identifier
    - **user**: Username (required for authorization)
    """
    if not song_service:
        raise HTTPException(status_code=500, detail="Service not initialized")
    
    song = song_service.get_song_by_id(song_id, user)
    if not song:
        raise HTTPException(status_code=404, detail="Song not found")
    
    return SongResponse.from_orm(song)


@songs_router.put("/songs/{song_id}", response_model=SongResponse)
async def update_song(
    song_id: str = Path(..., description="Song ID"),
    user: str = Query(..., description="Username"),
    song_data: SongUpdate = None
):
    """
    Update a song
    
    - **song_id**: The song's unique identifier
    - **user**: Username (required for authorization)
    - **song_data**: Updated song data (only provided fields will be updated)
    """
    if not song_service:
        raise HTTPException(status_code=500, detail="Service not initialized")
    
    if not song_data:
        raise HTTPException(status_code=400, detail="No update data provided")
    
    # Convert Pydantic model to dict, excluding None values
    updates = {k: v for k, v in song_data.dict().items() if v is not None}
    
    if not updates:
        raise HTTPException(status_code=400, detail="No valid fields to update")
    
    result = song_service.update_song(song_id, user, **updates)
    
    if not result["success"]:
        raise HTTPException(status_code=400, detail=result["message"])
    
    # Get the updated song
    updated_song = song_service.get_song_by_id(song_id, user)
    if not updated_song:
        raise HTTPException(status_code=404, detail="Song not found after update")
    
    return SongResponse.from_orm(updated_song)


@songs_router.delete("/songs/{song_id}", response_model=SuccessResponse)
async def delete_song(
    song_id: str = Path(..., description="Song ID"),
    user: str = Query(..., description="Username")
):
    """
    Delete a song
    
    - **song_id**: The song's unique identifier
    - **user**: Username (required for authorization)
    """
    if not song_service:
        raise HTTPException(status_code=500, detail="Service not initialized")
    
    result = song_service.delete_song(song_id, user)
    
    if not result["success"]:
        raise HTTPException(status_code=404, detail=result["message"])
    
    return SuccessResponse(message=result["message"])


@songs_router.get("/songs/search", response_model=SongSearchResponse)
async def search_songs(
    q: str = Query(..., min_length=1, description="Search query"),
    user: Optional[str] = Query(None, description="Filter by username"),
    limit: Optional[int] = Query(None, ge=1, le=1000, description="Limit number of results")
):
    """
    Search songs by title or artist
    
    - **q**: Search query (searches in title and artist fields)
    - **user**: Filter by username (optional)
    - **limit**: Maximum number of results to return (optional, max 1000)
    """
    if not song_service:
        raise HTTPException(status_code=500, detail="Service not initialized")
    
    result = song_service.search_songs(q, user)
    
    if not result["success"]:
        raise HTTPException(status_code=400, detail=result["message"])
    
    songs = result["results"]
    
    # Apply limit
    if limit and len(songs) > limit:
        songs = songs[:limit]
    
    return SongSearchResponse(
        success=True,
        results=[SongResponse.from_orm(song) for song in songs],
        message=result["message"],
        total_count=len(songs)
    )


@songs_router.post("/songs/{song_id}/play", response_model=PlaySongResponse)
async def play_song(
    song_id: str = Path(..., description="Song ID"),
    user: str = Query(..., description="Username")
):
    """
    Mark a song as played
    
    - **song_id**: The song's unique identifier
    - **user**: Username (required for authorization)
    """
    if not song_service:
        raise HTTPException(status_code=500, detail="Service not initialized")
    
    result = song_service.play_song(song_id, user)
    
    if not result["success"]:
        raise HTTPException(status_code=404, detail=result["message"])
    
    return PlaySongResponse(
        success=True,
        message=result["message"],
        song=SongResponse.from_orm(result["song"]) if "song" in result else None
    )


@songs_router.get("/users/{username}/stats", response_model=UserStatsResponse)
async def get_user_stats(
    username: str = Path(..., description="Username")
):
    """
    Get statistics for a user's song collection
    
    - **username**: The username to get statistics for
    """
    if not song_service:
        raise HTTPException(status_code=500, detail="Service not initialized")
    
    stats = song_service.get_user_stats(username)
    
    return UserStatsResponse(**stats)
