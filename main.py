#!/usr/bin/env python3
"""
Songs API Application
A FastAPI-based REST API for managing songs with MongoDB backend
"""

from fastapi import FastAPI, HTTPException, Query, Path
from fastapi.middleware.cors import CORSMiddleware
from typing import List, Optional
import uvicorn

from src.db.songs_db import SongsDatabase
from src.service.song_service import SongService
from src.api.schemas import (
    SongCreate, SongUpdate, SongResponse, SongSearchResponse, 
    UserStatsResponse, PlaySongResponse, ErrorResponse
)
from src.api.router import songs_router

# Initialize FastAPI app
app = FastAPI(
    title="Songs API",
    description="A REST API for managing songs with MongoDB backend",
    version="1.0.0",
    docs_url="/docs",
    redoc_url="/redoc"
)

# Add CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Configure this properly for production
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Initialize database and service
try:
    db = SongsDatabase()
    song_service = SongService(db)
except Exception as e:
    print(f"Error initializing database: {e}")
    raise

# Set the song service in the router
from src.api.router import set_song_service
set_song_service(song_service)

# Include the songs router
app.include_router(songs_router, prefix="/api/v1", tags=["songs"])

@app.get("/", response_model=dict)
async def root():
    """Root endpoint with API information"""
    return {
        "message": "Songs API",
        "version": "1.0.0",
        "docs": "/docs",
        "redoc": "/redoc"
    }

@app.get("/health", response_model=dict)
async def health_check():
    """Health check endpoint"""
    try:
        # Test database connection
        songs = song_service.get_songs()
        return {
            "status": "healthy",
            "database": "connected",
            "total_songs": len(songs)
        }
    except Exception as e:
        raise HTTPException(status_code=503, detail=f"Service unhealthy: {str(e)}")

if __name__ == "__main__":
    uvicorn.run(
        "main:app",
        host="0.0.0.0",
        port=8000,
        reload=True,
        log_level="info"
    )
