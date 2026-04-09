from pydantic import BaseModel, EmailStr, Field
from datetime import datetime


# ============================================================
# USER SCHEMAS
# ============================================================

class UserAuthBase(BaseModel):
    """
    Base schema for authentication-related inputs.

    Used for both:
    - user registration (UserCreate)
    - user login (UserLogin)

    Purpose:
    - avoid duplication of common fields
    - ensure consistent validation rules across auth flows
    """

    # User email (validated format via Pydantic)
    email: EmailStr

    # Plain-text password (will be hashed in service layer)
    password: str = Field(min_length=1)


class UserRead(BaseModel):
    """
    Data returned to the client for a user.
    """

    id: int
    email: EmailStr
    role: str
    created_at: datetime

    model_config = {"from_attributes": True}


# ============================================================
# CLIP SCHEMAS
# ============================================================

class ClipCreate(BaseModel):
    """
    Data required to create a clip.

    user_id is NOT provided by client (comes from auth context).
    """

    file_path: str = Field(min_length=1)


class ClipRead(BaseModel):
    """
    Data returned to the client for a clip.
    """

    id: int
    user_id: int
    file_path: str
    created_at: datetime

    model_config = {"from_attributes": True}