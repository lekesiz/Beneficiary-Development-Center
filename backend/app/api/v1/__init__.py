"""API v1 blueprint initialization."""

from flask import Blueprint
from app.api.v1 import auth, beneficiaries, evaluations, learning_paths, reports, dashboard, chat, users

# Create main API v1 blueprint
api_v1_bp = Blueprint("api_v1", __name__)

api_v1_bp.register_blueprint(auth.auth_bp, url_prefix="/auth")
api_v1_bp.register_blueprint(users.users_bp, url_prefix="/users")
api_v1_bp.register_blueprint(beneficiaries.bp, url_prefix="/beneficiaries")
# programs blueprint is now registered separately as enhanced_programs in app/__init__.py
api_v1_bp.register_blueprint(evaluations.evaluations_bp)
api_v1_bp.register_blueprint(learning_paths.learning_paths_bp)
api_v1_bp.register_blueprint(reports.reports_bp)
api_v1_bp.register_blueprint(dashboard.dashboard_bp)
api_v1_bp.register_blueprint(chat.bp)

# API metadata
API_VERSION = "1.0.0"
API_DESCRIPTION = "BDC REST API v1"


@api_v1_bp.route("/")
def api_info():
    """Get API information."""
    return {
        "version": API_VERSION,
        "description": API_DESCRIPTION,
        "endpoints": {
            "auth": "/api/v1/auth",
            "users": "/api/v1/users",
            "beneficiaries": "/api/v1/beneficiaries",
            "programs": "/api/v1/programs",
            "evaluations": "/api/v1/evaluations",
            "ai": "/api/v1/ai",
            "chat": "/api/v1/chat",
        },
    }
