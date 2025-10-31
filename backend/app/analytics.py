from datetime import datetime, timedelta
from typing import Dict, List
from motor.motor_asyncio import AsyncIOMotorDatabase

class AnalyticsEngine:
    """Track and analyze user behavior and system performance"""
    
    async def get_user_stats(self, user_id: str, db: AsyncIOMotorDatabase) -> Dict:
        """Get comprehensive user statistics"""
        
        # Count activities
        total_plays = await db.play_history.count_documents({"user_id": user_id})
        total_likes = await db.likes.count_documents({"user_id": user_id})
        total_skips = await db.skips.count_documents({"user_id": user_id})
        
        # Get recent activity (last 7 days)
        week_ago = datetime.utcnow() - timedelta(days=7)
        recent_plays = await db.play_history.count_documents({
            "user_id": user_id,
            "played_at": {"$gte": week_ago}
        })
        
        # Get top genres
        pipeline = [
            {"$match": {"user_id": user_id}},
            {"$group": {"_id": "$track_id", "count": {"$sum": 1}}},
            {"$sort": {"count": -1}},
            {"$limit": 10}
        ]
        top_tracks = await db.play_history.aggregate(pipeline).to_list(length=10)
        
        # Calculate engagement score
        if total_plays > 0:
            like_rate = total_likes / total_plays
            skip_rate = total_skips / total_plays
            engagement_score = (like_rate * 100) - (skip_rate * 50)
        else:
            engagement_score = 0
        
        return {
            "user_id": user_id,
            "total_plays": total_plays,
            "total_likes": total_likes,
            "total_skips": total_skips,
            "recent_plays_7d": recent_plays,
            "engagement_score": round(engagement_score, 2),
            "like_rate": round(like_rate * 100, 2) if total_plays > 0 else 0,
            "skip_rate": round(skip_rate * 100, 2) if total_plays > 0 else 0,
            "top_tracks_count": len(top_tracks)
        }
    
    async def get_system_stats(self, db: AsyncIOMotorDatabase) -> Dict:
        """Get overall system statistics"""
        
        total_users = await db.users.count_documents({})
        total_plays = await db.play_history.count_documents({})
        total_likes = await db.likes.count_documents({})
        
        # Active users (played in last 7 days)
        week_ago = datetime.utcnow() - timedelta(days=7)
        active_users = len(await db.play_history.distinct(
            "user_id",
            {"played_at": {"$gte": week_ago}}
        ))
        
        # Most popular tracks (last 30 days)
        month_ago = datetime.utcnow() - timedelta(days=30)
        pipeline = [
            {"$match": {"played_at": {"$gte": month_ago}}},
            {"$group": {"_id": "$track_id", "play_count": {"$sum": 1}}},
            {"$sort": {"play_count": -1}},
            {"$limit": 10}
        ]
        popular_tracks = await db.play_history.aggregate(pipeline).to_list(length=10)
        
        return {
            "total_users": total_users,
            "active_users_7d": active_users,
            "total_plays": total_plays,
            "total_likes": total_likes,
            "avg_plays_per_user": round(total_plays / total_users, 2) if total_users > 0 else 0,
            "popular_tracks_count": len(popular_tracks),
            "timestamp": datetime.utcnow().isoformat()
        }
    
    async def track_recommendation_feedback(
        self,
        user_id: str,
        track_id: str,
        action: str,  # 'play', 'like', 'skip'
        algorithm: str,
        db: AsyncIOMotorDatabase
    ):
        """Track how users interact with recommendations"""
        
        feedback = {
            "user_id": user_id,
            "track_id": track_id,
            "action": action,
            "algorithm": algorithm,
            "timestamp": datetime.utcnow()
        }
        
        await db.recommendation_feedback.insert_one(feedback)
    
    async def get_algorithm_performance(self, db: AsyncIOMotorDatabase) -> Dict:
        """Analyze which recommendation algorithms perform best"""
        
        pipeline = [
            {
                "$group": {
                    "_id": {
                        "algorithm": "$algorithm",
                        "action": "$action"
                    },
                    "count": {"$sum": 1}
                }
            },
            {"$sort": {"count": -1}}
        ]
        
        results = await db.recommendation_feedback.aggregate(pipeline).to_list(length=100)
        
        algorithm_stats = {}
        for result in results:
            algo = result['_id']['algorithm']
            action = result['_id']['action']
            count = result['count']
            
            if algo not in algorithm_stats:
                algorithm_stats[algo] = {"plays": 0, "likes": 0, "skips": 0}
            
            algorithm_stats[algo][action + "s"] = count
        
        # Calculate success rates
        for algo, stats in algorithm_stats.items():
            total = stats['plays'] + stats['likes'] + stats['skips']
            if total > 0:
                stats['like_rate'] = round((stats['likes'] / total) * 100, 2)
                stats['skip_rate'] = round((stats['skips'] / total) * 100, 2)
                stats['total_interactions'] = total
        
        return algorithm_stats


# Singleton instance
_analytics_instance = None

def get_analytics() -> AnalyticsEngine:
    """Get or create analytics engine instance"""
    global _analytics_instance
    if _analytics_instance is None:
        _analytics_instance = AnalyticsEngine()
    return _analytics_instance