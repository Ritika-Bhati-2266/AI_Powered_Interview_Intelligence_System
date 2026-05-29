from typing import Generator, Optional
from fastapi import Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer
from sqlalchemy.orm import Session

from .database import SessionLocal
from .config import settings
from . import models, auth

# Define OAuth2 schema pointing to login endpoint
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="/api/auth/login", auto_error=False)

def get_db() -> Generator:
    """
    Dependency function to yield a database session.
    Guarantees the session is closed after the request completes.
    """
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

def get_current_user(
    token: Optional[str] = Depends(oauth2_scheme), 
    db: Session = Depends(get_db)
) -> models.User:
    """
    Retrieves the currently authenticated user based on JWT verification.
    Raises 401 Unauthorized for invalid/expired tokens.
    """
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Could not validate credentials. Please log in.",
        headers={"WWW-Authenticate": "Bearer"},
    )
    
    if not token:
        raise credentials_exception

    # 1. Decode token payload
    payload = auth.decode_access_token(token)
    if payload is None:
        raise credentials_exception
    
    # 2. Extract values
    email: str = payload.get("sub")
    user_id: int = payload.get("uid")
    if email is None or user_id is None:
        raise credentials_exception
        
    # 3. Retrieve User from SQLite database
    user = db.query(models.User).filter(models.User.id == user_id).first()
    if user is None:
        raise credentials_exception
        
    return user
