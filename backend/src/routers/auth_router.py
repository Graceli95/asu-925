"""
Authentication routes for the FastAPI application
Handles user registration, login, and token management
"""

from datetime import timedelta
from fastapi import APIRouter, HTTPException, status, Depends, Request, Response
from fastapi.security import OAuth2PasswordRequestForm

from src.auth import get_current_user
from src.schemas import (
    UserRegister, 
    UserLogin, 
    Token, 
    UserResponse, 
    MessageResponse,
    RefreshTokenRequest
)
from src.dependencies import get_auth_service
from src.service.auth_service import AuthService

# Create router
router = APIRouter(
    prefix="/auth",
    tags=["authentication"],
    responses={404: {"description": "Not found"}},
)


@router.post("/register", response_model=UserResponse, status_code=201)
async def register_user(
    user_data: UserRegister,
    auth_service: AuthService = Depends(get_auth_service)
):
    """
    Register a new user
    
    Args:
        user_data: User registration data
        auth_service: Authentication service dependency
        
    Returns:
        UserResponse: Created user information
        
    Raises:
        HTTPException: If username or email already exists
    """
    try:
        result = await auth_service.register_user(user_data)
        
        if not result["success"]:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=result["message"]
            )
        
        return result["user"]
    except HTTPException:
        raise
    except Exception as e:
        print(f"Registration error: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Internal server error during registration"
        )


@router.post("/login", response_model=Token)
async def login_user(
    user_credentials: UserLogin,
    response: Response,
    auth_service: AuthService = Depends(get_auth_service)
):
    """
    Authenticate user and return JWT token
    
    Args:
        user_credentials: User login credentials
        response: FastAPI response object for setting cookies
        auth_service: Authentication service dependency
        
    Returns:
        Token: JWT access token
        
    Raises:
        HTTPException: If credentials are invalid
    """
    try:
        print(f"Login attempt for username: {user_credentials.username}")
        result = await auth_service.login_user(user_credentials)
        print(f"Login result: {result}")
        
        if not result["success"]:
            print(f"Login failed: {result['message']}")
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail=result["message"],
                headers={"WWW-Authenticate": "Bearer"},
            )
        
        token = result["token"]
        print(f"Login successful for user: {user_credentials.username}")
        
        # Set HTTP-only cookies for NextJS middleware
        print(f"Setting access_token cookie: {token.access_token[:20]}...")
        response.set_cookie(
            key="access_token",
            value=token.access_token,
            max_age=token.expires_in,
            httponly=True,
            secure=False,  # Set to True in production with HTTPS
            samesite="lax"  # Changed from "strict" to "lax" for CORS compatibility
        )
        
        print(f"Setting refresh_token cookie: {token.refresh_token[:20]}...")
        response.set_cookie(
            key="refresh_token",
            value=token.refresh_token,
            max_age=7 * 24 * 60 * 60,  # 7 days
            httponly=True,
            secure=False,  # Set to True in production with HTTPS
            samesite="lax"  # Changed from "strict" to "lax" for CORS compatibility
        )
        
        return token
    except HTTPException:
        raise
    except Exception as e:
        print(f"Login error: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Internal server error during login"
        )


@router.post("/login-form", response_model=Token)
async def login_user_form(
    response: Response,
    form_data: OAuth2PasswordRequestForm = Depends(),
    auth_service: AuthService = Depends(get_auth_service)
):
    """
    Authenticate user using OAuth2 form data (for Swagger UI compatibility)
    
    Args:
        form_data: OAuth2 form data
        response: FastAPI response object for setting cookies
        auth_service: Authentication service dependency
        
    Returns:
        Token: JWT access token
        
    Raises:
        HTTPException: If credentials are invalid
    """
    # Convert form data to UserLogin schema
    user_credentials = UserLogin(
        username=form_data.username,
        password=form_data.password
    )
    
    result = await auth_service.login_user(user_credentials)
    
    if not result["success"]:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail=result["message"],
            headers={"WWW-Authenticate": "Bearer"},
        )
    
    token = result["token"]
    
    # Set HTTP-only cookies for NextJS middleware
    response.set_cookie(
        key="access_token",
        value=token.access_token,
        max_age=token.expires_in,
        httponly=True,
        secure=False,  # Set to True in production with HTTPS
        samesite="strict"
    )
    
    response.set_cookie(
        key="refresh_token",
        value=token.refresh_token,
        max_age=7 * 24 * 60 * 60,  # 7 days
        httponly=True,
        secure=False,  # Set to True in production with HTTPS
        samesite="strict"
    )
    
    return token


@router.post("/refresh", response_model=Token)
async def refresh_token(
    request: Request,
    response: Response,
    refresh_request: RefreshTokenRequest = None,
    auth_service: AuthService = Depends(get_auth_service)
):
    """
    Refresh access token using refresh token
    
    Args:
        request: FastAPI request object (for accessing cookies)
        response: FastAPI response object for setting cookies
        refresh_request: Refresh token request containing refresh token (optional)
        auth_service: Authentication service dependency
        
    Returns:
        Token: New JWT access token
        
    Raises:
        HTTPException: If refresh token is invalid or expired
    """
    # Try to get refresh token from request body first, then from cookies
    refresh_token_value = None
    
    if refresh_request and refresh_request.refresh_token:
        refresh_token_value = refresh_request.refresh_token
        print(f"RefreshRouter: Using refresh token from request body")
    else:
        # Try to get refresh token from HTTP-only cookie
        refresh_token_value = request.cookies.get("refresh_token")
        print(f"RefreshRouter: Using refresh token from cookie: {refresh_token_value[:20] if refresh_token_value else 'None'}...")
    
    if not refresh_token_value:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Refresh token not provided"
        )
    
    # Create RefreshTokenRequest with the token
    refresh_request_obj = RefreshTokenRequest(refresh_token=refresh_token_value)
    result = await auth_service.refresh_token(refresh_request_obj)
    
    if not result["success"]:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail=result["message"]
        )
    
    token = result["token"]
    
    # Set HTTP-only cookies for NextJS middleware
    response.set_cookie(
        key="access_token",
        value=token.access_token,
        max_age=token.expires_in,
        httponly=True,
        secure=False,  # Set to True in production with HTTPS
        samesite="strict"
    )
    
    response.set_cookie(
        key="refresh_token",
        value=token.refresh_token,
        max_age=7 * 24 * 60 * 60,  # 7 days
        httponly=True,
        secure=False,  # Set to True in production with HTTPS
        samesite="strict"
    )
    
    return token


@router.get("/me", response_model=UserResponse)
async def get_current_user_info(
    request: Request,
    auth_service: AuthService = Depends(get_auth_service)
):
    """
    Get current user information
    
    Args:
        request: FastAPI request object (contains user info from middleware)
        auth_service: Authentication service dependency
        
    Returns:
        UserResponse: Current user information
    """
    # Get user info from request state (set by middleware)
    print(f"AuthRouter: /me endpoint called")
    print(f"AuthRouter: Request state attributes: {dir(request.state)}")
    print(f"AuthRouter: Has current_user: {hasattr(request.state, 'current_user')}")
    
    if not hasattr(request.state, 'current_user') or not request.state.current_user:
        print("AuthRouter: No current_user in request state")
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="User not authenticated"
        )
    
    current_user = request.state.current_user
    print(f"AuthRouter: Current user from middleware: {current_user}")
    result = await auth_service.get_current_user_info(current_user.username)
    
    if not result["success"]:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=result["message"]
        )
    
    return result["user"]


@router.post("/logout", response_model=MessageResponse)
async def logout_user(
    auth_service: AuthService = Depends(get_auth_service)
):
    """
    Logout user (client-side token removal)
    
    Args:
        auth_service: Authentication service dependency
    
    Returns:
        MessageResponse: Logout confirmation
    """
    result = await auth_service.logout_user()
    
    return MessageResponse(
        message=result["message"],
        success=result["success"]
    )
