"""
Database Connection and Session Management
Uses Supabase REST API for database operations
"""
from typing import AsyncGenerator, Optional
from sqlalchemy.ext.asyncio import AsyncSession, create_async_engine, async_sessionmaker
from sqlalchemy.pool import NullPool
import ssl

from app.core.config import settings
from app.db.models import Base

# Flag to track connection mode
USE_SUPABASE_REST = True  # Default to REST API since it works


def get_async_database_url(url: str) -> str:
    """Convert postgresql:// to postgresql+asyncpg:// for async support"""
    if url.startswith("postgresql://"):
        return url.replace("postgresql://", "postgresql+asyncpg://", 1)
    elif url.startswith("postgres://"):
        return url.replace("postgres://", "postgresql+asyncpg://", 1)
    return url


def get_connect_args():
    """Get connection arguments for Supabase SSL"""
    ssl_context = ssl.create_default_context()
    ssl_context.check_hostname = False
    ssl_context.verify_mode = ssl.CERT_NONE
    return {"ssl": ssl_context}


# Try to create async engine (may fail but we have REST fallback)
engine = None
async_session_maker = None

try:
    db_url = get_async_database_url(settings.DATABASE_URL)
    engine = create_async_engine(
        db_url,
        poolclass=NullPool,
        echo=False,
        connect_args=get_connect_args(),
    )
    async_session_maker = async_sessionmaker(
        engine,
        class_=AsyncSession,
        expire_on_commit=False,
        autocommit=False,
        autoflush=False,
    )
except Exception as e:
    print(f"⚠️ SQLAlchemy engine creation failed: {e}")
    print("   Will use Supabase REST API")


async def init_db() -> None:
    """Initialize database connection."""
    global USE_SUPABASE_REST
    
    # Try PostgreSQL first
    if engine:
        try:
            from sqlalchemy import text
            async with engine.begin() as conn:
                await conn.execute(text("SELECT 1"))
            print("✅ PostgreSQL connection successful")
            USE_SUPABASE_REST = False
            return
        except Exception as e:
            print(f"⚠️ PostgreSQL connection failed: {e}")
    
    # Fallback to Supabase REST API
    print("   Using Supabase REST API...")
    try:
        from app.db.supabase_client import init_supabase
        if init_supabase():
            USE_SUPABASE_REST = True
            print("✅ Supabase REST API connected")
        else:
            print("❌ Supabase REST API failed")
    except Exception as e2:
        print(f"❌ Supabase REST also failed: {e2}")


async def get_db() -> AsyncGenerator[AsyncSession, None]:
    """Dependency injection for database sessions."""
    if async_session_maker and not USE_SUPABASE_REST:
        async with async_session_maker() as session:
            try:
                yield session
                await session.commit()
            except Exception:
                await session.rollback()
                raise
            finally:
                await session.close()
    else:
        # Return a dummy session for REST API mode
        # The actual operations will use Supabase client directly
        yield None  # type: ignore


async def close_db() -> None:
    """Close database connections."""
    if engine:
        await engine.dispose()
