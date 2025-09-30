"""
FastAPI application for Songs CRUD operations
RESTful API for managing songs with MongoDB backend
"""

from fastapi import FastAPI, HTTPException, Query, Path
from fastapi.middleware.cors import CORSMiddleware
from typing import Optional
from datetime import datetime

from src.db.songs_db import SongsDatabase
from src.service.song_service import SongService
from src.schemas import (
    SongCreate,
    SongUpdate,
    SongResponse,
    SongListResponse,
    SearchResponse,
    MessageResponse,
    UserStatsResponse
)

# Initialize FastAPI app
app = FastAPI(
    title="Songs API",
    description="A RESTful API for managing songs with MongoDB backend",
    version="1.0.0"
)

# Add CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Initialize database and service
db = SongsDatabase()
song_service = SongService(db)


@app.on_event("shutdown")
async def shutdown_event():
    """Close database connection on shutdown"""
    db.close()


@app.get("/", response_model=MessageResponse)
async def root():
    """Root endpoint"""
    return {
        "message": "Welcome to Songs API! Visit /docs for API documentation.",
        "success": True
    }


@app.post("/songs", response_model=SongResponse, status_code=201)
async def create_song(song: SongCreate):
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
        id=str(created_song._id),
        title=created_song.title,
        artist=created_song.artist,
        user=created_song.user,
        genre=created_song.genre,
        year=created_song.year,
        created_at=created_song.created_at,
        updated_at=created_song.updated_at
    )


@app.get("/songs", response_model=SongListResponse)
async def list_songs(user: Optional[str] = Query(None, description="Filter songs by user")):
    """List all songs, optionally filtered by user"""
    songs = song_service.get_songs(user=user)
    
    song_responses = [
        SongResponse(
            id=str(song._id),
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


@app.get("/songs/search", response_model=SearchResponse)
async def search_songs(
    query: str = Query(..., min_length=1, description="Search query for title or artist"),
    user: Optional[str] = Query(None, description="Filter by user")
):
    """Search songs by title or artist"""
    result = song_service.search_songs(query, user=user)
    
    if not result["success"]:
        raise HTTPException(status_code=400, detail=result["message"])
    
    song_responses = [
        SongResponse(
            id=str(song._id),
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


@app.get("/songs/{song_id}", response_model=SongResponse)
async def get_song(
    song_id: str = Path(..., description="Song ID"),
    user: str = Query(..., description="Username for authorization")
):
    """Get a specific song by ID"""
    song = song_service.get_song_by_id(song_id, user)
    
    if not song:
        raise HTTPException(
            status_code=404,
            detail="Song not found or you don't have permission to access it"
        )
    
    return SongResponse(
        id=str(song._id),
        title=song.title,
        artist=song.artist,
        user=song.user,
        genre=song.genre,
        year=song.year,
        created_at=song.created_at,
        updated_at=song.updated_at
    )


@app.put("/songs/{song_id}", response_model=MessageResponse)
async def update_song(
    song_id: str,
    song_update: SongUpdate,
    user: str = Query(..., description="Username for authorization")
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


@app.delete("/songs/{song_id}", response_model=MessageResponse)
async def delete_song(
    song_id: str = Path(..., description="Song ID"),
    user: str = Query(..., description="Username for authorization")
):
    """Delete a song"""
    result = song_service.delete_song(song_id, user)
    
    if not result["success"]:
        raise HTTPException(status_code=404, detail=result["message"])
    
    return MessageResponse(message=result["message"], success=True)


@app.post("/songs/{song_id}/play", response_model=MessageResponse)
async def play_song(
    song_id: str = Path(..., description="Song ID"),
    user: str = Query(..., description="Username for authorization")
):
    """Mark a song as played"""
    result = song_service.play_song(song_id, user)
    
    if not result["success"]:
        raise HTTPException(status_code=404, detail=result["message"])
    
    return MessageResponse(message=result["message"], success=True)


@app.get("/users/{user}/stats", response_model=UserStatsResponse)
async def get_user_stats(user: str = Path(..., description="Username")):
    """Get statistics for a user's song collection"""
    stats = song_service.get_user_stats(user)
    
    return UserStatsResponse(
        user=user,
        total_songs=stats["total_songs"],
        genres=stats["genres"],
        years=stats["years"],
        artists=stats["artists"]
    )


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
