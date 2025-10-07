"""
Authentication routes for the FastAPI application
Handles user registration, login, and token management
"""

from datetime import timedelta
from fastapi import APIRouter, HTTPException, status, Depends, Request, Response
from fastapi.security import OAuth2PasswordRequestForm

from src.auth import (
    create_access_token, 
    authenticate_user, 
    get_current_user,
    get_current_user_from_request,
    get_password_hash,
    verify_token,
    ACCESS_TOKEN_EXPIRE_MINUTES
)
from src.schemas import (
    UserRegister, 
    UserLogin, 
    Token, 
    UserResponse, 
    MessageResponse,
    RefreshTokenRequest
)
from src.model import User
from src.dependencies import get_database
from src.db.song_db import SongsDatabase

# Create router
router = APIRouter(
    prefix="/auth",
    tags=["authentication"],
    responses={404: {"description": "Not found"}},
)


@router.post("/register", response_model=UserResponse, status_code=201)
async def register_user(
    user_data: UserRegister,
    db: SongsDatabase = Depends(get_database)
):
    """
    Register a new user
    
    Args:
        user_data: User registration data
        db: Database dependency
        
    Returns:
        UserResponse: Created user information
        
    Raises:
        HTTPException: If username or email already exists
    """
    # Check if username already exists
    existing_user = db.get_user_by_username(user_data.username)
    if existing_user:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Username already registered"
        )
    
    # Check if email already exists
    existing_email = db.get_user_by_email(user_data.email)
    if existing_email:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Email already registered"
        )
    
    # Hash password
    password_hash = get_password_hash(user_data.password)
    
    # Create user
    user = User(
        username=user_data.username,
        email=user_data.email,
        password_hash=password_hash,
        first_name=user_data.first_name,
        last_name=user_data.last_name
    )
    
    # Save to database
    created_user = db.add_user(user)
    if not created_user:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to create user"
        )
    
    return UserResponse(**created_user.to_response())


@router.post("/login", response_model=Token)
async def login_user(
    user_credentials: UserLogin,
    response: Response,
    db: SongsDatabase = Depends(get_database)
):
    """
    Authenticate user and return JWT token
    
    Args:
        user_credentials: User login credentials
        db: Database dependency
        
    Returns:
        Token: JWT access token
        
    Raises:
        HTTPException: If credentials are invalid
    """
    # Get user by username or email
    user = db.get_user_by_username(user_credentials.username)
    if not user:
        # Try to find by email
        user = db.get_user_by_email(user_credentials.username)
    
    # Authenticate user
    authenticated_user = authenticate_user(
        user_credentials.username, 
        user_credentials.password, 
        user
    )
    
    if not authenticated_user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect username or password",
            headers={"WWW-Authenticate": "Bearer"},
        )
    
    # Create access token
    access_token_expires = timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
    access_token = create_access_token(
        data={"sub": user.username, "user_id": str(user.id)},
        expires_delta=access_token_expires
    )
    
    # Create refresh token (longer expiration)
    refresh_token_expires = timedelta(days=7)  # 7 days
    refresh_token = create_access_token(
        data={
            "sub": user.username, 
            "user_id": str(user.id), 
            "type": "refresh",
            "version": user.refresh_token_version
        },
        expires_delta=refresh_token_expires
    )
    
    # Update last login
    user.update_last_login()
    db.update_user(user)
    
    # Set HTTP-only cookies for NextJS middleware
    response.set_cookie(
        key="access_token",
        value=access_token,
        max_age=ACCESS_TOKEN_EXPIRE_MINUTES * 60,
        httponly=True,
        secure=False,  # Set to True in production with HTTPS
        samesite="strict"
    )
    
    response.set_cookie(
        key="refresh_token",
        value=refresh_token,
        max_age=7 * 24 * 60 * 60,  # 7 days
        httponly=True,
        secure=False,  # Set to True in production with HTTPS
        samesite="strict"
    )
    
    return Token(
        access_token=access_token,
        token_type="bearer",
        expires_in=ACCESS_TOKEN_EXPIRE_MINUTES * 60,
        refresh_token=refresh_token
    )


@router.post("/login-form", response_model=Token)
async def login_user_form(
    response: Response,
    form_data: OAuth2PasswordRequestForm = Depends(),
    db: SongsDatabase = Depends(get_database)
):
    """
    Authenticate user using OAuth2 form data (for Swagger UI compatibility)
    
    Args:
        form_data: OAuth2 form data
        db: Database dependency
        
    Returns:
        Token: JWT access token
        
    Raises:
        HTTPException: If credentials are invalid
    """
    # Get user by username or email
    user = db.get_user_by_username(form_data.username)
    if not user:
        # Try to find by email
        user = db.get_user_by_email(form_data.username)
    
    # Authenticate user
    authenticated_user = authenticate_user(
        form_data.username, 
        form_data.password, 
        user
    )
    
    if not authenticated_user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect username or password",
            headers={"WWW-Authenticate": "Bearer"},
        )
    
    # Create access token
    access_token_expires = timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
    access_token = create_access_token(
        data={"sub": user.username, "user_id": str(user.id)},
        expires_delta=access_token_expires
    )
    
    # Create refresh token (longer expiration)
    refresh_token_expires = timedelta(days=7)  # 7 days
    refresh_token = create_access_token(
        data={
            "sub": user.username, 
            "user_id": str(user.id), 
            "type": "refresh",
            "version": user.refresh_token_version
        },
        expires_delta=refresh_token_expires
    )
    
    # Update last login
    user.update_last_login()
    db.update_user(user)
    
    # Set HTTP-only cookies for NextJS middleware
    response.set_cookie(
        key="access_token",
        value=access_token,
        max_age=ACCESS_TOKEN_EXPIRE_MINUTES * 60,
        httponly=True,
        secure=False,  # Set to True in production with HTTPS
        samesite="strict"
    )
    
    response.set_cookie(
        key="refresh_token",
        value=refresh_token,
        max_age=7 * 24 * 60 * 60,  # 7 days
        httponly=True,
        secure=False,  # Set to True in production with HTTPS
        samesite="strict"
    )
    
    return Token(
        access_token=access_token,
        token_type="bearer",
        expires_in=ACCESS_TOKEN_EXPIRE_MINUTES * 60,
        refresh_token=refresh_token
    )


@router.post("/refresh", response_model=Token)
async def refresh_token(
    refresh_request: RefreshTokenRequest,
    response: Response,
    db: SongsDatabase = Depends(get_database)
):
    """
    Refresh access token using refresh token
    
    Args:
        refresh_request: Refresh token request containing refresh token
        response: FastAPI response object for setting cookies
        db: Database dependency
        
    Returns:
        Token: New JWT access token
        
    Raises:
        HTTPException: If refresh token is invalid or expired
    """
    try:
        # Validate refresh token
        token_data = verify_token(refresh_request.refresh_token)
        
        # Check if it's a refresh token
        if not hasattr(token_data, 'type') or token_data.type != 'refresh':
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Invalid token type"
            )
        
        # Get user
        user = db.get_user_by_username(token_data.username)
        if not user:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="User not found"
            )
        
        # Check if refresh token version matches current version (token rotation security)
        if token_data.version != user.refresh_token_version:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Refresh token has been revoked"
            )
        
        # Increment refresh token version (invalidates all previous refresh tokens)
        user.refresh_token_version += 1
        db.update_user(user)
        
        # Create new access token
        access_token_expires = timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
        access_token = create_access_token(
            data={"sub": user.username, "user_id": str(user.id)},
            expires_delta=access_token_expires
        )
        
        # Create new refresh token with updated version
        refresh_token_expires = timedelta(days=7)  # 7 days
        refresh_token = create_access_token(
            data={
                "sub": user.username, 
                "user_id": str(user.id), 
                "type": "refresh",
                "version": user.refresh_token_version
            },
            expires_delta=refresh_token_expires
        )
        
        # Set HTTP-only cookies for NextJS middleware
        response.set_cookie(
            key="access_token",
            value=access_token,
            max_age=ACCESS_TOKEN_EXPIRE_MINUTES * 60,
            httponly=True,
            secure=False,  # Set to True in production with HTTPS
            samesite="strict"
        )
        
        response.set_cookie(
            key="refresh_token",
            value=refresh_token,
            max_age=7 * 24 * 60 * 60,  # 7 days
            httponly=True,
            secure=False,  # Set to True in production with HTTPS
            samesite="strict"
        )
        
        return Token(
            access_token=access_token,
            token_type="bearer",
            expires_in=ACCESS_TOKEN_EXPIRE_MINUTES * 60,
            refresh_token=refresh_token
        )
        
    except HTTPException:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid refresh token"
        )


@router.get("/me", response_model=UserResponse)
async def get_current_user_info(
    current_user = Depends(get_current_user),
    db: SongsDatabase = Depends(get_database)
):
    """
    Get current user information
    
    Args:
        current_user: Current authenticated user from JWT token
        db: Database dependency
        
    Returns:
        UserResponse: Current user information
    """
    
    user = db.get_user_by_username(current_user.username)
    if not user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="User not found"
        )
    
    return UserResponse(**user.to_response())


@router.post("/logout", response_model=MessageResponse)
async def logout_user():
    """
    Logout user (client-side token removal)
    
    Returns:
        MessageResponse: Logout confirmation
    """
    # In a stateless JWT system, logout is handled client-side
    # by removing the token. This endpoint is for confirmation.
    return MessageResponse(
        message="Successfully logged out",
        success=True
    )
