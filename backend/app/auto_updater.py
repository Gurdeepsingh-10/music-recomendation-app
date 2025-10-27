import asyncio
from .spotify_loader import SpotifyDatasetLoader

async def update_dataset():
    """
    Run this daily to keep dataset fresh
    Adds new tracks from trending playlists
    """
    print("🔄 Starting daily dataset update...")
    loader = SpotifyDatasetLoader()
    
    # Load additional 500 tracks each day
    await loader.load_tracks_from_playlists(target_count=500)
    
    print("✅ Daily update complete!")

if __name__ == "__main__":
    asyncio.run(update_dataset())