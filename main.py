"""
FastAPI application for Songs CRUD operations
RESTful API for managing songs with MongoDB backend
"""

from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.exceptions import RequestValidationError
from fastapi.responses import JSONResponse

from src.routers import song_router, user_router
from src.schemas import MessageResponse

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

# Custom Exception for Invalid Song ID Format
class InvalidSongIdFormatException(Exception):
    """Exception raised when song_id path parameter is not a valid integer"""
    def __init__(self, provided_value: str):
        self.provided_value = provided_value
        self.message = (
            f"Invalid song_id format. Expected an integer, but received '{provided_value}'. "
            f"The song_id path parameter must be a valid integer (e.g., /songs/123). "
            f"Please ensure you're providing a numeric value without quotes or special characters."
        )
        super().__init__(self.message)

# Custom Exception Handler for Song ID Validation Errors
@app.exception_handler(RequestValidationError)
async def song_id_validation_exception_handler(request: Request, exc: RequestValidationError):
    """
    Custom exception handler that provides explicit details when song_id is a string instead of integer.
    This handler intercepts FastAPI's validation errors and provides a more detailed response.
    """
    for error in exc.errors():
        if error.get("loc") == ("path", "song_id") and error.get("type") == "int_parsing":
            invalid_value = error.get("input", "unknown")
            return JSONResponse(
                status_code=422,
                content={
                    "detail": {
                        "error": "Invalid Song ID Format",
                        "message": (
                            f"The song_id path parameter must be a valid integer, "
                            f"but received '{invalid_value}' which is a string."
                        ),
                        "provided_value": str(invalid_value),
                        "expected_type": "integer",
                        "actual_type": "string",
                        "example": "Correct usage: GET /songs/123 (not /songs/abc)",
                        "parameter_location": "path",
                        "parameter_name": "song_id"
                    }
                }
            )
    return JSONResponse(
        status_code=422,
        content={"detail": exc.errors()}
    )

# Include routers
app.include_router(song_router)
app.include_router(user_router)

@app.get("/", response_model=MessageResponse)
async def root():
    """Root endpoint"""
    return {
        "message": "Welcome to Songs API! Visit /docs for API documentation.",
        "success": True
    }

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
