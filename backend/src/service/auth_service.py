"""
Authentication service layer for the Songs API application
Handles authentication business logic and coordinates between API and data layers
"""

from datetime import timedelta
from typing import Optional, Dict, Any
from src.auth import (
    create_access_token, 
    authenticate_user, 
    get_password_hash,
    verify_token,
    ACCESS_TOKEN_EXPIRE_MINUTES
)
from src.schemas import UserRegister, UserLogin, Token, UserResponse, RefreshTokenRequest
from src.model import User
from src.db.user_db import UserDatabase


class AuthService:
    """Service layer for authentication operations"""
    
    def __init__(self, user_db: UserDatabase):
        """Initialize the service with a user database instance"""
        self.user_db = user_db
    
    async def register_user(self, user_data: UserRegister) -> Dict[str, Any]:
        """
        Register a new user
        
        Args:
            user_data: User registration data
            
        Returns:
            Dict with 'success' boolean, 'user' object if successful, and 'message' string
        """
        try:
            # Check if username already exists
            existing_user = await self.user_db.get_user_by_username(user_data.username)
            if existing_user:
                return {
                    "success": False, 
                    "message": "Username already registered",
                    "user": None
                }
            
            # Check if email already exists
            existing_email = await self.user_db.get_user_by_email(user_data.email)
            if existing_email:
                return {
                    "success": False, 
                    "message": "Email already registered",
                    "user": None
                }
            
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
            created_user = await self.user_db.add_user(user)
            if not created_user:
                return {
                    "success": False, 
                    "message": "Failed to create user",
                    "user": None
                }
            
            return {
                "success": True,
                "message": "User registered successfully",
                "user": UserResponse(**created_user.to_response())
            }
            
        except Exception as e:
            return {
                "success": False,
                "message": f"Registration failed: {str(e)}",
                "user": None
            }
    
    async def login_user(self, user_credentials: UserLogin) -> Dict[str, Any]:
        """
        Authenticate user and return JWT token
        
        Args:
            user_credentials: User login credentials
            
        Returns:
            Dict with 'success' boolean, 'token' object if successful, and 'message' string
        """
        try:
            print(f"AuthService: Attempting login for {user_credentials.username}")
            
            # Get user by username or email
            user = await self.user_db.get_user_by_username(user_credentials.username)
            print(f"AuthService: User by username: {user}")
            
            if not user:
                # Try to find by email
                user = await self.user_db.get_user_by_email(user_credentials.username)
                print(f"AuthService: User by email: {user}")
            
            if not user:
                print("AuthService: User not found")
                return {
                    "success": False,
                    "message": "Incorrect username or password",
                    "token": None
                }
            
            print(f"AuthService: Found user: {user.username}, is_active: {user.is_active}")
            
            # Authenticate user
            print(f"AuthService: About to authenticate with password: {user_credentials.password[:3]}...")
            print(f"AuthService: User password hash: {user.password_hash[:20]}...")
            
            authenticated_user = authenticate_user(
                user_credentials.username, 
                user_credentials.password, 
                user
            )
            print(f"AuthService: Authentication result: {authenticated_user}")
            
            if not authenticated_user:
                print("AuthService: Authentication failed")
                return {
                    "success": False,
                    "message": "Incorrect username or password",
                    "token": None
                }
            
            print("AuthService: Creating tokens...")
            
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
            await self.user_db.update_user(user)
            
            token = Token(
                access_token=access_token,
                token_type="bearer",
                expires_in=ACCESS_TOKEN_EXPIRE_MINUTES * 60,
                refresh_token=refresh_token
            )
            
            print("AuthService: Login successful")
            
            return {
                "success": True,
                "message": "Login successful",
                "token": token
            }
            
        except Exception as e:
            print(f"AuthService: Login error: {e}")
            return {
                "success": False,
                "message": f"Login failed: {str(e)}",
                "token": None
            }
    
    async def refresh_token(self, refresh_request: RefreshTokenRequest) -> Dict[str, Any]:
        """
        Refresh access token using refresh token
        
        Args:
            refresh_request: Refresh token request containing refresh token
            
        Returns:
            Dict with 'success' boolean, 'token' object if successful, and 'message' string
        """
        try:
            # Validate refresh token
            token_data = verify_token(refresh_request.refresh_token)
            
            # Check if it's a refresh token
            if not hasattr(token_data, 'type') or token_data.type != 'refresh':
                return {
                    "success": False,
                    "message": "Invalid token type",
                    "token": None
                }
            
            # Get user
            user = await self.user_db.get_user_by_username(token_data.username)
            if not user:
                return {
                    "success": False,
                    "message": "User not found",
                    "token": None
                }
            
            # Check if refresh token version matches current version (token rotation security)
            if token_data.version != user.refresh_token_version:
                return {
                    "success": False,
                    "message": "Refresh token has been revoked",
                    "token": None
                }
            
            # Increment refresh token version (invalidates all previous refresh tokens)
            user.refresh_token_version += 1
            await self.user_db.update_user(user)
            
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
            
            token = Token(
                access_token=access_token,
                token_type="bearer",
                expires_in=ACCESS_TOKEN_EXPIRE_MINUTES * 60,
                refresh_token=refresh_token
            )
            
            return {
                "success": True,
                "message": "Token refreshed successfully",
                "token": token
            }
            
        except Exception as e:
            return {
                "success": False,
                "message": f"Token refresh failed: {str(e)}",
                "token": None
            }
    
    async def get_current_user_info(self, username: str) -> Dict[str, Any]:
        """
        Get current user information
        
        Args:
            username: Username of the current user
            
        Returns:
            Dict with 'success' boolean, 'user' object if successful, and 'message' string
        """
        try:
            user = await self.user_db.get_user_by_username(username)
            if not user:
                return {
                    "success": False,
                    "message": "User not found",
                    "user": None
                }
            
            return {
                "success": True,
                "message": "User information retrieved successfully",
                "user": UserResponse(**user.to_response())
            }
            
        except Exception as e:
            return {
                "success": False,
                "message": f"Failed to get user information: {str(e)}",
                "user": None
            }
    
    async def logout_user(self) -> Dict[str, Any]:
        """
        Logout user (client-side token removal)
        
        Returns:
            Dict with 'success' boolean and 'message' string
        """
        # In a stateless JWT system, logout is handled client-side
        # by removing the token. This endpoint is for confirmation.
        return {
            "success": True,
            "message": "Successfully logged out"
        }
