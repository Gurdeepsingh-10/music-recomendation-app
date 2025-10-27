from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from contextlib import asynccontextmanager
from .config import settings
from .database import connect_mongodb, close_mongodb, connect_postgres, close_postgres
from .routes import auth_routes, music_routes, recommendation_routes


@asynccontextmanager
async def lifespan(app: FastAPI):
    """Handles startup and shutdown events for database connections."""
    try:
        print("🚀 Starting Music Recommender API...")
        await connect_mongodb()
        await connect_postgres()
        yield
    finally:
        print("🛑 Shutting down...")
        await close_mongodb()
        await close_postgres()


# ------------------------------
# FastAPI App Initialization
# ------------------------------
app = FastAPI(
    title="🎵 Music Recommender API",
    description="Hybrid music recommendation system using content-based and collaborative filtering",
    version="1.0.0",
    lifespan=lifespan,
)


# ------------------------------
# CORS Configuration
# ------------------------------
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.BACKEND_CORS_ORIGINS,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


# ------------------------------
# Include Routers
# ------------------------------
app.include_router(auth_routes.router, prefix="/auth", tags=["Authentication"])
app.include_router(music_routes.router, prefix="/music", tags=["Music"])
app.include_router(recommendation_routes.router, prefix="/recommend", tags=["Recommendations"])


# ------------------------------
# Root & Health Check
# ------------------------------
@app.get("/", tags=["Root"])
async def root():
    return {
        "message": "🎶 Music Recommender API is running!",
        "version": "1.0.0",
        "status": "active"
    }


@app.get("/health", tags=["Monitoring"])
async def health_check():
    return {"status": "healthy", "database": "connected"}
