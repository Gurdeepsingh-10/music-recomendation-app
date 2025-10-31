from fastapi import APIRouter, Depends
from ..auth import get_current_user
from ..database import get_mongodb
from ..analytics import get_analytics

router = APIRouter(prefix="/analytics", tags=["Analytics"])

@router.get("/me")
async def get_my_stats(current_user: dict = Depends(get_current_user)):
    """Get your listening statistics"""
    db = get_mongodb()
    analytics = get_analytics()
    
    stats = await analytics.get_user_stats(current_user["user_id"], db)
    
    return {
        "user": current_user["user_id"],
        "statistics": stats
    }

@router.get("/system")
async def get_system_stats(current_user: dict = Depends(get_current_user)):
    """Get overall system statistics (all users)"""
    db = get_mongodb()
    analytics = get_analytics()
    
    stats = await analytics.get_system_stats(db)
    
    return {
        "system_statistics": stats
    }

@router.get("/algorithms")
async def get_algorithm_performance(current_user: dict = Depends(get_current_user)):
    """Get recommendation algorithm performance metrics"""
    db = get_mongodb()
    analytics = get_analytics()
    
    performance = await analytics.get_algorithm_performance(db)
    
    return {
        "algorithm_performance": performance
    }