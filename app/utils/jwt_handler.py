from jose import JWTError, jwt
from datetime import datetime, timedelta
import os

SECRET_KEY = os.getenv("SECRET_KEY", "your_secret_key")
ALGORITHM = "HS256"
ACCESS_TOKEN_EXPIRE_MINUTES = 30

def create_access_token(data: dict):
    """
    Create a JWT access token.
    
    Args:
        data: Data to encode in the token
        
    Returns:
        Encoded JWT token string
    """
    to_encode = data.copy()
    expire = datetime.utcnow() + timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
    to_encode.update({"exp": expire})
    return jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)

def verify_access_token(token: str):
    """
    Verify and decode a JWT token.
    
    Args:
        token: JWT token string
        
    Returns:
        Decoded token payload or None if invalid
    """
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        return payload
    except JWTError:
        return None

def get_token_data(token: str):
    """
    Extract username from JWT token.
    
    Args:
        token: JWT token string
        
    Returns:
        Username from token or None if invalid
    """
    payload = verify_access_token(token)
    if payload:
        return payload.get("sub")
    return None

def create_token_for_user(username: str) -> str:
    """
    Create an access token for a user.
    
    Args:
        username: Username to encode in token
        
    Returns:
        JWT access token
    """
    return create_access_token(data={"sub": username})

def validate_token(token: str) -> bool:
    """
    Validate if a token is valid.
    
    Args:
        token: JWT token string
        
    Returns:
        True if token is valid, False otherwise
    """
    return verify_access_token(token) is not None 