from motor.motor_asyncio import AsyncIOMotorClient
from .config import settings
import asyncio

async def init_mongodb_collections():
    """Create MongoDB collections for user activity"""
    
    print("🔄 Connecting to MongoDB...")
    client = AsyncIOMotorClient(settings.MONGODB_URL)
    db = client.music_recommender
    
    try:
        print("🔄 Creating collections...")
        
        # Create collections
        collections = ['users', 'play_history', 'likes', 'skips', 'user_vectors']
        
        existing_collections = await db.list_collection_names()
        
        for collection in collections:
            if collection not in existing_collections:
                await db.create_collection(collection)
                print(f"✅ Created collection: {collection}")
            else:
                print(f"⏩ Collection already exists: {collection}")
        
        print("🔄 Creating indexes...")
        
        # Create indexes
        await db.users.create_index("email", unique=True)
        await db.users.create_index("user_id", unique=True)
        await db.play_history.create_index([("user_id", 1), ("played_at", -1)])
        await db.likes.create_index([("user_id", 1), ("track_id", 1)], unique=True)
        await db.skips.create_index([("user_id", 1), ("track_id", 1)])
        await db.user_vectors.create_index("user_id", unique=True)
        
        print("✅ MongoDB collections and indexes created successfully!")
        
    except Exception as e:
        print(f"❌ Error creating MongoDB collections: {e}")
        raise
    finally:
        client.close()

if __name__ == "__main__":
    asyncio.run(init_mongodb_collections())