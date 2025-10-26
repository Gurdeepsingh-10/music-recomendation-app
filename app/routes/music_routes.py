from fastapi import APIRouter, Depends, HTTPException
from ..models import PlayEvent, LikeEvent, SkipEvent
from ..auth import get_current_user
from ..database import get_mongodb
from datetime import datetime

router = APIRouter(prefix="/music", tags=["Music"])

@router.post("/play")
async def log_play(event: PlayEvent, current_user: dict = Depends(get_current_user)):
    db = get_mongodb()
    
    play_data = event.dict()
    play_data["user_id"] = current_user["user_id"]
    play_data["played_at"] = datetime.utcnow()
    
    await db.play_history.insert_one(play_data)
    return {"status": "success", "message": "Play logged"}

@router.post("/like")
async def log_like(event: LikeEvent, current_user: dict = Depends(get_current_user)):
    db = get_mongodb()
    
    like_data = event.dict()
    like_data["user_id"] = current_user["user_id"]
    like_data["liked_at"] = datetime.utcnow()
    
    await db.likes.insert_one(like_data)
    return {"status": "success", "message": "Like logged"}

@router.post("/skip")
async def log_skip(event: SkipEvent, current_user: dict = Depends(get_current_user)):
    db = get_mongodb()
    
    skip_data = event.dict()
    skip_data["user_id"] = current_user["user_id"]
    skip_data["skipped_at"] = datetime.utcnow()
    
    await db.skips.insert_one(skip_data)
    return {"status": "success", "message": "Skip logged"}

@router.get("/history")
async def get_history(limit: int = 50, current_user: dict = Depends(get_current_user)):
    db = get_mongodb()
    
    history = await db.play_history.find(
        {"user_id": current_user["user_id"]}
    ).sort("played_at", -1).limit(limit).to_list(length=limit)
    
    return {"history": history}