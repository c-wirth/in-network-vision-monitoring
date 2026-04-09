from .models import User, Clip


# ============================================================
# USER REPOSITORY
# ============================================================

def create_user(db, email, hashed_password, role="user"):
    """
    Create a new user.
    Does NOT commit.
    """

    user = User(
        email=email,
        hashed_password=hashed_password,
        role=role
    )

    db.add(user)
    db.flush()
    return user


def get_user_by_email(db, email):
    """
    Retrieve a user by email.
    """

    return db.query(User).filter(User.email == email).first()


def get_user_by_id(db, user_id):
    """
    Retrieve a user by ID.
    """

    return db.query(User).filter(User.id == user_id).first()


# ============================================================
# CLIP REPOSITORY
# ============================================================

def create_clip(db, user_id, file_path):
    """
    Create a new clip.
    Does NOT commit.
    """

    clip = Clip(
        user_id=user_id,
        file_path=file_path
    )

    db.add(clip)
    db.flush()
    return clip


def get_clips_by_user(db, user_id, limit=50):
    """
    Get clips for a specific user.
    """

    return (
        db.query(Clip)
        .filter(Clip.user_id == user_id)
        .order_by(Clip.created_at.desc())
        .limit(limit)
        .all()
    )


def get_clip_by_id(db, clip_id):
    """
    Get a clip by ID.
    """

    return db.query(Clip).filter(Clip.id == clip_id).first()


def delete_clip(db, clip_id):
    """
    Delete a clip.
    Does NOT commit.
    """

    clip = get_clip_by_id(db, clip_id)

    if clip:
        db.delete(clip)

    return clip