"""Cache fallback implementation for when Redis is not available."""

from datetime import datetime, timedelta
from typing import Any, Optional
import logging

logger = logging.getLogger(__name__)


class InMemoryCache:
    """Simple in-memory cache implementation as fallback."""
    
    def __init__(self):
        self._cache = {}
        self._expiry = {}
    
    def get(self, key: str) -> Optional[Any]:
        """Get value from cache."""
        # Check if key exists and not expired
        if key in self._cache:
            if key in self._expiry:
                if datetime.utcnow() > self._expiry[key]:
                    # Expired, remove it
                    del self._cache[key]
                    del self._expiry[key]
                    return None
            return self._cache[key]
        return None
    
    def set(self, key: str, value: Any, timeout: Optional[int] = None) -> bool:
        """Set value in cache with optional timeout in seconds."""
        self._cache[key] = value
        if timeout:
            self._expiry[key] = datetime.utcnow() + timedelta(seconds=timeout)
        return True
    
    def delete(self, key: str) -> bool:
        """Delete key from cache."""
        if key in self._cache:
            del self._cache[key]
            if key in self._expiry:
                del self._expiry[key]
            return True
        return False
    
    def clear(self) -> None:
        """Clear all cache."""
        self._cache.clear()
        self._expiry.clear()


# Global in-memory cache instance
_in_memory_cache = InMemoryCache()


class CacheWrapper:
    """Wrapper that tries Redis cache first, falls back to in-memory."""
    
    def __init__(self, redis_cache):
        self.redis_cache = redis_cache
        self.fallback = _in_memory_cache
    
    def get(self, key: str) -> Optional[Any]:
        """Get value from cache."""
        try:
            if self.redis_cache:
                return self.redis_cache.get(key)
        except Exception as e:
            logger.debug(f"Redis get failed, using fallback: {str(e)}")
        return self.fallback.get(key)
    
    def set(self, key: str, value: Any, timeout: Optional[int] = None) -> bool:
        """Set value in cache."""
        try:
            if self.redis_cache:
                return self.redis_cache.set(key, value, timeout=timeout)
        except Exception as e:
            logger.debug(f"Redis set failed, using fallback: {str(e)}")
        return self.fallback.set(key, value, timeout)
    
    def delete(self, key: str) -> bool:
        """Delete key from cache."""
        try:
            if self.redis_cache:
                return self.redis_cache.delete(key)
        except Exception as e:
            logger.debug(f"Redis delete failed, using fallback: {str(e)}")
        return self.fallback.delete(key)
    
    def clear(self) -> None:
        """Clear cache."""
        try:
            if self.redis_cache:
                self.redis_cache.clear()
        except Exception as e:
            logger.debug(f"Redis clear failed, using fallback: {str(e)}")
        self.fallback.clear()