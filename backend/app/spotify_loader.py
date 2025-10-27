import asyncpg
from .config import settings
import asyncio
import random

class MusicDatasetLoader:
    """
    Load curated music dataset directly into PostgreSQL
    No external API needed - uses generated realistic data
    """
    
    async def load_sample_dataset(self, target_count=5000):
        """Load realistic sample music data"""
        print(f"🎯 Target: {target_count} tracks")
        print("🔄 Connecting to PostgreSQL...")
        
        conn = await asyncpg.connect(settings.POSTGRES_URL)
        loaded_count = 0
        
        try:
            existing_count = await conn.fetchval("SELECT COUNT(*) FROM tracks")
            print(f"📊 Existing tracks: {existing_count}")
            
            # Realistic music data based on common patterns
            genres = ['Pop', 'Rock', 'Hip-Hop', 'Electronic', 'R&B', 'Country', 'Jazz', 'Classical', 'Indie', 'Latin']
            
            artists_by_genre = {
                'Pop': ['Taylor Swift', 'Ed Sheeran', 'Ariana Grande', 'Dua Lipa', 'The Weeknd', 'Billie Eilish', 'Harry Styles', 'Olivia Rodrigo', 'Selena Gomez', 'Justin Bieber'],
                'Rock': ['Queen', 'The Beatles', 'Led Zeppelin', 'Pink Floyd', 'AC/DC', 'Nirvana', 'Foo Fighters', 'Imagine Dragons', 'Coldplay', 'Arctic Monkeys'],
                'Hip-Hop': ['Drake', 'Kendrick Lamar', 'J. Cole', 'Travis Scott', 'Post Malone', 'Eminem', 'Kanye West', '21 Savage', 'Lil Baby', 'Future'],
                'Electronic': ['Calvin Harris', 'The Chainsmokers', 'Marshmello', 'Kygo', 'Avicii', 'Deadmau5', 'Daft Punk', 'David Guetta', 'Martin Garrix', 'Tiësto'],
                'R&B': ['The Weeknd', 'Frank Ocean', 'SZA', 'Khalid', 'H.E.R.', 'Bryson Tiller', 'Jhené Aiko', 'Summer Walker', 'Brent Faiyaz', 'Daniel Caesar'],
                'Country': ['Luke Combs', 'Morgan Wallen', 'Kane Brown', 'Blake Shelton', 'Carrie Underwood', 'Luke Bryan', 'Thomas Rhett', 'Florida Georgia Line', 'Keith Urban', 'Miranda Lambert'],
                'Jazz': ['Miles Davis', 'John Coltrane', 'Louis Armstrong', 'Billie Holiday', 'Duke Ellington', 'Ella Fitzgerald', 'Charlie Parker', 'Thelonious Monk', 'Nina Simone', 'Herbie Hancock'],
                'Classical': ['Mozart', 'Beethoven', 'Bach', 'Chopin', 'Tchaikovsky', 'Vivaldi', 'Debussy', 'Brahms', 'Handel', 'Schubert'],
                'Indie': ['Tame Impala', 'Arctic Monkeys', 'The 1975', 'Vampire Weekend', 'Mac DeMarco', 'MGMT', 'Foster the People', 'Two Door Cinema Club', 'Phoenix', 'The Strokes'],
                'Latin': ['Bad Bunny', 'J Balvin', 'Rosalía', 'Karol G', 'Ozuna', 'Maluma', 'Daddy Yankee', 'Anuel AA', 'Rauw Alejandro', 'Peso Pluma']
            }
            
            # Genre-specific audio feature ranges
            genre_profiles = {
                'Pop': {'tempo': (100, 130), 'energy': (0.6, 0.9), 'danceability': (0.6, 0.9), 'valence': (0.5, 0.9)},
                'Rock': {'tempo': (110, 140), 'energy': (0.7, 1.0), 'danceability': (0.3, 0.6), 'valence': (0.4, 0.7)},
                'Hip-Hop': {'tempo': (70, 100), 'energy': (0.6, 0.9), 'danceability': (0.7, 1.0), 'valence': (0.3, 0.7)},
                'Electronic': {'tempo': (120, 140), 'energy': (0.7, 1.0), 'danceability': (0.7, 1.0), 'valence': (0.5, 0.9)},
                'R&B': {'tempo': (80, 110), 'energy': (0.4, 0.7), 'danceability': (0.6, 0.8), 'valence': (0.3, 0.6)},
                'Country': {'tempo': (90, 120), 'energy': (0.5, 0.8), 'danceability': (0.5, 0.8), 'valence': (0.5, 0.8)},
                'Jazz': {'tempo': (60, 120), 'energy': (0.3, 0.7), 'danceability': (0.4, 0.7), 'valence': (0.4, 0.7)},
                'Classical': {'tempo': (60, 100), 'energy': (0.2, 0.6), 'danceability': (0.1, 0.4), 'valence': (0.3, 0.7)},
                'Indie': {'tempo': (100, 130), 'energy': (0.5, 0.8), 'danceability': (0.5, 0.7), 'valence': (0.4, 0.7)},
                'Latin': {'tempo': (90, 120), 'energy': (0.7, 0.9), 'danceability': (0.7, 0.95), 'valence': (0.6, 0.9)}
            }
            
            print(f"\n🎵 Generating {target_count} realistic tracks...\n")
            
            track_counter = existing_count + 1
            
            for i in range(target_count):
                genre = random.choice(genres)
                artist = random.choice(artists_by_genre[genre])
                profile = genre_profiles[genre]
                
                # Generate track data
                track_id = f"track_{track_counter:06d}"
                title = f"{random.choice(['Love', 'Night', 'Summer', 'Dream', 'Heart', 'Fire', 'Sky', 'Star', 'Hope', 'Time', 'Blue', 'Gold', 'Wild', 'Sweet', 'Lost', 'Free', 'Dark', 'Light'])} {random.choice(['Song', 'Anthem', 'Melody', 'Beat', 'Rhythm', 'Vibes', 'Dreams', 'Nights', 'Days', 'Life', 'Soul', 'Way', 'Road', 'City', 'World'])}"
                album = f"{artist} - Album {random.randint(1, 10)}"
                year = random.randint(1990, 2024)
                duration = random.uniform(120, 300)
                
                # Audio features based on genre
                tempo = random.uniform(*profile['tempo'])
                energy = random.uniform(*profile['energy'])
                danceability = random.uniform(*profile['danceability'])
                valence = random.uniform(*profile['valence'])
                acousticness = random.uniform(0.0, 0.7)
                instrumentalness = random.uniform(0.0, 0.3) if genre != 'Classical' else random.uniform(0.5, 1.0)
                liveness = random.uniform(0.05, 0.35)
                speechiness = random.uniform(0.03, 0.15) if genre != 'Hip-Hop' else random.uniform(0.15, 0.5)
                loudness = random.uniform(-12, -3)
                
                try:
                    await conn.execute("""
                        INSERT INTO tracks (
                            track_id, title, artist, album, genre, year, duration,
                            tempo, energy, danceability, valence, acousticness,
                            instrumentalness, liveness, speechiness, loudness
                        ) VALUES ($1, $2, $3, $4, $5, $6, $7, $8, $9, $10, $11, $12, $13, $14, $15, $16)
                        ON CONFLICT (track_id) DO NOTHING
                    """,
                        track_id, title, artist, album, genre, year, duration,
                        tempo, energy, danceability, valence, acousticness,
                        instrumentalness, liveness, speechiness, loudness
                    )
                    
                    loaded_count += 1
                    track_counter += 1
                    
                    if loaded_count % 500 == 0:
                        print(f"  ✅ {loaded_count}/{target_count} tracks loaded...")
                
                except Exception as e:
                    print(f"  ⚠️ Error loading track: {e}")
                    continue
            
            total_count = await conn.fetchval("SELECT COUNT(*) FROM tracks")
            
            print(f"\n" + "="*50)
            print(f"✅ Loading complete!")
            print(f"📊 New tracks loaded: {loaded_count}")
            print(f"🎵 Total tracks in database: {total_count}")
            print("="*50)
            
        except Exception as e:
            print(f"\n❌ Error: {e}")
            raise
        finally:
            await conn.close()

async def main():
    print("="*50)
    print("🎵 MUSIC DATASET LOADER")
    print("="*50)
    
    loader = MusicDatasetLoader()
    await loader.load_sample_dataset(target_count=5000)
    
    print("\n✅ All done! Tracks are ready in PostgreSQL.")
    print("💡 Run this script again to load more tracks.")

if __name__ == "__main__":
    asyncio.run(main())