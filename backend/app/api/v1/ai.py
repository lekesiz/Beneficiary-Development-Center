"""AI API endpoints."""

from flask import Blueprint

ai_bp = Blueprint("ai", __name__)


@ai_bp.route("/")
def ai_info():
    """Get AI service info."""
    return {"message": "AI service endpoint"}