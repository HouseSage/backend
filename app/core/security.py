from passlib.context import CryptContext
from fastapi import Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer
from jose import JWTError, jwt
from app.core.config import settings
from app.core.exceptions import UnauthorizedException
from app.models import models
from app.db.database import SessionLocal
from sqlalchemy.orm import Session

pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

# OAuth2 scheme for FastAPI
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="/api/v1/auth/token")

# Verifies a plain password against a hashed password
def verify_password(plain_password: str, hashed_password: str) -> bool:
    return pwd_context.verify(plain_password, hashed_password)

# Returns a hashed version of the password
def get_password_hash(password: str) -> str:
    return pwd_context.hash(password)

# Get a user from the database by email
def get_user_by_email(db: Session, email: str):
    return db.query(models.User).filter(models.User.email == email).first()

# Get a user from the database by id
def get_user_by_id(db: Session, user_id):
    return db.query(models.User).filter(models.User.id == user_id).first()

# Decode JWT and get current user
def get_current_user(token: str = Depends(oauth2_scheme)):
    try:
        payload = jwt.decode(token, settings.SECRET_KEY, algorithms=[settings.ALGORITHM])
        user_id: str = payload.get("sub")
        if user_id is None:
            raise UnauthorizedException("Could not validate credentials")
    except JWTError:
        raise UnauthorizedException("Could not validate credentials")
    db = SessionLocal()
    user = get_user_by_id(db, user_id)
    db.close()
    if user is None:
        raise UnauthorizedException("Could not validate credentials")
    return user

# For endpoints that require an active user
def get_current_active_user(current_user: models.User = Depends(get_current_user)):
    # Add any additional checks here (e.g., is_active flag)
    return current_user
