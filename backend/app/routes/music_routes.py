from fastapi import APIRouter, Depends, HTTPException
from ..models import PlayEvent, LikeEvent, SkipEvent
from ..auth import get_current_user
from ..database import get_mongodb, get_postgres
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

@router.get("/tracks")
async def get_tracks(
    limit: int = 20,
    offset: int = 0,
    genre: str = None,
    current_user: dict = Depends(get_current_user)
):
    """Get list of tracks with pagination"""
    pool = get_postgres()
    
    async with pool.acquire() as conn:
        if genre:
            query = "SELECT * FROM tracks WHERE genre ILIKE $1 ORDER BY track_id LIMIT $2 OFFSET $3"
            tracks = await conn.fetch(query, f"%{genre}%", limit, offset)
        else:
            query = "SELECT * FROM tracks ORDER BY track_id LIMIT $1 OFFSET $2"
            tracks = await conn.fetch(query, limit, offset)
        
        # Get total count
        if genre:
            total = await conn.fetchval("SELECT COUNT(*) FROM tracks WHERE genre ILIKE $1", f"%{genre}%")
        else:
            total = await conn.fetchval("SELECT COUNT(*) FROM tracks")
        
        return {
            "tracks": [dict(track) for track in tracks],
            "total": total,
            "limit": limit,
            "offset": offset
        }

@router.get("/tracks/{track_id}")
async def get_track(
    track_id: str,
    current_user: dict = Depends(get_current_user)
):
    """Get specific track details"""
    pool = get_postgres()
    
    async with pool.acquire() as conn:
        track = await conn.fetchrow(
            "SELECT * FROM tracks WHERE track_id = $1",
            track_id
        )
        
        if not track:
            raise HTTPException(status_code=404, detail="Track not found")
        
        return {"track": dict(track)}

@router.get("/genres")
async def get_genres(current_user: dict = Depends(get_current_user)):
    """Get list of available genres"""
    pool = get_postgres()
    
    async with pool.acquire() as conn:
        genres = await conn.fetch(
            "SELECT DISTINCT genre FROM tracks WHERE genre IS NOT NULL ORDER BY genre"
        )
        
        return {"genres": [g['genre'] for g in genres]}

@router.get("/search")
async def search_tracks(
    q: str,
    limit: int = 20,
    current_user: dict = Depends(get_current_user)
):
    """Search tracks by title, artist, or album"""
    pool = get_postgres()
    
    async with pool.acquire() as conn:
        query = """
            SELECT * FROM tracks 
            WHERE title ILIKE $1 
               OR artist ILIKE $1 
               OR album ILIKE $1
            LIMIT $2
        """
        search_term = f"%{q}%"
        tracks = await conn.fetch(query, search_term, limit)
        
        return {
            "query": q,
            "results": [dict(track) for track in tracks],
            "count": len(tracks)
        }