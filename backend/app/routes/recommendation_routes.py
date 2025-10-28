from ..user_profiler import get_profiler
from fastapi import APIRouter, Depends, HTTPException
from ..auth import get_current_user
from ..database import get_postgres, get_mongodb
from ..recommender import get_recommender
from typing import Optional

router = APIRouter(prefix="/recommendations", tags=["Recommendations"])

@router.get("/similar/{track_id}")
async def get_similar_tracks(
    track_id: str,
    limit: int = 20,
    current_user: dict = Depends(get_current_user)
):
    """
    Get tracks similar to a specific track
    Based on audio features (tempo, energy, etc.)
    """
    pool = await get_postgres()  # ✅ FIXED
    recommender = get_recommender()
    
    async with pool.acquire() as conn:
        # Check if track exists
        track = await conn.fetchrow(
            "SELECT * FROM tracks WHERE track_id = $1",
            track_id
        )
        
        if not track:
            raise HTTPException(status_code=404, detail="Track not found")
        
        # Get similar tracks
        similar_tracks = await recommender.get_similar_tracks(
            track_id=track_id,
            conn=conn,
            limit=limit
        )
        
        return {
            "based_on": dict(track),
            "recommendations": similar_tracks,
            "algorithm": "content_based_similarity"
        }


@router.get("/genre/{genre}")
async def get_genre_recommendations(
    genre: str,
    limit: int = 20,
    current_user: dict = Depends(get_current_user)
):
    """Get recommendations from a specific genre"""
    pool = await get_postgres()  # ✅ FIXED
    recommender = get_recommender()
    
    async with pool.acquire() as conn:
        recommendations = await recommender.get_recommendations_by_genre(
            genre=genre,
            conn=conn,
            limit=limit
        )
        
        return {
            "genre": genre,
            "recommendations": recommendations,
            "algorithm": "genre_based"
        }


@router.get("/popular")
async def get_popular_recommendations(
    limit: int = 50,
    current_user: dict = Depends(get_current_user)
):
    """Get popular tracks (for cold start)"""
    pool = await get_postgres()  # ✅ FIXED
    recommender = get_recommender()
    
    async with pool.acquire() as conn:
        recommendations = await recommender.get_popular_tracks(
            conn=conn,
            limit=limit
        )
        
        return {
            "recommendations": recommendations,
            "algorithm": "popularity_based"
        }


@router.get("/for-you")
async def get_personalized_recommendations(
    limit: int = 20,
    current_user: dict = Depends(get_current_user)
):
    """
    Get personalized recommendations based on user's listening history
    Falls back to popular tracks if no history
    """
    pool = await get_postgres()  # ✅ FIXED
    db = get_mongodb()
    recommender = get_recommender()
    
    # Get user's recent listening history
    recent_plays = await db.play_history.find(
        {"user_id": current_user["user_id"]}
    ).sort("played_at", -1).limit(10).to_list(length=10)
    
    async with pool.acquire() as conn:
        if recent_plays:
            # Get recommendations based on recent plays
            seed_track_ids = [play["track_id"] for play in recent_plays]
            recommendations = await recommender.get_diverse_recommendations(
                seed_track_ids=seed_track_ids,
                conn=conn,
                limit=limit
            )
            algorithm = "personalized_content_based"
        else:
            # Cold start: return popular tracks
            recommendations = await recommender.get_popular_tracks(
                conn=conn,
                limit=limit
            )
            algorithm = "cold_start_popular"
        
        return {
            "recommendations": recommendations,
            "algorithm": algorithm,
            "based_on_tracks": len(recent_plays)
        }
@router.get("/personalized")
async def get_personalized_recommendations_advanced(
    limit: int = 20,
    exclude_played: bool = True,
    current_user: dict = Depends(get_current_user)
):
    """
    Advanced personalized recommendations based on user's complete listening profile.
    Uses the user's feature vector built from their listening history.
    """
    pool = await get_postgres()   # ✅ FIXED: added await
    db = get_mongodb()            # MongoDB getter is already sync
    profiler = get_profiler()
    
    async with pool.acquire() as conn:
        recommendations = await profiler.get_personalized_recommendations(
            user_id=current_user["user_id"],
            db=db,
            conn=conn,
            limit=limit,
            exclude_played=exclude_played
        )
        
        if not recommendations:
            # Fallback to popular tracks
            from ..recommender import get_recommender
            recommender = get_recommender()
            recommendations = await recommender.get_popular_tracks(conn=conn, limit=limit)
            algorithm = "fallback_popular"
        else:
            algorithm = "user_based_personalization"
        
        return {
            "recommendations": recommendations,
            "algorithm": algorithm,
            "user_id": current_user["user_id"]
        }


@router.post("/refresh-profile")
async def refresh_user_profile(current_user: dict = Depends(get_current_user)):
    """
    Manually refresh user's taste profile.
    Useful after user has listened to many new tracks.
    """
    pool = await get_postgres()   # ✅ FIXED: added await
    db = get_mongodb()
    profiler = get_profiler()
    
    async with pool.acquire() as conn:
        profile = await profiler.build_user_vector(
            user_id=current_user["user_id"],
            db=db,
            conn=conn
        )
        
        if not profile:
            return {
                "status": "no_data",
                "message": "No listening history found. Listen to some tracks first!"
            }
        
        return {
            "status": "success",
            "message": "Profile refreshed successfully",
            "profile": {
                "total_plays": profile['total_plays'],
                "total_likes": profile['total_likes'],
                "top_genres": list(profile['genre_preferences'].keys())
            }
        }
