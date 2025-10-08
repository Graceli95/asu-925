"""
User routes for the FastAPI application
Handles all CRUD operations for users
"""

from fastapi import APIRouter, HTTPException, Query, Path, Depends, status
from typing import Optional, List

from src.dependencies import get_user_service
from src.service.user_service import UserService
from src.schemas import MessageResponse, UserStatsResponse, UserResponse, UserUpdate
from src.auth import get_current_user

# Create router
router = APIRouter(
    prefix="/users",
    tags=["users"],
    responses={404: {"description": "Not found"}},
)


@router.get("/{username}/stats", response_model=UserStatsResponse)
async def get_user_stats(
    username: str = Path(..., description="Username"),
    user_service: UserService = Depends(get_user_service)
):
    """Get statistics for a user"""
    result = await user_service.get_user_stats(username)
    
    if not result["success"]:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=result["message"]
        )
    
    stats = result["stats"]
    
    return UserStatsResponse(
        user=username,
        total_songs=stats.get("total_songs", 0),
        genres=stats.get("genres", {}),
        years=stats.get("years", {}),
        artists=stats.get("artists", {})
    )

@router.get("/{username}", response_model=UserResponse)
async def get_user(
    username: str = Path(..., description="Username"),
    user_service: UserService = Depends(get_user_service)
):
    """Get a specific user by username"""
    result = await user_service.get_user_by_username(username)
    
    if not result["success"]:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=result["message"]
        )
    
    return result["user"]


@router.get("", response_model=List[UserResponse])
async def list_users(
    user_service: UserService = Depends(get_user_service)
):
    """Get all users"""
    result = await user_service.get_all_users()
    
    if not result["success"]:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=result["message"]
        )
    
    return result["users"]


@router.put("/{username}", response_model=UserResponse)
async def update_user(
    username: str = Path(..., description="Username"),
    user_update: UserUpdate = None,
    current_user = Depends(get_current_user),
    user_service: UserService = Depends(get_user_service)
):
    """Update user information (users can only update their own profile)"""
    # Users can only update their own profile
    if current_user.username != username:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="You can only update your own profile"
        )
    
    result = await user_service.update_user(username, user_update)
    
    if not result["success"]:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=result["message"]
        )
    
    return result["user"]


@router.delete("/{username}", response_model=MessageResponse)
async def delete_user(
    username: str = Path(..., description="Username"),
    current_user = Depends(get_current_user),
    user_service: UserService = Depends(get_user_service)
):
    """Delete user account (users can only delete their own account)"""
    # Users can only delete their own account
    if current_user.username != username:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="You can only delete your own account"
        )
    
    result = await user_service.delete_user(username)
    
    if not result["success"]:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=result["message"]
        )
    
    return MessageResponse(
        message=result["message"],
        success=True
    )


@router.post("/{username}/activate", response_model=MessageResponse)
async def activate_user(
    username: str = Path(..., description="Username"),
    user_service: UserService = Depends(get_user_service)
):
    """Activate a user account (admin only)"""
    result = await user_service.activate_user(username)
    
    if not result["success"]:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=result["message"]
        )
    
    return MessageResponse(
        message=result["message"],
        success=True
    )


@router.post("/{username}/deactivate", response_model=MessageResponse)
async def deactivate_user(
    username: str = Path(..., description="Username"),
    user_service: UserService = Depends(get_user_service)
):
    """Deactivate a user account (admin only)"""
    result = await user_service.deactivate_user(username)
    
    if not result["success"]:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=result["message"]
        )
    
    return MessageResponse(
        message=result["message"],
        success=True
    )
