"""JWT utility functions for handling identity conversion."""

from flask_jwt_extended import get_jwt_identity as _get_jwt_identity
from typing import Optional


def get_current_user_id() -> Optional[int]:
    """Get the current user ID from JWT token.
    
    Handles conversion from string to integer identity.
    
    Returns:
        User ID as integer or None if not authenticated
    """
    identity = _get_jwt_identity()
    if identity is None:
        return None
    
    # Convert string identity back to integer
    try:
        return int(identity)
    except (ValueError, TypeError):
        return None


# Re-export for convenience
get_jwt_identity = _get_jwt_identity