"""Flask extensions."""
from app import db
import redis
import os

# Redis client (initialized in app factory if Redis URL is available)
redis_client = None

def init_redis(app):
    """Initialize Redis client."""
    global redis_client
    redis_url = app.config.get('REDIS_URL')
    if redis_url:
        try:
            redis_client = redis.from_url(redis_url, decode_responses=True)
            redis_client.ping()
            app.logger.info("Redis connection established")
        except Exception as e:
            app.logger.warning(f"Redis connection failed: {e}")
            redis_client = None
    return redis_client