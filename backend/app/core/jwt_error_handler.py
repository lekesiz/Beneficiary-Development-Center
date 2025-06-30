"""Enhanced JWT error handling."""

from flask import jsonify
from flask_jwt_extended import JWTManager
from flask_jwt_extended.exceptions import (
    NoAuthorizationError, InvalidHeaderError,
    CSRFError, JWTDecodeError, WrongTokenError, RevokedTokenError,
    FreshTokenRequired, UserLookupError, UserClaimsVerificationError
)
import logging

logger = logging.getLogger(__name__)


def register_jwt_error_handlers(jwt: JWTManager):
    """Register detailed JWT error handlers."""
    
    @jwt.invalid_token_loader
    def invalid_token_callback(error_string):
        logger.error(f"JWT Invalid Token: {error_string}")
        return jsonify({
            'message': 'Invalid authentication token',
            'error': 'invalid_token',
            'details': error_string
        }), 401
    
    @jwt.unauthorized_loader
    def missing_token_callback(error_string):
        logger.error(f"JWT Missing Token: {error_string}")
        return jsonify({
            'message': 'Authorization header missing',
            'error': 'missing_token',
            'details': error_string
        }), 401
    
    @jwt.expired_token_loader
    def expired_token_callback(jwt_header, jwt_data):
        logger.error(f"JWT Expired Token: {jwt_data}")
        return jsonify({
            'message': 'Token has expired',
            'error': 'token_expired',
            'token_type': jwt_data.get('type', 'access')
        }), 401
    
    @jwt.revoked_token_loader
    def revoked_token_callback(jwt_header, jwt_data):
        logger.error(f"JWT Revoked Token: {jwt_data}")
        return jsonify({
            'message': 'Token has been revoked',
            'error': 'token_revoked'
        }), 401
    
    @jwt.needs_fresh_token_loader
    def needs_fresh_token_callback(jwt_header, jwt_data):
        return jsonify({
            'message': 'Fresh token required',
            'error': 'fresh_token_required'
        }), 401
    
    @jwt.user_lookup_loader
    def user_lookup_callback(jwt_header, jwt_data):
        """Load user from JWT data."""
        from app.models.user import User
        from app import db
        
        identity = jwt_data["sub"]
        # Convert string identity back to integer
        try:
            user_id = int(identity)
        except (ValueError, TypeError):
            logger.error(f"JWT User Lookup: Invalid identity format: {identity}")
            return None
            
        user = db.session.get(User, user_id)
        
        if user:
            logger.debug(f"JWT User Lookup: Found user {user.email}")
        else:
            logger.error(f"JWT User Lookup: User not found for ID {user_id}")
            
        return user