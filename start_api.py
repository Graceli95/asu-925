#!/usr/bin/env python3
"""
Script to start the FastAPI server
"""

import uvicorn

if __name__ == "__main__":
    print("🚀 Starting Songs API...")
    print("📖 API Documentation: http://localhost:8000/docs")
    print("📚 Alternative Documentation: http://localhost:8000/redoc")
    print("\nPress CTRL+C to stop the server\n")
    
    uvicorn.run(
        "main:app",
        host="0.0.0.0",
        port=8000,
        reload=True
    )
