from fastapi import APIRouter, Depends, HTTPException
from ..models import PlayEvent, LikeEvent, SkipEvent
from ..auth import get_current_user
from ..database import get_mongodb, get_postgres
from datetime import datetime

router = APIRouter(prefix="/music", tags=["Music"])

# -------------------- PLAY --------------------
@router.post("/play", summary="Log a track play")
async def log_play(event: PlayEvent, current_user: dict = Depends(get_current_user)):
    db = get_mongodb()
    if not db:
        raise HTTPException(status_code=500, detail="MongoDB not connected")

    play_data = event.dict()
    play_data["user_id"] = current_user["user_id"]
    play_data["played_at"] = datetime.utcnow()

    await db.play_history.insert_one(play_data)
    return {"status": "success", "message": "Play logged"}


# -------------------- LIKE --------------------
@router.post("/like", summary="Log a track like")
async def log_like(event: LikeEvent, current_user: dict = Depends(get_current_user)):
    db = get_mongodb()
    if not db:
        raise HTTPException(status_code=500, detail="MongoDB not connected")

    like_data = event.dict()
    like_data["user_id"] = current_user["user_id"]
    like_data["liked_at"] = datetime.utcnow()

    await db.likes.insert_one(like_data)
    return {"status": "success", "message": "Like logged"}


# -------------------- SKIP --------------------
@router.post("/skip", summary="Log a track skip")
async def log_skip(event: SkipEvent, current_user: dict = Depends(get_current_user)):
    db = get_mongodb()
    if not db:
        raise HTTPException(status_code=500, detail="MongoDB not connected")

    skip_data = event.dict()
    skip_data["user_id"] = current_user["user_id"]
    skip_data["skipped_at"] = datetime.utcnow()

    await db.skips.insert_one(skip_data)
    return {"status": "success", "message": "Skip logged"}


# -------------------- HISTORY --------------------
@router.get("/history", summary="Get play history")
async def get_history(limit: int = 50, current_user: dict = Depends(get_current_user)):
    db = get_mongodb()
    if not db:
        raise HTTPException(status_code=500, detail="MongoDB not connected")

    history = await db.play_history.find(
        {"user_id": current_user["user_id"]}
    ).sort("played_at", -1).limit(limit).to_list(length=limit)

    return {"history": history}


# -------------------- TRACK LIST --------------------
@router.get("/tracks", summary="Get list of tracks with pagination")
async def get_tracks(
    limit: int = 20,
    offset: int = 0,
    genre: str = None,
    current_user: dict = Depends(get_current_user)
):
    pool = await get_postgres()
    if not pool:
        raise HTTPException(status_code=500, detail="PostgreSQL not connected")

    async with pool.acquire() as conn:
        if genre:
            query = """
                SELECT * FROM tracks 
                WHERE genre ILIKE $1 
                ORDER BY track_id 
                LIMIT $2 OFFSET $3
            """
            tracks = await conn.fetch(query, f"%{genre}%", limit, offset)
            total = await conn.fetchval(
                "SELECT COUNT(*) FROM tracks WHERE genre ILIKE $1", f"%{genre}%"
            )
        else:
            query = """
                SELECT * FROM tracks 
                ORDER BY track_id 
                LIMIT $1 OFFSET $2
            """
            tracks = await conn.fetch(query, limit, offset)
            total = await conn.fetchval("SELECT COUNT(*) FROM tracks")

        return {
            "tracks": [dict(track) for track in tracks],
            "total": total,
            "limit": limit,
            "offset": offset,
        }


# -------------------- TRACK DETAIL --------------------
@router.get("/tracks/{track_id}", summary="Get specific track details")
async def get_track(
    track_id: str,
    current_user: dict = Depends(get_current_user)
):
    pool = await get_postgres()
    if not pool:
        raise HTTPException(status_code=500, detail="PostgreSQL not connected")

    async with pool.acquire() as conn:
        track = await conn.fetchrow("SELECT * FROM tracks WHERE track_id = $1", track_id)

        if not track:
            raise HTTPException(status_code=404, detail="Track not found")

        return {"track": dict(track)}


# -------------------- GENRES --------------------
@router.get("/genres", summary="Get available genres")
async def get_genres(current_user: dict = Depends(get_current_user)):
    pool = await get_postgres()
    if not pool:
        raise HTTPException(status_code=500, detail="PostgreSQL not connected")

    async with pool.acquire() as conn:
        genres = await conn.fetch(
            "SELECT DISTINCT genre FROM tracks WHERE genre IS NOT NULL ORDER BY genre"
        )
        return {"genres": [g["genre"] for g in genres]}


# -------------------- SEARCH --------------------
@router.get("/search", summary="Search tracks by title, artist, or album")
async def search_tracks(
    q: str,
    limit: int = 20,
    current_user: dict = Depends(get_current_user)
):
    pool = await get_postgres()
    if not pool:
        raise HTTPException(status_code=500, detail="PostgreSQL not connected")

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
            "count": len(tracks),
        }
