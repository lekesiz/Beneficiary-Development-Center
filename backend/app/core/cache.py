"""
Simple cache implementation for development
In production, use Redis or similar
"""

from datetime import datetime, timedelta
from typing import Any, Optional, Dict


class SimpleCache:
    """Simple in-memory cache implementation."""

    def __init__(self):
        self._cache: Dict[str, Dict[str, Any]] = {}

    def get(self, key: str) -> Optional[Any]:
        """Get value from cache."""
        if key in self._cache:
            entry = self._cache[key]
            if entry["expires_at"] is None or entry["expires_at"] > datetime.utcnow():
                return entry["value"]
            else:
                # Remove expired entry
                del self._cache[key]
        return None

    def set(self, key: str, value: Any, timeout: Optional[int] = None) -> None:
        """
        Set value in cache.

        Args:
            key: Cache key
            value: Value to store
            timeout: Timeout in seconds (None for no expiration)
        """
        expires_at = None
        if timeout is not None:
            expires_at = datetime.utcnow() + timedelta(seconds=timeout)

        self._cache[key] = {"value": value, "expires_at": expires_at}

    def delete(self, key: str) -> None:
        """Delete key from cache."""
        if key in self._cache:
            del self._cache[key]

    def clear(self) -> None:
        """Clear all cache entries."""
        self._cache.clear()


# Global cache instance
cache = SimpleCache()
