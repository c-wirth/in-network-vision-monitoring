from .models import User, Clip, DetectionEvent


# ============================================================
# ============================================================
# ============================================================
"""
User Repository (MVP)

Handles database operations related to User.
Only includes what we need for the demo.
"""
# ============================================================
# ============================================================
# ============================================================

# ============================================================
# CREATE
# ============================================================

def create_user(db, email, hashed_password, role="user"):
    """
    Create a new user and add it to the database session.

    NOTE:
    - This does NOT commit the transaction.
    - Caller is responsible for db.commit() or db.rollback()
    """

    user = User(
        email=email,
        hashed_password=hashed_password,
        role=role
    )

    db.add(user)

    # Flush ensures user.id is available immediately
    # This is important for service layer workflows
    db.flush()

    return user


# ============================================================
# READ
# ============================================================

def get_user_by_email(db, email):
    """
    Retrieve a user by their email.

    Returns:
    - User object if found
    - None if not found
    """

    return db.query(User).filter(User.email == email).first()

# ============================================================
# ============================================================
# ============================================================
"""
Clip Repository (MVP)

Handles database operations related to Clip.
"""
# ============================================================
# ============================================================
# ============================================================

# ============================================================
# CREATE
# ============================================================

def create_clip(db, user_id, file_path, start_time, end_time=None):
    """
    Create a new clip.

    NOTE:
    - Does NOT commit
    - Caller is responsible for db.commit() or db.rollback()
    """

    clip = Clip(
        user_id=user_id,
        file_path=file_path,
        start_time=start_time,
        end_time=end_time
    )

    db.add(clip)

    # Flush sends the INSERT to the database without committing
    # This ensures clip.id is available immediately
    db.flush()

    return clip

# ============================================================
# READ
# ============================================================

def get_clips_by_user(db, user_id, limit=50):
    """
    Get clips for a specific user.

    Returns:
    - List of Clip objects (possibly empty)

    NOTE:
    - Results are limited to prevent large queries
    """

    return (
        db.query(Clip)
        .filter(Clip.user_id == user_id)
        # Order by newest clips first so results are consistent and predictable
        .order_by(Clip.created_at.desc())
        # Limit results to avoid large queries
        .limit(limit)
        .all()
    )


def get_clip_by_id(db, clip_id):
    """
    Get a single clip by ID.

    Useful for validating existence before deletion.
    """

    return db.query(Clip).filter(Clip.id == clip_id).first()


# ============================================================
# DELETE
# ============================================================

def delete_clip(db, clip_id):
    """
    Delete a clip.

    IMPORTANT:
    - Due to cascade, associated DetectionEvents will also be deleted.
    - Does NOT commit.
    - Caller is responsible for db.commit() or db.rollback()
    """

    clip = get_clip_by_id(db, clip_id)

    if clip:
        db.delete(clip)

    # Returns:
    # - Clip object if it existed and was deleted
    # - None if no clip was found with that ID
    return clip


# ============================================================
# ============================================================
# ============================================================
"""
Detection Event Repository (MVP)

Handles database operations related to DetectionEvent.
"""
# ============================================================
# ============================================================
# ============================================================

# ============================================================
# CREATE
# ============================================================

def create_event(db, clip_id, timestamp, confidence, offset_seconds=None):
    """
    Create a new detection event.

    NOTE:
    - Does NOT commit
    - Caller is responsible for db.commit() or db.rollback()
    """

    event = DetectionEvent(
        clip_id=clip_id,
        timestamp=timestamp,
        confidence=confidence,
        offset_seconds=offset_seconds
    )

    db.add(event)

    # Flush ensures event.id is generated before commit
    db.flush()

    return event



# ============================================================
# READ
# ============================================================

def get_events_by_clip(db, clip_id, limit=50):
    """
    Get detection events for a specific clip.

    Returns:
    - List of DetectionEvent objects

    Ordered by most recent first.
    """

    return (
        db.query(DetectionEvent)
        .filter(DetectionEvent.clip_id == clip_id)
        .order_by(DetectionEvent.timestamp.desc())
        .limit(limit)
        .all()
    )


def get_recent_events(db, limit=50):
    """
    Get most recent detection events across all clips.

    Returns:
    - List of DetectionEvent objects

    Ordered by newest first.
    """

    return (
        db.query(DetectionEvent)
        .order_by(DetectionEvent.timestamp.desc())
        .limit(limit)
        .all()
    )