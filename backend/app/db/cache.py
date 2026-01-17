"""
Cache Backend for OTP Storage
Supports Redis or in-memory dict for development.
"""
import asyncio
from abc import ABC, abstractmethod
from datetime import datetime, timedelta
from typing import Optional, Dict, Any
import json

from app.core.config import settings


class CacheBackend(ABC):
    """Abstract cache backend interface."""
    
    @abstractmethod
    async def set(self, key: str, value: Any, ttl_seconds: int) -> None:
        """Set a value with TTL."""
        pass
    
    @abstractmethod
    async def get(self, key: str) -> Optional[Any]:
        """Get a value by key."""
        pass
    
    @abstractmethod
    async def delete(self, key: str) -> None:
        """Delete a key."""
        pass
    
    @abstractmethod
    async def exists(self, key: str) -> bool:
        """Check if key exists."""
        pass
    
    @abstractmethod
    async def ttl(self, key: str) -> int:
        """Get remaining TTL in seconds."""
        pass


class InMemoryCache(CacheBackend):
    """
    In-memory cache implementation for development/testing.
    Thread-safe using asyncio locks.
    """
    
    def __init__(self):
        self._store: Dict[str, Dict[str, Any]] = {}
        self._lock = asyncio.Lock()
    
    async def set(self, key: str, value: Any, ttl_seconds: int) -> None:
        """Set a value with TTL."""
        async with self._lock:
            expires_at = datetime.utcnow() + timedelta(seconds=ttl_seconds)
            self._store[key] = {
                "value": json.dumps(value) if not isinstance(value, str) else value,
                "expires_at": expires_at
            }
    
    async def get(self, key: str) -> Optional[Any]:
        """Get a value by key, returns None if expired or not found."""
        async with self._lock:
            if key not in self._store:
                return None
            
            entry = self._store[key]
            if datetime.utcnow() > entry["expires_at"]:
                del self._store[key]
                return None
            
            value = entry["value"]
            try:
                return json.loads(value)
            except (json.JSONDecodeError, TypeError):
                return value
    
    async def delete(self, key: str) -> None:
        """Delete a key."""
        async with self._lock:
            self._store.pop(key, None)
    
    async def exists(self, key: str) -> bool:
        """Check if key exists and is not expired."""
        return await self.get(key) is not None
    
    async def ttl(self, key: str) -> int:
        """Get remaining TTL in seconds."""
        async with self._lock:
            if key not in self._store:
                return -2  # Key doesn't exist
            
            entry = self._store[key]
            remaining = (entry["expires_at"] - datetime.utcnow()).total_seconds()
            
            if remaining <= 0:
                del self._store[key]
                return -2
            
            return int(remaining)
    
    async def cleanup_expired(self) -> int:
        """Remove all expired entries. Returns count of removed entries."""
        async with self._lock:
            now = datetime.utcnow()
            expired_keys = [
                key for key, entry in self._store.items()
                if now > entry["expires_at"]
            ]
            for key in expired_keys:
                del self._store[key]
            return len(expired_keys)


class RedisCache(CacheBackend):
    """
    Redis cache implementation for production.
    """
    
    def __init__(self, redis_url: str):
        self._redis_url = redis_url
        self._redis = None
    
    async def _get_redis(self):
        """Lazy initialization of Redis connection."""
        if self._redis is None:
            import redis.asyncio as redis
            self._redis = redis.from_url(self._redis_url, decode_responses=True)
        return self._redis
    
    async def set(self, key: str, value: Any, ttl_seconds: int) -> None:
        """Set a value with TTL."""
        r = await self._get_redis()
        serialized = json.dumps(value) if not isinstance(value, str) else value
        await r.setex(key, ttl_seconds, serialized)
    
    async def get(self, key: str) -> Optional[Any]:
        """Get a value by key."""
        r = await self._get_redis()
        value = await r.get(key)
        if value is None:
            return None
        try:
            return json.loads(value)
        except (json.JSONDecodeError, TypeError):
            return value
    
    async def delete(self, key: str) -> None:
        """Delete a key."""
        r = await self._get_redis()
        await r.delete(key)
    
    async def exists(self, key: str) -> bool:
        """Check if key exists."""
        r = await self._get_redis()
        return await r.exists(key) > 0
    
    async def ttl(self, key: str) -> int:
        """Get remaining TTL in seconds."""
        r = await self._get_redis()
        return await r.ttl(key)
    
    async def close(self) -> None:
        """Close Redis connection."""
        if self._redis:
            await self._redis.close()


# Global cache instance - use InMemoryCache for development
_cache: Optional[CacheBackend] = None


def get_cache() -> CacheBackend:
    """Get the cache backend instance."""
    global _cache
    if _cache is None:
        # Check if Redis should be used
        if settings.USE_REDIS:
            try:
                _cache = RedisCache(settings.REDIS_URL)
                print("✅ Using Redis cache")
            except Exception as e:
                print(f"⚠️ Redis connection failed: {e}, using in-memory cache")
                _cache = InMemoryCache()
        else:
            print("📦 Using in-memory cache (USE_REDIS=false)")
            _cache = InMemoryCache()
    return _cache


def set_cache(cache: CacheBackend) -> None:
    """Set the cache backend instance (for testing)."""
    global _cache
    _cache = cache
