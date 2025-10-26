from pydantic import BaseModel, EmailStr, Field
from typing import Optional, List
from datetime import datetime

# User Models
class UserCreate(BaseModel):
    email: EmailStr
    password: str
    username: str

class UserLogin(BaseModel):
    email: EmailStr
    password: str

class User(BaseModel):
    id: str
    email: EmailStr
    username: str
    created_at: datetime

class Token(BaseModel):
    access_token: str
    token_type: str

# Music Models
class Track(BaseModel):
    track_id: str
    title: str
    artist: str
    album: Optional[str] = None
    genre: Optional[str] = None
    year: Optional[int] = None
    duration: Optional[float] = None
    tempo: Optional[float] = None
    energy: Optional[float] = None
    danceability: Optional[float] = None
    valence: Optional[float] = None

# User Activity Models
class PlayEvent(BaseModel):
    user_id: str
    track_id: str
    played_at: datetime = Field(default_factory=datetime.utcnow)
    duration_played: float  # seconds
    completed: bool = False

class LikeEvent(BaseModel):
    user_id: str
    track_id: str
    liked_at: datetime = Field(default_factory=datetime.utcnow)

class SkipEvent(BaseModel):
    user_id: str
    track_id: str
    skipped_at: datetime = Field(default_factory=datetime.utcnow)
    position: float  # where in the track they skipped

# Recommendation Models
class RecommendationRequest(BaseModel):
    user_id: str
    limit: int = 20

class RecommendationResponse(BaseModel):
    recommendations: List[Track]
    algorithm: str
    generated_at: datetime = Field(default_factory=datetime.utcnow)