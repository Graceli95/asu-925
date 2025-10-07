"""
Middleware for JWT authentication and request processing
"""

from fastapi import Request, HTTPException, status
from fastapi.responses import JSONResponse
from starlette.middleware.base import BaseHTTPMiddleware
from starlette.types import ASGIApp
import time
import logging

from src.auth import verify_token

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class JWTAuthMiddleware(BaseHTTPMiddleware):
    """
    Middleware to handle JWT authentication for protected routes
    """
    
    def __init__(self, app: ASGIApp, protected_paths: list = None):
        super().__init__(app)
        # Define paths that require authentication
        self.protected_paths = protected_paths or [
            "/songs",
            "/users",
            "/auth/me"
        ]
        # Define paths that should be excluded from auth (public endpoints)
        self.excluded_paths = [
            "/",
            "/docs",
            "/redoc",
            "/openapi.json",
            "/auth/register",
            "/auth/login",
            "/auth/login-form"
        ]
    
    async def dispatch(self, request: Request, call_next):
        """
        Process request and check JWT authentication for protected routes
        """
        start_time = time.time()
        
        # Get the request path
        path = request.url.path
        
        # Skip authentication for excluded paths
        if any(path.startswith(excluded) for excluded in self.excluded_paths):
            response = await call_next(request)
            return response
        
        # Check if the path requires authentication
        requires_auth = any(path.startswith(protected) for protected in self.protected_paths)
        
        if requires_auth:
            # Extract token from Authorization header
            authorization = request.headers.get("Authorization")
            
            if not authorization:
                return JSONResponse(
                    status_code=status.HTTP_401_UNAUTHORIZED,
                    content={
                        "detail": "Authorization header missing",
                        "error": "authentication_required"
                    },
                    headers={"WWW-Authenticate": "Bearer"}
                )
            
            # Check if it's a Bearer token
            if not authorization.startswith("Bearer "):
                return JSONResponse(
                    status_code=status.HTTP_401_UNAUTHORIZED,
                    content={
                        "detail": "Invalid authorization header format. Expected 'Bearer <token>'",
                        "error": "invalid_auth_format"
                    },
                    headers={"WWW-Authenticate": "Bearer"}
                )
            
            # Extract the token
            token = authorization.split(" ")[1]
            
            try:
                # Verify the token
                token_data = verify_token(token)
                
                # Add user information to request state for use in route handlers
                request.state.current_user = token_data
                request.state.user_id = token_data.user_id
                request.state.username = token_data.username
                
                logger.info(f"Authenticated user: {token_data.username} for path: {path}")
                
            except HTTPException as e:
                return JSONResponse(
                    status_code=e.status_code,
                    content={
                        "detail": e.detail,
                        "error": "invalid_token"
                    },
                    headers={"WWW-Authenticate": "Bearer"}
                )
            except Exception as e:
                logger.error(f"Unexpected error during token verification: {str(e)}")
                return JSONResponse(
                    status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                    content={
                        "detail": "Internal server error during authentication",
                        "error": "auth_error"
                    }
                )
        
        # Process the request
        response = await call_next(request)
        
        # Add processing time to response headers
        process_time = time.time() - start_time
        response.headers["X-Process-Time"] = str(process_time)
        
        return response


class RequestLoggingMiddleware(BaseHTTPMiddleware):
    """
    Middleware to log all incoming requests
    """
    
    async def dispatch(self, request: Request, call_next):
        start_time = time.time()
        
        # Log the incoming request
        logger.info(f"Incoming request: {request.method} {request.url.path}")
        
        # Process the request
        response = await call_next(request)
        
        # Calculate processing time
        process_time = time.time() - start_time
        
        # Log the response
        logger.info(
            f"Response: {response.status_code} for {request.method} {request.url.path} "
            f"(took {process_time:.4f}s)"
        )
        
        return response


class CORSSecurityMiddleware(BaseHTTPMiddleware):
    """
    Enhanced CORS middleware with security headers
    """
    
    async def dispatch(self, request: Request, call_next):
        response = await call_next(request)
        
        # Add security headers
        response.headers["X-Content-Type-Options"] = "nosniff"
        response.headers["X-Frame-Options"] = "DENY"
        response.headers["X-XSS-Protection"] = "1; mode=block"
        response.headers["Referrer-Policy"] = "strict-origin-when-cross-origin"
        
        return response
