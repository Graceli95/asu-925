"""
FastAPI application for Songs CRUD operations
RESTful API for managing songs with MongoDB backend
"""

from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.exceptions import RequestValidationError
from fastapi.responses import JSONResponse
from fastapi.security import HTTPBearer

from src.routers import song_router, user_router, auth_router
from src.schemas import MessageResponse
from src.middleware import RequestLoggingMiddleware, CORSSecurityMiddleware

# Initialize FastAPI app
app = FastAPI(
    title="Songs API",
    description="A RESTful API for managing songs with MongoDB backend",
    version="1.0.0",
    # Add OpenAPI security configuration
    openapi_tags=[
        {
            "name": "authentication",
            "description": "User authentication and JWT token management"
        },
        {
            "name": "songs", 
            "description": "Song CRUD operations (requires authentication)"
        },
        {
            "name": "users",
            "description": "User management operations (requires authentication)"
        }
    ]
)

# Add CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Add custom middleware (order matters - last added is first executed)
app.add_middleware(CORSSecurityMiddleware)
app.add_middleware(RequestLoggingMiddleware)

# Add security configuration for Swagger UI
# Define the security scheme
security_scheme = {
    "type": "http",
    "scheme": "bearer",
    "bearerFormat": "JWT",
    "description": "Enter JWT token obtained from /auth/login endpoint"
}

# Add security scheme to OpenAPI
from fastapi.openapi.utils import get_openapi

def custom_openapi():
    if app.openapi_schema:
        return app.openapi_schema
    
    openapi_schema = get_openapi(
        title=app.title,
        version=app.version,
        description=app.description,
        routes=app.routes,
        tags=app.openapi_tags
    )
    
    openapi_schema["components"]["securitySchemes"] = {
        "bearerAuth": security_scheme
    }
    
    # Add security requirements to protected endpoints
    for path in openapi_schema["paths"]:
        if any(protected in path for protected in ["/songs", "/users", "/auth/me"]):
            for method in openapi_schema["paths"][path]:
                if method in ["get", "post", "put", "delete"]:
                    openapi_schema["paths"][path][method]["security"] = [{"bearerAuth": []}]
    
    app.openapi_schema = openapi_schema
    return app.openapi_schema

app.openapi = custom_openapi

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

@app.exception_handler(RequestValidationError)
async def validation_exception_handler(request: Request, exc: RequestValidationError):
    """Handle validation errors with proper JSON serialization"""
    return JSONResponse(
        status_code=422,
        content={
            "detail": [
                {
                    "loc": list(error.get("loc", [])), 
                    "msg": error.get("msg", ""), 
                    "type": error.get("type", "")
                } 
                for error in exc.errors()
            ]
        }
    )

# Include routers
app.include_router(auth_router)
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
