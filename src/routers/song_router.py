"""
Song routes for the FastAPI application
Handles all CRUD operations for songs
"""

from fastapi import APIRouter, HTTPException, Query, Path, Depends
from typing import Optional
from datetime import datetime

from src.dependencies import get_song_service
from src.service.song_service import SongService
from src.schemas import (
    SongCreate,
    SongUpdate,
    SongResponse,
    SongListResponse,
    SearchResponse,
    MessageResponse
)

# Create router
router = APIRouter(
    prefix="/songs",
    tags=["songs"],
    responses={404: {"description": "Not found"}},
)

@router.post("", response_model=SongResponse, status_code=201)
async def create_song(
    song: SongCreate,
    song_service: SongService = Depends(get_song_service)
):
    """Create a new song"""
    # Validate year is not in the future
    if song.year and song.year > datetime.now().year:
        raise HTTPException(
            status_code=400,
            detail=f"Year cannot be in the future (current year: {datetime.now().year})"
        )
    
    result = song_service.add_song(
        title=song.title,
        artist=song.artist,
        user=song.user,
        genre=song.genre,
        year=song.year
    )
    
    if not result["success"]:
        raise HTTPException(status_code=400, detail=result["message"])
    
    # Get the created song
    created_song = song_service.get_songs(user=song.user)[0]
    
    return SongResponse(
        id=str(created_song.id),
        title=created_song.title,
        artist=created_song.artist,
        user=created_song.user,
        genre=created_song.genre,
        year=created_song.year,
        created_at=created_song.created_at,
        updated_at=created_song.updated_at
    )

@router.get("", response_model=SongListResponse)
async def list_songs(
    user: Optional[str] = Query(None, description="Filter songs by user"),
    song_service: SongService = Depends(get_song_service)
):
    """List all songs, optionally filtered by user"""
    songs = song_service.get_songs(user=user)
    
    song_responses = [
        SongResponse(
            id=str(song.id),
            title=song.title,
            artist=song.artist,
            user=song.user,
            genre=song.genre,
            year=song.year,
            created_at=song.created_at,
            updated_at=song.updated_at
        )
        for song in songs
    ]
    
    return SongListResponse(songs=song_responses, count=len(song_responses))

@router.get("/search", response_model=SearchResponse)
async def search_songs(
    query: str = Query(..., min_length=1, description="Search query for title or artist"),
    user: Optional[str] = Query(None, description="Filter by user"),
    song_service: SongService = Depends(get_song_service)
):
    """Search songs by title or artist"""
    result = song_service.search_songs(query, user=user)
    
    if not result["success"]:
        raise HTTPException(status_code=400, detail=result["message"])
    
    song_responses = [
        SongResponse(
            id=str(song.id),
            title=song.title,
            artist=song.artist,
            user=song.user,
            genre=song.genre,
            year=song.year,
            created_at=song.created_at,
            updated_at=song.updated_at
        )
        for song in result["results"]
    ]
    
    return SearchResponse(
        results=song_responses,
        count=len(song_responses),
        message=result["message"]
    )

# This endpoint is being used as an example for int_parsing problems for an example, 
# do not relate it back to the mongoDB
@router.get("/{song_id}", response_model=SongResponse)
async def get_song(
    song_id: int = Path(..., description="Song ID"),
    user: str = Query(..., description="Username for authorization"),
    song_service: SongService = Depends(get_song_service)
):
    """Get a specific song by ID"""
    song = song_service.get_song_by_id(song_id, user)
    
    if not song:
        raise HTTPException(
            status_code=404,
            detail="Song not found or you don't have permission to access it"
        )
    
    return SongResponse(
        id=str(song.id),
        title=song.title,
        artist=song.artist,
        user=song.user,
        genre=song.genre,
        year=song.year,
        created_at=song.created_at,
        updated_at=song.updated_at
    )

@router.put("/{song_id}", response_model=MessageResponse)
async def update_song(
    song_update: SongUpdate,
    song_id: str = Path(..., description="Song ID"),
    user: str = Query(..., description="Username for authorization"),
    song_service: SongService = Depends(get_song_service)
):
    """Update a song"""
    # Validate year is not in the future
    if song_update.year and song_update.year > datetime.now().year:
        raise HTTPException(
            status_code=400,
            detail=f"Year cannot be in the future (current year: {datetime.now().year})"
        )
    
    # Filter out None values
    updates = song_update.model_dump(exclude_none=True)
    
    if not updates:
        raise HTTPException(status_code=400, detail="No updates provided")
    
    result = song_service.update_song(song_id, user, **updates)
    
    if not result["success"]:
        raise HTTPException(status_code=400, detail=result["message"])
    
    return MessageResponse(message=result["message"], success=True)

@router.delete("/{song_id}", response_model=MessageResponse)
async def delete_song(
    song_id: str = Path(..., description="Song ID"),
    user: str = Query(..., description="Username for authorization"),
    song_service: SongService = Depends(get_song_service)
):
    """Delete a song"""
    result = song_service.delete_song(song_id, user)
    
    if not result["success"]:
        raise HTTPException(status_code=404, detail=result["message"])
    
    return MessageResponse(message=result["message"], success=True)

@router.post("/{song_id}/play", response_model=MessageResponse)
async def play_song(
    song_id: str = Path(..., description="Song ID"),
    user: str = Query(..., description="Username for authorization"),
    song_service: SongService = Depends(get_song_service)
):
    """Mark a song as played"""
    result = song_service.play_song(song_id, user)
    
    if not result["success"]:
        raise HTTPException(status_code=404, detail=result["message"])
    
    return MessageResponse(message=result["message"], success=True)
