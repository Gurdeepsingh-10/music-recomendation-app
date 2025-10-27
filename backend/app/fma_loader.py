import pandas as pd
import asyncpg
from .config import settings
import asyncio
from pathlib import Path

class FMADatasetLoader:
    """Load Free Music Archive dataset into PostgreSQL"""
    
    def __init__(self):
        self.data_path = Path(__file__).parent.parent.parent / "data" / "fma_metadata"
        
    async def load_tracks(self, limit=None):
        """
        Load real track data from FMA dataset
        """
        print("🔄 Loading FMA dataset CSV files...")
        
        try:
            # Load tracks metadata
            tracks_file = self.data_path / "tracks.csv"
            
            if not tracks_file.exists():
                print(f"❌ File not found: {tracks_file}")
                print("📥 Please download the dataset first:")
                print("   python download_dataset.py")
                return
            
            print("📖 Reading tracks.csv...")
            tracks_df = pd.read_csv(tracks_file, header=[0, 1], index_col=0)
            
            # Flatten multi-level columns
            tracks_df.columns = ['_'.join(col).strip() for col in tracks_df.columns.values]
            
            print(f"✅ Found {len(tracks_df)} tracks in dataset")
            
            if limit:
                tracks_df = tracks_df.head(limit)
                print(f"📊 Loading first {limit} tracks...")
            
            print("🔄 Connecting to PostgreSQL...")
            conn = await asyncpg.connect(settings.POSTGRES_URL)
            
            loaded_count = 0
            skipped_count = 0
            
            try:
                print("\n🎵 Inserting tracks into database...\n")
                
                for idx, row in tracks_df.iterrows():
                    try:
                        # Extract track information
                        track_id = str(idx).zfill(6)
                        
                        # Get title (try multiple column names)
                        title = None
                        for col in ['track_title', 'title', 'track_name']:
                            if col in row and pd.notna(row[col]):
                                title = str(row[col])[:500]
                                break
                        
                        if not title:
                            title = f"Track {track_id}"
                        
                        # Get artist
                        artist = "Unknown Artist"
                        for col in ['artist_name', 'track_artist_name', 'album_artist_name']:
                            if col in row and pd.notna(row[col]):
                                artist = str(row[col])[:500]
                                break
                        
                        # Get album
                        album = "Unknown Album"
                        for col in ['album_title', 'album_name']:
                            if col in row and pd.notna(row[col]):
                                album = str(row[col])[:500]
                                break
                        
                        # Get genre (top level genre)
                        genre = "Unknown"
                        for col in ['track_genre_top', 'track_genres', 'genre']:
                            if col in row and pd.notna(row[col]):
                                genre = str(row[col])[:100]
                                break
                        
                        # Get year
                        year = None
                        for col in ['album_date_released', 'track_date_created', 'year']:
                            if col in row and pd.notna(row[col]):
                                try:
                                    year_str = str(row[col])[:4]
                                    year = int(year_str)
                                    if year < 1900 or year > 2025:
                                        year = None
                                    break
                                except:
                                    continue
                        
                        # Get duration
                        duration = None
                        for col in ['track_duration', 'duration']:
                            if col in row and pd.notna(row[col]):
                                try:
                                    duration = float(row[col])
                                    if duration > 0:
                                        break
                                except:
                                    continue
                        
                        if not duration:
                            duration = 180.0  # default 3 minutes
                        
                        # Audio features (with safe defaults)
                        tempo = float(row.get('track_tempo', 120.0)) if pd.notna(row.get('track_tempo')) else 120.0
                        
                        # For features that should be 0-1, normalize if needed
                        def get_feature(feature_name, default=0.5):
                            val = row.get(feature_name, default)
                            if pd.isna(val):
                                return default
                            val = float(val)
                            # If value is outside 0-1, normalize it
                            if val < 0 or val > 1:
                                return default
                            return val
                        
                        energy = get_feature('track_energy', 0.5)
                        danceability = get_feature('track_danceability', 0.5)
                        valence = get_feature('track_valence', 0.5)
                        acousticness = get_feature('track_acousticness', 0.3)
                        instrumentalness = get_feature('track_instrumentalness', 0.1)
                        liveness = get_feature('track_liveness', 0.15)
                        speechiness = get_feature('track_speechiness', 0.05)
                        
                        # Loudness (typically -60 to 0 dB)
                        loudness = float(row.get('track_loudness', -8.0)) if pd.notna(row.get('track_loudness')) else -8.0
                        if loudness > 0:
                            loudness = -8.0
                        
                        # Insert into database
                        await conn.execute("""
                            INSERT INTO tracks (
                                track_id, title, artist, album, genre, year, duration,
                                tempo, energy, danceability, valence, acousticness,
                                instrumentalness, liveness, speechiness, loudness
                            ) VALUES ($1, $2, $3, $4, $5, $6, $7, $8, $9, $10, $11, $12, $13, $14, $15, $16)
                            ON CONFLICT (track_id) DO NOTHING
                        """,
                            f"fma_{track_id}",
                            title, artist, album, genre, year, duration,
                            tempo, energy, danceability, valence, acousticness,
                            instrumentalness, liveness, speechiness, loudness
                        )
                        
                        loaded_count += 1
                        
                        if loaded_count % 500 == 0:
                            print(f"  ✅ {loaded_count} tracks loaded...")
                    
                    except Exception as e:
                        skipped_count += 1
                        if skipped_count < 10:  # Only show first few errors
                            print(f"  ⚠️ Skipped track {idx}: {e}")
                        continue
                
                total_count = await conn.fetchval("SELECT COUNT(*) FROM tracks")
                
                print(f"\n" + "="*50)
                print(f"✅ Loading complete!")
                print(f"📊 New tracks loaded: {loaded_count}")
                print(f"⏭️  Skipped: {skipped_count}")
                print(f"🎵 Total tracks in database: {total_count}")
                print("="*50)
            
            finally:
                await conn.close()
        
        except Exception as e:
            print(f"\n❌ Error: {e}")
            import traceback
            traceback.print_exc()
            raise

async def main():
    print("="*50)
    print("🎵 FMA DATASET LOADER (REAL DATA)")
    print("="*50)
    
    loader = FMADatasetLoader()
    
    # Load tracks (start with 5000, can do more later)
    await loader.load_tracks(limit=5000)
    
    print("\n✅ All done! Real tracks are loaded.")

if __name__ == "__main__":
    asyncio.run(main())