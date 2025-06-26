"""User management API endpoints."""

from flask import Blueprint, request, jsonify
from flask_jwt_extended import jwt_required, get_jwt_identity
from app.models.user import User
from app.extensions import db
from app.core.logging import log_user_action

users_bp = Blueprint("users", __name__)


@users_bp.route("/")
def get_users():
    """Get all users."""
    return {"message": "Users endpoint"}


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
        user = User.query.get(user_id)
        
        if not user:
            return jsonify({"message": "User not found"}), 404
        
        # Get request data
        data = request.get_json()
        
        if not data or 'notifications' not in data:
            return jsonify({"message": "Invalid preferences format"}), 400
        
        # Update preferences in the JSONB column
        if not user.preferences:
            user.preferences = {}
        
        # Update notification preferences
        user.preferences['notifications'] = data['notifications']
        
        # Mark the column as modified for SQLAlchemy to detect the change
        db.session.query(User).filter_by(id=user_id).update(
            {"preferences": user.preferences},
            synchronize_session=False
        )
        
        db.session.commit()
        
        # Log the action
        log_user_action(
            "update_preferences",
            user_id=user.id,
            tenant_id=user.tenant_id,
            email=user.email,
            preferences_type="notifications"
        )
        
        return jsonify({
            "message": "Preferences updated successfully",
            "preferences": user.preferences
        }), 200
        
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
        user = User.query.get(user_id)
        
        if not user:
            return jsonify({"message": "User not found"}), 404
        
        # Get preferences, return default if not set
        preferences = user.preferences or {}
        
        # Ensure notifications structure exists with defaults
        if 'notifications' not in preferences:
            preferences['notifications'] = {
                'email': {
                    'new_message': True,
                    'appointment_reminder': True,
                    'evaluation_completed': True,
                    'course_enrollment': True,
                    'program_update': True
                },
                'in_app': {
                    'new_message': True,
                    'appointment_reminder': True,
                    'evaluation_completed': True,
                    'course_enrollment': True,
                    'program_update': True
                }
            }
        
        return jsonify({"preferences": preferences}), 200
        
    except Exception as e:
        return jsonify({"message": f"Failed to get preferences: {str(e)}"}), 500