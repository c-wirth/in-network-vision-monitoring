# server/main.py

"""
Main FastAPI application entry point.

Responsibilities:
- Initialize database tables
- Configure CORS for frontend communication
- Provide authentication endpoints
- Provide protected user endpoints
"""
import os
from pathlib import Path
from fastapi import FastAPI, Depends, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from sqlalchemy.orm import Session

# ---- Database + Models ----
from user_access.database import engine, Base, get_db
from user_access import models, schemas

# ---- Authentication Utilities ----
from dotenv import load_dotenv
from user_access.auth import (
    hash_password,
    verify_password,
    create_access_token,
    get_current_user,
)

# =====================================================
# FastAPI App Initialization
# =====================================================

app = FastAPI()

# -----------------------------------------------------
# CORS Configuration
# -----------------------------------------------------
# Allow the Vite frontend (running on localhost:5173)
# to communicate with this backend during development.

load_dotenv(Path(__file__).resolve().parent.parent / ".env")

origins = [os.getenv("FRONTEND_URL")]

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# -----------------------------------------------------
# Database Initialization
# -----------------------------------------------------
# Create database tables automatically if they do not exist.
Base.metadata.create_all(bind=engine)


# =====================================================
# Protected Endpoints
# =====================================================

@app.get("/api/status")
def get_status(current_user=Depends(get_current_user)):
    """
    Protected system status endpoint.

    Requires a valid JWT token.
    Returns basic system state and authenticated user info.
    """
    return {
        "ok": True,
        "user": current_user.email,
        "role": current_user.role
    }


@app.get("/api/me", response_model=schemas.UserResponse)
def get_current_user_info(current_user=Depends(get_current_user)):
    """
    Return the currently authenticated user.

    Used by the frontend to:
    - Verify login state
    - Retrieve role information
    """
    return current_user


# =====================================================
# Authentication Endpoints
# =====================================================

@app.post("/api/register", response_model=schemas.UserResponse)
def register_user(user: schemas.UserCreate, db: Session = Depends(get_db)):
    """
    Create a new user account.

    Steps:
    1. Ensure email is not already registered.
    2. Hash the password securely.
    3. Store the new user in the database.
    """

    existing_user = db.query(models.User).filter(
        models.User.email == user.email
    ).first()

    if existing_user:
        raise HTTPException(
            status_code=400,
            detail="Email already registered"
        )

    hashed_pw = hash_password(user.password)

    new_user = models.User(
        email=user.email,
        hashed_password=hashed_pw
    )

    db.add(new_user)
    db.commit()
    db.refresh(new_user)

    return new_user


@app.post("/api/login")
def login_user(user: schemas.UserLogin, db: Session = Depends(get_db)):
    """
    Authenticate a user using email and password.

    If valid:
        Returns a signed JWT token.
    If invalid:
        Returns HTTP 401 Unauthorized.
    """

    db_user = db.query(models.User).filter(
        models.User.email == user.email
    ).first()

    if not db_user:
        raise HTTPException(
            status_code=401,
            detail="Invalid email or password"
        )

    if not verify_password(user.password, db_user.hashed_password):
        raise HTTPException(
            status_code=401,
            detail="Invalid email or password"
        )

    access_token = create_access_token(
        data={
            "sub": db_user.email,   # JWT subject (identity)
            "role": db_user.role   # Custom claim for role-based access
        }
    )

    return {
        "access_token": access_token,
        "token_type": "bearer"
    }


# =====================================================
# Run with:
# uvicorn main:app --reload
# =====================================================
