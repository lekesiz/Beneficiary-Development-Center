"""
Dashboard API endpoints
"""

from flask import Blueprint, jsonify, request
from datetime import datetime, timedelta
from flask_jwt_extended import jwt_required, get_jwt_identity
from app.core.database import get_db
from app.models.learning_path import LearningPath, MilestoneProgress
from app.models.user import User
from app.models.beneficiary import Beneficiary
from app.models.program import Program
from app.models.evaluation import Evaluation
from app.models.coach_note import CoachNote
from app.models.course_session import CourseSession
from app.models.audit_log import AuditLog
from app.extensions import db, limiter
from app.core.jwt_utils import get_current_user_id
from app.core.audit import audit_read
from app.core.rate_limiting import api_rate_limit
from app.core.decorators import require_permission
from sqlalchemy import func, desc, and_
from app.utils.response import success_response, error_response

dashboard_bp = Blueprint("dashboard", __name__, url_prefix="/api/v1/dashboard")


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


@dashboard_bp.route("/stats", methods=["GET"])
@jwt_required()
@require_permission(['admin', 'trainer'])
@limiter.limit(api_rate_limit)
@audit_read('dashboard_stats')
def get_dashboard_stats():
    """Get general dashboard statistics for admin/trainer view"""
    try:
        tenant_id = request.headers.get('X-Tenant-ID')
        if not tenant_id:
            return error_response('Tenant ID is required', 400)
        
        # Get current stats
        total_beneficiaries = Beneficiary.query.filter_by(tenant_id=tenant_id).count()
        active_programs = Program.query.filter_by(tenant_id=tenant_id, status='active').count()
        completed_evaluations = Evaluation.query.filter_by(tenant_id=tenant_id).count()
        
        # Calculate completion rate
        total_evaluations = Evaluation.query.filter_by(tenant_id=tenant_id).count()
        completion_rate = round((completed_evaluations / total_evaluations * 100) if total_evaluations > 0 else 0, 1)
        
        # Get growth percentages (comparing to last month)
        last_month = datetime.utcnow() - timedelta(days=30)
        
        # Beneficiary growth
        last_month_beneficiaries = Beneficiary.query.filter(
            and_(Beneficiary.tenant_id == tenant_id, Beneficiary.created_at <= last_month)
        ).count()
        beneficiary_growth = calculate_growth_percentage(total_beneficiaries, last_month_beneficiaries)
        
        # Program growth  
        last_month_programs = Program.query.filter(
            and_(Program.tenant_id == tenant_id, Program.created_at <= last_month)
        ).count()
        program_growth = calculate_growth_percentage(active_programs, last_month_programs)
        
        # Evaluation growth
        last_month_evaluations = Evaluation.query.filter(
            and_(Evaluation.tenant_id == tenant_id, Evaluation.created_at <= last_month)
        ).count()
        evaluation_growth = calculate_growth_percentage(completed_evaluations, last_month_evaluations)
        
        return success_response({
            'total_beneficiaries': total_beneficiaries,
            'active_programs': active_programs,
            'completed_evaluations': completed_evaluations,
            'completion_rate': completion_rate,
            'beneficiary_growth': beneficiary_growth,
            'program_growth': program_growth,
            'evaluation_growth': evaluation_growth,
            'completion_growth': f"+{completion_rate}%"
        })
        
    except Exception as e:
        return error_response(f'Failed to fetch dashboard stats: {str(e)}', 500)


@dashboard_bp.route("/activities", methods=["GET"])
@jwt_required()
@require_permission(['admin', 'trainer'])
@limiter.limit(api_rate_limit)
@audit_read('dashboard_activities')
def get_recent_activities():
    """Get recent activities for dashboard"""
    try:
        tenant_id = request.headers.get('X-Tenant-ID')
        limit = request.args.get('limit', 10, type=int)
        
        if not tenant_id:
            return error_response('Tenant ID is required', 400)
        
        activities = []
        
        # Recent beneficiary enrollments
        recent_beneficiaries = Beneficiary.query.filter_by(tenant_id=tenant_id)\
            .order_by(desc(Beneficiary.created_at)).limit(3).all()
        
        for beneficiary in recent_beneficiaries:
            activities.append({
                'id': f'beneficiary_{beneficiary.id}',
                'title': 'New beneficiary enrolled',
                'description': f'{beneficiary.first_name} {beneficiary.last_name} joined the program',
                'time': format_time_ago(beneficiary.created_at),
                'type': 'beneficiary',
                'created_at': beneficiary.created_at.isoformat()
            })
        
        # Recent program activities
        recent_programs = Program.query.filter_by(tenant_id=tenant_id)\
            .order_by(desc(Program.created_at)).limit(2).all()
        
        for program in recent_programs:
            activities.append({
                'id': f'program_{program.id}',
                'title': 'Program created',
                'description': f'{program.name} program was created',
                'time': format_time_ago(program.created_at),
                'type': 'program',
                'created_at': program.created_at.isoformat()
            })
        
        # Recent coach notes
        recent_notes = CoachNote.query.filter_by(tenant_id=tenant_id)\
            .order_by(desc(CoachNote.created_at)).limit(3).all()
        
        for note in recent_notes:
            activities.append({
                'id': f'note_{note.id}',
                'title': 'Coach note added',
                'description': f'Note added for {note.student.first_name} {note.student.last_name}',
                'time': format_time_ago(note.created_at),
                'type': 'coach_note',
                'user_name': f'{note.coach.first_name} {note.coach.last_name}',
                'created_at': note.created_at.isoformat()
            })
        
        # Sort all activities by creation time and limit
        activities.sort(key=lambda x: x['created_at'], reverse=True)
        activities = activities[:limit]
        
        return success_response({'activities': activities})
        
    except Exception as e:
        return error_response(f'Failed to fetch recent activities: {str(e)}', 500)


@dashboard_bp.route("/upcoming-events", methods=["GET"])
@jwt_required()
@require_permission(['admin', 'trainer'])
@limiter.limit(api_rate_limit)
@audit_read('dashboard_events')
def get_upcoming_events():
    """Get upcoming events for dashboard"""
    try:
        tenant_id = request.headers.get('X-Tenant-ID')
        limit = request.args.get('limit', 5, type=int)
        
        if not tenant_id:
            return error_response('Tenant ID is required', 400)
        
        events = []
        now = datetime.utcnow()
        next_month = now + timedelta(days=30)
        
        # Upcoming course sessions
        upcoming_sessions = CourseSession.query.filter(
            and_(
                CourseSession.tenant_id == tenant_id,
                CourseSession.start_date >= now,
                CourseSession.start_date <= next_month
            )
        ).order_by(CourseSession.start_date).limit(limit).all()
        
        for session in upcoming_sessions:
            events.append({
                'id': f'session_{session.id}',
                'title': f'{session.course.title} - {session.title}',
                'date': session.start_date.strftime('%b %d, %Y'),
                'participants': session.course.enrollments.count() if session.course else 0,
                'type': 'course_session',
                'location': session.location
            })
        
        # Upcoming evaluations
        upcoming_evaluations = Evaluation.query.filter(
            and_(
                Evaluation.tenant_id == tenant_id,
                Evaluation.start_date >= now,
                Evaluation.start_date <= next_month
            )
        ).order_by(Evaluation.start_date).limit(3).all()
        
        for evaluation in upcoming_evaluations:
            events.append({
                'id': f'evaluation_{evaluation.id}',
                'title': f'{evaluation.title} Evaluation',
                'date': evaluation.start_date.strftime('%b %d, %Y'),
                'participants': evaluation.course.enrollments.count() if evaluation.course else 0,
                'type': 'evaluation'
            })
        
        # Sort by date and limit
        events.sort(key=lambda x: datetime.strptime(x['date'], '%b %d, %Y'))
        events = events[:limit]
        
        return success_response({'events': events})
        
    except Exception as e:
        return error_response(f'Failed to fetch upcoming events: {str(e)}', 500)


def calculate_growth_percentage(current, previous):
    """Calculate growth percentage between current and previous values"""
    if previous == 0:
        return "+100%" if current > 0 else "0%"
    
    growth = ((current - previous) / previous) * 100
    sign = "+" if growth >= 0 else ""
    return f"{sign}{growth:.1f}%"


def format_time_ago(timestamp):
    """Format timestamp as 'X time ago'"""
    now = datetime.utcnow()
    diff = now - timestamp
    
    if diff.days > 0:
        return f"{diff.days} day{'s' if diff.days != 1 else ''} ago"
    elif diff.seconds > 3600:
        hours = diff.seconds // 3600
        return f"{hours} hour{'s' if hours != 1 else ''} ago"
    elif diff.seconds > 60:
        minutes = diff.seconds // 60
        return f"{minutes} minute{'s' if minutes != 1 else ''} ago"
    else:
        return "Just now"


@dashboard_bp.route("/activity", methods=["GET"])
@jwt_required()
@limiter.limit(api_rate_limit)
@audit_read('dashboard_activity')
def get_dashboard_activity():
    """Get recent activity for dashboard."""
    try:
        user_id = get_current_user_id()
        current_user = db.session.query(User).filter_by(id=user_id).first()
        
        if not current_user:
            return error_response("User not found", 404)
        
        # Get query parameters
        limit = min(request.args.get('limit', 20, type=int), 100)
        offset = request.args.get('offset', 0, type=int)
        
        # Get recent audit logs for the tenant
        recent_activities = db.session.query(AuditLog).filter_by(
            tenant_id=current_user.tenant_id
        ).order_by(desc(AuditLog.created_at)).limit(limit).offset(offset).all()
        
        activities = []
        for log in recent_activities:
            # Get user info
            user = db.session.query(User).filter_by(id=log.user_id).first()
            
            activities.append({
                'id': log.id,
                'action': log.action,
                'resource_type': log.resource_type,
                'resource_id': log.resource_id,
                'user': {
                    'id': user.id,
                    'name': user.full_name,
                    'email': user.email
                } if user else None,
                'details': log.details,
                'created_at': log.created_at.isoformat(),
                'time_ago': _format_time_ago(log.created_at)
            })
        
        # Get total count
        total_count = db.session.query(func.count(AuditLog.id)).filter_by(
            tenant_id=current_user.tenant_id
        ).scalar()
        
        return success_response({
            'activities': activities,
            'pagination': {
                'limit': limit,
                'offset': offset,
                'total': total_count,
                'has_more': offset + limit < total_count
            }
        })
        
    except Exception as e:
        return error_response(str(e), 500)
