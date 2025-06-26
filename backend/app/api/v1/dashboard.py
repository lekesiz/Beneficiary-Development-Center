"""
Dashboard API endpoints
"""

from flask import Blueprint, jsonify
from datetime import datetime, timedelta
from flask_jwt_extended import jwt_required, get_jwt_identity
from app.core.database import get_db
from app.models.learning_path import LearningPath, MilestoneProgress
from app.models.user import User
from app.extensions import db

dashboard_bp = Blueprint("dashboard", __name__, url_prefix="/api/dashboard")


@dashboard_bp.route("/student", methods=["GET"])
@jwt_required()
def get_student_dashboard():
    """Get student dashboard data."""
    user_id = get_jwt_identity()
    user = db.session.get(User, user_id)
    db = get_db()

    try:
        # Calculate overall statistics
        active_paths = (
            db.query(LearningPath)
            .filter(
                LearningPath.user_id == user.id,
                LearningPath.tenant_id == user.tenant_id,
                LearningPath.status.in_(["accepted", "in_progress"]),
                LearningPath.is_deleted.is_(False),
            )
            .all()
        )

        total_milestones = 0
        completed_milestones = 0
        weekly_hours = 0

        for path in active_paths:
            path_milestones = [m for m in path.milestones if not m.is_deleted]
            total_milestones += len(path_milestones)

            for milestone in path_milestones:
                progress = (
                    db.query(MilestoneProgress)
                    .filter(MilestoneProgress.milestone_id == milestone.id, MilestoneProgress.user_id == user.id)
                    .first()
                )

                if progress and progress.status == "completed":
                    completed_milestones += 1

                # Calculate weekly hours from recent activity
                if progress and progress.started_at:
                    week_ago = datetime.utcnow() - timedelta(days=7)
                    if progress.started_at >= week_ago:
                        weekly_hours += (progress.time_spent_minutes or 0) / 60

        overall_progress = (completed_milestones / total_milestones * 100) if total_milestones > 0 else 0

        # Get upcoming evaluations
        upcoming_evaluations = []
        # TODO: Implement when evaluation scheduling is added

        # Get recent achievements
        recent_achievements = []
        recent_milestones = (
            db.query(MilestoneProgress)
            .filter(
                MilestoneProgress.user_id == user.id,
                MilestoneProgress.status == "completed",
                MilestoneProgress.completed_at.isnot(None),
            )
            .order_by(MilestoneProgress.completed_at.desc())
            .limit(5)
            .all()
        )

        for progress in recent_milestones:
            milestone = progress.milestone
            recent_achievements.append(
                {
                    "id": progress.id,
                    "title": f"Tamamlandı: {milestone.title}",
                    "earned_at": progress.completed_at.isoformat(),
                }
            )

        # Check for alerts
        alerts = []

        # Check for stalled progress
        in_progress_milestones = (
            db.query(MilestoneProgress)
            .filter(MilestoneProgress.user_id == user.id, MilestoneProgress.status == "in_progress")
            .all()
        )

        for progress in in_progress_milestones:
            if progress.started_at:
                days_since_start = (datetime.utcnow() - progress.started_at).days
                if days_since_start > 7:
                    alerts.append(
                        {"type": "warning", "message": f"{progress.milestone.title} için 7 günden fazla süre geçti"}
                    )

        # Check for low progress
        if overall_progress < 25 and total_milestones > 0:
            alerts.append({"type": "info", "message": "Öğrenme hedeflerinizde ilerleme kaydetmeyi unutmayın!"})

        return jsonify(
            {
                "stats": {
                    "overall_progress": round(overall_progress),
                    "completed_milestones": completed_milestones,
                    "weekly_hours": round(weekly_hours, 1),
                    "active_paths": len(active_paths),
                },
                "upcoming_evaluations": upcoming_evaluations,
                "recent_achievements": recent_achievements,
                "alerts": alerts,
            }
        )

    except Exception as e:
        return jsonify({"success": False, "error": str(e)}), 500
