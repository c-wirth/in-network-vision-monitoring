from .db_components.connections import SessionLocal
from .db_components import repositories


class DBInterface:
    """
    High-level DB interface.

    Responsibilities:
    - Manage DB session lifecycle (open, commit, rollback, close)
    - Delegate data operations to repositories
    - Provide a clean API for service layer

    IMPORTANT:
    - No business logic here (e.g., no password hashing)
    - All methods handle their own transactions
    """

    def __init__(self):
        # Factory used to create new DB sessions
        self.SessionLocal = SessionLocal

    # ------------------------
    # USER
    # ------------------------
    def create_user(self, email, hashed_password, role="user"):
        """
        Create a new user.

        EXPECTATIONS:
        - hashed_password must already be hashed (no hashing here)

        TRANSACTION:
        - Commits on success
        - Rolls back on failure
        """
        db = self.SessionLocal()
        try:
            user = repositories.create_user(db, email, hashed_password, role)
            db.commit()
            db.refresh(user)
            return user
        except Exception:
            db.rollback()
            raise
        finally:
            db.close()

    def get_all_users(self):
        """
        Retrieve all users.

        Used for:
        - determining if a primary user exists
        """
        db = self.SessionLocal()
        try:
            return repositories.get_all_users(db)
        finally:
            db.close()

    def get_user_by_role(self, role):
        """
        Retrieve a user by role (e.g., "primary").

        Used for:
        - notification routing
        """
        db = self.SessionLocal()
        try:
            return repositories.get_user_by_role(db, role)
        finally:
            db.close()

    def get_user_by_email(self, email):
        """
        Retrieve a user by email.

        NOTE:
        - Read-only operation (no commit)
        """
        db = self.SessionLocal()
        try:
            return repositories.get_user_by_email(db, email)
        finally:
            db.close()

    def get_user_by_id(self, user_id):
        """
        Retrieve a user by ID.

        NOTE:
        - Read-only operation (no commit)
        """
        db = self.SessionLocal()
        try:
            return repositories.get_user_by_id(db, user_id)
        finally:
            db.close()

    # ------------------------
    # CLIP
    # ------------------------
    def create_clip(self, file_path):
        """
        Create a new clip record.

        EXPECTATIONS:
        - file_path points to a valid file on disk

        TRANSACTION:
        - Commits on success
        - Rolls back on failure
        """
        db = self.SessionLocal()
        try:
            clip = repositories.create_clip(db, file_path)
            db.commit()
            db.refresh(clip)
            return clip
        except Exception:
            db.rollback()
            raise
        finally:
            db.close()

    def get_clips_by_user(self, user_id):
        """
        Retrieve clips for a user.

        NOTE:
        - Read-only operation
        - Results are limited in repository layer
        """
        db = self.SessionLocal()
        try:
            return repositories.get_clips_by_user(db, user_id)
        finally:
            db.close()

    def delete_clip(self, clip_id):
        """
        Delete a clip.

        BEHAVIOR:
        - If clip does not exist, returns None
        - Otherwise deletes and commits

        TRANSACTION:
        - Commits on success
        - Rolls back on failure
        """
        db = self.SessionLocal()
        try:
            clip = repositories.delete_clip(db, clip_id)
            db.commit()
            return clip
        except Exception:
            db.rollback()
            raise
        finally:
            db.close()