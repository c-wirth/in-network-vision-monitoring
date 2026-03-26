# db_infrastructure/db_components/schemas.py

"""
SCHEMAS (Pydantic Models)

This file defines the structure and validation rules for data
entering and leaving the API.

Key ideas:
- Schemas are NOT database models
- They validate input before it reaches the database
- They define what data is returned to the frontend

We use two types of schemas:
1. Create schemas → for incoming data (requests)
2. Read schemas → for outgoing data (responses)
"""

from pydantic import BaseModel, EmailStr, Field, model_validator
from datetime import datetime
from typing import Optional


# ============================================================
# USER SCHEMAS
# ============================================================

class UserCreate(BaseModel):
    """
    Data required to create a user.

    Validation:
    - email must be a valid email format
    - hashed_password must not be empty
    """

    email: EmailStr
    hashed_password: str = Field(min_length=1)
    role: str = "user"  # default role


class UserRead(BaseModel):
    """
    Data returned to the client for a user.
    """

    id: int
    email: EmailStr
    role: str
    created_at: datetime

    # Allows conversion from SQLAlchemy objects → Pydantic
    model_config = {"from_attributes": True}


# ============================================================
# CLIP SCHEMAS
# ============================================================

class ClipCreate(BaseModel):
    """
    Data required to create a clip.

    Validation:
    - file_path must not be empty
    - start_time is required
    - end_time (if provided) must be >= start_time
    """

    user_id: int
    file_path: str = Field(min_length=1)
    start_time: datetime
    end_time: Optional[datetime] = None

    @model_validator(mode="after")
    def validate_times(self):
        """
        Ensure end_time is not before start_time.
        """
        if self.end_time and self.end_time < self.start_time:
            raise ValueError("end_time must be >= start_time")
        return self


class ClipRead(BaseModel):
    """
    Data returned to the client for a clip.
    """

    id: int
    user_id: int
    file_path: str
    start_time: datetime
    end_time: Optional[datetime]
    created_at: datetime

    model_config = {"from_attributes": True}


# ============================================================
# DETECTION EVENT SCHEMAS
# ============================================================

class DetectionEventCreate(BaseModel):
    """
    Data required to create a detection event.

    Validation:
    - timestamp is required
    - confidence must be between 0.0 and 1.0
    - offset_seconds (if provided) must be >= 0
    """

    clip_id: int
    timestamp: datetime
    confidence: float = Field(ge=0.0, le=1.0)
    offset_seconds: Optional[float] = Field(default=None, ge=0.0)


class DetectionEventRead(BaseModel):
    """
    Data returned to the client for a detection event.
    """

    id: int
    clip_id: int
    timestamp: datetime
    confidence: float
    offset_seconds: Optional[float]
    created_at: datetime

    model_config = {"from_attributes": True}