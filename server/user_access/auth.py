# server/user_access/auth.py

"""
Authentication utilities.

Responsibilities:
- Password hashing and verification
- JWT token creation
- JWT token validation
- Current user extraction dependency
"""

from datetime import datetime, timedelta
from typing import Optional

from fastapi import Depends, HTTPException, status
from fastapi.security import HTTPBearer
from jose import JWTError, jwt
from passlib.context import CryptContext
from sqlalchemy.orm import Session

from .database import get_db
from . import models

from dotenv import load_dotenv
from pathlib import Path
import os


# =====================================================
# Password Hashing Configuration
# =====================================================

# bcrypt hashing context
pwd_context = CryptContext(
    schemes=["bcrypt"],
    deprecated="auto"
)


def hash_password(password: str) -> str:
    """
    Hash a plain-text password using bcrypt.
    """
    return pwd_context.hash(password)


def verify_password(plain_password: str, hashed_password: str) -> bool:
    """
    Verify a plain-text password against its hashed version.
    """
    return pwd_context.verify(plain_password, hashed_password)


# =====================================================
# JWT Configuration
# =====================================================

load_dotenv(Path(__file__).resolve().parent.parent.parent / ".env")
SECRET_KEY = os.getenv("SECRET_KEY")


ALGORITHM = "HS256"
ACCESS_TOKEN_EXPIRE_MINUTES = 60


def create_access_token(
    data: dict,
    expires_delta: Optional[timedelta] = None
) -> str:
    """
    Create a signed JWT token.

    The 'sub' claim is used for user identity.
    Additional claims (e.g., role) may be included.
    """

    to_encode = data.copy()

    if expires_delta:
        expire = datetime.utcnow() + expires_delta
    else:
        expire = datetime.utcnow() + timedelta(
            minutes=ACCESS_TOKEN_EXPIRE_MINUTES
        )

    to_encode.update({"exp": expire})

    encoded_jwt = jwt.encode(
        to_encode,
        SECRET_KEY,
        algorithm=ALGORITHM
    )

    return encoded_jwt


# =====================================================
# Token Validation / Dependency
# =====================================================

# Defines how the token is expected to be sent.
# Client must send:
# Authorization: Bearer <token>
oauth2_scheme = HTTPBearer()


def get_current_user(
    credentials = Depends(oauth2_scheme),
    db: Session = Depends(get_db)
):
    token = credentials.credentials
    """
    Dependency that:
    1. Extracts JWT from Authorization header
    2. Decodes and validates token
    3. Retrieves user from database
    4. Returns the authenticated user object
    """

    try:
        payload = jwt.decode(
            token,
            SECRET_KEY,
            algorithms=[ALGORITHM]
        )

        email: str = payload.get("sub")

        if email is None:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Invalid authentication credentials"
            )

    except JWTError:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid authentication credentials"
        )

    # Fetch user from database
    user = db.query(models.User).filter(
        models.User.email == email
    ).first()

    if user is None:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="User not found"
        )

    return user

