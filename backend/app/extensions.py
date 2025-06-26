"""Flask extensions initialization.

This module initializes all Flask extensions in a single place
to avoid circular imports.
"""

from flask_sqlalchemy import SQLAlchemy
from flask_migrate import Migrate
from flask_jwt_extended import JWTManager
from flask_cors import CORS
from flask_caching import Cache
from flask_limiter import Limiter
from flask_limiter.util import get_remote_address
from flask_socketio import SocketIO
from flask_mail import Mail

# Initialize extensions
db = SQLAlchemy()

# Monkey patch for SQLAlchemy 2.x compatibility
# Add remove() method to Session class if it doesn't exist
def _add_remove_method():
    """Add remove() method to Session for backwards compatibility"""
    from sqlalchemy.orm import Session
    if not hasattr(Session, 'remove'):
        Session.remove = Session.close

try:
    _add_remove_method()
except Exception:
    pass  # Ignore if patching fails
migrate = Migrate()
jwt = JWTManager()
cors = CORS()
cache = Cache()
limiter = Limiter(key_func=get_remote_address)
socketio = SocketIO()
mail = Mail()

# Redis client placeholder for testing
redis_client = None
