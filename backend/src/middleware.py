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
            "/auth/login-form",
            "/auth/refresh"
        ]
    
    async def dispatch(self, request: Request, call_next):
        """
        Process request and check JWT authentication for protected routes
        """
        start_time = time.time()
        
        # Get the request path
        path = request.url.path
        method = request.method
        
        print(f"JWTAuthMiddleware: Processing {method} request for {path}")
        
        # Skip authentication for OPTIONS requests (CORS preflight)
        if method == "OPTIONS":
            print(f"JWTAuthMiddleware: Skipping auth for OPTIONS request")
            response = await call_next(request)
            return response
        
        # Skip authentication for excluded paths (exact match only)
        is_excluded = path in self.excluded_paths
        print(f"JWTAuthMiddleware: Path {path} is excluded: {is_excluded}")
        print(f"JWTAuthMiddleware: Excluded paths: {self.excluded_paths}")
        
        if is_excluded:
            print(f"JWTAuthMiddleware: Skipping auth for {path}")
            response = await call_next(request)
            return response
        
        # Check if the path requires authentication
        requires_auth = any(path.startswith(protected) for protected in self.protected_paths)
        
        print(f"JWTAuthMiddleware: Path {path} requires auth: {requires_auth}")
        print(f"JWTAuthMiddleware: Protected paths: {self.protected_paths}")
        
        if requires_auth:
            print(f"JWTAuthMiddleware: Starting authentication for {path}")
            # Extract token from Authorization header or cookies
            authorization = request.headers.get("Authorization")
            token = None
            
            if authorization:
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
                
                # Extract the token from header
                token = authorization.split(" ")[1]
            else:
                # Try to get token from HTTP-only cookie
                print(f"Middleware: No Authorization header, checking cookies...")
                print(f"Middleware: Available cookies: {list(request.cookies.keys())}")
                token = request.cookies.get("access_token")
                print(f"Middleware: access_token cookie value: {token[:20] if token else 'None'}...")
            
            if not token:
                print(f"Middleware: No token found for {path}")
                print(f"Middleware: Authorization header: {authorization}")
                print(f"Middleware: Cookies: {request.cookies}")
                return JSONResponse(
                    status_code=status.HTTP_401_UNAUTHORIZED,
                    content={
                        "detail": "Authorization token missing",
                        "error": "authentication_required"
                    },
                    headers={"WWW-Authenticate": "Bearer"}
                )
            
            print(f"Middleware: Found token for {path}: {token[:20]}...")
            
            try:
                # Verify the token
                print(f"Middleware: Verifying token: {token[:20]}...")
                token_data = verify_token(token)
                print(f"Middleware: Token verification successful: {token_data}")
                
                # Add user information to request state for use in route handlers
                request.state.current_user = token_data
                request.state.user_id = token_data.user_id
                request.state.username = token_data.username
                
                logger.info(f"Authenticated user: {token_data.username} for path: {path}")
                print(f"Middleware: Successfully authenticated user {token_data.username} for {path}")
                
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
        print(f"JWTAuthMiddleware: Processing request without auth requirement")
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
