import requests
import json
import time
import random

BASE_URL = "http://localhost:8000"

class MusicUser:
    def __init__(self, username, email, password):
        self.username = username
        self.email = email
        self.password = password
        self.token = None
        self.listened_tracks = []
        self.liked_tracks = []
        self.skipped_tracks = []
    
    def signup(self):
        """Sign up new user"""
        print(f"\n{'='*60}")
        print(f"👤 USER: {self.username}")
        print(f"{'='*60}")
        
        signup_data = {
            "email": self.email,
            "password": self.password,
            "username": self.username
        }
        response = requests.post(f"{BASE_URL}/auth/signup", json=signup_data)
        
        if response.status_code == 201:
            self.token = response.json()["access_token"]
            print(f"✅ Signed up successfully!")
            return True
        elif response.status_code == 400:
            print(f"⚠️ User already exists, logging in...")
            return self.login()
        else:
            print(f"❌ Signup failed: {response.status_code}")
            return False
    
    def login(self):
        """Login existing user"""
        login_data = {"email": self.email, "password": self.password}
        response = requests.post(f"{BASE_URL}/auth/login", json=login_data)
        
        if response.status_code == 200:
            self.token = response.json()["access_token"]
            print(f"✅ Logged in successfully!")
            return True
        else:
            print(f"❌ Login failed")
            return False
    
    def browse_tracks(self, genre=None, limit=10):
        """Browse available tracks"""
        headers = {"Authorization": f"Bearer {self.token}"}
        
        print(f"\n🎵 Browsing tracks{f' (Genre: {genre})' if genre else ''}...")
        
        params = {"limit": limit}
        if genre:
            params["genre"] = genre
        
        response = requests.get(f"{BASE_URL}/music/tracks", params=params, headers=headers)
        
        if response.status_code == 200:
            tracks = response.json()["tracks"]
            print(f"✅ Found {len(tracks)} tracks")
            return tracks
        else:
            print(f"❌ Failed to get tracks")
            return []
    
    def listen_to_track(self, track):
        """Simulate listening to a track"""
        headers = {"Authorization": f"Bearer {self.token}"}
        
        track_id = track["track_id"]
        title = track["title"]
        artist = track["artist"]
        duration = track.get("duration", 180)
        
        # Simulate listening behavior
        listen_duration = random.uniform(30, duration)
        completed = listen_duration > (duration * 0.8)
        
        print(f"\n▶️  Now Playing: '{title}' by {artist}")
        print(f"   Duration: {duration:.0f}s | Listened: {listen_duration:.0f}s | Completed: {completed}")
        
        # Log the play
        play_data = {
            "user_id": "dummy",
            "track_id": track_id,
            "duration_played": listen_duration,
            "completed": completed
        }
        
        response = requests.post(f"{BASE_URL}/music/play", json=play_data, headers=headers)
        
        if response.status_code == 200:
            self.listened_tracks.append(track_id)
            print(f"   ✅ Play logged")
            
            # Decide if user likes or skips
            if completed and random.random() > 0.3:  # 70% chance to like if completed
                self.like_track(track_id, title, artist)
            elif not completed and random.random() > 0.5:  # 50% chance to skip if not completed
                self.skip_track(track_id, title, artist, listen_duration)
            else:
                print(f"   ⚪ Neutral (no action)")
        else:
            print(f"   ❌ Failed to log play")
        
        time.sleep(0.5)  # Simulate time between actions
        return completed
    
    def like_track(self, track_id, title, artist):
        """Like a track"""
        headers = {"Authorization": f"Bearer {self.token}"}
        
        like_data = {
            "user_id": "dummy",
            "track_id": track_id
        }
        
        response = requests.post(f"{BASE_URL}/music/like", json=like_data, headers=headers)
        
        if response.status_code == 200:
            self.liked_tracks.append(track_id)
            print(f"   ❤️  LIKED: '{title}' by {artist}")
        else:
            print(f"   ❌ Failed to like")
    
    def skip_track(self, track_id, title, artist, position):
        """Skip a track"""
        headers = {"Authorization": f"Bearer {self.token}"}
        
        skip_data = {
            "user_id": "dummy",
            "track_id": track_id,
            "position": position
        }
        
        response = requests.post(f"{BASE_URL}/music/skip", json=skip_data, headers=headers)
        
        if response.status_code == 200:
            self.skipped_tracks.append(track_id)
            print(f"   ⏭️  SKIPPED: '{title}' by {artist} at {position:.0f}s")
        else:
            print(f"   ❌ Failed to skip")
    
    def get_recommendations(self, limit=5):
        """Get personalized recommendations"""
        headers = {"Authorization": f"Bearer {self.token}"}
        
        print(f"\n{'='*60}")
        print(f"🎯 GETTING PERSONALIZED RECOMMENDATIONS")
        print(f"{'='*60}")
        
        response = requests.get(f"{BASE_URL}/recommendations/for-you?limit={limit}", headers=headers)
        
        if response.status_code == 200:
            data = response.json()
            recommendations = data["recommendations"]
            algorithm = data["algorithm"]
            
            print(f"\n✅ Algorithm: {algorithm}")
            print(f"📊 Based on {len(self.listened_tracks)} plays, {len(self.liked_tracks)} likes, {len(self.skipped_tracks)} skips")
            print(f"\n🎵 Recommended tracks:")
            
            for i, track in enumerate(recommendations):
                print(f"\n   {i+1}. '{track['title']}' by {track['artist']}")
                print(f"      Genre: {track.get('genre', 'Unknown')}")
                if 'similarity_score' in track:
                    print(f"      Match Score: {track['similarity_score']:.2f}")
                if 'personalization_score' in track:
                    print(f"      Personal Score: {track['personalization_score']:.2f}")
            
            return recommendations
        else:
            print(f"❌ Failed to get recommendations")
            return []
    
    def get_similar_to(self, track_id, title, artist, limit=5):
        """Get tracks similar to a specific track"""
        headers = {"Authorization": f"Bearer {self.token}"}
        
        print(f"\n{'='*60}")
        print(f"🔍 FINDING SIMILAR TRACKS")
        print(f"{'='*60}")
        print(f"Based on: '{title}' by {artist}")
        
        response = requests.get(f"{BASE_URL}/recommendations/similar/{track_id}?limit={limit}", headers=headers)
        
        if response.status_code == 200:
            data = response.json()
            similar = data["recommendations"]
            
            print(f"\n✅ Found {len(similar)} similar tracks:")
            
            for i, track in enumerate(similar):
                print(f"\n   {i+1}. '{track['title']}' by {track['artist']}")
                print(f"      Similarity: {track['similarity_score']:.2f}")
                print(f"      Genre: {track.get('genre', 'Unknown')}")
            
            return similar
        else:
            print(f"❌ Failed to get similar tracks")
            return []
    
    def show_summary(self):
        """Show user activity summary"""
        print(f"\n{'='*60}")
        print(f"📊 SESSION SUMMARY FOR {self.username}")
        print(f"{'='*60}")
        print(f"🎵 Tracks Played: {len(self.listened_tracks)}")
        print(f"❤️  Tracks Liked: {len(self.liked_tracks)}")
        print(f"⏭️  Tracks Skipped: {len(self.skipped_tracks)}")
        print(f"{'='*60}\n")


def simulate_user_session():
    """Simulate a complete user session"""
    
    print("\n" + "="*60)
    print("🎵 MUSIC RECOMMENDER - USER SIMULATION")
    print("="*60)
    
    # Create user
    user_id = random.randint(1000, 9999)
    user = MusicUser(
        username=f"MusicLover{user_id}",
        email=f"user{user_id}@example.com",
        password="password123"
    )
    
    # Step 1: Signup/Login
    if not user.signup():
        return
    
    time.sleep(1)
    
    # Step 2: Browse and listen to tracks (first session - exploring)
    print(f"\n{'='*60}")
    print("📱 SESSION 1: DISCOVERING MUSIC")
    print(f"{'='*60}")
    
    tracks = user.browse_tracks(limit=15)
    
    if not tracks:
        return
    
    # Listen to 5-8 random tracks
    num_tracks = random.randint(5, 8)
    selected_tracks = random.sample(tracks, min(num_tracks, len(tracks)))
    
    for track in selected_tracks:
        user.listen_to_track(track)
    
    time.sleep(1)
    
    # Step 3: Get recommendations based on initial listening
    recommendations = user.get_recommendations(limit=8)
    
    time.sleep(1)
    
    # Step 4: Listen to some recommended tracks
    if recommendations:
        print(f"\n{'='*60}")
        print("📱 SESSION 2: LISTENING TO RECOMMENDATIONS")
        print(f"{'='*60}")
        
        num_recs = random.randint(3, 5)
        selected_recs = random.sample(recommendations, min(num_recs, len(recommendations)))
        
        for track in selected_recs:
            user.listen_to_track(track)
    
    time.sleep(1)
    
    # Step 5: Find similar to a liked track
    if user.liked_tracks:
        print(f"\n{'='*60}")
        print("📱 SESSION 3: EXPLORING SIMILAR MUSIC")
        print(f"{'='*60}")
        
        # Get details of a liked track
        liked_track_id = random.choice(user.liked_tracks)
        headers = {"Authorization": f"Bearer {user.token}"}
        response = requests.get(f"{BASE_URL}/music/tracks/{liked_track_id}", headers=headers)
        
        if response.status_code == 200:
            liked_track = response.json()["track"]
            similar = user.get_similar_to(
                liked_track_id,
                liked_track["title"],
                liked_track["artist"],
                limit=5
            )
            
            # Listen to 2-3 similar tracks
            if similar:
                num_similar = random.randint(2, 3)
                for track in similar[:num_similar]:
                    user.listen_to_track(track)
    
    time.sleep(1)
    
    # Step 6: Final recommendations
    print(f"\n{'='*60}")
    print("📱 FINAL RECOMMENDATIONS (REFINED)")
    print(f"{'='*60}")
    
    user.get_recommendations(limit=10)
    
    # Show summary
    user.show_summary()


def simulate_multiple_users(num_users=3):
    """Simulate multiple users with different music tastes"""
    
    print("\n" + "="*70)
    print("🎵 SIMULATING MULTIPLE USERS WITH DIFFERENT MUSIC PREFERENCES")
    print("="*70)
    
    # Different user profiles
    user_profiles = [
        {"name": "RockFan", "genre": "Rock"},
        {"name": "HipHopHead", "genre": "Hip-Hop"},
        {"name": "PopLover", "genre": "Pop"},
        {"name": "ElectronicVibes", "genre": "Electronic"},
    ]
    
    for i in range(min(num_users, len(user_profiles))):
        profile = user_profiles[i]
        user_id = random.randint(1000, 9999)
        
        user = MusicUser(
            username=f"{profile['name']}{user_id}",
            email=f"{profile['name'].lower()}{user_id}@example.com",
            password="password123"
        )
        
        if not user.signup():
            continue
        
        print(f"\n🎧 Preferred Genre: {profile['genre']}")
        
        # Browse genre-specific tracks
        tracks = user.browse_tracks(genre=profile['genre'], limit=10)
        
        if tracks:
            # Listen to 4-6 tracks
            num_tracks = random.randint(4, 6)
            for track in tracks[:num_tracks]:
                user.listen_to_track(track)
            
            # Get recommendations
            user.get_recommendations(limit=5)
            user.show_summary()
        
        time.sleep(2)


if __name__ == "__main__":
    print("\n🎵 Choose simulation mode:")
    print("1. Single user detailed session")
    print("2. Multiple users with different tastes")
    print("3. Quick test (single user, fewer interactions)")
    
    choice = input("\nEnter choice (1/2/3) or press Enter for default (1): ").strip()
    
    if choice == "2":
        num = input("How many users? (1-4, default 3): ").strip()
        try:
            num_users = int(num) if num else 3
        except:
            num_users = 3
        simulate_multiple_users(num_users)
    elif choice == "3":
        # Quick test
        user_id = random.randint(1000, 9999)
        user = MusicUser(f"QuickTest{user_id}", f"quick{user_id}@example.com", "pass123")
        if user.signup():
            tracks = user.browse_tracks(limit=5)
            for track in tracks[:3]:
                user.listen_to_track(track)
            user.get_recommendations(limit=5)
            user.show_summary()
    else:
        simulate_user_session()
    
    print("\n✅ Simulation complete!")