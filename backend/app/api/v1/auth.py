"""Authentication API endpoints."""
from datetime import datetime, timedelta
from flask import Blueprint, request, jsonify, current_app
from flask_jwt_extended import (
    create_access_token, create_refresh_token,
    jwt_required, get_jwt_identity, get_jwt
)
from app.models.user import User
from app.models.tenant import Tenant
from app.services.auth_service import AuthService
from app.utils.validators import validate_email, validate_password
from app.utils.decorators import rate_limit
from app import db, cache

auth_bp = Blueprint('auth', __name__)


@auth_bp.route('/register', methods=['POST'])
@rate_limit("5 per hour")
def register():
    """Register a new user."""
    data = request.get_json()
    
    # Validate required fields
    required_fields = ['email', 'password', 'first_name', 'last_name', 'tenant_id']
    for field in required_fields:
        if field not in data:
            return jsonify({'message': f'{field} is required'}), 400
    
    # Validate email
    if not validate_email(data['email']):
        return jsonify({'message': 'Invalid email format'}), 400
    
    # Validate password
    is_valid, message = validate_password(data['password'])
    if not is_valid:
        return jsonify({'message': message}), 400
    
    # Check if tenant exists
    tenant = Tenant.query.get(data['tenant_id'])
    if not tenant or not tenant.is_active:
        return jsonify({'message': 'Invalid tenant'}), 400
    
    # Check if email already exists for this tenant
    existing_user = User.query.filter_by(
        email=data['email'],
        tenant_id=data['tenant_id']
    ).first()
    
    if existing_user:
        return jsonify({'message': 'Email already registered'}), 409
    
    # Check if tenant can add more users
    if not tenant.can_add_user():
        return jsonify({'message': 'Tenant user limit reached'}), 403
    
    try:
        # Create user
        user = AuthService.register_user(data)
        
        # Generate tokens
        access_token = create_access_token(
            identity=user.id,
            additional_claims={
                'tenant_id': user.tenant_id,
                'role': user.role
            }
        )
        refresh_token = create_refresh_token(
            identity=user.id,
            additional_claims={'tenant_id': user.tenant_id}
        )
        
        return jsonify({
            'message': 'User registered successfully',
            'user': user.to_dict(),
            'access_token': access_token,
            'refresh_token': refresh_token
        }), 201
        
    except Exception as e:
        db.session.rollback()
        current_app.logger.error(f"Registration error: {str(e)}")
        return jsonify({'message': 'Registration failed'}), 500


@auth_bp.route('/login', methods=['POST'])
@rate_limit("10 per hour")
def login():
    """Login user."""
    data = request.get_json()
    
    # Validate required fields
    if not data.get('email') or not data.get('password'):
        return jsonify({'message': 'Email and password are required'}), 400
    
    # Get tenant ID from header or data
    tenant_id = request.headers.get(current_app.config['TENANT_HEADER'])
    if not tenant_id and 'tenant_id' in data:
        tenant_id = data['tenant_id']
    
    if not tenant_id:
        return jsonify({'message': 'Tenant ID is required'}), 400
    
    # Find user
    user = User.query.filter_by(
        email=data['email'],
        tenant_id=int(tenant_id)
    ).first()
    
    if not user:
        return jsonify({'message': 'Invalid credentials'}), 401
    
    # Check if account is locked
    if user.is_locked():
        return jsonify({'message': 'Account is locked. Please try again later.'}), 403
    
    # Verify password
    if not user.verify_password(data['password']):
        user.increment_failed_login()
        return jsonify({'message': 'Invalid credentials'}), 401
    
    # Check if user is active
    if not user.is_active:
        return jsonify({'message': 'Account is inactive'}), 403
    
    # Check if tenant is active
    if not user.tenant.is_active:
        return jsonify({'message': 'Tenant is inactive'}), 403
    
    # Update last login
    user.update_last_login(request.remote_addr)
    
    # Generate tokens
    access_token = create_access_token(
        identity=user.id,
        additional_claims={
            'tenant_id': user.tenant_id,
            'role': user.role
        }
    )
    refresh_token = create_refresh_token(
        identity=user.id,
        additional_claims={'tenant_id': user.tenant_id}
    )
    
    return jsonify({
        'user': user.to_dict(),
        'access_token': access_token,
        'refresh_token': refresh_token
    }), 200


@auth_bp.route('/refresh', methods=['POST'])
@jwt_required(refresh=True)
def refresh():
    """Refresh access token."""
    identity = get_jwt_identity()
    claims = get_jwt()
    
    # Get user
    user = User.query.get(identity)
    if not user or not user.is_active:
        return jsonify({'message': 'Invalid user'}), 401
    
    # Generate new access token
    access_token = create_access_token(
        identity=user.id,
        additional_claims={
            'tenant_id': user.tenant_id,
            'role': user.role
        }
    )
    
    return jsonify({'access_token': access_token}), 200


@auth_bp.route('/logout', methods=['POST'])
@jwt_required()
def logout():
    """Logout user."""
    # Get token ID
    jti = get_jwt()['jti']
    
    # Add token to blacklist (using Redis)
    try:
        # Token will be blacklisted for its remaining lifetime
        token_exp = get_jwt()['exp']
        now = datetime.utcnow()
        expires_in = token_exp - int(now.timestamp())
        
        if expires_in > 0:
            cache.set(f"blacklist_{jti}", "true", timeout=expires_in)
        
        return jsonify({'message': 'Logged out successfully'}), 200
    except Exception as e:
        current_app.logger.error(f"Logout error: {str(e)}")
        return jsonify({'message': 'Logout failed'}), 500


@auth_bp.route('/forgot-password', methods=['POST'])
@rate_limit("3 per hour")
def forgot_password():
    """Request password reset."""
    data = request.get_json()
    
    if not data.get('email'):
        return jsonify({'message': 'Email is required'}), 400
    
    # Get tenant ID
    tenant_id = request.headers.get(current_app.config['TENANT_HEADER'])
    if not tenant_id and 'tenant_id' in data:
        tenant_id = data['tenant_id']
    
    if not tenant_id:
        return jsonify({'message': 'Tenant ID is required'}), 400
    
    # Find user
    user = User.query.filter_by(
        email=data['email'],
        tenant_id=int(tenant_id)
    ).first()
    
    # Always return success to prevent email enumeration
    if user and user.is_active:
        try:
            AuthService.send_password_reset_email(user)
        except Exception as e:
            current_app.logger.error(f"Password reset email error: {str(e)}")
    
    return jsonify({
        'message': 'If the email exists, a password reset link has been sent.'
    }), 200


@auth_bp.route('/reset-password', methods=['POST'])
def reset_password():
    """Reset password with token."""
    data = request.get_json()
    
    if not data.get('token') or not data.get('password'):
        return jsonify({'message': 'Token and password are required'}), 400
    
    # Validate password
    is_valid, message = validate_password(data['password'])
    if not is_valid:
        return jsonify({'message': message}), 400
    
    # Reset password
    try:
        user = AuthService.reset_password(data['token'], data['password'])
        if user:
            return jsonify({'message': 'Password reset successfully'}), 200
        else:
            return jsonify({'message': 'Invalid or expired token'}), 400
    except Exception as e:
        current_app.logger.error(f"Password reset error: {str(e)}")
        return jsonify({'message': 'Password reset failed'}), 500


@auth_bp.route('/verify-email/<token>', methods=['GET'])
def verify_email(token):
    """Verify email address."""
    try:
        user = AuthService.verify_email(token)
        if user:
            return jsonify({'message': 'Email verified successfully'}), 200
        else:
            return jsonify({'message': 'Invalid or expired token'}), 400
    except Exception as e:
        current_app.logger.error(f"Email verification error: {str(e)}")
        return jsonify({'message': 'Email verification failed'}), 500


@auth_bp.route('/me', methods=['GET'])
@jwt_required()
def get_current_user():
    """Get current user information."""
    user_id = get_jwt_identity()
    user = User.query.get(user_id)
    
    if not user:
        return jsonify({'message': 'User not found'}), 404
    
    return jsonify({'user': user.to_dict(include_roles=True)}), 200


@auth_bp.route('/change-password', methods=['POST'])
@jwt_required()
def change_password():
    """Change user password."""
    user_id = get_jwt_identity()
    user = User.query.get(user_id)
    
    if not user:
        return jsonify({'message': 'User not found'}), 404
    
    data = request.get_json()
    
    if not data.get('old_password') or not data.get('new_password'):
        return jsonify({'message': 'Old and new passwords are required'}), 400
    
    # Verify old password
    if not user.verify_password(data['old_password']):
        return jsonify({'message': 'Invalid old password'}), 401
    
    # Validate new password
    is_valid, message = validate_password(data['new_password'])
    if not is_valid:
        return jsonify({'message': message}), 400
    
    # Update password
    user.set_password(data['new_password'])
    user.save()
    
    return jsonify({'message': 'Password changed successfully'}), 200