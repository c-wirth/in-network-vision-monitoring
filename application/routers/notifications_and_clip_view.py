from fastapi import APIRouter, Depends
from application.services.auth_dependency import get_current_user
from core.db_infrastructure.db_interface import DBInterface

router = APIRouter()

db = DBInterface()


# ------------------------
# GET ALL CLIPS
# ------------------------
@router.get("/clips")
def get_clips(user=Depends(get_current_user)):
    # ignoring user_id (shared system)
    return db.get_clips_by_user(1)  # temporary


# ------------------------
# DELETE CLIP
# ------------------------
@router.delete("/clips/{clip_id}")
def delete_clip(clip_id: int, user=Depends(get_current_user)):
    return db.delete_clip(clip_id)