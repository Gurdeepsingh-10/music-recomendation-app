import numpy as np
from sklearn.preprocessing import StandardScaler
from sklearn.metrics.pairwise import cosine_similarity
import asyncpg
from .config import settings
from typing import List, Dict
import json

class ContentBasedRecommender:
    """
    Content-based recommendation engine
    Recommends tracks based on audio feature similarity
    """
    
    def __init__(self):
        self.feature_columns = [
            'tempo', 'energy', 'danceability', 'valence',
            'acousticness', 'instrumentalness', 'liveness',
            'speechiness', 'loudness'
        ]
        self.scaler = StandardScaler()
        self.tracks_cache = None
        self.features_cache = None
        self.track_ids_cache = None
    
    async def load_all_tracks(self, conn):
        """Load all tracks and their features into memory for fast computation"""
        
        if self.tracks_cache is not None:
            return  # Already loaded
        
        print("🔄 Loading track features into memory...")
        
        query = f"""
            SELECT track_id, title, artist, album, genre, year,
                   {', '.join(self.feature_columns)}
            FROM tracks
            WHERE tempo IS NOT NULL 
            AND energy IS NOT NULL
            ORDER BY track_id
        """
        
        tracks = await conn.fetch(query)
        
        if not tracks:
            raise Exception("No tracks found in database!")
        
        self.tracks_cache = [dict(track) for track in tracks]
        self.track_ids_cache = [track['track_id'] for track in self.tracks_cache]
        
        # Extract feature matrix
        features = []
        for track in self.tracks_cache:
            feature_vector = [float(track[col]) for col in self.feature_columns]
            features.append(feature_vector)
        
        features_array = np.array(features)
        
        # Normalize features
        self.features_cache = self.scaler.fit_transform(features_array)
        
        print(f"✅ Loaded {len(self.tracks_cache)} tracks")
        print(f"📊 Feature matrix shape: {self.features_cache.shape}")
    
    async def get_similar_tracks(
        self,
        track_id: str,
        conn,
        limit: int = 20,
        min_similarity: float = 0.5
    ) -> List[Dict]:
        """
        Find tracks similar to the given track_id
        Returns list of similar tracks with similarity scores
        """
        
        # Load tracks if not already loaded
        await self.load_all_tracks(conn)
        
        # Find the track index
        if track_id not in self.track_ids_cache:
            return []
        
        track_idx = self.track_ids_cache.index(track_id)
        
        # Get feature vector for this track
        query_features = self.features_cache[track_idx].reshape(1, -1)
        
        # Calculate cosine similarity with all tracks
        similarities = cosine_similarity(query_features, self.features_cache)[0]
        
        # Get indices of most similar tracks (excluding the query track itself)
        similar_indices = np.argsort(similarities)[::-1]
        
        # Filter and format results
        recommendations = []
        for idx in similar_indices:
            if idx == track_idx:  # Skip the query track itself
                continue
            
            similarity_score = float(similarities[idx])
            
            if similarity_score < min_similarity:
                continue
            
            track = self.tracks_cache[idx].copy()
            track['similarity_score'] = similarity_score
            recommendations.append(track)
            
            if len(recommendations) >= limit:
                break
        
        return recommendations
    
    async def get_recommendations_by_genre(
        self,
        genre: str,
        conn,
        limit: int = 20
    ) -> List[Dict]:
        """
        Get popular tracks from a specific genre
        Used for cold start when user has no history
        """
        
        await self.load_all_tracks(conn)
        
        # Filter tracks by genre
        genre_tracks = [
            track for track in self.tracks_cache
            if track['genre'] and genre.lower() in track['genre'].lower()
        ]
        
        # Return random sample if we have enough
        if len(genre_tracks) > limit:
            import random
            return random.sample(genre_tracks, limit)
        
        return genre_tracks[:limit]
    
    async def get_recommendations_by_features(
        self,
        target_features: Dict[str, float],
        conn,
        limit: int = 20
    ) -> List[Dict]:
        """
        Get tracks matching specific audio feature profile
        Example: {tempo: 120, energy: 0.8, danceability: 0.7}
        """
        
        await self.load_all_tracks(conn)
        
        # Create feature vector from target features
        query_vector = []
        for col in self.feature_columns:
            query_vector.append(target_features.get(col, 0.5))  # Default to 0.5
        
        query_vector = np.array(query_vector).reshape(1, -1)
        query_normalized = self.scaler.transform(query_vector)
        
        # Calculate similarities
        similarities = cosine_similarity(query_normalized, self.features_cache)[0]
        similar_indices = np.argsort(similarities)[::-1]
        
        # Get top matches
        recommendations = []
        for idx in similar_indices[:limit]:
            track = self.tracks_cache[idx].copy()
            track['similarity_score'] = float(similarities[idx])
            recommendations.append(track)
        
        return recommendations
    
    async def get_popular_tracks(
        self,
        conn,
        limit: int = 50
    ) -> List[Dict]:
        """
        Get popular tracks for cold start
        Based on recency (year) and balanced across genres
        """
        
        await self.load_all_tracks(conn)
        
        # Sort by year (newer = more popular assumption)
        sorted_tracks = sorted(
            self.tracks_cache,
            key=lambda x: (x['year'] or 0, x['track_id']),
            reverse=True
        )
        
        return sorted_tracks[:limit]
    
    async def get_diverse_recommendations(
        self,
        seed_track_ids: List[str],
        conn,
        limit: int = 20
    ) -> List[Dict]:
        """
        Get diverse recommendations based on multiple seed tracks
        Useful when user has listened to several tracks
        """
        
        await self.load_all_tracks(conn)
        
        # Get features for all seed tracks
        seed_indices = []
        for track_id in seed_track_ids:
            if track_id in self.track_ids_cache:
                seed_indices.append(self.track_ids_cache.index(track_id))
        
        if not seed_indices:
            return await self.get_popular_tracks(conn, limit)
        
        # Average the feature vectors of seed tracks
        seed_features = self.features_cache[seed_indices]
        avg_features = np.mean(seed_features, axis=0).reshape(1, -1)
        
        # Find similar tracks
        similarities = cosine_similarity(avg_features, self.features_cache)[0]
        similar_indices = np.argsort(similarities)[::-1]
        
        # Exclude seed tracks from recommendations
        recommendations = []
        for idx in similar_indices:
            if idx in seed_indices:
                continue
            
            track = self.tracks_cache[idx].copy()
            track['similarity_score'] = float(similarities[idx])
            recommendations.append(track)
            
            if len(recommendations) >= limit:
                break
        
        return recommendations


# Singleton instance
_recommender_instance = None

def get_recommender() -> ContentBasedRecommender:
    """Get or create recommender instance"""
    global _recommender_instance
    if _recommender_instance is None:
        _recommender_instance = ContentBasedRecommender()
    return _recommender_instance