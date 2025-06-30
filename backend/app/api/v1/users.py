"""User management API endpoints."""

from flask import Blueprint, request, jsonify
from flask_jwt_extended import jwt_required, get_jwt_identity
from app.models.user import User
from app.extensions import db
from app.core.logging import log_user_action

users_bp = Blueprint("users", __name__)


@users_bp.route("/")
@jwt_required()
def get_users():
    """Get all users."""
    from app.core.jwt_utils import get_current_user_id
    from app.core.decorators import requires_role
    
    try:
        current_user_id = get_current_user_id()
        current_user = db.session.query(User).filter_by(id=current_user_id).first()
        
        if not current_user:
            return jsonify({"error": "User not found"}), 404
            
        # Only admins and managers can list all users
        if current_user.role not in ["admin", "manager"]:
            return jsonify({"error": "Insufficient permissions"}), 403
        
        # Get users from same tenant
        users = db.session.query(User).filter_by(tenant_id=current_user.tenant_id).all()
        
        return jsonify({
            "users": [user.to_dict() for user in users],
            "total": len(users)
        }), 200
        
    except Exception as e:
        return jsonify({"error": str(e)}), 500


@users_bp.route("/<int:user_id>")
@jwt_required()
def get_user(user_id):
    """Get a specific user by ID."""
    from app.core.jwt_utils import get_current_user_id
    
    try:
        current_user_id = get_current_user_id()
        current_user = db.session.query(User).filter_by(id=current_user_id).first()
        
        if not current_user:
            return jsonify({"error": "User not found"}), 404
        
        # Users can view their own profile, admins/managers can view any user
        if user_id != current_user_id and current_user.role not in ["admin", "manager"]:
            return jsonify({"error": "Insufficient permissions"}), 403
        
        # Get the requested user
        user = db.session.query(User).filter_by(
            id=user_id, 
            tenant_id=current_user.tenant_id
        ).first()
        
        if not user:
            return jsonify({"error": "User not found"}), 404
        
        return jsonify(user.to_dict(include_roles=True)), 200
        
    except Exception as e:
        return jsonify({"error": str(e)}), 500


@users_bp.route("/me/preferences", methods=["PUT"])
@jwt_required()
def update_user_preferences():
    """Update User Notification Preferences
    ---
    put:
      tags:
        - Users
      summary: Update notification preferences for the current user
      description: |
        Update the notification preferences for the authenticated user.
        Supports email and in-app notifications for various categories.
      security:
        - bearerAuth: []
      requestBody:
        required: true
        content:
          application/json:
            schema:
              type: object
              properties:
                notifications:
                  type: object
                  properties:
                    email:
                      type: object
                      properties:
                        new_message:
                          type: boolean
                          description: Email notifications for new messages
                          example: true
                        appointment_reminder:
                          type: boolean
                          description: Email notifications for appointment reminders
                          example: true
                        evaluation_completed:
                          type: boolean
                          description: Email notifications when evaluations are completed
                          example: false
                        course_enrollment:
                          type: boolean
                          description: Email notifications for course enrollments
                          example: true
                        program_update:
                          type: boolean
                          description: Email notifications for program updates
                          example: true
                    in_app:
                      type: object
                      properties:
                        new_message:
                          type: boolean
                          description: In-app notifications for new messages
                          example: true
                        appointment_reminder:
                          type: boolean
                          description: In-app notifications for appointment reminders
                          example: true
                        evaluation_completed:
                          type: boolean
                          description: In-app notifications when evaluations are completed
                          example: true
                        course_enrollment:
                          type: boolean
                          description: In-app notifications for course enrollments
                          example: true
                        program_update:
                          type: boolean
                          description: In-app notifications for program updates
                          example: true
      responses:
        200:
          description: Preferences updated successfully
          content:
            application/json:
              schema:
                type: object
                properties:
                  message:
                    type: string
                    example: Preferences updated successfully
                  preferences:
                    type: object
                    description: Updated preferences object
        400:
          description: Invalid request data
          content:
            application/json:
              schema:
                type: object
                properties:
                  message:
                    type: string
                    example: Invalid preferences format
        404:
          description: User not found
          content:
            application/json:
              schema:
                type: object
                properties:
                  message:
                    type: string
                    example: User not found
        500:
          description: Server error
          content:
            application/json:
              schema:
                type: object
                properties:
                  message:
                    type: string
                    example: Failed to update preferences
    """
    try:
        # Get current user
        user_id = get_jwt_identity()
        user = db.session.get(User, user_id)

        if not user:
            return jsonify({"message": "User not found"}), 404

        # Get request data
        data = request.get_json()

        if not data or "notifications" not in data:
            return jsonify({"message": "Invalid preferences format"}), 400

        # Update preferences in the JSONB column
        if not user.preferences:
            user.preferences = {}

        # Update notification preferences
        user.preferences["notifications"] = data["notifications"]

        # Mark the column as modified for SQLAlchemy to detect the change
        db.session.query(User).filter_by(id=user_id).update(
            {"preferences": user.preferences}, synchronize_session=False
        )

        db.session.commit()

        # Log the action
        log_user_action(
            "update_preferences",
            user_id=user.id,
            tenant_id=user.tenant_id,
            email=user.email,
            preferences_type="notifications",
        )

        return jsonify({"message": "Preferences updated successfully", "preferences": user.preferences}), 200

    except Exception as e:
        db.session.rollback()
        return jsonify({"message": f"Failed to update preferences: {str(e)}"}), 500


@users_bp.route("/me/preferences", methods=["GET"])
@jwt_required()
def get_user_preferences():
    """Get User Notification Preferences
    ---
    get:
      tags:
        - Users
      summary: Get notification preferences for the current user
      description: |
        Retrieve the notification preferences for the authenticated user.
      security:
        - bearerAuth: []
      responses:
        200:
          description: Preferences retrieved successfully
          content:
            application/json:
              schema:
                type: object
                properties:
                  preferences:
                    type: object
                    properties:
                      notifications:
                        type: object
                        properties:
                          email:
                            type: object
                            description: Email notification settings
                          in_app:
                            type: object
                            description: In-app notification settings
        404:
          description: User not found
          content:
            application/json:
              schema:
                type: object
                properties:
                  message:
                    type: string
                    example: User not found
    """
    try:
        # Get current user
        user_id = get_jwt_identity()
        user = db.session.get(User, user_id)

        if not user:
            return jsonify({"message": "User not found"}), 404

        # Get preferences, return default if not set
        preferences = user.preferences or {}

        # Ensure notifications structure exists with defaults
        if "notifications" not in preferences:
            preferences["notifications"] = {
                "email": {
                    "new_message": True,
                    "appointment_reminder": True,
                    "evaluation_completed": True,
                    "course_enrollment": True,
                    "program_update": True,
                },
                "in_app": {
                    "new_message": True,
                    "appointment_reminder": True,
                    "evaluation_completed": True,
                    "course_enrollment": True,
                    "program_update": True,
                },
            }

        return jsonify({"preferences": preferences}), 200

    except Exception as e:
        return jsonify({"message": f"Failed to get preferences: {str(e)}"}), 500
