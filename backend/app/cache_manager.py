from typing import Optional, Dict, Any
import json
import hashlib
from datetime import datetime, timedelta

class CacheManager:
    """
    In-memory cache for recommendations and user profiles
    Reduces database load and improves response times
    """
    
    def __init__(self, ttl_minutes: int = 30):
        self.cache: Dict[str, Dict[str, Any]] = {}
        self.ttl_minutes = ttl_minutes
    
    def _get_key(self, prefix: str, identifier: str) -> str:
        """Generate cache key"""
        return f"{prefix}:{identifier}"
    
    def _is_expired(self, timestamp: datetime) -> bool:
        """Check if cache entry is expired"""
        age = datetime.utcnow() - timestamp
        return age > timedelta(minutes=self.ttl_minutes)
    
    def get(self, prefix: str, identifier: str) -> Optional[Any]:
        """Get item from cache"""
        key = self._get_key(prefix, identifier)
        
        if key in self.cache:
            entry = self.cache[key]
            
            if not self._is_expired(entry['timestamp']):
                return entry['data']
            else:
                # Remove expired entry
                del self.cache[key]
        
        return None
    
    def set(self, prefix: str, identifier: str, data: Any):
        """Set item in cache"""
        key = self._get_key(prefix, identifier)
        
        self.cache[key] = {
            'data': data,
            'timestamp': datetime.utcnow()
        }
    
    def clear_user_cache(self, user_id: str):
        """Clear all cache entries for a user"""
        keys_to_remove = [
            k for k in self.cache.keys() 
            if user_id in k
        ]
        
        for key in keys_to_remove:
            del self.cache[key]
    
    def clear_all(self):
        """Clear entire cache"""
        self.cache.clear()
    
    def get_stats(self) -> Dict[str, Any]:
        """Get cache statistics"""
        total_entries = len(self.cache)
        expired = sum(
            1 for entry in self.cache.values()
            if self._is_expired(entry['timestamp'])
        )
        
        return {
            "total_entries": total_entries,
            "active_entries": total_entries - expired,
            "expired_entries": expired,
            "cache_ttl_minutes": self.ttl_minutes
        }


# Singleton instance
_cache_instance = None

def get_cache_manager() -> CacheManager:
    """Get or create cache manager instance"""
    global _cache_instance
    if _cache_instance is None:
        _cache_instance = CacheManager(ttl_minutes=30)
    return _cache_instance