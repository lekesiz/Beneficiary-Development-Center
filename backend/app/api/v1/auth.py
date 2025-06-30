"""Authentication API endpoints."""

from datetime import datetime
from flask import Blueprint, request, jsonify, current_app
from flask_jwt_extended import create_access_token, create_refresh_token, jwt_required, get_jwt_identity, get_jwt
from app.models.user import User
from app.models.tenant import Tenant
from app.services.auth_service import AuthService
from app.utils.validators import validate_email, validate_password
from app.utils.decorators import rate_limit
from app.core.logging import log_user_action, log_security_event
from app import db, cache

auth_bp = Blueprint("auth", __name__)


@auth_bp.route("/register", methods=["POST"])
@rate_limit("5 per hour")
def register():
    """User Registration
    ---
    post:
      tags:
        - Authentication
      summary: Register a new user
      description: |
        Register a new user account with email, password, and personal information.
        The user will be associated with the specified tenant.
      requestBody:
        required: true
        content:
          application/json:
            schema:
              type: object
              required:
                - email
                - password
                - first_name
                - last_name
                - tenant_id
              properties:
                email:
                  type: string
                  format: email
                  description: User email address
                  example: user@example.com
                password:
                  type: string
                  format: password
                  description: Strong password (min 8 chars)
                  example: SecurePassword123!
                first_name:
                  type: string
                  description: User's first name
                  example: John
                last_name:
                  type: string
                  description: User's last name
                  example: Doe
                tenant_id:
                  type: integer
                  description: ID of the tenant to associate with
                  example: 1
      responses:
        201:
          description: User registered successfully
          content:
            application/json:
              schema:
                type: object
                properties:
                  message:
                    type: string
                    example: User registered successfully
                  user:
                    $ref: '#/components/schemas/User'
                  access_token:
                    type: string
                    description: JWT access token
                  refresh_token:
                    type: string
                    description: JWT refresh token
        400:
          description: Invalid input data
          content:
            application/json:
              schema:
                $ref: '#/components/schemas/Error'
        403:
          description: Tenant user limit reached
          content:
            application/json:
              schema:
                $ref: '#/components/schemas/Error'
        409:
          description: Email already registered
          content:
            application/json:
              schema:
                $ref: '#/components/schemas/Error'
        429:
          description: Rate limit exceeded
          content:
            application/json:
              schema:
                $ref: '#/components/schemas/Error'
        500:
          description: Registration failed
          content:
            application/json:
              schema:
                $ref: '#/components/schemas/Error'
    """
    data = request.get_json()

    # Validate required fields
    required_fields = ["email", "password", "first_name", "last_name", "tenant_id"]
    for field in required_fields:
        if field not in data:
            return jsonify({"message": f"{field} is required"}), 400

    # Validate email
    if not validate_email(data["email"]):
        return jsonify({"message": "Invalid email format"}), 400

    # Validate password
    is_valid, message = validate_password(data["password"])
    if not is_valid:
        return jsonify({"message": message}), 400

    # Check if tenant exists
    tenant = db.session.get(Tenant, data["tenant_id"])
    if not tenant or not tenant.is_active:
        return jsonify({"message": "Invalid tenant"}), 400

    # Check if email already exists for this tenant
    existing_user = db.session.query(User).filter_by(email=data["email"], tenant_id=data["tenant_id"]).first()

    if existing_user:
        return jsonify({"message": "Email already registered"}), 409

    # Check if tenant can add more users
    if not tenant.can_add_user():
        return jsonify({"message": "Tenant user limit reached"}), 403

    try:
        # Create user
        user = AuthService.register_user(data)

        # Log user registration
        log_user_action("register", user_id=user.id, tenant_id=user.tenant_id, email=user.email, role=user.role)

        # Generate tokens
        access_token = create_access_token(
            identity=user.id, additional_claims={"tenant_id": user.tenant_id, "role": user.role}
        )
        refresh_token = create_refresh_token(identity=user.id, additional_claims={"tenant_id": user.tenant_id})

        return (
            jsonify(
                {
                    "message": "User registered successfully",
                    "user": user.to_dict(),
                    "access_token": access_token,
                    "refresh_token": refresh_token,
                }
            ),
            201,
        )

    except Exception as e:
        db.session.rollback()
        current_app.logger.error(f"Registration error: {str(e)}")
        return jsonify({"message": "Registration failed"}), 500


@auth_bp.route("/login", methods=["POST"])
@rate_limit("10 per hour")
def login():
    """User Authentication
    ---
    post:
      tags:
        - Authentication
      summary: Authenticate a user and get access tokens
      description: |
        Authenticate a user with email and password to get JWT access and refresh tokens.
        The tenant context can be provided via header or request body.
      requestBody:
        required: true
        content:
          application/json:
            schema:
              type: object
              required:
                - email
                - password
              properties:
                email:
                  type: string
                  format: email
                  description: User email address
                  example: admin@bdc.com
                password:
                  type: string
                  format: password
                  description: User password
                  example: admin123
                tenant_id:
                  type: integer
                  description: Tenant ID (if not provided in header)
                  example: 1
      parameters:
        - in: header
          name: X-Tenant-ID
          schema:
            type: string
          description: Tenant ID header
          example: "1"
      responses:
        200:
          description: Successful authentication
          content:
            application/json:
              schema:
                type: object
                properties:
                  access_token:
                    type: string
                    description: JWT access token
                    example: eyJ0eXAiOiJKV1QiLCJhbGciOiJIUzI1NiJ9...
                  refresh_token:
                    type: string
                    description: JWT refresh token
                    example: eyJ0eXAiOiJKV1QiLCJhbGciOiJIUzI1NiJ9...
                  user:
                    type: object
                    properties:
                      id:
                        type: integer
                        example: 1
                      email:
                        type: string
                        example: admin@bdc.com
                      role:
                        type: string
                        example: admin
                      full_name:
                        type: string
                        example: John Doe
                      tenant_id:
                        type: integer
                        example: 1
        400:
          description: Bad request - missing required fields
          content:
            application/json:
              schema:
                $ref: '#/components/schemas/Error'
              examples:
                missing_fields:
                  value:
                    error: Email and password are required
                missing_tenant:
                  value:
                    error: Tenant ID is required
        401:
          description: Invalid credentials
          content:
            application/json:
              schema:
                $ref: '#/components/schemas/Error'
              example:
                error: Invalid credentials
        403:
          description: Account locked or inactive
          content:
            application/json:
              schema:
                $ref: '#/components/schemas/Error'
              example:
                error: Account is locked. Please try again later.
        429:
          description: Too many requests
          content:
            application/json:
              schema:
                $ref: '#/components/schemas/Error'
              example:
                error: Rate limit exceeded
    """
    data = request.get_json()

    # Validate required fields
    if not data.get("email") or not data.get("password"):
        return jsonify({"message": "Email and password are required"}), 400

    # Get tenant ID from header or data
    tenant_id = request.headers.get(current_app.config["TENANT_HEADER"])
    if not tenant_id and "tenant_id" in data:
        tenant_id = data["tenant_id"]

    if not tenant_id:
        return jsonify({"message": "Tenant ID is required"}), 400

    # Find user
    user = db.session.query(User).filter_by(email=data["email"], tenant_id=int(tenant_id)).first()

    if not user:
        log_security_event(
            "failed_login", severity="warning", email=data["email"], tenant_id=tenant_id, reason="user_not_found"
        )
        return jsonify({"message": "Invalid credentials"}), 401

    # Check if account is locked
    if user.is_locked():
        log_security_event(
            "login_blocked", severity="warning", user_id=user.id, tenant_id=user.tenant_id, reason="account_locked"
        )
        return jsonify({"message": "Account is locked. Please try again later."}), 403

    # Verify password
    if not user.verify_password(data["password"]):
        user.increment_failed_login()
        log_security_event(
            "failed_login",
            severity="warning",
            user_id=user.id,
            tenant_id=user.tenant_id,
            email=data["email"],
            reason="invalid_password",
        )
        return jsonify({"message": "Invalid credentials"}), 401

    # Check if user is active
    if not user.is_active:
        log_security_event(
            "login_blocked", severity="warning", user_id=user.id, tenant_id=user.tenant_id, reason="user_inactive"
        )
        return jsonify({"message": "Account is inactive"}), 403

    # Check if tenant is active
    if not user.tenant.is_active:
        log_security_event(
            "login_blocked", severity="warning", user_id=user.id, tenant_id=user.tenant_id, reason="tenant_inactive"
        )
        return jsonify({"message": "Tenant is inactive"}), 403

    # Update last login
    user.update_last_login(request.remote_addr)

    # Generate tokens
    access_token = create_access_token(
        identity=str(user.id), additional_claims={"tenant_id": user.tenant_id, "role": user.role}
    )
    refresh_token = create_refresh_token(identity=str(user.id), additional_claims={"tenant_id": user.tenant_id})

    # Log successful login with structured data
    log_user_action("login", user_id=user.id, tenant_id=user.tenant_id, email=user.email, role=user.role)

    # Additional structured logging example
    current_app.logger.info(
        "User logged in successfully",
        extra={
            "user_id": user.id,
            "tenant_id": user.tenant_id,
            "email": user.email,
            "role": user.role,
            "login_method": "password",
            "ip_address": request.remote_addr,
            "user_agent": request.headers.get("User-Agent", "Unknown"),
        },
    )

    return jsonify({"user": user.to_dict(), "access_token": access_token, "refresh_token": refresh_token}), 200


@auth_bp.route("/refresh", methods=["POST"])
@jwt_required(refresh=True)
def refresh():
    """Refresh Access Token
    ---
    post:
      tags:
        - Authentication
      summary: Refresh access token using refresh token
      description: |
        Generate a new access token using a valid refresh token.
        The refresh token must be provided in the Authorization header.
      security:
        - bearerAuth: []
      responses:
        200:
          description: New access token generated
          content:
            application/json:
              schema:
                type: object
                properties:
                  access_token:
                    type: string
                    description: New JWT access token
                    example: eyJ0eXAiOiJKV1QiLCJhbGciOiJIUzI1NiJ9...
        401:
          description: Invalid or expired refresh token
          content:
            application/json:
              schema:
                $ref: '#/components/schemas/Error'
    """
    identity = get_jwt_identity()
    
    # Convert string identity back to integer
    try:
        user_id = int(identity)
    except (ValueError, TypeError):
        return jsonify({"message": "Invalid user identity"}), 400

    # Get user
    user = db.session.get(User, user_id)
    if not user or not user.is_active:
        return jsonify({"message": "Invalid user"}), 401

    # Generate new access token
    access_token = create_access_token(
        identity=str(user.id), additional_claims={"tenant_id": user.tenant_id, "role": user.role}
    )

    return jsonify({"access_token": access_token}), 200


@auth_bp.route("/logout", methods=["POST"])
@jwt_required()
def logout():
    """Logout User
    ---
    post:
      tags:
        - Authentication
      summary: Logout current user
      description: |
        Logout the current user by blacklisting their access token.
        The token will be added to a blacklist for its remaining lifetime.
      security:
        - bearerAuth: []
      responses:
        200:
          description: Logged out successfully
          content:
            application/json:
              schema:
                type: object
                properties:
                  message:
                    type: string
                    example: Logged out successfully
        500:
          description: Logout failed
          content:
            application/json:
              schema:
                $ref: '#/components/schemas/Error'
    """
    # Get token ID
    jti = get_jwt()["jti"]

    # Add token to blacklist (using Redis)
    try:
        # Token will be blacklisted for its remaining lifetime
        token_exp = get_jwt()["exp"]
        now = datetime.utcnow()
        expires_in = token_exp - int(now.timestamp())

        if expires_in > 0:
            cache.set(f"blacklist_{jti}", "true", timeout=expires_in)

        # Log logout action
        user_id = get_jwt_identity()
        claims = get_jwt()
        log_user_action("logout", user_id=user_id, tenant_id=claims.get("tenant_id"))

        return jsonify({"message": "Logged out successfully"}), 200
    except Exception as e:
        current_app.logger.error(f"Logout error: {str(e)}")
        return jsonify({"message": "Logout failed"}), 500


@auth_bp.route("/forgot-password", methods=["POST"])
@rate_limit("3 per hour")
def forgot_password():
    """Request password reset."""
    data = request.get_json()

    if not data.get("email"):
        return jsonify({"message": "Email is required"}), 400

    # Get tenant ID
    tenant_id = request.headers.get(current_app.config["TENANT_HEADER"])
    if not tenant_id and "tenant_id" in data:
        tenant_id = data["tenant_id"]

    if not tenant_id:
        return jsonify({"message": "Tenant ID is required"}), 400

    # Find user
    user = db.session.query(User).filter_by(email=data["email"], tenant_id=int(tenant_id)).first()

    # Always return success to prevent email enumeration
    if user and user.is_active:
        try:
            AuthService.send_password_reset_email(user)
            current_app.logger.info(
                "Password reset email sent",
                extra={
                    "user_id": user.id,
                    "tenant_id": user.tenant_id,
                    "email": user.email,
                    "action": "password_reset_requested",
                },
            )
        except Exception as e:
            current_app.logger.error(
                "Password reset email error",
                extra={
                    "user_id": user.id,
                    "tenant_id": user.tenant_id,
                    "email": user.email,
                    "error": str(e),
                    "error_type": type(e).__name__,
                },
            )

    return jsonify({"message": "If the email exists, a password reset link has been sent."}), 200


@auth_bp.route("/reset-password", methods=["POST"])
def reset_password():
    """Reset password with token."""
    data = request.get_json()

    if not data.get("token") or not data.get("password"):
        return jsonify({"message": "Token and password are required"}), 400

    # Validate password
    is_valid, message = validate_password(data["password"])
    if not is_valid:
        return jsonify({"message": message}), 400

    # Reset password
    try:
        user = AuthService.reset_password(data["token"], data["password"])
        if user:
            return jsonify({"message": "Password reset successfully"}), 200
        else:
            return jsonify({"message": "Invalid or expired token"}), 400
    except Exception as e:
        current_app.logger.error(f"Password reset error: {str(e)}")
        return jsonify({"message": "Password reset failed"}), 500


@auth_bp.route("/verify-email/<token>", methods=["GET"])
def verify_email(token):
    """Verify email address."""
    try:
        user = AuthService.verify_email(token)
        if user:
            return jsonify({"message": "Email verified successfully"}), 200
        else:
            return jsonify({"message": "Invalid or expired token"}), 400
    except Exception as e:
        current_app.logger.error(f"Email verification error: {str(e)}")
        return jsonify({"message": "Email verification failed"}), 500


@auth_bp.route("/me", methods=["GET"])
@jwt_required()
def get_current_user():
    """Get current user information."""
    identity = get_jwt_identity()
    # Convert string identity back to integer
    try:
        user_id = int(identity)
    except (ValueError, TypeError):
        return jsonify({"message": "Invalid user identity"}), 400
        
    user = db.session.get(User, user_id)

    if not user:
        return jsonify({"message": "User not found"}), 404

    return jsonify({"user": user.to_dict(include_roles=True)}), 200


@auth_bp.route("/change-password", methods=["POST"])
@jwt_required()
def change_password():
    """Change user password."""
    identity = get_jwt_identity()
    # Convert string identity back to integer
    try:
        user_id = int(identity)
    except (ValueError, TypeError):
        return jsonify({"message": "Invalid user identity"}), 400
        
    user = db.session.get(User, user_id)

    if not user:
        return jsonify({"message": "User not found"}), 404

    data = request.get_json()

    if not data.get("old_password") or not data.get("new_password"):
        return jsonify({"message": "Old and new passwords are required"}), 400

    # Verify old password
    if not user.verify_password(data["old_password"]):
        return jsonify({"message": "Invalid old password"}), 401

    # Validate new password
    is_valid, message = validate_password(data["new_password"])
    if not is_valid:
        return jsonify({"message": message}), 400

    # Update password
    user.set_password(data["new_password"])
    user.save()

    # Log password change
    log_security_event("password_changed", user_id=user.id, tenant_id=user.tenant_id, email=user.email)

    return jsonify({"message": "Password changed successfully"}), 200
