from fastapi import Depends, HTTPException, status, Header
from jose import JWTError
from app.models import TokenData
from app.utils.hashing import verify_password, hash_password
from app.utils.jwt_handler import create_access_token as create_jwt_token, verify_access_token
from app.database import get_database

def create_access_token(data: dict):
    """Create JWT access token."""
    return create_jwt_token(data)

async def signup_user(email: str, password: str):
    """
    Sign up a new user.

    Args:
        email: User's email address
        password: User's password

    Returns:
        Success message

    Raises:
        HTTPException: If email already exists
    """
    db = get_database()
    if db is None:
        raise HTTPException(status_code=500, detail="Database connection failed")

    # Check if user already exists
    user = await db["users"].find_one({"email": email})
    if user:
        raise HTTPException(status_code=400, detail="Email already registered")

    # Hash password and create user
    hashed_pw = hash_password(password)
    await db["users"].insert_one({"email": email, "password": hashed_pw})
    return {"message": "User created successfully"}

async def login_user(email: str, password: str):
    """
    Log in a user.

    Args:
        email: User's email address
        password: User's password

    Returns:
        Access token and token type

    Raises:
        HTTPException: If credentials are invalid
    """
    db = get_database()
    if db is None:
        raise HTTPException(status_code=500, detail="Database connection failed")

    # Find user by email
    user = await db["users"].find_one({"email": email})
    if not user or not verify_password(password, user["password"]):
        raise HTTPException(status_code=401, detail="Invalid credentials")

    # Create access token
    token = create_access_token({"email": user["email"], "id": str(user["_id"]), "sub": user["email"]})
    return {"access_token": token, "token_type": "bearer"}

async def get_current_user(Authorization: str = Header(...)):
    """
    Get current user from JWT token in Authorization header.
    
    Args:
        Authorization: Bearer token from header

    Returns:
        TokenData object (e.g., username)
    """
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Could not validate credentials",
        headers={"WWW-Authenticate": "Bearer"},
    )

    try:
        token = Authorization.split(" ")[1]
        payload = verify_access_token(token)
        if payload is None:
            raise credentials_exception

        email: str = payload.get("sub")
        if email is None:
            raise credentials_exception
        return TokenData(username=email)
    except (JWTError, IndexError, AttributeError):
        raise credentials_exception

async def get_current_active_user(current_user: TokenData = Depends(get_current_user)):
    """Ensure current user is active."""
    if not current_user or not current_user.username:
        raise HTTPException(status_code=400, detail="Inactive user")
    return current_user
