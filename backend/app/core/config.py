"""
Application Configuration
"""
from pydantic_settings import BaseSettings
from typing import Optional


class Settings(BaseSettings):
    """Application settings loaded from environment variables."""
    
    # Supabase Database Configuration
    # Format: postgresql://postgres.[project-ref]:[password]@aws-0-[region].pooler.supabase.com:6543/postgres
    DATABASE_URL: str = "postgresql://postgres:postgres@localhost:5432/isavs"
    
    # Supabase Project Settings (optional - for direct Supabase client)
    SUPABASE_URL: Optional[str] = None
    SUPABASE_ANON_KEY: Optional[str] = None
    SUPABASE_SERVICE_KEY: Optional[str] = None
    SUPABASE_JWT_SECRET: Optional[str] = None  # For JWT verification
    
    # Redis Cache (optional - falls back to in-memory)
    REDIS_URL: str = "redis://localhost:6379/0"
    USE_REDIS: bool = False
    
    # OTP Settings
    OTP_TTL_SECONDS: int = 60  # 60 seconds as per 2026 spec
    OTP_MAX_RESEND_ATTEMPTS: int = 2
    
    # Face Recognition (Cosine Similarity with 0.6 threshold)
    FACE_SIMILARITY_THRESHOLD: float = 0.6
    
    # Geofencing
    GEOFENCE_RADIUS_METERS: float = 50.0  # 50 meter radius
    CLASSROOM_LATITUDE: Optional[float] = None  # Set in .env
    CLASSROOM_LONGITUDE: Optional[float] = None  # Set in .env
    
    # Security
    SECRET_KEY: str = "your-secret-key-change-in-production"
    
    # Three-Strike Policy
    MAX_CONSECUTIVE_FAILURES: int = 3
    
    # Emotion-based Liveness Detection (2026 Standard)
    REQUIRE_SMILE: bool = False  # Disabled for easier testing
    SMILE_CONFIDENCE_THRESHOLD: float = 0.7
    
    # CORS Origins (Dual Portal System: Teacher Port 2001, Student Port 2002)
    CORS_ORIGINS: str = "http://localhost:2001,http://localhost:2002,http://localhost:3000,http://localhost:5173"
    
    class Config:
        env_file = ".env"
        extra = "ignore"


settings = Settings()
