from motor.motor_asyncio import AsyncIOMotorClient
from typing import Optional
from .config import settings
import asyncpg

# MongoDB Connection
mongodb_client: Optional[AsyncIOMotorClient] = None
mongodb_db = None

async def connect_mongodb():
    global mongodb_client, mongodb_db
    try:
        mongodb_client = AsyncIOMotorClient(settings.MONGODB_URL)
        mongodb_db = mongodb_client.music_recommender
        # Test connection
        await mongodb_client.admin.command('ping')
        print("✅ Connected to MongoDB")
    except Exception as e:
        print(f"❌ MongoDB connection error: {e}")
        raise

async def close_mongodb():
    global mongodb_client
    if mongodb_client:
        mongodb_client.close()
        print("MongoDB connection closed")

def get_mongodb():
    return mongodb_db

# PostgreSQL Connection Pool
postgres_pool: Optional[asyncpg.Pool] = None

async def connect_postgres():
    global postgres_pool
    try:
        # We'll configure this in Step 2 with Supabase credentials
        # For now, just a placeholder
        print("⏳ PostgreSQL connection will be configured in Step 2")
    except Exception as e:
        print(f"❌ PostgreSQL connection error: {e}")
        raise

async def close_postgres():
    global postgres_pool
    if postgres_pool:
        await postgres_pool.close()
        print("PostgreSQL connection closed")

async def get_postgres():
    return postgres_pool
