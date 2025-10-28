from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from contextlib import asynccontextmanager
from .config import settings
from .database import connect_mongodb, close_mongodb, connect_postgres, close_postgres
from .routes import auth_routes, music_routes, recommendation_routes

@asynccontextmanager
async def lifespan(app: FastAPI):
    # Startup
    print("🚀 Starting Music Recommender API...")
    await connect_mongodb()
    await connect_postgres()
    yield
    # Shutdown
    print("🛑 Shutting down...")
    await close_mongodb()
    await close_postgres()

app = FastAPI(
    title="Music Recommender API",
    description="Hybrid music recommendation system with content-based and user-based filtering",
    version="1.0.0",
    lifespan=lifespan
)

# CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.BACKEND_CORS_ORIGINS,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Include routers
app.include_router(auth_routes.router)
app.include_router(music_routes.router)
app.include_router(recommendation_routes.router)  # This line adds recommendation routes

@app.get("/")
async def root():
    return {
        "message": "Music Recommender API",
        "version": "1.0.0",
        "status": "running"
    }

@app.get("/health")
async def health_check():
    return {"status": "healthy"}