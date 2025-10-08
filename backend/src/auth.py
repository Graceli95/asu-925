"""
Authentication utilities for JWT token handling
"""

import os
from datetime import datetime, timedelta
from typing import Optional, Union
from jose import JWTError, jwt
from fastapi import HTTPException, status, Depends, Request
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from passlib.context import CryptContext
from dotenv import load_dotenv

from src.schemas import TokenData

# Load environment variables
load_dotenv()

# Configuration
SECRET_KEY = os.getenv("JWT_SECRET_KEY", "your-super-secure-secret-key-here-32-chars-min")
ALGORITHM = os.getenv("JWT_ALGORITHM", "HS256")
ACCESS_TOKEN_EXPIRE_MINUTES = int(os.getenv("JWT_ACCESS_TOKEN_EXPIRE_MINUTES", "30"))

# Password hashing
try:
    pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")
except Exception as e:
    # Fallback to argon2 if bcrypt fails
    print(f"Warning: bcrypt failed ({e}), falling back to argon2")
    pwd_context = CryptContext(schemes=["argon2"], deprecated="auto")

# Security scheme
security = HTTPBearer()


def verify_password(plain_password: str, hashed_password: str) -> bool:
    """Verify a password against its hash"""
    return pwd_context.verify(plain_password, hashed_password)


def get_password_hash(password: str) -> str:
    """Hash a password"""
    return pwd_context.hash(password)


def create_access_token(data: dict, expires_delta: Optional[timedelta] = None) -> str:
    """
    Create a JWT access token
    
    Args:
        data: Data to encode in the token
        expires_delta: Token expiration time
        
    Returns:
        Encoded JWT token
    """
    to_encode = data.copy()
    
    if expires_delta:
        expire = datetime.utcnow() + expires_delta
    else:
        expire = datetime.utcnow() + timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
    
    to_encode.update({"exp": expire})
    encoded_jwt = jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)
    return encoded_jwt


def verify_token(token: str) -> TokenData:
    """
    Verify and decode a JWT token
    
    Args:
        token: JWT token to verify
        
    Returns:
        TokenData object with user information
        
    Raises:
        HTTPException: If token is invalid or expired
    """
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Could not validate credentials",
        headers={"WWW-Authenticate": "Bearer"},
    )
    
    try:
        print(f"Auth: Verifying token: {token[:20]}...")
        print(f"Auth: Using SECRET_KEY: {SECRET_KEY[:10]}...")
        print(f"Auth: Using ALGORITHM: {ALGORITHM}")
        
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        print(f"Auth: Token payload decoded successfully: {payload}")
        
        username: str = payload.get("sub")
        user_id: str = payload.get("user_id")
        token_type: str = payload.get("type")
        version: int = payload.get("version")
        
        print(f"Auth: Extracted data - username: {username}, user_id: {user_id}, type: {token_type}, version: {version}")
        
        if username is None:
            print("Auth: Username is None, raising credentials exception")
            raise credentials_exception
            
        token_data = TokenData(username=username, user_id=user_id, type=token_type, version=version)
        print(f"Auth: Created TokenData: {token_data}")
        return token_data
        
    except JWTError as e:
        print(f"Auth: JWTError during token verification: {e}")
        raise credentials_exception


async def get_current_user(credentials: HTTPAuthorizationCredentials = Depends(security)) -> TokenData:
    """
    Dependency to get the current authenticated user from JWT token
    
    Args:
        credentials: HTTP Bearer token credentials
        
    Returns:
        TokenData object with user information
        
    Raises:
        HTTPException: If token is invalid or expired
    """
    token = credentials.credentials
    return verify_token(token)


async def get_current_user_from_request(request: Request) -> TokenData:
    """
    Get current user from request state (set by middleware)
    
    Args:
        request: FastAPI request object
        
    Returns:
        TokenData object with user information
        
    Raises:
        HTTPException: If user not found in request state
    """
    if not hasattr(request.state, 'current_user'):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="User not authenticated",
            headers={"WWW-Authenticate": "Bearer"},
        )
    
    return request.state.current_user


async def get_current_active_user(current_user: TokenData = Depends(get_current_user)) -> TokenData:
    """
    Dependency to get the current active user
    
    Args:
        current_user: Current user from JWT token
        
    Returns:
        TokenData object with user information
        
    Raises:
        HTTPException: If user is inactive
    """
    # Note: In a real application, you would check if the user is active in the database
    # For now, we assume all authenticated users are active
    return current_user


def authenticate_user(username: str, password: str, user) -> Union[bool, dict]:
    """
    Authenticate a user with username/email and password
    
    Args:
        username: Username or email
        password: Plain text password
        user: User object from database
        
    Returns:
        False if authentication fails, user dict if successful
    """
    print(f"Auth: Starting authentication for user: {username}")
    print(f"Auth: User object: {user}")
    
    if not user:
        print("Auth: No user provided")
        return False
    
    print(f"Auth: User is_active: {user.is_active}")
    print(f"Auth: About to verify password...")
    
    try:
        password_valid = verify_password(password, user.password_hash)
        print(f"Auth: Password verification result: {password_valid}")
    except Exception as e:
        print(f"Auth: Password verification error: {e}")
        return False
    
    if not password_valid:
        print("Auth: Password verification failed")
        return False
    
    if not user.is_active:
        print("Auth: User account is inactive")
        return False
    
    print("Auth: Authentication successful")
    return user.to_response()


async def get_current_user_from_middleware(request: Request) -> TokenData:
    """
    Get current user from request state (set by middleware)
    
    Args:
        request: FastAPI request object
        
    Returns:
        TokenData object with user information
        
    Raises:
        HTTPException: If user not found in request state
    """
    if not hasattr(request.state, 'current_user') or not request.state.current_user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="User not authenticated",
            headers={"WWW-Authenticate": "Bearer"},
        )
    
    return request.state.current_user


# Optional authentication dependency (doesn't raise exception if no token)
async def get_current_user_optional(
    credentials: Optional[HTTPAuthorizationCredentials] = Depends(security)
) -> Optional[TokenData]:
    """
    Optional authentication dependency that doesn't raise exception if no token provided
    
    Args:
        credentials: HTTP Bearer token credentials (optional)
        
    Returns:
        TokenData object if valid token provided, None otherwise
    """
    if not credentials:
        return None
    
    try:
        return verify_token(credentials.credentials)
    except HTTPException:
        return None
