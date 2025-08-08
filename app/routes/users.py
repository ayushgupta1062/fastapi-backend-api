from fastapi import APIRouter, HTTPException, Depends, status, Request, Header
from typing import List
from app.models import User, UserCreate, UserUpdate
from app.auth import get_current_active_user, create_access_token, signup_user, login_user
from app.utils.hashing import hash_password
from app.utils.jwt_handler import verify_access_token
from datetime import timedelta

router = APIRouter()

# Mock database - replace with actual database
users_db = []

@router.post("/signup")
async def signup(data: dict):
    """
    Sign up a new user.
    
    Args:
        data: Dictionary containing email and password
        
    Returns:
        Success message
    """
    return await signup_user(data["email"], data["password"])

@router.post("/signin")
async def signin(data: dict):
    """
    Sign in a user.
    
    Args:
        data: Dictionary containing email and password
        
    Returns:
        Access token and user information
    """
    return await login_user(data["email"], data["password"])

@router.get("/profile")
async def get_profile(Authorization: str = Header(...)):
    """
    Get user profile using JWT token.
    
    Args:
        Authorization: Bearer token in header
        
    Returns:
        User profile information
    """
    try:
        token = Authorization.split(" ")[1]
        user_data = verify_access_token(token)
        if not user_data:
            return {"error": "Invalid or expired token"}
        return {"user": user_data}
    except (IndexError, ValueError):
        return {"error": "Invalid authorization header format"}

@router.post("/", response_model=User)
async def create_user(user: UserCreate):
    """Create a new user."""
    # Check if user already exists
    if any(u["username"] == user.username for u in users_db):
        raise HTTPException(
            status_code=400,
            detail="Username already registered"
        )
    
    # Create new user
    user_dict = user.dict()
    user_dict["id"] = len(users_db) + 1
    user_dict["hashed_password"] = hash_password(user.password)
    user_dict["is_active"] = True
    user_dict["created_at"] = "2024-01-01T00:00:00"
    
    # Remove password from response
    del user_dict["password"]
    users_db.append(user_dict)
    
    return user_dict

@router.get("/", response_model=List[User])
async def get_users(current_user = Depends(get_current_active_user)):
    """Get all users."""
    return users_db

@router.get("/me", response_model=User)
async def get_current_user_info(current_user = Depends(get_current_active_user)):
    """Get current user information."""
    # Find user in mock database
    for user in users_db:
        if user["username"] == current_user.username:
            return user
    raise HTTPException(status_code=404, detail="User not found")

@router.put("/me", response_model=User)
async def update_current_user(
    user_update: UserUpdate,
    current_user = Depends(get_current_active_user)
):
    """Update current user information."""
    # Find and update user in mock database
    for user in users_db:
        if user["username"] == current_user.username:
            update_data = user_update.dict(exclude_unset=True)
            user.update(update_data)
            return user
    raise HTTPException(status_code=404, detail="User not found")

@router.delete("/me")
async def delete_current_user(current_user = Depends(get_current_active_user)):
    """Delete current user."""
    # Find and delete user from mock database
    for i, user in enumerate(users_db):
        if user["username"] == current_user.username:
            del users_db[i]
            return {"message": "User deleted successfully"}
    raise HTTPException(status_code=404, detail="User not found") 