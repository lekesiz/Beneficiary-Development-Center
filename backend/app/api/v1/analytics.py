"""
Analytics API endpoints for comprehensive data analysis and metrics
"""

from flask import Blueprint, jsonify, request
from datetime import datetime, timedelta
from flask_jwt_extended import jwt_required
from app.extensions import db, limiter
from app.models.user import User
from app.models.beneficiary import Beneficiary
from app.models.program import Program
from app.models.evaluation import Evaluation
from app.models.coach_note import CoachNote
from app.models.learning_path import LearningPath, MilestoneProgress
from app.core.decorators import require_permission
from app.core.audit import audit_read
from app.core.rate_limiting import api_rate_limit
from app.utils.response import success_response, error_response
from sqlalchemy import func, desc, and_, or_
import json

analytics_bp = Blueprint("analytics", __name__, url_prefix="/api/v1/analytics")


@analytics_bp.route("/overview", methods=["GET"])
@jwt_required()
@require_permission(['admin', 'trainer'])
@limiter.limit(api_rate_limit)
@audit_read('analytics_overview')
def get_analytics_overview():
    """Get analytics overview with key metrics"""
    try:
        tenant_id = request.headers.get('X-Tenant-ID')
        if not tenant_id:
            return error_response('Tenant ID is required', 400)
        
        # Get query parameters
        days = request.args.get('days', 30, type=int)
        end_date = datetime.utcnow()
        start_date = end_date - timedelta(days=days)
        
        # Get active students count
        active_students = User.query.filter_by(
            tenant_id=tenant_id, 
            role='student'
        ).count()
        
        # Get programs count
        active_programs = Program.query.filter_by(
            tenant_id=tenant_id,
            status='active'
        ).count()
        
        # Get recent milestones completed
        recent_milestones = MilestoneProgress.query.join(User).filter(
            and_(
                User.tenant_id == tenant_id,
                MilestoneProgress.completed_at >= start_date,
                MilestoneProgress.status == 'completed'
            )
        ).count()
        
        # Get evaluation statistics
        evaluations = Evaluation.query.filter_by(tenant_id=tenant_id).filter(
            Evaluation.created_at >= start_date
        ).all()
        
        total_evaluations = len(evaluations)
        avg_evaluation_score = 0
        # Calculate average score from attempts instead
        from app.models.evaluation import EvaluationAttempt, AttemptStatus
        attempts = db.session.query(EvaluationAttempt).join(Evaluation).filter(
            and_(
                Evaluation.tenant_id == tenant_id,
                EvaluationAttempt.status == AttemptStatus.COMPLETED,
                EvaluationAttempt.started_at >= start_date
            )
        ).all()
        if attempts:
            scores = [a.percentage_score for a in attempts if a.percentage_score is not None]
            avg_evaluation_score = sum(scores) / len(scores) if scores else 0
        
        # Get learning path statistics
        learning_paths = LearningPath.query.filter_by(tenant_id=tenant_id).all()
        active_paths = len([p for p in learning_paths if p.status == 'in_progress'])
        completed_paths = len([p for p in learning_paths if p.status == 'completed'])
        
        # Calculate completion rate
        total_paths = len(learning_paths)
        completion_rate = (completed_paths / total_paths * 100) if total_paths > 0 else 0
        
        # Get engagement metrics for the period
        engaged_students = User.query.join(MilestoneProgress).filter(
            and_(
                User.tenant_id == tenant_id,
                User.role == 'student',
                MilestoneProgress.updated_at >= start_date
            )
        ).distinct().count()
        
        engagement_rate = (engaged_students / active_students * 100) if active_students > 0 else 0
        
        return success_response({
            'overview': {
                'students': {
                    'total': active_students,
                    'engaged': engaged_students,
                    'engagement_rate': round(engagement_rate, 2)
                },
                'programs': {
                    'total': active_programs,
                    'active_learning_paths': active_paths,
                    'completed_learning_paths': completed_paths,
                    'completion_rate': round(completion_rate, 2)
                },
                'milestones': {
                    'completed_recent': recent_milestones,
                    'daily_average': round(recent_milestones / days, 2)
                },
                'evaluations': {
                    'total_recent': total_evaluations,
                    'average_score': round(avg_evaluation_score, 2)
                }
            },
            'period': {
                'start_date': start_date.isoformat(),
                'end_date': end_date.isoformat(),
                'days': days
            }
        })
        
    except Exception as e:
        return error_response(f'Failed to fetch analytics overview: {str(e)}', 500)


@analytics_bp.route("/performance-trends", methods=["GET"])
@jwt_required()
@require_permission(['admin', 'trainer'])
@limiter.limit(api_rate_limit)
@audit_read('analytics_performance_trends')
def get_performance_trends():
    """Get performance analytics trends over time"""
    try:
        tenant_id = request.headers.get('X-Tenant-ID')
        if not tenant_id:
            return error_response('Tenant ID is required', 400)
        
        # Get query parameters
        days = request.args.get('days', 30, type=int)
        user_ids = request.args.getlist('user_ids', type=int)
        program_ids = request.args.getlist('program_ids', type=int)
        
        # Calculate date range
        end_date = datetime.utcnow()
        start_date = end_date - timedelta(days=days)
        
        # Base query for milestone progress
        query = db.session.query(MilestoneProgress).join(User).filter(
            User.tenant_id == tenant_id,
            MilestoneProgress.completed_at.between(start_date, end_date)
        )
        
        # Apply filters
        if user_ids:
            query = query.filter(MilestoneProgress.user_id.in_(user_ids))
        
        # Get completed milestones grouped by date
        milestones = query.order_by(MilestoneProgress.completed_at).all()
        
        # Process data for trend analysis
        trends = {}
        for milestone in milestones:
            date_key = milestone.completed_at.strftime('%Y-%m-%d')
            if date_key not in trends:
                trends[date_key] = {
                    'date': date_key,
                    'completions': 0,
                    'average_score': 0,
                    'users': set(),
                    'total_score': 0
                }
            
            trends[date_key]['completions'] += 1
            trends[date_key]['users'].add(milestone.user_id)
            if milestone.score:
                trends[date_key]['total_score'] += milestone.score
        
        # Calculate averages and format response
        trend_data = []
        for date_key, data in sorted(trends.items()):
            average_score = (data['total_score'] / data['completions']) if data['completions'] > 0 else 0
            trend_data.append({
                'date': data['date'],
                'completions': data['completions'],
                'active_users': len(data['users']),
                'average_score': round(average_score, 2)
            })
        
        return success_response({
            'trends': trend_data,
            'period': {
                'start_date': start_date.isoformat(),
                'end_date': end_date.isoformat(),
                'days': days
            },
            'summary': {
                'total_completions': sum(t['completions'] for t in trend_data),
                'unique_users': len(set().union(*[trends[d]['users'] for d in trends])) if trends else 0,
                'overall_average': round(sum(t['average_score'] for t in trend_data) / len(trend_data), 2) if trend_data else 0
            }
        })
        
    except Exception as e:
        return error_response(f'Failed to fetch performance trends: {str(e)}', 500)


@analytics_bp.route("/completion-rates", methods=["GET"])
@jwt_required()
@require_permission(['admin', 'trainer'])
@limiter.limit(api_rate_limit)
@audit_read('analytics_completion_rates')
def get_completion_rates():
    """Get course/program completion rate analytics"""
    try:
        tenant_id = request.headers.get('X-Tenant-ID')
        if not tenant_id:
            return error_response('Tenant ID is required', 400)
        
        # Get programs and their completion rates
        programs = Program.query.filter_by(tenant_id=tenant_id).all()
        completion_data = []
        
        for program in programs:
            # Get all learning paths for this program
            paths = LearningPath.query.filter_by(
                tenant_id=tenant_id,
                program_id=program.id
            ).all()
            
            if not paths:
                continue
            
            total_enrolled = len(paths)
            completed = len([p for p in paths if p.status == 'completed'])
            in_progress = len([p for p in paths if p.status == 'in_progress'])
            dropped = len([p for p in paths if p.status == 'dropped'])
            
            completion_rate = (completed / total_enrolled * 100) if total_enrolled > 0 else 0
            
            completion_data.append({
                'program_id': program.id,
                'program_name': program.name,
                'total_enrolled': total_enrolled,
                'completed': completed,
                'in_progress': in_progress,
                'dropped': dropped,
                'completion_rate': round(completion_rate, 2),
                'retention_rate': round(((completed + in_progress) / total_enrolled * 100), 2) if total_enrolled > 0 else 0
            })
        
        # Sort by completion rate
        completion_data.sort(key=lambda x: x['completion_rate'], reverse=True)
        
        # Calculate overall statistics
        total_enrolled = sum(p['total_enrolled'] for p in completion_data)
        total_completed = sum(p['completed'] for p in completion_data)
        total_in_progress = sum(p['in_progress'] for p in completion_data)
        
        overall_completion = (total_completed / total_enrolled * 100) if total_enrolled > 0 else 0
        overall_retention = ((total_completed + total_in_progress) / total_enrolled * 100) if total_enrolled > 0 else 0
        
        return success_response({
            'programs': completion_data,
            'overall_stats': {
                'total_enrolled': total_enrolled,
                'total_completed': total_completed,
                'total_in_progress': total_in_progress,
                'overall_completion_rate': round(overall_completion, 2),
                'overall_retention_rate': round(overall_retention, 2)
            }
        })
        
    except Exception as e:
        return error_response(f'Failed to fetch completion rates: {str(e)}', 500)


@analytics_bp.route("/engagement-metrics", methods=["GET"])
@jwt_required()
@require_permission(['admin', 'trainer'])
@limiter.limit(api_rate_limit)
@audit_read('analytics_engagement')
def get_engagement_metrics():
    """Get user engagement analytics"""
    try:
        tenant_id = request.headers.get('X-Tenant-ID')
        if not tenant_id:
            return error_response('Tenant ID is required', 400)
        
        days = request.args.get('days', 30, type=int)
        end_date = datetime.utcnow()
        start_date = end_date - timedelta(days=days)
        
        # Get all users for this tenant
        users = User.query.filter_by(tenant_id=tenant_id, role='student').all()
        
        engagement_data = []
        
        for user in users:
            # Count recent activities
            recent_milestones = MilestoneProgress.query.filter(
                and_(
                    MilestoneProgress.user_id == user.id,
                    MilestoneProgress.updated_at >= start_date
                )
            ).count()
            
            # Count recent evaluations
            recent_evaluations = Evaluation.query.join(User).filter(
                and_(
                    User.id == user.id,
                    Evaluation.created_at >= start_date
                )
            ).count()
            
            # Calculate engagement score
            activity_score = min(recent_milestones * 2, 20)  # Max 20 points for milestones
            evaluation_score = min(recent_evaluations * 5, 30)  # Max 30 points for evaluations
            
            # Check for recent login (simplified - would need login tracking in real implementation)
            recent_login_score = 20 if user.updated_at >= start_date else 0
            
            total_score = activity_score + evaluation_score + recent_login_score
            engagement_level = 'High' if total_score >= 50 else 'Medium' if total_score >= 25 else 'Low'
            
            engagement_data.append({
                'user_id': user.id,
                'user_name': f"{user.first_name} {user.last_name}",
                'email': user.email,
                'recent_milestones': recent_milestones,
                'recent_evaluations': recent_evaluations,
                'engagement_score': total_score,
                'engagement_level': engagement_level,
                'last_activity': user.updated_at.isoformat() if user.updated_at else None
            })
        
        # Sort by engagement score
        engagement_data.sort(key=lambda x: x['engagement_score'], reverse=True)
        
        # Calculate summary statistics
        high_engagement = len([u for u in engagement_data if u['engagement_level'] == 'High'])
        medium_engagement = len([u for u in engagement_data if u['engagement_level'] == 'Medium'])
        low_engagement = len([u for u in engagement_data if u['engagement_level'] == 'Low'])
        
        avg_score = sum(u['engagement_score'] for u in engagement_data) / len(engagement_data) if engagement_data else 0
        
        return success_response({
            'engagement_data': engagement_data,
            'summary': {
                'total_users': len(engagement_data),
                'high_engagement': high_engagement,
                'medium_engagement': medium_engagement,
                'low_engagement': low_engagement,
                'average_score': round(avg_score, 2),
                'period_days': days
            }
        })
        
    except Exception as e:
        return error_response(f'Failed to fetch engagement metrics: {str(e)}', 500)


@analytics_bp.route("/risk-analysis", methods=["GET"])
@jwt_required()
@require_permission(['admin', 'trainer'])
@limiter.limit(api_rate_limit)
@audit_read('analytics_risk_analysis')
def get_risk_analysis():
    """Analyze students at risk of dropping out"""
    try:
        tenant_id = request.headers.get('X-Tenant-ID')
        if not tenant_id:
            return error_response('Tenant ID is required', 400)
        
        # Get all students with active learning paths
        students = User.query.filter_by(tenant_id=tenant_id, role='student').all()
        
        risk_analysis = []
        
        for student in students:
            active_paths = LearningPath.query.filter_by(
                user_id=student.id,
                status='in_progress'
            ).all()
            
            if not active_paths:
                continue
            
            risk_factors = []
            risk_score = 0
            
            # Check for stalled progress
            recent_activity = MilestoneProgress.query.filter(
                and_(
                    MilestoneProgress.user_id == student.id,
                    MilestoneProgress.updated_at >= datetime.utcnow() - timedelta(days=7)
                )
            ).count()
            
            if recent_activity == 0:
                risk_factors.append("No activity in last 7 days")
                risk_score += 30
            
            # Check milestone completion rate
            total_milestones = 0
            completed_milestones = 0
            
            for path in active_paths:
                if path.milestones:
                    total_milestones += len([m for m in path.milestones if not m.is_deleted])
                    completed = MilestoneProgress.query.filter_by(
                        user_id=student.id,
                        status='completed'
                    ).join(path.milestones).count()
                    completed_milestones += completed
            
            completion_rate = (completed_milestones / total_milestones * 100) if total_milestones > 0 else 0
            
            if completion_rate < 25:
                risk_factors.append("Low completion rate (<25%)")
                risk_score += 25
            elif completion_rate < 50:
                risk_factors.append("Below average completion rate (<50%)")
                risk_score += 15
            
            # Check evaluation performance
            recent_evaluations = Evaluation.query.join(User).filter(
                and_(
                    User.id == student.id,
                    Evaluation.created_at >= datetime.utcnow() - timedelta(days=30)
                )
            ).all()
            
            if recent_evaluations:
                avg_score = sum(e.score or 0 for e in recent_evaluations) / len(recent_evaluations)
                if avg_score < 60:
                    risk_factors.append("Low evaluation scores (<60%)")
                    risk_score += 20
            
            # Check for negative coach notes
            negative_notes = CoachNote.query.filter(
                and_(
                    CoachNote.student_id == student.id,
                    CoachNote.category.in_(['challenge', 'concern']),
                    CoachNote.created_at >= datetime.utcnow() - timedelta(days=14)
                )
            ).count()
            
            if negative_notes > 0:
                risk_factors.append(f"{negative_notes} concern notes in last 2 weeks")
                risk_score += negative_notes * 10
            
            # Determine risk level
            if risk_score >= 50:
                risk_level = 'High'
            elif risk_score >= 25:
                risk_level = 'Medium'
            else:
                risk_level = 'Low'
            
            risk_analysis.append({
                'student_id': student.id,
                'student_name': f"{student.first_name} {student.last_name}",
                'email': student.email,
                'risk_score': risk_score,
                'risk_level': risk_level,
                'risk_factors': risk_factors,
                'completion_rate': round(completion_rate, 2),
                'active_programs': len(active_paths),
                'last_activity': student.updated_at.isoformat() if student.updated_at else None
            })
        
        # Sort by risk score (highest risk first)
        risk_analysis.sort(key=lambda x: x['risk_score'], reverse=True)
        
        # Calculate summary
        high_risk = len([s for s in risk_analysis if s['risk_level'] == 'High'])
        medium_risk = len([s for s in risk_analysis if s['risk_level'] == 'Medium'])
        low_risk = len([s for s in risk_analysis if s['risk_level'] == 'Low'])
        
        return success_response({
            'risk_analysis': risk_analysis,
            'summary': {
                'total_students': len(risk_analysis),
                'high_risk': high_risk,
                'medium_risk': medium_risk,
                'low_risk': low_risk,
                'needs_immediate_attention': high_risk
            }
        })
        
    except Exception as e:
        return error_response(f'Failed to perform risk analysis: {str(e)}', 500)


@analytics_bp.route("/learning-patterns", methods=["GET"])
@jwt_required()
@require_permission(['admin', 'trainer'])
@limiter.limit(api_rate_limit)
@audit_read('analytics_learning_patterns')
def get_learning_patterns():
    """Analyze learning patterns and preferences"""
    try:
        tenant_id = request.headers.get('X-Tenant-ID')
        if not tenant_id:
            return error_response('Tenant ID is required', 400)
        
        days = request.args.get('days', 60, type=int)
        start_date = datetime.utcnow() - timedelta(days=days)
        
        # Get milestone completions with timing data
        milestones = MilestoneProgress.query.join(User).filter(
            and_(
                User.tenant_id == tenant_id,
                MilestoneProgress.completed_at >= start_date,
                MilestoneProgress.status == 'completed'
            )
        ).all()
        
        # Analyze completion patterns
        patterns = {
            'completion_by_hour': {},
            'completion_by_day': {},
            'average_time_to_complete': {},
            'skill_preferences': {},
            'difficulty_progression': {}
        }
        
        # Initialize hour and day counters
        for hour in range(24):
            patterns['completion_by_hour'][hour] = 0
        for day in range(7):  # 0=Monday, 6=Sunday
            patterns['completion_by_day'][day] = 0
        
        total_completion_time = 0
        completion_count = 0
        
        for milestone in milestones:
            if milestone.completed_at:
                # Hour of completion
                hour = milestone.completed_at.hour
                patterns['completion_by_hour'][hour] += 1
                
                # Day of week
                day = milestone.completed_at.weekday()
                patterns['completion_by_day'][day] += 1
                
                # Time to complete (if we have start time)
                if milestone.started_at and milestone.completed_at:
                    time_diff = (milestone.completed_at - milestone.started_at).total_seconds() / 3600  # hours
                    total_completion_time += time_diff
                    completion_count += 1
                
                # Skill category analysis (simplified)
                if milestone.milestone and hasattr(milestone.milestone, 'category'):
                    category = milestone.milestone.category or 'general'
                    patterns['skill_preferences'][category] = patterns['skill_preferences'].get(category, 0) + 1
        
        # Calculate average completion time
        avg_completion_time = total_completion_time / completion_count if completion_count > 0 else 0
        
        # Find peak learning times
        peak_hour = max(patterns['completion_by_hour'].items(), key=lambda x: x[1])[0]
        peak_day = max(patterns['completion_by_day'].items(), key=lambda x: x[1])[0]
        
        day_names = ['Monday', 'Tuesday', 'Wednesday', 'Thursday', 'Friday', 'Saturday', 'Sunday']
        
        # Format response
        formatted_patterns = {
            'completion_by_hour': [
                {'hour': hour, 'completions': count}
                for hour, count in patterns['completion_by_hour'].items()
            ],
            'completion_by_day': [
                {'day': day_names[day], 'day_number': day, 'completions': count}
                for day, count in patterns['completion_by_day'].items()
            ],
            'skill_preferences': [
                {'skill': skill, 'completions': count}
                for skill, count in patterns['skill_preferences'].items()
            ],
            'insights': {
                'peak_learning_hour': f"{peak_hour}:00",
                'peak_learning_day': day_names[peak_day],
                'average_completion_time_hours': round(avg_completion_time, 2),
                'total_completions_analyzed': len(milestones),
                'analysis_period_days': days
            }
        }
        
        return success_response(formatted_patterns)
        
    except Exception as e:
        return error_response(f'Failed to analyze learning patterns: {str(e)}', 500)


@analytics_bp.route("/export", methods=["POST"])
@jwt_required()
@require_permission(['admin', 'trainer'])
@limiter.limit("10 per hour")
@audit_read('analytics_export')
def export_analytics():
    """Export analytics data in various formats"""
    try:
        tenant_id = request.headers.get('X-Tenant-ID')
        if not tenant_id:
            return error_response('Tenant ID is required', 400)
        
        data = request.get_json()
        if not data:
            return error_response('Request body is required', 400)
        
        export_type = data.get('type', 'performance')
        format_type = data.get('format', 'json')
        days = data.get('days', 30)
        
        # Collect the requested analytics data
        export_data = {}
        
        if export_type in ['performance', 'all']:
            # Get performance trends data
            # This would call the internal functions from above endpoints
            pass  # Implementation would mirror the above endpoints
        
        if export_type in ['engagement', 'all']:
            # Get engagement data
            pass
        
        if export_type in ['risk', 'all']:
            # Get risk analysis data
            pass
        
        # For now, return a success response indicating export capability
        return success_response({
            'message': 'Analytics export functionality ready',
            'export_type': export_type,
            'format': format_type,
            'period_days': days,
            'note': 'Full implementation would generate downloadable file'
        })
        
    except Exception as e:
        return error_response(f'Failed to export analytics: {str(e)}', 500)