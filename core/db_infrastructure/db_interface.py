# core/db_infrastructure/db_components/db_interface
from .db_components.connections import SessionLocal
from .db_components import repositories
from pathlib import Path
import cv2
import numpy as np
from datetime import datetime
import os
from dotenv import load_dotenv
import imageio.v2 as imageio

load_dotenv()
CLIP_PATH = os.getenv("CLIP_STORAGE_PATH")


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

    def get_all_clips(self):
        """
        Retrieve all clips.

        Used for:
        - UI display (global clips, no user filtering)
        """
        db = self.SessionLocal()
        try:
            return repositories.get_all_clips(db)
        finally:
            db.close()

    def get_recent_clips(self, limit=2):
        """
        Return the most recent clips ordered by created_at DESC.

        Needed for cooldown logic:
        - clips[0] = current (just created)
        - clips[1] = previous clip
        """
        session = SessionLocal()
        try:
            return (
                session.query(repositories.Clip)
                .order_by(repositories.Clip.created_at.desc())
                .limit(limit)
                .all()
            )
        finally:
            session.close()

    def create_clip_from_frames(self, clip_data: dict):
        db = self.SessionLocal()
        try:
            # ------------------------
            # 1. SETUP
            # ------------------------
            save_root = Path(CLIP_PATH)
            save_root.mkdir(parents=True, exist_ok=True)

            clip_name = clip_data.get("clip_name") or f"clip_{datetime.now().strftime('%Y%m%d_%H%M%S')}"
            video_path = save_root / f"{clip_name}.mp4"

            frames = clip_data.get("frames", [])
            if not frames:
                raise ValueError("No frames in clip_data")

            fps = clip_data.get("fps", 10)

            # ------------------------
            # 2. PREPARE FRAMES
            # ------------------------
            frames_np = []
            for frame_bytes in frames:
                frame = cv2.imdecode(np.frombuffer(frame_bytes, np.uint8), cv2.IMREAD_COLOR)
                frame = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
                frames_np.append(frame)

            # ------------------------
            # 3. WRITE VIDEO (H.264 via imageio)
            # ------------------------
            imageio.mimsave(video_path, frames_np, fps=fps)

            print(f"[DEBUG] Video written (imageio): {video_path}")

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

    def delete_clip(self, clip_id):
        db = self.SessionLocal()
        try:
            # ------------------------
            # 1. GET CLIP
            # ------------------------
            clip = repositories.get_clip_by_id(db, clip_id)

            if not clip:
                return None

            # ------------------------
            # 2. DELETE FILE
            # ------------------------
            from pathlib import Path

            file_path = Path(clip.file_path)

            if file_path.exists():
                file_path.unlink()
                print(f"[DEBUG] Deleted file: {file_path}")
            else:
                print(f"[WARNING] File not found: {file_path}")

            # ------------------------
            # 3. DELETE DB RECORD
            # ------------------------
            repositories.delete_clip(db, clip_id)

            db.commit()
            return clip

        except Exception:
            db.rollback()
            raise
        finally:
            db.close()