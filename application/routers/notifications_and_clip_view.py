from fastapi import APIRouter, Depends
from application.services.auth_dependency import get_current_user
from core.db_infrastructure.db_interface import DBInterface
from pathlib import Path

router = APIRouter()

db = DBInterface()


# ------------------------
# GET ALL CLIPS
# ------------------------
@router.get("/")
def get_clips():
    clips = db.get_all_clips()

    result = []
    for clip in clips:
        filename = Path(clip.file_path).name

        result.append({
            "id": clip.id,
            "url": f"/clips/{filename}"
        })

    return result


# ------------------------
# DELETE CLIP
# ------------------------
@router.delete("/{clip_id}")
def delete_clip(clip_id: int, user=Depends(get_current_user)):
    return db.delete_clip(clip_id)