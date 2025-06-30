"""
Advanced Learning System API endpoints
For Bilan de Compétence Platform - Personalized Learning
"""
from flask import Blueprint, request, jsonify
from flask_jwt_extended import jwt_required
from app.models.learning_advanced import (
    AdvancedLearningContent, PersonalizedLearningPath, PathContent,
    AdvancedLearningMilestone, MentorshipMatch, MentorshipSession,
    JobSimulation, SimulationAttempt, ContentRecommendation, ContentProgress,
    ContentType, LearningPathStatus, MentorshipStatus, SimulationType
)
from app.models.user import User
from app.extensions import db
from app.core.decorators import tenant_required
from app.core.jwt_utils import get_current_user_id
from app.core.pagination import paginate
from datetime import datetime, date, timedelta
from sqlalchemy import and_, or_, func
import json
import random

bp = Blueprint('learning_advanced', __name__, url_prefix='/api/v1/learning')

@bp.route('/content', methods=['GET'])
@jwt_required()
@tenant_required
def get_learning_content():
    """Get learning content with filters"""
    query = AdvancedLearningContent.query
    
    # Filter by content type
    content_type = request.args.get('type')
    if content_type:
        query = query.filter(AdvancedLearningContent.content_type == ContentType[content_type.upper()])
    
    # Filter by skill categories
    skill = request.args.get('skill')
    if skill:
        query = query.filter(AdvancedLearningContent.skill_categories.contains([skill]))
    
    # Filter by difficulty
    difficulty = request.args.get('difficulty')
    if difficulty:
        query = query.filter(AdvancedLearningContent.difficulty_level == int(difficulty))
    
    # Filter by language
    language = request.args.get('language', 'fr')
    query = query.filter(AdvancedLearningContent.language == language)
    
    # Filter by free/paid
    is_free = request.args.get('is_free')
    if is_free is not None:
        query = query.filter(AdvancedLearningContent.is_free == (is_free.lower() == 'true'))
    
    # Sort by relevance or rating
    sort_by = request.args.get('sort_by', 'relevance')
    if sort_by == 'rating':
        query = query.order_by(AdvancedLearningContent.average_rating.desc())
    elif sort_by == 'completion':
        query = query.order_by(AdvancedLearningContent.completion_rate.desc())
    else:
        query = query.order_by(AdvancedLearningContent.relevance_score.desc())
    
    return paginate(query, AdvancedLearningContent)

@bp.route('/content/<int:id>', methods=['GET'])
@jwt_required()
@tenant_required
def get_content_detail(id):
    """Get detailed content information"""
    user_id = get_current_user_id()
    
    content = AdvancedLearningContent.query.filter_by(id=id).first_or_404()
    
    # Get user's progress
    progress = ContentProgress.query.filter_by(
        user_id=user_id,
        content_id=id
    ).first()
    
    return jsonify({
        'id': content.id,
        'title': content.title,
        'description': content.description,
        'content_type': content.content_type.value,
        'content_url': content.content_url,
        'duration_minutes': content.duration_minutes,
        'difficulty_level': content.difficulty_level,
        'skill_categories': content.skill_categories,
        'tags': content.tags,
        'language': content.language,
        'learning_objectives': content.learning_objectives,
        'prerequisites': content.prerequisites,
        'target_audience': content.target_audience,
        'quality_score': content.quality_score,
        'average_rating': content.average_rating,
        'completion_rate': content.completion_rate,
        'provider_name': content.provider_name,
        'is_free': content.is_free,
        'price': content.price,
        'key_concepts': content.key_concepts,
        'user_progress': {
            'progress_percentage': progress.progress_percentage if progress else 0,
            'is_completed': progress.is_completed if progress else False,
            'score': progress.score if progress else None,
            'time_spent': progress.total_time_spent if progress else 0
        } if progress else None
    })

@bp.route('/paths', methods=['GET'])
@jwt_required()
@tenant_required
def get_learning_paths():
    """Get user's personalized learning paths"""
    user_id = get_current_user_id()
    
    paths = PersonalizedLearningPath.query.filter_by(user_id=user_id).all()
    
    return jsonify({
        'learning_paths': [{
            'id': path.id,
            'title': path.title,
            'description': path.description,
            'status': path.status.value if path.status else None,
            'start_date': path.start_date.isoformat() if path.start_date else None,
            'target_end_date': path.target_end_date.isoformat() if path.target_end_date else None,
            'primary_goal': path.primary_goal,
            'overall_progress': path.overall_progress,
            'milestones_completed': path.milestones_completed,
            'total_time_spent': path.total_time_spent,
            'average_score': path.average_score,
            'contents_count': len(path.contents),
            'created_at': path.created_at.isoformat()
        } for path in paths]
    })

@bp.route('/paths', methods=['POST'])
@jwt_required()
@tenant_required
def create_learning_path():
    """Create a personalized learning path"""
    user_id = get_current_user_id()
    data = request.get_json()
    
    path = PersonalizedLearningPath(
        user_id=user_id,
        title=data['title'],
        description=data.get('description'),
        status=LearningPathStatus.DRAFT,
        start_date=date.fromisoformat(data['start_date']) if data.get('start_date') else date.today(),
        target_end_date=date.fromisoformat(data['target_end_date']) if data.get('target_end_date') else None,
        primary_goal=data.get('primary_goal'),
        learning_objectives=data.get('learning_objectives', []),
        target_skills=data.get('target_skills', []),
        learning_style=data.get('learning_style', 'mixed'),
        time_availability=data.get('time_availability', 5),  # hours per week
        preferred_content_types=data.get('preferred_content_types', []),
        preferred_duration=data.get('preferred_duration', 'medium'),
        adaptation_enabled=data.get('adaptation_enabled', True),
        difficulty_adjustment=data.get('difficulty_adjustment', True),
        content_diversity=data.get('content_diversity', 0.7)
    )
    
    db.session.add(path)
    db.session.commit()
    
    # Generate initial content recommendations
    generate_path_content(path)
    
    return jsonify({
        'id': path.id,
        'title': path.title,
        'message': 'Learning path created successfully'
    }), 201

@bp.route('/paths/<int:id>', methods=['GET'])
@jwt_required()
@tenant_required
def get_learning_path_detail(id):
    """Get detailed learning path information"""
    user_id = get_current_user_id()
    
    path = PersonalizedLearningPath.query.filter_by(id=id, user_id=user_id).first_or_404()
    
    return jsonify({
        'id': path.id,
        'title': path.title,
        'description': path.description,
        'status': path.status.value if path.status else None,
        'start_date': path.start_date.isoformat() if path.start_date else None,
        'target_end_date': path.target_end_date.isoformat() if path.target_end_date else None,
        'actual_end_date': path.actual_end_date.isoformat() if path.actual_end_date else None,
        'primary_goal': path.primary_goal,
        'learning_objectives': path.learning_objectives,
        'target_skills': path.target_skills,
        'learning_style': path.learning_style,
        'time_availability': path.time_availability,
        'preferred_content_types': path.preferred_content_types,
        'preferred_duration': path.preferred_duration,
        'adaptation_enabled': path.adaptation_enabled,
        'overall_progress': path.overall_progress,
        'skills_acquired': path.skills_acquired,
        'milestones_completed': path.milestones_completed,
        'total_time_spent': path.total_time_spent,
        'average_score': path.average_score,
        'completion_rate': path.completion_rate,
        'engagement_level': path.engagement_level,
        'contents': [{
            'id': pc.content.id,
            'title': pc.content.title,
            'content_type': pc.content.content_type.value,
            'order_index': pc.order_index,
            'is_mandatory': pc.is_mandatory,
            'is_completed': pc.is_completed,
            'score': pc.score,
            'scheduled_date': pc.scheduled_date.isoformat() if pc.scheduled_date else None
        } for pc in sorted(path.contents, key=lambda x: x.order_index)],
        'milestones': [{
            'id': m.id,
            'title': m.title,
            'order_index': m.order_index,
            'is_completed': m.is_completed,
            'completion_date': m.completion_date.isoformat() if m.completion_date else None
        } for m in sorted(path.milestones, key=lambda x: x.order_index)]
    })

@bp.route('/paths/<int:id>/activate', methods=['POST'])
@jwt_required()
@tenant_required
def activate_learning_path(id):
    """Activate a learning path"""
    user_id = get_current_user_id()
    
    path = PersonalizedLearningPath.query.filter_by(id=id, user_id=user_id).first_or_404()
    
    if path.status != LearningPathStatus.DRAFT:
        return jsonify({'error': 'Path is not in draft status'}), 400
    
    if not path.contents:
        return jsonify({'error': 'Path must have content before activation'}), 400
    
    path.status = LearningPathStatus.ACTIVE
    path.start_date = date.today()
    
    db.session.commit()
    
    return jsonify({
        'message': 'Learning path activated',
        'start_date': path.start_date.isoformat()
    })

@bp.route('/paths/<int:path_id>/content/<int:content_id>/complete', methods=['POST'])
@jwt_required()
@tenant_required
def complete_path_content(path_id, content_id):
    """Mark content as completed in a learning path"""
    user_id = get_current_user_id()
    data = request.get_json()
    
    path = PersonalizedLearningPath.query.filter_by(id=path_id, user_id=user_id).first_or_404()
    
    # Find path content
    path_content = PathContent.query.filter_by(
        path_id=path_id,
        content_id=content_id
    ).first_or_404()
    
    path_content.is_completed = True
    path_content.completion_date = datetime.utcnow()
    path_content.score = data.get('score')
    path_content.time_spent = data.get('time_spent', 0)
    
    # Update content progress
    progress = ContentProgress.query.filter_by(
        user_id=user_id,
        content_id=content_id
    ).first()
    
    if not progress:
        progress = ContentProgress(
            user_id=user_id,
            content_id=content_id
        )
        db.session.add(progress)
    
    progress.is_completed = True
    progress.completion_date = datetime.utcnow()
    progress.progress_percentage = 100.0
    progress.score = data.get('score')
    progress.total_time_spent = (progress.total_time_spent or 0) + data.get('time_spent', 0)
    
    # Update path progress
    completed_contents = sum(1 for pc in path.contents if pc.is_completed)
    path.overall_progress = (completed_contents / len(path.contents)) * 100 if path.contents else 0
    path.total_time_spent = (path.total_time_spent or 0) + data.get('time_spent', 0)
    
    # Check for milestone completion
    check_milestone_completion(path)
    
    # Adapt learning path if enabled
    if path.adaptation_enabled:
        adapt_learning_path(path, path_content)
    
    db.session.commit()
    
    return jsonify({
        'message': 'Content completed',
        'path_progress': path.overall_progress
    })

@bp.route('/mentorship/available', methods=['GET'])
@jwt_required()
@tenant_required
def get_available_mentors():
    """Get available mentors"""
    user_id = get_current_user_id()
    
    # Get user's skills and goals
    user = User.query.get(user_id)
    
    # Find mentors with matching expertise
    # TODO: Implement proper matching algorithm
    potential_mentors = User.query.filter(
        User.id != user_id,
        User.role.in_(['trainer', 'consultant'])
    ).all()
    
    return jsonify({
        'mentors': [{
            'id': mentor.id,
            'name': mentor.full_name,
            'expertise': [],  # TODO: Get from profile
            'rating': 4.5,  # TODO: Calculate from feedback
            'availability': 'available'
        } for mentor in potential_mentors[:10]]  # Limit to 10
    })

@bp.route('/mentorship/request', methods=['POST'])
@jwt_required()
@tenant_required
def request_mentorship():
    """Request mentorship from a mentor"""
    user_id = get_current_user_id()
    data = request.get_json()
    
    # Check if already matched
    existing = MentorshipMatch.query.filter_by(
        mentee_id=user_id,
        mentor_id=data['mentor_id'],
        status__in=[MentorshipStatus.PENDING, MentorshipStatus.MATCHED, MentorshipStatus.ACTIVE]
    ).first()
    
    if existing:
        return jsonify({'error': 'Mentorship already requested or active'}), 400
    
    match = MentorshipMatch(
        mentee_id=user_id,
        mentor_id=data['mentor_id'],
        status=MentorshipStatus.PENDING,
        requested_date=datetime.utcnow(),
        mentorship_goals=data.get('goals', []),
        focus_areas=data.get('focus_areas', []),
        meeting_frequency=data.get('meeting_frequency', 'biweekly'),
        meeting_duration=data.get('meeting_duration', 60),
        communication_preferences=data.get('communication_preferences', ['video'])
    )
    
    # Calculate match score
    # TODO: Implement proper matching algorithm
    match.match_score = random.uniform(70, 95)
    match.match_reasons = ['Shared industry experience', 'Complementary skills']
    
    db.session.add(match)
    db.session.commit()
    
    # TODO: Notify mentor
    
    return jsonify({
        'id': match.id,
        'match_score': match.match_score,
        'message': 'Mentorship request sent'
    }), 201

@bp.route('/mentorship/<int:id>/accept', methods=['POST'])
@jwt_required()
@tenant_required
def accept_mentorship(id):
    """Accept a mentorship request"""
    user_id = get_current_user_id()
    
    match = MentorshipMatch.query.filter_by(
        id=id,
        mentor_id=user_id,
        status=MentorshipStatus.PENDING
    ).first_or_404()
    
    match.status = MentorshipStatus.MATCHED
    match.matched_date = datetime.utcnow()
    match.start_date = date.today()
    
    db.session.commit()
    
    # TODO: Notify mentee
    
    return jsonify({'message': 'Mentorship accepted'})

@bp.route('/mentorship/<int:id>/sessions', methods=['POST'])
@jwt_required()
@tenant_required
def create_mentorship_session(id):
    """Create a mentorship session"""
    user_id = get_current_user_id()
    data = request.get_json()
    
    match = MentorshipMatch.query.filter_by(id=id).first_or_404()
    
    # Verify user is part of the match
    if user_id not in [match.mentee_id, match.mentor_id]:
        return jsonify({'error': 'Unauthorized'}), 403
    
    session = MentorshipSession(
        match_id=id,
        session_date=datetime.fromisoformat(data['session_date']),
        duration_minutes=data.get('duration_minutes', 60),
        topics_discussed=data.get('topics_discussed', []),
        key_insights=data.get('key_insights'),
        action_items=data.get('action_items', []),
        resources_shared=data.get('resources_shared', [])
    )
    
    db.session.add(session)
    
    # Update match statistics
    match.sessions_completed = (match.sessions_completed or 0) + 1
    
    # Update match status if first session
    if match.status == MentorshipStatus.MATCHED:
        match.status = MentorshipStatus.ACTIVE
    
    db.session.commit()
    
    return jsonify({
        'id': session.id,
        'message': 'Session created successfully'
    }), 201

@bp.route('/simulations', methods=['GET'])
@jwt_required()
@tenant_required
def get_job_simulations():
    """Get available job simulations"""
    query = JobSimulation.query
    
    # Filter by type
    sim_type = request.args.get('type')
    if sim_type:
        query = query.filter(JobSimulation.simulation_type == SimulationType[sim_type.upper()])
    
    # Filter by job role
    job_role = request.args.get('job_role')
    if job_role:
        query = query.filter(JobSimulation.job_role.ilike(f'%{job_role}%'))
    
    # Filter by difficulty
    difficulty = request.args.get('difficulty')
    if difficulty:
        query = query.filter(JobSimulation.difficulty_level == int(difficulty))
    
    query = query.order_by(JobSimulation.created_at.desc())
    
    return paginate(query, JobSimulation)

@bp.route('/simulations/<int:id>/start', methods=['POST'])
@jwt_required()
@tenant_required
def start_simulation(id):
    """Start a job simulation"""
    user_id = get_current_user_id()
    
    simulation = JobSimulation.query.filter_by(id=id).first_or_404()
    
    # Create attempt
    attempt = SimulationAttempt(
        simulation_id=id,
        user_id=user_id,
        start_time=datetime.utcnow()
    )
    
    db.session.add(attempt)
    db.session.commit()
    
    return jsonify({
        'attempt_id': attempt.id,
        'simulation': {
            'id': simulation.id,
            'title': simulation.title,
            'scenario_data': simulation.scenario_data,
            'duration_minutes': simulation.duration_minutes
        }
    }), 201

@bp.route('/simulations/<int:simulation_id>/attempts/<int:attempt_id>/complete', methods=['POST'])
@jwt_required()
@tenant_required
def complete_simulation(simulation_id, attempt_id):
    """Complete a simulation attempt"""
    user_id = get_current_user_id()
    data = request.get_json()
    
    attempt = SimulationAttempt.query.filter_by(
        id=attempt_id,
        simulation_id=simulation_id,
        user_id=user_id
    ).first_or_404()
    
    if attempt.end_time:
        return jsonify({'error': 'Simulation already completed'}), 400
    
    attempt.end_time = datetime.utcnow()
    attempt.time_spent = int((attempt.end_time - attempt.start_time).total_seconds() / 60)
    attempt.responses = data.get('responses', {})
    attempt.decisions_made = data.get('decisions_made', [])
    
    # Calculate scores
    # TODO: Implement proper scoring based on simulation rubric
    attempt.total_score = random.uniform(60, 95)
    attempt.skill_scores = {
        'communication': random.uniform(70, 90),
        'problem_solving': random.uniform(65, 85),
        'leadership': random.uniform(60, 90)
    }
    
    # Generate AI feedback
    if attempt.simulation.ai_feedback_enabled:
        attempt.ai_feedback = generate_simulation_feedback(attempt)
        attempt.strengths_identified = ['Clear communication', 'Good time management']
        attempt.areas_for_improvement = ['Decision making under pressure']
    
    # Determine pass/fail
    attempt.passed = attempt.total_score >= (attempt.simulation.passing_score or 70)
    
    db.session.commit()
    
    return jsonify({
        'total_score': attempt.total_score,
        'passed': attempt.passed,
        'skill_scores': attempt.skill_scores,
        'ai_feedback': attempt.ai_feedback,
        'strengths': attempt.strengths_identified,
        'improvements': attempt.areas_for_improvement
    })

@bp.route('/recommendations', methods=['GET'])
@jwt_required()
@tenant_required
def get_content_recommendations():
    """Get personalized content recommendations"""
    user_id = get_current_user_id()
    
    # Get active recommendations
    recommendations = ContentRecommendation.query.filter_by(
        user_id=user_id,
        viewed=False
    ).filter(
        or_(
            ContentRecommendation.expires_date.is_(None),
            ContentRecommendation.expires_date >= datetime.utcnow()
        )
    ).order_by(ContentRecommendation.recommendation_score.desc()).limit(10).all()
    
    # If no recommendations, generate some
    if not recommendations:
        generate_content_recommendations(user_id)
        recommendations = ContentRecommendation.query.filter_by(
            user_id=user_id,
            viewed=False
        ).order_by(ContentRecommendation.recommendation_score.desc()).limit(10).all()
    
    return jsonify({
        'recommendations': [{
            'id': rec.id,
            'content': {
                'id': rec.content.id,
                'title': rec.content.title,
                'content_type': rec.content.content_type.value,
                'duration_minutes': rec.content.duration_minutes,
                'difficulty_level': rec.content.difficulty_level
            },
            'score': rec.recommendation_score,
            'reason': rec.recommendation_reason,
            'type': rec.recommendation_type
        } for rec in recommendations]
    })

@bp.route('/recommendations/<int:id>/view', methods=['POST'])
@jwt_required()
@tenant_required
def mark_recommendation_viewed(id):
    """Mark a recommendation as viewed"""
    user_id = get_current_user_id()
    
    recommendation = ContentRecommendation.query.filter_by(
        id=id,
        user_id=user_id
    ).first_or_404()
    
    recommendation.viewed = True
    db.session.commit()
    
    return jsonify({'message': 'Marked as viewed'})

@bp.route('/progress/summary', methods=['GET'])
@jwt_required()
@tenant_required
def get_learning_progress_summary():
    """Get user's overall learning progress summary"""
    user_id = get_current_user_id()
    
    # Get active learning paths
    active_paths = PersonalizedLearningPath.query.filter_by(
        user_id=user_id,
        status=LearningPathStatus.ACTIVE
    ).all()
    
    # Get content progress
    content_progress = ContentProgress.query.filter_by(user_id=user_id).all()
    
    # Get mentorship status
    active_mentorships = MentorshipMatch.query.filter(
        or_(
            MentorshipMatch.mentee_id == user_id,
            MentorshipMatch.mentor_id == user_id
        ),
        MentorshipMatch.status == MentorshipStatus.ACTIVE
    ).all()
    
    # Get simulation attempts
    recent_simulations = SimulationAttempt.query.filter_by(
        user_id=user_id
    ).order_by(SimulationAttempt.start_time.desc()).limit(5).all()
    
    summary = {
        'active_paths': len(active_paths),
        'total_time_spent': sum(path.total_time_spent or 0 for path in active_paths),
        'average_progress': sum(path.overall_progress for path in active_paths) / len(active_paths) if active_paths else 0,
        'content_completed': sum(1 for cp in content_progress if cp.is_completed),
        'skills_in_progress': list(set(
            skill for path in active_paths 
            for skill in (path.target_skills or [])
        )),
        'active_mentorships': len(active_mentorships),
        'recent_simulations': [{
            'title': sim.simulation.title,
            'date': sim.start_time.isoformat(),
            'score': sim.total_score,
            'passed': sim.passed
        } for sim in recent_simulations]
    }
    
    return jsonify(summary)

# Helper functions

def generate_path_content(path):
    """Generate initial content for a learning path"""
    # TODO: Implement AI-based content selection
    # For now, select random content matching skills
    
    contents = AdvancedLearningContent.query.filter(
        AdvancedLearningContent.skill_categories.overlap(path.target_skills)
    ).limit(10).all()
    
    for i, content in enumerate(contents):
        path_content = PathContent(
            path_id=path.id,
            content_id=content.id,
            order_index=i,
            is_mandatory=i < 5  # First 5 are mandatory
        )
        db.session.add(path_content)

def check_milestone_completion(path):
    """Check if any milestones are completed"""
    for milestone in path.milestones:
        if milestone.is_completed:
            continue
            
        # Check if required contents are completed
        if milestone.required_contents:
            completed_ids = [pc.content_id for pc in path.contents if pc.is_completed]
            if all(req_id in completed_ids for req_id in milestone.required_contents):
                milestone.is_completed = True
                milestone.completion_date = datetime.utcnow()
                path.milestones_completed = (path.milestones_completed or 0) + 1

def adapt_learning_path(path, completed_content):
    """Adapt learning path based on performance"""
    if not path.difficulty_adjustment:
        return
    
    # If user scored poorly, add easier content
    if completed_content.score and completed_content.score < 70:
        # TODO: Add remedial content
        pass
    
    # If user scored well, potentially skip similar content
    elif completed_content.score and completed_content.score > 90:
        # TODO: Mark similar content as skippable
        pass

def generate_simulation_feedback(attempt):
    """Generate AI feedback for simulation attempt"""
    # TODO: Implement actual AI feedback generation
    return {
        'overall': 'Good performance with room for improvement in decision-making.',
        'specific_feedback': {
            'communication': 'Clear and concise communication throughout.',
            'problem_solving': 'Showed good analytical skills but could improve on creative solutions.',
            'time_management': 'Completed within the allocated time.'
        },
        'recommendations': [
            'Practice active listening techniques',
            'Work on presenting multiple solution options'
        ]
    }

def generate_content_recommendations(user_id):
    """Generate content recommendations for user"""
    # TODO: Implement AI-based recommendation engine
    # For now, select random high-quality content
    
    contents = AdvancedLearningContent.query.filter(
        AdvancedLearningContent.quality_score >= 80
    ).order_by(func.random()).limit(5).all()
    
    for content in contents:
        recommendation = ContentRecommendation(
            user_id=user_id,
            content_id=content.id,
            recommendation_score=random.uniform(70, 95),
            recommendation_reason=['Based on your learning goals', 'Popular in your field'],
            recommendation_type='skill_gap',
            expires_date=datetime.utcnow() + timedelta(days=30)
        )
        db.session.add(recommendation)
    
    db.session.commit()