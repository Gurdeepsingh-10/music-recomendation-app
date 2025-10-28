import numpy as np
from datetime import datetime, timedelta
from typing import Dict, List
import asyncpg
from motor.motor_asyncio import AsyncIOMotorDatabase

class UserProfiler:
    """
    Builds and updates user taste profiles based on listening behavior
    """
    
    def __init__(self):
        self.feature_columns = [
            'tempo', 'energy', 'danceability', 'valence',
            'acousticness', 'instrumentalness', 'liveness',
            'speechiness', 'loudness'
        ]
    
    async def build_user_vector(
        self,
        user_id: str,
        db: AsyncIOMotorDatabase,
        conn: asyncpg.Connection
    ) -> Dict:
        """
        Build user preference vector based on their listening history
        """
        
        print(f"🔄 Building profile for user: {user_id}")
        
        # Get user's listening history (last 100 plays)
        plays = await db.play_history.find(
            {"user_id": user_id}
        ).sort("played_at", -1).limit(100).to_list(length=100)
        
        # Get user's likes
        likes = await db.likes.find(
            {"user_id": user_id}
        ).to_list(length=None)
        
        # Get user's skips
        skips = await db.skips.find(
            {"user_id": user_id}
        ).to_list(length=None)
        
        print(f"📊 User activity: {len(plays)} plays, {len(likes)} likes, {len(skips)} skips")
        
        if not plays and not likes:
            print("⚠️ No user activity found - returning empty profile")
            return None
        
        # Build weighted track list
        track_weights = {}
        
        # Likes get highest weight
        for like in likes:
            track_id = like['track_id']
            track_weights[track_id] = track_weights.get(track_id, 0) + 1.0
        
        # Plays get medium weight (based on completion)
        for play in plays:
            track_id = play['track_id']
            # If they completed the track, higher weight
            if play.get('completed', False):
                track_weights[track_id] = track_weights.get(track_id, 0) + 0.8
            else:
                # Partial play gets lower weight
                duration_played = play.get('duration_played', 0)
                if duration_played > 30:  # At least 30 seconds
                    track_weights[track_id] = track_weights.get(track_id, 0) + 0.5
        
        # Skips get negative weight
        for skip in skips:
            track_id = skip['track_id']
            track_weights[track_id] = track_weights.get(track_id, 0) - 0.5
        
        # Remove tracks with negative or zero weights
        track_weights = {k: v for k, v in track_weights.items() if v > 0}
        
        if not track_weights:
            print("⚠️ No positive track interactions found")
            return None
        
        print(f"✅ Found {len(track_weights)} weighted tracks")
        
        # Get audio features for these tracks
        track_ids = list(track_weights.keys())
        
        query = f"""
            SELECT track_id, {', '.join(self.feature_columns)}
            FROM tracks
            WHERE track_id = ANY($1)
        """
        
        tracks = await conn.fetch(query, track_ids)
        
        if not tracks:
            print("⚠️ No track features found")
            return None
        
        # Build weighted feature vector
        weighted_features = np.zeros(len(self.feature_columns))
        total_weight = 0
        
        for track in tracks:
            track_id = track['track_id']
            weight = track_weights.get(track_id, 0)
            
            if weight > 0:
                features = np.array([float(track[col]) for col in self.feature_columns])
                weighted_features += features * weight
                total_weight += weight
        
        if total_weight == 0:
            return None
        
        # Normalize by total weight
        user_vector = weighted_features / total_weight
        
        # Calculate genre preferences
        genre_weights = {}
        for track in tracks:
            track_id = track['track_id']
            weight = track_weights.get(track_id, 0)
            
            # Get genre from track
            genre_query = "SELECT genre FROM tracks WHERE track_id = $1"
            genre_row = await conn.fetchrow(genre_query, track_id)
            
            if genre_row and genre_row['genre']:
                genre = genre_row['genre']
                genre_weights[genre] = genre_weights.get(genre, 0) + weight
        
        # Normalize genre weights
        total_genre_weight = sum(genre_weights.values())
        if total_genre_weight > 0:
            genre_preferences = {
                genre: weight / total_genre_weight
                for genre, weight in genre_weights.items()
            }
        else:
            genre_preferences = {}
        
        # Sort genres by preference
        top_genres = sorted(
            genre_preferences.items(),
            key=lambda x: x[1],
            reverse=True
        )[:5]
        
        print(f"🎵 Top genres: {[g[0] for g in top_genres]}")
        
        # Create user profile
        user_profile = {
            "user_id": user_id,
            "feature_vector": user_vector.tolist(),
            "genre_preferences": dict(top_genres),
            "total_plays": len(plays),
            "total_likes": len(likes),
            "total_skips": len(skips),
            "last_updated": datetime.utcnow(),
            "track_count": len(track_weights)
        }
        
        # Save to MongoDB
        await db.user_vectors.update_one(
            {"user_id": user_id},
            {"$set": user_profile},
            upsert=True
        )
        
        print(f"✅ User profile saved")
        
        return user_profile
    
    async def get_user_vector(
        self,
        user_id: str,
        db: AsyncIOMotorDatabase
    ) -> Dict:
        """Get cached user vector from MongoDB"""
        
        user_vector = await db.user_vectors.find_one({"user_id": user_id})
        
        if not user_vector:
            return None
        
        # Check if it's stale (older than 24 hours)
        last_updated = user_vector.get('last_updated')
        if last_updated:
            age = datetime.utcnow() - last_updated
            if age > timedelta(hours=24):
                print("⚠️ User vector is stale (>24h old)")
                return None
        
        return user_vector
    
    async def get_personalized_recommendations(
        self,
        user_id: str,
        db: AsyncIOMotorDatabase,
        conn: asyncpg.Connection,
        limit: int = 20,
        exclude_played: bool = True
    ) -> List[Dict]:
        """
        Get personalized recommendations based on user's taste profile
        """
        
        # Try to get cached user vector
        user_profile = await self.get_user_vector(user_id, db)
        
        # If no cache or stale, rebuild
        if not user_profile:
            user_profile = await self.build_user_vector(user_id, db, conn)
        
        if not user_profile:
            print("⚠️ Could not build user profile - no data")
            return []
        
        user_vector = np.array(user_profile['feature_vector'])
        
        # Get tracks to compare against
        # Exclude already played tracks if requested
        if exclude_played:
            played_tracks = await db.play_history.distinct("track_id", {"user_id": user_id})
            
            if played_tracks:
                query = f"""
                    SELECT track_id, title, artist, album, genre, year,
                           {', '.join(self.feature_columns)}
                    FROM tracks
                    WHERE track_id != ALL($1)
                    LIMIT 1000
                """
                candidates = await conn.fetch(query, played_tracks)
            else:
                query = f"""
                    SELECT track_id, title, artist, album, genre, year,
                           {', '.join(self.feature_columns)}
                    FROM tracks
                    LIMIT 1000
                """
                candidates = await conn.fetch(query)
        else:
            query = f"""
                SELECT track_id, title, artist, album, genre, year,
                       {', '.join(self.feature_columns)}
                FROM tracks
                LIMIT 1000
            """
            candidates = await conn.fetch(query)
        
        if not candidates:
            return []
        
        print(f"📊 Evaluating {len(candidates)} candidate tracks")
        
        # Calculate similarity to user profile
        track_scores = []
        
        for track in candidates:
            track_features = np.array([float(track[col]) for col in self.feature_columns])
            
            # Cosine similarity
            dot_product = np.dot(user_vector, track_features)
            user_norm = np.linalg.norm(user_vector)
            track_norm = np.linalg.norm(track_features)
            
            if user_norm > 0 and track_norm > 0:
                similarity = dot_product / (user_norm * track_norm)
            else:
                similarity = 0
            
            # Boost if genre matches user preferences
            genre = track['genre']
            genre_boost = 0
            if genre and genre in user_profile.get('genre_preferences', {}):
                genre_boost = user_profile['genre_preferences'][genre] * 0.2
            
            final_score = similarity + genre_boost
            
            track_dict = dict(track)
            track_dict['personalization_score'] = float(final_score)
            track_scores.append(track_dict)
        
        # Sort by score
        track_scores.sort(key=lambda x: x['personalization_score'], reverse=True)
        
        print(f"✅ Returning top {limit} personalized recommendations")
        
        return track_scores[:limit]


# Singleton instance
_profiler_instance = None

def get_profiler() -> UserProfiler:
    """Get or create profiler instance"""
    global _profiler_instance
    if _profiler_instance is None:
        _profiler_instance = UserProfiler()
    return _profiler_instance