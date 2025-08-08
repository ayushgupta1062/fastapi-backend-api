from fastapi import APIRouter, HTTPException, Depends
from pydantic import BaseModel
from app.auth import signup_user, login_user, get_current_active_user
from app.models import Token

router = APIRouter()

class UserSignup(BaseModel):
    email: str
    password: str

class UserLogin(BaseModel):
    email: str
    password: str

@router.post("/signup")
async def signup(user_data: UserSignup):
    """
    Sign up a new user.
    
    Args:
        user_data: User signup data (email, password)
        
    Returns:
        Success message
    """
    try:
        result = await signup_user(user_data.email, user_data.password)
        return result
    except HTTPException as e:
        raise e
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Signup failed: {str(e)}")

@router.post("/signin", response_model=Token)
async def signin(user_data: UserLogin):
    """
    Sign in a user.
    
    Args:
        user_data: User login data (email, password)
        
    Returns:
        Access token and token type
    """
    try:
        result = await login_user(user_data.email, user_data.password)
        return result
    except HTTPException as e:
        raise e
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Login failed: {str(e)}")

@router.get("/me")
async def get_current_user_info(current_user = Depends(get_current_active_user)):
    """
    Get current user information.
    
    Args:
        current_user: Current authenticated user
        
    Returns:
        Current user information
    """
    return {"user": current_user} 