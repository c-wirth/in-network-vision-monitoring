from .db_components.connections import SessionLocal
from .db_components import repositories
from pathlib import Path
import cv2
import numpy as np
from datetime import datetime


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

    def create_clip_from_frames(self, clip_data: dict):
        db = self.SessionLocal()
        try:
            # ------------------------
            # 1. SETUP
            # ------------------------
            save_root = Path("~/Desktop/stream_output").expanduser()
            save_root.mkdir(parents=True, exist_ok=True)

            clip_name = clip_data.get("clip_name") or f"clip_{datetime.now().strftime('%Y%m%d_%H%M%S')}"
            video_path = save_root / f"{clip_name}.mp4"

            frames = clip_data.get("frames", [])
            if not frames:
                raise ValueError("No frames in clip_data")

            fps = clip_data.get("fps", 10)

            # ------------------------
            # 2. INIT VIDEO WRITER
            # ------------------------
            first_frame = cv2.imdecode(np.frombuffer(frames[0], np.uint8), cv2.IMREAD_COLOR)
            height, width, _ = first_frame.shape

            fourcc = cv2.VideoWriter_fourcc(*"mp4v")
            writer = cv2.VideoWriter(str(video_path), fourcc, fps, (width, height))

            # ------------------------
            # 3. WRITE FRAMES
            # ------------------------
            for frame_bytes in frames:
                frame = cv2.imdecode(np.frombuffer(frame_bytes, np.uint8), cv2.IMREAD_COLOR)
                writer.write(frame)

            writer.release()

            # ------------------------
            # 4. DB RECORD
            # ------------------------
            clip = repositories.create_clip(db, str(video_path))

            db.commit()
            db.refresh(clip)
            return clip

        except Exception:
            db.rollback()
            raise
        finally:
            db.close()

    def create_clip_from_file(self, file_path: str):
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

    def create_clip_record(self, file_path):
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