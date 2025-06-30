"""
Bilan de Compétence Dashboard API
Integrated view for all Bilan systems
"""
from flask import Blueprint, request, jsonify
from flask_jwt_extended import jwt_required
from app.models.assessment import Assessment, AssessmentStatus
from app.models.career import CareerPath, SkillGapAnalysis, JobOpportunity
from app.models.compliance import BilanSession, TimeLog, CertifiedConsultant
from app.models.learning_advanced import PersonalizedLearningPath, MentorshipMatch, SimulationAttempt
from app.models.user import User
from app.extensions import db
from app.core.decorators import tenant_required
from app.core.jwt_utils import get_current_user_id
from datetime import datetime, date, timedelta
from sqlalchemy import and_, or_, func

bp = Blueprint('bilan_dashboard', __name__, url_prefix='/api/v1/bilan')

@bp.route('/dashboard', methods=['GET'])
@jwt_required()
@tenant_required
def get_bilan_dashboard():
    """Get comprehensive Bilan de Compétence dashboard data"""
    user_id = get_current_user_id()
    user = User.query.get(user_id)
    
    # Initialize dashboard data
    dashboard_data = {
        'user': {
            'id': user.id,
            'name': user.full_name,
            'role': user.role,
            'email': user.email
        },
        'overview': {},
        'assessments': {},
        'career': {},
        'compliance': {},
        'learning': {},
        'actions_required': [],
        'recent_activities': []
    }
    
    # Get data based on user role
    if user.role in ['admin', 'consultant']:
        dashboard_data = get_consultant_dashboard(user_id, dashboard_data)
    else:
        dashboard_data = get_beneficiary_dashboard(user_id, dashboard_data)
    
    return jsonify(dashboard_data)

def get_beneficiary_dashboard(user_id, dashboard_data):
    """Get dashboard data for beneficiaries"""
    
    # Overview statistics
    active_sessions = BilanSession.query.filter_by(
        beneficiary_id=user_id,
        status='IN_PROGRESS'
    ).count()
    
    total_hours = db.session.query(func.sum(BilanSession.duration_minutes)).filter_by(
        beneficiary_id=user_id
    ).scalar() or 0
    
    dashboard_data['overview'] = {
        'bilan_status': get_bilan_status(user_id),
        'total_hours_completed': total_hours / 60,
        'active_sessions': active_sessions,
        'completion_percentage': calculate_bilan_completion(user_id)
    }
    
    # Assessment summary
    assessments = Assessment.query.filter_by(beneficiary_id=user_id).all()
    dashboard_data['assessments'] = {
        'total': len(assessments),
        'completed': sum(1 for a in assessments if a.status == AssessmentStatus.COMPLETED),
        'pending': sum(1 for a in assessments if a.status in [AssessmentStatus.SENT, AssessmentStatus.IN_PROGRESS]),
        'average_score': calculate_average_assessment_score(assessments),
        'recent': [{
            'id': a.id,
            'title': a.title,
            'type': a.assessment_type.value,
            'status': a.status.value,
            'completion_rate': a.completion_rate
        } for a in sorted(assessments, key=lambda x: x.created_at, reverse=True)[:3]]
    }
    
    # Career progress
    career_path = CareerPath.query.filter_by(user_id=user_id).order_by(
        CareerPath.created_at.desc()
    ).first()
    
    skill_analysis = SkillGapAnalysis.query.filter_by(user_id=user_id).order_by(
        SkillGapAnalysis.analysis_date.desc()
    ).first()
    
    dashboard_data['career'] = {
        'current_path': {
            'id': career_path.id,
            'target_role': career_path.target_job_title,
            'progress': career_path.progress_percentage,
            'milestones_completed': sum(1 for m in career_path.milestones if m.status == 'completed')
        } if career_path else None,
        'skill_gaps': len(skill_analysis.skill_gaps) if skill_analysis else 0,
        'priority_skills': skill_analysis.priority_skills[:3] if skill_analysis else [],
        'job_matches': JobOpportunity.query.filter_by(user_id=user_id).count()
    }
    
    # Compliance status
    sessions = BilanSession.query.filter_by(beneficiary_id=user_id).all()
    phases_completed = set(s.phase.value for s in sessions if s.status == 'COMPLETED')
    
    dashboard_data['compliance'] = {
        'contract_number': sessions[0].contract_number if sessions else None,
        'phases_completed': list(phases_completed),
        'phases_remaining': [p for p in ['PRELIMINARY', 'INVESTIGATION', 'CONCLUSION'] if p not in phases_completed],
        'total_sessions': len(sessions),
        'next_session': get_next_session(user_id)
    }
    
    # Learning progress
    active_paths = PersonalizedLearningPath.query.filter_by(
        user_id=user_id,
        status='ACTIVE'
    ).all()
    
    dashboard_data['learning'] = {
        'active_paths': len(active_paths),
        'average_progress': sum(p.overall_progress for p in active_paths) / len(active_paths) if active_paths else 0,
        'total_learning_hours': sum(p.total_time_spent or 0 for p in active_paths) / 60,
        'skills_acquired': sum(len(p.skills_acquired or []) for p in active_paths),
        'mentorship_active': MentorshipMatch.query.filter_by(
            mentee_id=user_id,
            status='ACTIVE'
        ).count() > 0
    }
    
    # Actions required
    dashboard_data['actions_required'] = get_beneficiary_actions(user_id)
    
    # Recent activities
    dashboard_data['recent_activities'] = get_recent_activities(user_id)
    
    return dashboard_data

def get_consultant_dashboard(user_id, dashboard_data):
    """Get dashboard data for consultants"""
    
    # Check if certified consultant
    consultant = CertifiedConsultant.query.filter_by(user_id=user_id).first()
    
    if consultant:
        dashboard_data['consultant_info'] = {
            'certification_number': consultant.certification_number,
            'certification_valid': consultant.expiry_date > date.today(),
            'bilans_completed': consultant.bilans_completed,
            'current_bilans': consultant.current_bilans_count,
            'max_bilans': consultant.max_concurrent_bilans,
            'average_rating': consultant.average_rating
        }
    
    # Overview for consultant
    active_sessions = BilanSession.query.filter_by(
        consultant_id=user_id,
        status='IN_PROGRESS'
    ).count()
    
    total_beneficiaries = db.session.query(func.count(func.distinct(BilanSession.beneficiary_id))).filter_by(
        consultant_id=user_id
    ).scalar() or 0
    
    dashboard_data['overview'] = {
        'active_sessions': active_sessions,
        'total_beneficiaries': total_beneficiaries,
        'sessions_this_month': get_sessions_this_month(user_id),
        'compliance_rate': calculate_consultant_compliance_rate(user_id)
    }
    
    # Active beneficiaries
    active_beneficiaries = db.session.query(BilanSession).filter_by(
        consultant_id=user_id
    ).filter(BilanSession.status.in_(['SCHEDULED', 'IN_PROGRESS'])).all()
    
    dashboard_data['active_beneficiaries'] = [{
        'id': session.beneficiary_id,
        'name': session.beneficiary.full_name,
        'phase': session.phase.value,
        'next_session': session.scheduled_start.isoformat() if session.status == 'SCHEDULED' else None,
        'progress': calculate_beneficiary_progress(session.beneficiary_id)
    } for session in active_beneficiaries[:5]]
    
    # Upcoming sessions
    upcoming_sessions = BilanSession.query.filter_by(
        consultant_id=user_id,
        status='SCHEDULED'
    ).filter(
        BilanSession.scheduled_start >= datetime.utcnow(),
        BilanSession.scheduled_start <= datetime.utcnow() + timedelta(days=7)
    ).order_by(BilanSession.scheduled_start).limit(5).all()
    
    dashboard_data['upcoming_sessions'] = [{
        'id': s.id,
        'beneficiary_name': s.beneficiary.full_name,
        'date': s.scheduled_start.isoformat(),
        'phase': s.phase.value,
        'duration': (s.scheduled_end - s.scheduled_start).total_seconds() / 60
    } for s in upcoming_sessions]
    
    # Compliance alerts
    dashboard_data['compliance_alerts'] = get_consultant_compliance_alerts(user_id)
    
    # Actions required
    dashboard_data['actions_required'] = get_consultant_actions(user_id)
    
    return dashboard_data

@bp.route('/timeline/<int:beneficiary_id>', methods=['GET'])
@jwt_required()
@tenant_required
def get_bilan_timeline(beneficiary_id):
    """Get complete Bilan timeline for a beneficiary"""
    user_id = get_current_user_id()
    
    # Verify permissions
    if user_id != beneficiary_id:
        # Check if consultant for this beneficiary
        session = BilanSession.query.filter_by(
            beneficiary_id=beneficiary_id,
            consultant_id=user_id
        ).first()
        
        if not session:
            return jsonify({'error': 'Unauthorized'}), 403
    
    # Get all timeline events
    timeline_events = []
    
    # Sessions
    sessions = BilanSession.query.filter_by(beneficiary_id=beneficiary_id).all()
    for session in sessions:
        timeline_events.append({
            'type': 'session',
            'date': session.scheduled_start.isoformat(),
            'title': f'{session.phase.value} Session',
            'description': f'Duration: {session.duration_minutes or 0} minutes',
            'status': session.status.value
        })
    
    # Assessments
    assessments = Assessment.query.filter_by(beneficiary_id=beneficiary_id).all()
    for assessment in assessments:
        timeline_events.append({
            'type': 'assessment',
            'date': assessment.created_at.isoformat(),
            'title': assessment.title,
            'description': f'Type: {assessment.assessment_type.value}',
            'status': assessment.status.value
        })
    
    # Career milestones
    career_path = CareerPath.query.filter_by(user_id=beneficiary_id).first()
    if career_path:
        for milestone in career_path.milestones:
            timeline_events.append({
                'type': 'milestone',
                'date': (milestone.completed_date or milestone.target_date).isoformat() if milestone.completed_date or milestone.target_date else None,
                'title': milestone.title,
                'description': milestone.description,
                'status': milestone.status
            })
    
    # Sort by date
    timeline_events.sort(key=lambda x: x['date'] if x['date'] else '9999-12-31', reverse=True)
    
    return jsonify({'timeline': timeline_events})

@bp.route('/progress/<int:beneficiary_id>', methods=['GET'])
@jwt_required()
@tenant_required
def get_bilan_progress(beneficiary_id):
    """Get detailed Bilan progress for a beneficiary"""
    user_id = get_current_user_id()
    
    # Verify permissions
    if user_id != beneficiary_id:
        session = BilanSession.query.filter_by(
            beneficiary_id=beneficiary_id,
            consultant_id=user_id
        ).first()
        
        if not session:
            return jsonify({'error': 'Unauthorized'}), 403
    
    progress = {
        'overall_completion': calculate_bilan_completion(beneficiary_id),
        'phases': get_phase_progress(beneficiary_id),
        'assessments': get_assessment_progress(beneficiary_id),
        'career_planning': get_career_progress(beneficiary_id),
        'learning': get_learning_progress(beneficiary_id),
        'compliance': get_compliance_status(beneficiary_id)
    }
    
    return jsonify(progress)

@bp.route('/recommendations/<int:beneficiary_id>', methods=['GET'])
@jwt_required()
@tenant_required
def get_bilan_recommendations(beneficiary_id):
    """Get AI-powered recommendations for next steps"""
    user_id = get_current_user_id()
    
    # Verify permissions
    if user_id != beneficiary_id:
        session = BilanSession.query.filter_by(
            beneficiary_id=beneficiary_id,
            consultant_id=user_id
        ).first()
        
        if not session:
            return jsonify({'error': 'Unauthorized'}), 403
    
    recommendations = {
        'immediate_actions': get_immediate_recommendations(beneficiary_id),
        'skill_development': get_skill_recommendations(beneficiary_id),
        'career_opportunities': get_career_recommendations(beneficiary_id),
        'learning_suggestions': get_learning_recommendations(beneficiary_id)
    }
    
    return jsonify(recommendations)

# Helper functions

def get_bilan_status(user_id):
    """Determine overall Bilan status"""
    sessions = BilanSession.query.filter_by(beneficiary_id=user_id).all()
    
    if not sessions:
        return 'not_started'
    
    phases_completed = set(s.phase.value for s in sessions if s.status == 'COMPLETED')
    
    if len(phases_completed) == 3:
        return 'completed'
    elif len(phases_completed) > 0:
        return 'in_progress'
    else:
        return 'started'

def calculate_bilan_completion(user_id):
    """Calculate overall Bilan completion percentage"""
    # Check phases (33% each)
    sessions = BilanSession.query.filter_by(beneficiary_id=user_id).all()
    phases_completed = set(s.phase.value for s in sessions if s.status == 'COMPLETED')
    phase_completion = len(phases_completed) / 3 * 33
    
    # Check assessments (34%)
    assessments = Assessment.query.filter_by(beneficiary_id=user_id).all()
    assessment_completion = (sum(1 for a in assessments if a.status == AssessmentStatus.COMPLETED) / 
                           max(len(assessments), 1)) * 34
    
    # Check career planning (33%)
    career_path = CareerPath.query.filter_by(user_id=user_id).first()
    career_completion = (career_path.progress_percentage / 100 * 33) if career_path else 0
    
    return min(phase_completion + assessment_completion + career_completion, 100)

def calculate_average_assessment_score(assessments):
    """Calculate average assessment score"""
    scores = [a.average_score for a in assessments if a.average_score is not None]
    return sum(scores) / len(scores) if scores else 0

def get_next_session(user_id):
    """Get next scheduled session"""
    session = BilanSession.query.filter_by(
        beneficiary_id=user_id,
        status='SCHEDULED'
    ).filter(
        BilanSession.scheduled_start >= datetime.utcnow()
    ).order_by(BilanSession.scheduled_start).first()
    
    if session:
        return {
            'id': session.id,
            'date': session.scheduled_start.isoformat(),
            'phase': session.phase.value,
            'consultant_name': session.consultant.full_name
        }
    return None

def get_beneficiary_actions(user_id):
    """Get required actions for beneficiary"""
    actions = []
    
    # Check for pending assessments
    pending_assessments = Assessment.query.filter_by(
        beneficiary_id=user_id,
        status='SENT'
    ).count()
    
    if pending_assessments > 0:
        actions.append({
            'type': 'assessment',
            'priority': 'high',
            'message': f'{pending_assessments} assessment(s) waiting for completion',
            'action': 'complete_assessment'
        })
    
    # Check for scheduled sessions
    upcoming_session = BilanSession.query.filter_by(
        beneficiary_id=user_id,
        status='SCHEDULED'
    ).filter(
        BilanSession.scheduled_start <= datetime.utcnow() + timedelta(days=3)
    ).first()
    
    if upcoming_session:
        actions.append({
            'type': 'session',
            'priority': 'medium',
            'message': f'Session scheduled for {upcoming_session.scheduled_start.strftime("%Y-%m-%d %H:%M")}',
            'action': 'prepare_session'
        })
    
    # Check learning path progress
    active_path = PersonalizedLearningPath.query.filter_by(
        user_id=user_id,
        status='ACTIVE'
    ).first()
    
    if active_path and active_path.overall_progress < 50:
        actions.append({
            'type': 'learning',
            'priority': 'low',
            'message': 'Continue your learning path',
            'action': 'continue_learning'
        })
    
    return actions

def get_recent_activities(user_id):
    """Get recent activities for user"""
    activities = []
    
    # Recent sessions
    recent_sessions = BilanSession.query.filter_by(
        beneficiary_id=user_id
    ).order_by(BilanSession.updated_at.desc()).limit(3).all()
    
    for session in recent_sessions:
        activities.append({
            'type': 'session',
            'date': session.updated_at.isoformat(),
            'description': f'{session.phase.value} session {session.status.value.lower()}'
        })
    
    # Recent assessments
    recent_assessments = Assessment.query.filter_by(
        beneficiary_id=user_id
    ).order_by(Assessment.updated_at.desc()).limit(3).all()
    
    for assessment in recent_assessments:
        activities.append({
            'type': 'assessment',
            'date': assessment.updated_at.isoformat(),
            'description': f'{assessment.title} - {assessment.status.value.lower()}'
        })
    
    # Sort by date
    activities.sort(key=lambda x: x['date'], reverse=True)
    
    return activities[:5]

def get_sessions_this_month(consultant_id):
    """Get number of sessions this month for consultant"""
    start_of_month = date.today().replace(day=1)
    
    return BilanSession.query.filter_by(
        consultant_id=consultant_id
    ).filter(
        BilanSession.scheduled_start >= start_of_month
    ).count()

def calculate_consultant_compliance_rate(consultant_id):
    """Calculate compliance rate for consultant's sessions"""
    # Implementation would check compliance checks for consultant's sessions
    return 95.0  # Placeholder

def calculate_beneficiary_progress(beneficiary_id):
    """Calculate progress for a specific beneficiary"""
    return calculate_bilan_completion(beneficiary_id)

def get_consultant_compliance_alerts(consultant_id):
    """Get compliance alerts for consultant"""
    alerts = []
    
    # Check certification expiry
    consultant = CertifiedConsultant.query.filter_by(user_id=consultant_id).first()
    if consultant and consultant.expiry_date <= date.today() + timedelta(days=30):
        alerts.append({
            'type': 'certification',
            'severity': 'high',
            'message': f'Certification expires on {consultant.expiry_date.isoformat()}'
        })
    
    # Check incomplete sessions
    incomplete_sessions = BilanSession.query.filter_by(
        consultant_id=consultant_id,
        status='IN_PROGRESS'
    ).filter(
        BilanSession.scheduled_end < datetime.utcnow() - timedelta(days=7)
    ).count()
    
    if incomplete_sessions > 0:
        alerts.append({
            'type': 'sessions',
            'severity': 'medium',
            'message': f'{incomplete_sessions} session(s) need completion'
        })
    
    return alerts

def get_consultant_actions(consultant_id):
    """Get required actions for consultant"""
    actions = []
    
    # Check for sessions to validate
    sessions_to_validate = BilanSession.query.filter_by(
        consultant_id=consultant_id,
        status='COMPLETED',
        validated_by_consultant=False
    ).count()
    
    if sessions_to_validate > 0:
        actions.append({
            'type': 'validation',
            'priority': 'high',
            'message': f'{sessions_to_validate} session(s) need validation',
            'action': 'validate_sessions'
        })
    
    # Check for reports to generate
    completed_bilans = db.session.query(BilanSession.beneficiary_id).filter_by(
        consultant_id=consultant_id
    ).group_by(BilanSession.beneficiary_id).having(
        func.count(func.distinct(BilanSession.phase)) == 3
    ).count()
    
    if completed_bilans > 0:
        actions.append({
            'type': 'report',
            'priority': 'medium',
            'message': f'{completed_bilans} synthesis report(s) to generate',
            'action': 'generate_reports'
        })
    
    return actions

def get_phase_progress(beneficiary_id):
    """Get progress for each Bilan phase"""
    sessions = BilanSession.query.filter_by(beneficiary_id=beneficiary_id).all()
    
    phases = {
        'PRELIMINARY': {'completed': False, 'hours': 0},
        'INVESTIGATION': {'completed': False, 'hours': 0},
        'CONCLUSION': {'completed': False, 'hours': 0}
    }
    
    for session in sessions:
        phase = session.phase.value
        if session.status == 'COMPLETED':
            phases[phase]['completed'] = True
            phases[phase]['hours'] += (session.duration_minutes or 0) / 60
    
    return phases

def get_assessment_progress(beneficiary_id):
    """Get assessment progress"""
    assessments = Assessment.query.filter_by(beneficiary_id=beneficiary_id).all()
    
    return {
        'total': len(assessments),
        'completed': sum(1 for a in assessments if a.status == AssessmentStatus.COMPLETED),
        'average_score': calculate_average_assessment_score(assessments),
        'by_type': {
            assessment_type: sum(1 for a in assessments if a.assessment_type.value == assessment_type)
            for assessment_type in ['SELF', 'PEER', 'MANAGER']
        }
    }

def get_career_progress(beneficiary_id):
    """Get career planning progress"""
    career_path = CareerPath.query.filter_by(user_id=beneficiary_id).first()
    
    if not career_path:
        return {'status': 'not_started'}
    
    return {
        'status': career_path.career_status.value,
        'progress_percentage': career_path.progress_percentage,
        'milestones_completed': sum(1 for m in career_path.milestones if m.status == 'completed'),
        'total_milestones': len(career_path.milestones),
        'estimated_completion': career_path.estimated_completion.isoformat() if career_path.estimated_completion else None
    }

def get_learning_progress(beneficiary_id):
    """Get learning progress"""
    paths = PersonalizedLearningPath.query.filter_by(user_id=beneficiary_id).all()
    
    return {
        'paths_created': len(paths),
        'active_paths': sum(1 for p in paths if p.status == 'ACTIVE'),
        'average_progress': sum(p.overall_progress for p in paths) / len(paths) if paths else 0,
        'total_hours': sum(p.total_time_spent or 0 for p in paths) / 60
    }

def get_compliance_status(beneficiary_id):
    """Get compliance status"""
    sessions = BilanSession.query.filter_by(beneficiary_id=beneficiary_id).all()
    
    total_hours = sum(s.duration_minutes or 0 for s in sessions) / 60
    required_hours = 24
    
    return {
        'hours_completed': total_hours,
        'hours_required': required_hours,
        'is_compliant': total_hours >= required_hours,
        'missing_elements': get_missing_compliance_elements(beneficiary_id)
    }

def get_missing_compliance_elements(beneficiary_id):
    """Get missing compliance elements"""
    missing = []
    
    sessions = BilanSession.query.filter_by(beneficiary_id=beneficiary_id).all()
    phases_completed = set(s.phase.value for s in sessions if s.status == 'COMPLETED')
    
    for phase in ['PRELIMINARY', 'INVESTIGATION', 'CONCLUSION']:
        if phase not in phases_completed:
            missing.append(f'{phase} phase not completed')
    
    total_hours = sum(s.duration_minutes or 0 for s in sessions) / 60
    if total_hours < 24:
        missing.append(f'Only {total_hours:.1f} hours completed (24 required)')
    
    return missing

def get_immediate_recommendations(beneficiary_id):
    """Get immediate action recommendations"""
    recommendations = []
    
    # Check incomplete assessments
    pending_assessments = Assessment.query.filter_by(
        beneficiary_id=beneficiary_id,
        status='SENT'
    ).all()
    
    if pending_assessments:
        recommendations.append({
            'action': 'Complete pending assessments',
            'reason': f'{len(pending_assessments)} assessment(s) are waiting for your input',
            'priority': 'high'
        })
    
    # Check next phase
    sessions = BilanSession.query.filter_by(beneficiary_id=beneficiary_id).all()
    phases_completed = set(s.phase.value for s in sessions if s.status == 'COMPLETED')
    
    if 'PRELIMINARY' not in phases_completed:
        recommendations.append({
            'action': 'Schedule preliminary phase session',
            'reason': 'This is the first required phase of your Bilan',
            'priority': 'high'
        })
    elif 'INVESTIGATION' not in phases_completed:
        recommendations.append({
            'action': 'Begin investigation phase',
            'reason': 'Explore your skills and career options in depth',
            'priority': 'medium'
        })
    
    return recommendations

def get_skill_recommendations(beneficiary_id):
    """Get skill development recommendations"""
    skill_analysis = SkillGapAnalysis.query.filter_by(
        user_id=beneficiary_id
    ).order_by(SkillGapAnalysis.analysis_date.desc()).first()
    
    if not skill_analysis:
        return []
    
    return [{
        'skill': skill,
        'current_level': skill_analysis.current_skills.get(skill, 0),
        'required_level': skill_analysis.required_skills.get(skill, 0),
        'priority': 'high' if skill in skill_analysis.critical_gaps else 'medium'
    } for skill in skill_analysis.priority_skills[:5]]

def get_career_recommendations(beneficiary_id):
    """Get career opportunity recommendations"""
    opportunities = JobOpportunity.query.filter_by(
        user_id=beneficiary_id
    ).order_by(JobOpportunity.match_score.desc()).limit(3).all()
    
    return [{
        'job_title': opp.job_title,
        'company': opp.company_name,
        'match_score': opp.match_score,
        'key_matching_skills': opp.matching_skills[:3] if opp.matching_skills else []
    } for opp in opportunities]

def get_learning_recommendations(beneficiary_id):
    """Get learning recommendations"""
    # Get skill gaps
    skill_analysis = SkillGapAnalysis.query.filter_by(
        user_id=beneficiary_id
    ).order_by(SkillGapAnalysis.analysis_date.desc()).first()
    
    if not skill_analysis or not skill_analysis.recommended_courses:
        return []
    
    return skill_analysis.recommended_courses[:5]