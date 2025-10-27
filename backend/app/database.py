from motor.motor_asyncio import AsyncIOMotorClient
from typing import Optional
from .config import settings
import asyncpg
import os 

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
        print(f"⏳ MongoDB not configured yet (will setup in Step 2)")

async def close_mongodb():
    global mongodb_client
    if mongodb_client:
        mongodb_client.close()
        print("MongoDB connection closed")

def get_mongodb():
    return mongodb_db

# PostgreSQL Connection Pool (using asyncpg - no compilation needed!)
postgres_pool: Optional[asyncpg.Pool] = None
async def connect_postgres():
    global postgres_pool
    try:
        POSTGRES_URL = os.getenv("POSTGRES_URL")
        if not POSTGRES_URL:
            raise ValueError("❌ POSTGRES_URL not found in environment variables")

        postgres_pool = await asyncpg.create_pool(dsn=POSTGRES_URL)
        async with postgres_pool.acquire() as conn:
            await conn.execute("SELECT 1;")  # simple ping
        print("✅ Connected to PostgreSQL (Supabase)")
    except Exception as e:
        print(f"❌ Failed to connect to PostgreSQL: {e}")

async def close_postgres():
    global postgres_pool
    if postgres_pool:
        await postgres_pool.close()
        print("PostgreSQL connection closed")

async def get_postgres():
    return postgres_pool