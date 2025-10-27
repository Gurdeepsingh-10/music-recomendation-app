import asyncpg
from .config import settings
import asyncio

async def init_postgres_tables():
    """Create PostgreSQL tables for music metadata"""
    
    print("🔄 Connecting to PostgreSQL...")
    conn = await asyncpg.connect(settings.POSTGRES_URL)
    
    try:
        print("🔄 Creating tables...")
        
        # Tracks table
        await conn.execute("""
            CREATE TABLE IF NOT EXISTS tracks (
                track_id VARCHAR(255) PRIMARY KEY,
                title VARCHAR(500) NOT NULL,
                artist VARCHAR(500) NOT NULL,
                album VARCHAR(500),
                genre VARCHAR(100),
                year INTEGER,
                duration FLOAT,
                tempo FLOAT,
                energy FLOAT,
                danceability FLOAT,
                valence FLOAT,
                acousticness FLOAT,
                instrumentalness FLOAT,
                liveness FLOAT,
                speechiness FLOAT,
                loudness FLOAT,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        """)
        print("✅ Tracks table created")
        
        # Artists table
        await conn.execute("""
            CREATE TABLE IF NOT EXISTS artists (
                artist_id SERIAL PRIMARY KEY,
                artist_name VARCHAR(500) UNIQUE NOT NULL,
                genre VARCHAR(100),
                popularity INTEGER,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        """)
        print("✅ Artists table created")
        
        # Create indexes for faster queries
        await conn.execute("""
            CREATE INDEX IF NOT EXISTS idx_tracks_artist ON tracks(artist);
        """)
        await conn.execute("""
            CREATE INDEX IF NOT EXISTS idx_tracks_genre ON tracks(genre);
        """)
        await conn.execute("""
            CREATE INDEX IF NOT EXISTS idx_tracks_year ON tracks(year);
        """)
        print("✅ Indexes created")
        
        print("✅ PostgreSQL tables created successfully!")
        
    except Exception as e:
        print(f"❌ Error creating tables: {e}")
        raise
    finally:
        await conn.close()

if __name__ == "__main__":
    asyncio.run(init_postgres_tables())