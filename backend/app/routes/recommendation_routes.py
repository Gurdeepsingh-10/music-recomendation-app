from fastapi import APIRouter, Depends, HTTPException
from ..auth import get_current_user
from ..database import get_postgres, get_mongodb
from ..recommender import get_recommender
from ..hybrid_recommender import get_hybrid_recommender

router = APIRouter(prefix="/recommendations", tags=["Recommendations"])

@router.get("/similar/{track_id}")
async def get_similar_tracks(
    track_id: str,
    limit: int = 20,
    current_user: dict = Depends(get_current_user)
):
    """Get tracks similar to a specific track"""
    pool = get_postgres()
    recommender = get_recommender()
    
    async with pool.acquire() as conn:
        track = await conn.fetchrow(
            "SELECT * FROM tracks WHERE track_id = $1",
            track_id
        )
        
        if not track:
            raise HTTPException(status_code=404, detail="Track not found")
        
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
    pool = get_postgres()
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
    pool = get_postgres()
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
    """Get personalized recommendations based on listening history"""
    pool = get_postgres()
    db = get_mongodb()
    recommender = get_recommender()
    
    recent_plays = await db.play_history.find(
        {"user_id": current_user["user_id"]}
    ).sort("played_at", -1).limit(10).to_list(length=10)
    
    async with pool.acquire() as conn:
        if recent_plays:
            seed_track_ids = [play["track_id"] for play in recent_plays]
            recommendations = await recommender.get_diverse_recommendations(
                seed_track_ids=seed_track_ids,
                conn=conn,
                limit=limit
            )
            algorithm = "personalized_content_based"
        else:
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
    
@router.get("/hybrid")
async def get_hybrid_recommendations(
    limit: int = 20,
    exclude_played: bool = True,
    current_user: dict = Depends(get_current_user)
):
    """
    🎯 HYBRID RECOMMENDATIONS - Best of all algorithms!
    
    Combines:
    - Content-based filtering (audio features)
    - User-based filtering (your taste profile)
    - Popularity signals (what's trending)
    
    Adapts based on your listening history:
    - New user (< 3 plays): Popular & diverse tracks
    - Learning (3-10 plays): Similar to what you've played
    - Personalized (10+ plays): Full hybrid engine
    """
    pool = get_postgres()
    db = get_mongodb()
    hybrid = get_hybrid_recommender()
    
    async with pool.acquire() as conn:
        recommendations = await hybrid.get_hybrid_recommendations(
            user_id=current_user["user_id"],
            db=db,
            conn=conn,
            limit=limit,
            exclude_played=exclude_played
        )
        
        return {
            "recommendations": recommendations,
            "algorithm": "hybrid_multi_strategy",
            "user_id": current_user["user_id"],
            "count": len(recommendations)
        }