# db_infrastructure/db_components/models.py

"""
This file defines the DATABASE STRUCTURE for the application using SQLAlchemy ORM.

Key idea:
- Each class = one table in the database
- Each attribute = one column in that table
- Relationships define how tables are connected

These models DO NOT contain business logic or queries.
They only describe how data is stored.
"""

from sqlalchemy import Column, Integer, String, Float, DateTime, ForeignKey
from sqlalchemy.orm import declarative_base, relationship
from datetime import datetime

# Base class that all models must inherit from
# SQLAlchemy uses this to keep track of all tables
Base = declarative_base()


# ============================================================
# USER MODEL
# ============================================================
class User(Base):
    """
    Represents a user of the system.

    One user can have many clips.
    """

    __tablename__ = "users"  # name of the table in the database

    # Primary key (unique identifier for each user)
    id = Column(Integer, primary_key=True, index=True)

    # User login information
    email = Column(String, unique=True, index=True, nullable=False)
    hashed_password = Column(String, nullable=False)

    # Role for authorization (e.g., "user", "admin")
    role = Column(String, default="user", nullable=False)

    # When the user was created
    created_at = Column(DateTime, default=datetime.utcnow)

    # Relationship:
    # One user -> many clips
    # This allows: user.clips
    # Cascade ensures that when a User is deleted,
    # all associated Clips are also deleted automatically
    clips = relationship("Clip", back_populates="user", cascade="all, delete")


# ============================================================
# CLIP MODEL
# ============================================================
class Clip(Base):
    """
    Represents a video clip saved by the system.

    A clip:
    - belongs to one user
    - can have many detection events
    """

    __tablename__ = "clips"

    # Primary key
    id = Column(Integer, primary_key=True, index=True)

    # Foreign key:
    # Links this clip to a user in the "users" table
    # Indexed for fast lookup of all clips belonging to a user
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False, index=True)

    # File location on disk (NOT stored in the database itself)
    file_path = Column(String, nullable=False)

    # When the clip starts and ends (real-world time)
    start_time = Column(DateTime, nullable=False)
    end_time = Column(DateTime, nullable=True)

    # When this record was created in the database
    created_at = Column(DateTime, default=datetime.utcnow)

    # Relationships:
    # Clip -> User (many-to-one)
    user = relationship("User", back_populates="clips")

    # Clip -> DetectionEvents (one-to-many)
    # This allows: clip.detection_events
    # Cascade ensures that when a Clip is deleted,
    # all associated DetectionEvents are also deleted
    detection_events = relationship(
        "DetectionEvent",
        back_populates="clip",
        cascade="all, delete"
    )


# ============================================================
# DETECTION EVENT MODEL
# ============================================================
class DetectionEvent(Base):
    """
    Represents a single detection made by the ML model.

    Example:
    - A human detected at a specific moment in time
    - Associated with a specific clip

    Important:
    This is a TIME-SERIES type table (many rows over time).
    """

    __tablename__ = "detection_events"

    # Primary key
    id = Column(Integer, primary_key=True, index=True)

    # Foreign key:
    # Links this event to a clip
    # Indexed for fast lookup of all detection events for a clip
    clip_id = Column(Integer, ForeignKey("clips.id"), nullable=False, index=True)

    # When the detection happened (absolute timestamp)
    # Indexed because we will frequently query by time
    timestamp = Column(DateTime, index=True, nullable=False)

    # Confidence score from the ML model (e.g., 0.0 to 1.0)
    # Indexed to support filtering (e.g., high-confidence detections)
    confidence = Column(Float, nullable=False, index=True)

    # Optional:
    # How many seconds into the clip the detection occurred
    # (useful for precise playback positioning)
    offset_seconds = Column(Float, nullable=True)

    # When this record was created in the database
    created_at = Column(DateTime, default=datetime.utcnow)

    # Relationship:
    # DetectionEvent -> Clip (many-to-one)
    # This allows: event.clip
    clip = relationship("Clip", back_populates="detection_events")

