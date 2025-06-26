"""
Authentication Service
"""

from typing import Dict, Optional
from werkzeug.security import generate_password_hash, check_password_hash
from flask_jwt_extended import create_access_token, create_refresh_token
from datetime import datetime, timedelta
from sqlalchemy.orm import Session

from app.models.user import User
from app.core.exceptions import ValidationError, UnauthorizedError


class AuthService:
    """Service for authentication operations."""

    def __init__(self, db: Session):
        self.db = db

    def register_user(
        self, email: str, password: str, first_name: str, last_name: str, role: str, tenant_id: int
    ) -> User:
        """
        Register a new user.

        Args:
            email: User email
            password: Plain text password
            first_name: User's first name
            last_name: User's last name
            role: User role
            tenant_id: Tenant ID

        Returns:
            Created user object
        """
        # Check if user already exists
        existing_user = self.db.query(User).filter(User.email == email, User.tenant_id == tenant_id).first()

        if existing_user:
            raise ValidationError("User with this email already exists")

        # Create new user
        user = User(
            email=email,
            password_hash=generate_password_hash(password),
            first_name=first_name,
            last_name=last_name,
            role=role,
            tenant_id=tenant_id,
            is_active=True,
        )

        self.db.add(user)
        self.db.commit()
        self.db.refresh(user)

        return user

    def login(self, email: str, password: str, tenant_id: int) -> Dict[str, str]:
        """
        Authenticate user and generate tokens.

        Args:
            email: User email
            password: Plain text password
            tenant_id: Tenant ID

        Returns:
            Dictionary with access and refresh tokens
        """
        # Find user
        user = self.db.query(User).filter(User.email == email, User.tenant_id == tenant_id).first()

        if not user or not check_password_hash(user.password_hash, password):
            raise UnauthorizedError("Invalid email or password")

        if not user.is_active:
            raise UnauthorizedError("User account is deactivated")

        # Update last login
        user.last_login = datetime.utcnow()
        self.db.commit()

        # Generate tokens
        access_token = create_access_token(
            identity=str(user.id),
            additional_claims={"email": user.email, "role": user.role, "tenant_id": user.tenant_id},
        )

        refresh_token = create_refresh_token(
            identity=str(user.id),
            additional_claims={"email": user.email, "role": user.role, "tenant_id": user.tenant_id},
        )

        return {
            "access_token": access_token,
            "refresh_token": refresh_token,
            "user": {
                "id": user.id,
                "email": user.email,
                "first_name": user.first_name,
                "last_name": user.last_name,
                "role": user.role,
                "tenant_id": user.tenant_id,
            },
        }

    def refresh_token(self, user_id: int) -> Dict[str, str]:
        """
        Generate new access token from refresh token.

        Args:
            user_id: User ID from JWT

        Returns:
            New access token
        """
        user = self.db.query(User).filter(User.id == user_id).first()

        if not user or not user.is_active:
            raise UnauthorizedError("Invalid user")

        # Generate new access token
        access_token = create_access_token(
            identity=str(user.id),
            additional_claims={"email": user.email, "role": user.role, "tenant_id": user.tenant_id},
        )

        return {"access_token": access_token}

    def change_password(self, user_id: int, current_password: str, new_password: str) -> bool:
        """
        Change user password.

        Args:
            user_id: User ID
            current_password: Current password
            new_password: New password

        Returns:
            Success status
        """
        user = self.db.query(User).filter(User.id == user_id).first()

        if not user:
            raise ValidationError("User not found")

        if not check_password_hash(user.password_hash, current_password):
            raise ValidationError("Current password is incorrect")

        user.password_hash = generate_password_hash(new_password)
        self.db.commit()

        return True

    def request_password_reset(self, email: str, tenant_id: int) -> Optional[str]:
        """
        Request password reset token.

        Args:
            email: User email
            tenant_id: Tenant ID

        Returns:
            Reset token if user exists
        """
        user = self.db.query(User).filter(User.email == email, User.tenant_id == tenant_id).first()

        if not user:
            return None

        # Generate reset token (in production, this would be a secure random token)
        # For now, using JWT with short expiration
        reset_token = create_access_token(
            identity=str(user.id), additional_claims={"type": "password_reset"}, expires_delta=timedelta(hours=1)
        )

        return reset_token

    def reset_password(self, token: str, new_password: str) -> bool:
        """
        Reset password with token.

        Args:
            token: Reset token
            new_password: New password

        Returns:
            Success status
        """
        # In production, validate the token properly
        # For now, this is a placeholder

        # Extract user_id from token and reset password
        # This is simplified - in production, use proper token validation

        return True
