import numpy as np
from sklearn.preprocessing import StandardScaler
from sklearn.metrics.pairwise import cosine_similarity
import asyncpg
from motor.motor_asyncio import AsyncIOMotorDatabase
from typing import List, Dict, Optional
from .recommender import get_recommender
from .user_profiler import get_profiler

class HybridRecommender:
    """
    Hybrid recommendation engine combining:
    - Content-based filtering (audio features)
    - User-based filtering (listening history)
    - Popularity-based boosting
    """
    
    def __init__(self):
        self.content_recommender = get_recommender()
        self.user_profiler = get_profiler()
        
        # Weights for hybrid scoring
        self.content_weight = 0.4
        self.user_weight = 0.4
        self.popularity_weight = 0.2
    
    async def get_hybrid_recommendations(
        self,
        user_id: str,
        db: AsyncIOMotorDatabase,
        conn: asyncpg.Connection,
        limit: int = 20,
        exclude_played: bool = True
    ) -> List[Dict]:
        """
        Get hybrid recommendations combining all strategies
        """
        
        print(f"🔄 Generating hybrid recommendations for user: {user_id}")
        
        # Check if user has enough history
        play_count = await db.play_history.count_documents({"user_id": user_id})
        like_count = await db.likes.count_documents({"user_id": user_id})
        
        print(f"📊 User history: {play_count} plays, {like_count} likes")
        
        # Get played tracks to exclude
        played_track_ids = []
        if exclude_played:
            played_track_ids = await db.play_history.distinct("track_id", {"user_id": user_id})
            print(f"🚫 Excluding {len(played_track_ids)} already played tracks")
        
        # Strategy selection based on user history
        if play_count < 3:
            # Cold start: Use popularity + genre diversity
            print("❄️ Cold start detected - using popularity-based recommendations")
            return await self._cold_start_recommendations(
                conn=conn,
                exclude_ids=played_track_ids,
                limit=limit
            )
        
        elif play_count < 10:
            # Warm start: Content-based + some popularity
            print("🌡️ Warm start - using content-based with popularity boost")
            return await self._warm_start_recommendations(
                user_id=user_id,
                db=db,
                conn=conn,
                exclude_ids=played_track_ids,
                limit=limit
            )
        
        else:
            # Full hybrid: All strategies combined
            print("🔥 Full hybrid mode - combining all strategies")
            return await self._full_hybrid_recommendations(
                user_id=user_id,
                db=db,
                conn=conn,
                exclude_ids=played_track_ids,
                limit=limit
            )
    
    async def _cold_start_recommendations(
        self,
        conn: asyncpg.Connection,
        exclude_ids: List[str],
        limit: int
    ) -> List[Dict]:
        """
        Cold start strategy: Popular tracks across diverse genres
        """
        
        # Get popular tracks from different genres
        query = """
            WITH ranked_tracks AS (
                SELECT *,
                       ROW_NUMBER() OVER (PARTITION BY genre ORDER BY year DESC, track_id) as rn
                FROM tracks
                WHERE track_id != ALL($1)
                  AND genre IS NOT NULL
            )
            SELECT track_id, title, artist, album, genre, year,
                   tempo, energy, danceability, valence, acousticness,
                   instrumentalness, liveness, speechiness, loudness
            FROM ranked_tracks
            WHERE rn <= 5
            LIMIT $2
        """
        
        tracks = await conn.fetch(query, exclude_ids if exclude_ids else [], limit)
        
        recommendations = []
        for track in tracks:
            track_dict = dict(track)
            # Simple popularity score based on recency
            year = track_dict.get('year', 2000)
            track_dict['hybrid_score'] = min(year / 2024.0, 1.0) if year else 0.5
            track_dict['recommendation_reason'] = 'Popular & Diverse'
            recommendations.append(track_dict)
        
        return recommendations
    
    async def _warm_start_recommendations(
        self,
        user_id: str,
        db: AsyncIOMotorDatabase,
        conn: asyncpg.Connection,
        exclude_ids: List[str],
        limit: int
    ) -> List[Dict]:
        """
        Warm start: Content-based on recent plays + popularity
        """
        
        # Get user's recent plays
        recent_plays = await db.play_history.find(
            {"user_id": user_id}
        ).sort("played_at", -1).limit(5).to_list(length=5)
        
        if not recent_plays:
            return await self._cold_start_recommendations(conn, exclude_ids, limit)
        
        # Get tracks similar to recent plays
        seed_track_ids = [play["track_id"] for play in recent_plays]
        
        # Load recommender data
        await self.content_recommender.load_all_tracks(conn)
        
        # Get diverse recommendations based on seeds
        recommendations = await self.content_recommender.get_diverse_recommendations(
            seed_track_ids=seed_track_ids,
            conn=conn,
            limit=limit * 2  # Get extra for filtering
        )
        
        # Filter out played tracks
        filtered_recs = [
            rec for rec in recommendations
            if rec['track_id'] not in exclude_ids
        ]
        
        # Add hybrid scoring
        for rec in filtered_recs[:limit]:
            content_score = rec.get('similarity_score', 0.5)
            year = rec.get('year', 2000)
            popularity_score = min(year / 2024.0, 1.0) if year else 0.5
            
            rec['hybrid_score'] = (
                content_score * 0.7 +
                popularity_score * 0.3
            )
            rec['recommendation_reason'] = 'Similar to your recent plays'
        
        return filtered_recs[:limit]
    
    async def _full_hybrid_recommendations(
        self,
        user_id: str,
        db: AsyncIOMotorDatabase,
        conn: asyncpg.Connection,
        exclude_ids: List[str],
        limit: int
    ) -> List[Dict]:
        """
        Full hybrid: Combine content-based, user-based, and popularity
        """
        
        # Get candidate tracks (larger pool)
        candidate_limit = min(limit * 5, 500)
        
        if exclude_ids:
            query = """
                SELECT track_id, title, artist, album, genre, year,
                       tempo, energy, danceability, valence, acousticness,
                       instrumentalness, liveness, speechiness, loudness
                FROM tracks
                WHERE track_id != ALL($1)
                ORDER BY RANDOM()
                LIMIT $2
            """
            candidates = await conn.fetch(query, exclude_ids, candidate_limit)
        else:
            query = """
                SELECT track_id, title, artist, album, genre, year,
                       tempo, energy, danceability, valence, acousticness,
                       instrumentalness, liveness, speechiness, loudness
                FROM tracks
                ORDER BY RANDOM()
                LIMIT $1
            """
            candidates = await conn.fetch(query, candidate_limit)
        
        if not candidates:
            return []
        
        print(f"📊 Evaluating {len(candidates)} candidate tracks")
        
        # Load content recommender
        await self.content_recommender.load_all_tracks(conn)
        
        # Get user profile
        user_profile = await self.user_profiler.get_user_vector(user_id, db)
        
        if not user_profile:
            print("🔄 Building user profile...")
            user_profile = await self.user_profiler.build_user_vector(user_id, db, conn)
        
        scored_tracks = []
        
        for track in candidates:
            track_dict = dict(track)
            track_id = track_dict['track_id']
            
            # 1. Content-based score (similarity to user's taste)
            content_score = 0.5  # Default
            
            if user_profile:
                user_vector = np.array(user_profile['feature_vector'])
                track_features = np.array([
                    float(track[col]) for col in [
                        'tempo', 'energy', 'danceability', 'valence',
                        'acousticness', 'instrumentalness', 'liveness',
                        'speechiness', 'loudness'
                    ]
                ])
                
                # Cosine similarity
                dot_product = np.dot(user_vector, track_features)
                user_norm = np.linalg.norm(user_vector)
                track_norm = np.linalg.norm(track_features)
                
                if user_norm > 0 and track_norm > 0:
                    content_score = dot_product / (user_norm * track_norm)
                    content_score = max(0, min(1, content_score))  # Clip to [0,1]
            
            # 2. User-based score (genre preference)
            user_score = 0.5  # Default
            
            if user_profile and 'genre_preferences' in user_profile:
                genre = track_dict.get('genre', '')
                if genre and genre in user_profile['genre_preferences']:
                    user_score = user_profile['genre_preferences'][genre]
                    user_score = min(user_score, 1.0)
            
            # 3. Popularity score (recency)
            popularity_score = 0.5  # Default
            year = track_dict.get('year')
            if year and year > 1900:
                # More recent = higher score
                popularity_score = min((year - 1950) / 74.0, 1.0)  # Normalize 1950-2024
            
            # Combine scores with weights
            hybrid_score = (
                content_score * self.content_weight +
                user_score * self.user_weight +
                popularity_score * self.popularity_weight
            )
            
            track_dict['content_score'] = float(content_score)
            track_dict['user_score'] = float(user_score)
            track_dict['popularity_score'] = float(popularity_score)
            track_dict['hybrid_score'] = float(hybrid_score)
            track_dict['recommendation_reason'] = self._get_recommendation_reason(
                content_score, user_score, popularity_score
            )
            
            scored_tracks.append(track_dict)
        
        # Sort by hybrid score
        scored_tracks.sort(key=lambda x: x['hybrid_score'], reverse=True)
        
        # Add diversity (avoid too many from same artist/genre)
        diverse_recommendations = self._add_diversity(scored_tracks, limit)
        
        print(f"✅ Generated {len(diverse_recommendations)} hybrid recommendations")
        
        return diverse_recommendations
    
    def _get_recommendation_reason(
        self,
        content_score: float,
        user_score: float,
        popularity_score: float
    ) -> str:
        """Generate human-readable recommendation reason"""
        
        scores = {
            'content': content_score,
            'user': user_score,
            'popularity': popularity_score
        }
        
        dominant = max(scores, key=scores.get)
        
        reasons = {
            'content': 'Matches your listening patterns',
            'user': 'Fits your taste profile',
            'popularity': 'Trending and popular'
        }
        
        return reasons[dominant]
    
    def _add_diversity(
        self,
        tracks: List[Dict],
        limit: int
    ) -> List[Dict]:
        """
        Add diversity to recommendations
        Avoid too many tracks from same artist or genre
        """
        
        selected = []
        artist_count = {}
        genre_count = {}
        
        for track in tracks:
            if len(selected) >= limit:
                break
            
            artist = track.get('artist', 'Unknown')
            genre = track.get('genre', 'Unknown')
            
            # Limit tracks per artist (max 2)
            if artist_count.get(artist, 0) >= 2:
                continue
            
            # Limit tracks per genre (max 40% of recommendations)
            if genre_count.get(genre, 0) >= limit * 0.4:
                continue
            
            selected.append(track)
            artist_count[artist] = artist_count.get(artist, 0) + 1
            genre_count[genre] = genre_count.get(genre, 0) + 1
        
        # If we don't have enough diverse tracks, fill with remaining
        if len(selected) < limit:
            remaining = [t for t in tracks if t not in selected]
            selected.extend(remaining[:limit - len(selected)])
        
        return selected


# Singleton instance
_hybrid_recommender_instance = None

def get_hybrid_recommender() -> HybridRecommender:
    """Get or create hybrid recommender instance"""
    global _hybrid_recommender_instance
    if _hybrid_recommender_instance is None:
        _hybrid_recommender_instance = HybridRecommender()
    return _hybrid_recommender_instance