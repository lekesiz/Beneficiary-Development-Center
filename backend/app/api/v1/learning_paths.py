"""
Learning Paths API endpoints
"""
from flask import Blueprint, request, jsonify
from datetime import datetime
from app.models.learning_path import LearningPath, LearningMilestone, LearningPathUpdate, MilestoneProgress
from app.models.user import User
from app.services.learning_path_service import learning_path_service
from app.services.student_profile_service import student_profile_service
from app.core.socketio import emit_coach_notification
from app.core.auth import require_auth, get_current_user
from app.core.database import get_db
from app.core.exceptions import ValidationError, NotFoundError, ForbiddenError

learning_paths_bp = Blueprint('learning_paths', __name__, url_prefix='/api/learning-paths')


@learning_paths_bp.route('/<int:path_id>', methods=['GET'])
@require_auth
def get_learning_path(path_id: int):
    """Get a learning path by ID"""
    user = get_current_user()
    
    learning_path = learning_path_service.get_learning_path(
        path_id=path_id,
        tenant_id=user.tenant_id,
        user=user
    )
    
    return jsonify(learning_path.to_dict())


@learning_paths_bp.route('/my-paths', methods=['GET'])
@require_auth
def get_my_learning_paths():
    """Get learning paths for a specific user (used by coach panel)."""
    user = get_current_user()
    db = get_db()
    
    user_id = request.args.get('user_id', type=int)
    status = request.args.get('status', '')
    
    # If user_id provided and requester is coach/admin, get that user's paths
    if user_id and user.role in ['admin', 'manager', 'instructor', 'trainer']:
        target_user_id = user_id
    else:
        target_user_id = user.id
    
    query = db.query(LearningPath).filter(
        LearningPath.user_id == target_user_id,
        LearningPath.tenant_id == user.tenant_id,
        LearningPath.is_deleted == False
    )
    
    if status:
        statuses = status.split(',')
        query = query.filter(LearningPath.status.in_(statuses))
    
    paths = query.all()
    
    result = []
    for path in paths:
        # Calculate progress
        total_milestones = len([m for m in path.milestones if not m.is_deleted])
        completed_milestones = 0
        
        for milestone in path.milestones:
            if milestone.is_deleted:
                continue
            progress = db.query(MilestoneProgress).filter(
                MilestoneProgress.milestone_id == milestone.id,
                MilestoneProgress.user_id == target_user_id,
                MilestoneProgress.status == 'completed'
            ).first()
            if progress:
                completed_milestones += 1
        
        overall_progress = (completed_milestones / total_milestones * 100) if total_milestones > 0 else 0
        
        result.append({
            'id': path.id,
            'title': path.title,
            'description': path.description,
            'status': path.status,
            'overall_progress': round(overall_progress),
            'total_milestones': total_milestones,
            'completed_milestones': completed_milestones,
            'created_at': path.created_at.isoformat()
        })
    
    return jsonify(result)


@learning_paths_bp.route('/students/<int:student_id>/suggest-updates', methods=['POST'])
@require_auth
def suggest_learning_path_updates(student_id: int):
    """
    Generate learning path update suggestions for a student.
    
    Returns list of suggested updates based on AI analysis.
    """
    user = get_current_user()
    db = get_db()
    
    suggestions = learning_path_service.suggest_learning_path_updates(
        student_id=student_id,
        tenant_id=user.tenant_id,
        requesting_user=user
    )
    
    return jsonify({
        'suggestions': [s.to_dict() for s in suggestions],
        'total': len(suggestions)
    })


@learning_paths_bp.route('/<int:path_id>/pending-updates', methods=['GET'])
@require_auth
def get_pending_updates(path_id: int):
    """Get pending update suggestions for a learning path."""
    user = get_current_user()
    db = get_db()
    
    updates = learning_path_service.get_pending_updates(
        learning_path_id=path_id,
        tenant_id=user.tenant_id,
        user=user
    )
    
    return jsonify({
        'updates': [u.to_dict() for u in updates],
        'total': len(updates)
    })


@learning_paths_bp.route('/updates/<int:update_id>/approve', methods=['POST'])
@require_auth
def approve_update(update_id: int):
    """Approve a learning path update suggestion."""
    user = get_current_user()
    db = get_db()
    
    # Get update
    update = db.query(LearningPathUpdate).filter(
        LearningPathUpdate.id == update_id,
        LearningPathUpdate.tenant_id == user.tenant_id
    ).first()
    
    if not update:
        raise NotFoundError("Update not found")
    
    # Check permissions
    if user.role not in ['admin', 'manager', 'instructor', 'trainer']:
        raise ForbiddenError("You don't have permission to approve updates")
    
    # Approve update
    update.status = 'approved'
    update.approved_by_user_id = user.id
    update.approved_at = datetime.utcnow()
    
    db.commit()
    
    return jsonify({
        'message': 'Update approved successfully',
        'update': update.to_dict()
    })


@learning_paths_bp.route('/updates/<int:update_id>/reject', methods=['POST'])
@require_auth
def reject_update(update_id: int):
    """Reject a learning path update suggestion."""
    user = get_current_user()
    db = get_db()
    data = request.get_json()
    
    # Get update
    update = db.query(LearningPathUpdate).filter(
        LearningPathUpdate.id == update_id,
        LearningPathUpdate.tenant_id == user.tenant_id
    ).first()
    
    if not update:
        raise NotFoundError("Update not found")
    
    # Check permissions
    if user.role not in ['admin', 'manager', 'instructor', 'trainer']:
        raise ForbiddenError("You don't have permission to reject updates")
    
    # Reject update
    update.status = 'rejected'
    update.rejection_reason = data.get('reason', 'No reason provided')
    
    db.commit()
    
    return jsonify({
        'message': 'Update rejected successfully',
        'update': update.to_dict()
    })


@learning_paths_bp.route('/updates/<int:update_id>/apply', methods=['POST'])
@require_auth
def apply_update(update_id: int):
    """Apply an approved learning path update."""
    user = get_current_user()
    db = get_db()
    
    learning_path = learning_path_service.apply_learning_path_update(
        update_id=update_id,
        tenant_id=user.tenant_id,
        user=user
    )
    
    return jsonify({
        'message': 'Update applied successfully',
        'learning_path': learning_path.to_dict()
    })


@learning_paths_bp.route('/<int:path_id>/accept', methods=['POST'])
@require_auth
def accept_learning_path(path_id: int):
    """Accept a proposed learning path"""
    user = get_current_user()
    data = request.get_json() or {}
    
    learning_path = learning_path_service.accept_learning_path(
        path_id=path_id,
        tenant_id=user.tenant_id,
        user=user,
        customization_notes=data.get('customization_notes')
    )
    
    return jsonify(learning_path.to_dict())


@learning_paths_bp.route('/<int:path_id>', methods=['PUT'])
@require_auth
def update_learning_path(path_id: int):
    """Update learning path details"""
    user = get_current_user()
    data = request.get_json()
    
    if not data:
        raise ValidationError("Request body is required")
    
    learning_path = learning_path_service.update_learning_path(
        path_id=path_id,
        tenant_id=user.tenant_id,
        user=user,
        updates=data
    )
    
    return jsonify(learning_path.to_dict())


@learning_paths_bp.route('/<int:path_id>/milestones/<int:milestone_id>/progress', methods=['PUT'])
@require_auth
def update_milestone_progress(path_id: int, milestone_id: int):
    """Update milestone progress"""
    user = get_current_user()
    data = request.get_json()
    
    if not data or 'progress' not in data:
        raise ValidationError("progress is required")
    
    milestone = learning_path_service.update_milestone_progress(
        path_id=path_id,
        milestone_id=milestone_id,
        tenant_id=user.tenant_id,
        user=user,
        progress=data['progress'],
        notes=data.get('notes')
    )
    
    return jsonify(milestone.to_dict())


@learning_paths_bp.route('/<int:path_id>/feedback', methods=['POST'])
@require_auth
def provide_feedback(path_id: int):
    """Provide feedback on a learning path"""
    user = get_current_user()
    data = request.get_json()
    
    if not data or 'feedback' not in data:
        raise ValidationError("feedback is required")
    
    learning_path = learning_path_service.provide_feedback(
        path_id=path_id,
        tenant_id=user.tenant_id,
        user=user,
        feedback=data['feedback'],
        rating=data.get('rating')
    )
    
    return jsonify(learning_path.to_dict())


# ==================== Student Endpoints ====================

@learning_paths_bp.route('/student/milestones', methods=['GET'])
@require_auth
def get_student_milestones():
    """Get current student's milestones with progress."""
    user = get_current_user()
    db = get_db()
    
    try:
        # Get all active learning paths for the student
        learning_paths = db.query(LearningPath).filter(
            LearningPath.user_id == user.id,
            LearningPath.tenant_id == user.tenant_id,
            LearningPath.is_deleted == False,
            LearningPath.status.in_(['accepted', 'in_progress'])
        ).all()
        
        milestones = []
        for path in learning_paths:
            for milestone in path.milestones:
                if milestone.is_deleted:
                    continue
                    
                # Get progress for this milestone
                progress = db.query(MilestoneProgress).filter(
                    MilestoneProgress.milestone_id == milestone.id,
                    MilestoneProgress.user_id == user.id
                ).first()
                
                milestone_data = {
                    'id': milestone.id,
                    'title': milestone.title,
                    'description': milestone.description,
                    'objective': milestone.objective,
                    'week_number': milestone.week_number,
                    'estimated_hours': milestone.estimated_hours,
                    'skill_focus': milestone.skill_focus,
                    'status': progress.status if progress else 'pending',
                    'progress': progress.progress_percentage if progress else 0,
                    'activities': milestone.activities or [],
                    'resources': milestone.resources or [],
                    'completed_activities': progress.completed_activities if progress else [],
                    'started_at': progress.started_at.isoformat() if progress and progress.started_at else None,
                    'completed_at': progress.completed_at.isoformat() if progress and progress.completed_at else None,
                    'help_requested': progress.help_requested if progress else False,
                    'learning_path_id': path.id,
                    'learning_path_title': path.title
                }
                milestones.append(milestone_data)
        
        # Sort milestones by week number and status
        milestones.sort(key=lambda x: (
            0 if x['status'] == 'in_progress' else 1 if x['status'] == 'pending' else 2,
            x['week_number']
        ))
        
        return jsonify({
            'success': True,
            'milestones': milestones
        })
        
    except Exception as e:
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500


@learning_paths_bp.route('/milestones/<int:milestone_id>/start', methods=['POST'])
@require_auth
def start_milestone(milestone_id: int):
    """Start working on a milestone."""
    user = get_current_user()
    db = get_db()
    
    try:
        milestone = db.query(LearningMilestone).get(milestone_id)
        if not milestone:
            raise NotFoundError("Milestone not found")
        
        # Check if user has access to this milestone
        if milestone.learning_path.user_id != user.id:
            raise NotFoundError("Milestone not found")
        
        # Get or create progress record
        progress = db.query(MilestoneProgress).filter(
            MilestoneProgress.milestone_id == milestone_id,
            MilestoneProgress.user_id == user.id
        ).first()
        
        if not progress:
            progress = MilestoneProgress(
                milestone_id=milestone_id,
                user_id=user.id,
                tenant_id=user.tenant_id,
                status='in_progress',
                progress_percentage=0,
                started_at=datetime.utcnow()
            )
            db.add(progress)
        else:
            progress.status = 'in_progress'
            progress.started_at = datetime.utcnow()
        
        # Update learning path status if needed
        if milestone.learning_path.status == 'accepted':
            milestone.learning_path.status = 'in_progress'
        
        db.commit()
        
        return jsonify({
            'success': True,
            'message': 'Milestone started successfully',
            'milestone_id': milestone_id
        })
        
    except Exception as e:
        db.rollback()
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500


@learning_paths_bp.route('/milestones/<int:milestone_id>/complete', methods=['POST'])
@require_auth
def complete_milestone(milestone_id: int):
    """Mark a milestone as completed."""
    user = get_current_user()
    db = get_db()
    
    try:
        milestone = db.query(LearningMilestone).get(milestone_id)
        if not milestone:
            raise NotFoundError("Milestone not found")
        
        # Check if user has access to this milestone
        if milestone.learning_path.user_id != user.id:
            raise NotFoundError("Milestone not found")
        
        # Get progress record
        progress = db.query(MilestoneProgress).filter(
            MilestoneProgress.milestone_id == milestone_id,
            MilestoneProgress.user_id == user.id
        ).first()
        
        if not progress:
            raise ValidationError("Milestone not started")
        
        progress.status = 'completed'
        progress.progress_percentage = 100
        progress.completed_at = datetime.utcnow()
        
        # Check if all milestones in the path are completed
        path = milestone.learning_path
        all_completed = all(
            db.query(MilestoneProgress).filter(
                MilestoneProgress.milestone_id == m.id,
                MilestoneProgress.user_id == user.id,
                MilestoneProgress.status == 'completed'
            ).first() is not None
            for m in path.milestones if not m.is_deleted
        )
        
        if all_completed:
            path.status = 'completed'
        
        db.commit()
        
        # Send completion notification to coaches
        notification_data = {
            'type': 'milestone_completed',
            'student_id': user.id,
            'student_name': user.name,
            'milestone_id': milestone_id,
            'milestone_title': milestone.title,
            'learning_path_title': milestone.learning_path.title,
            'timestamp': datetime.utcnow().isoformat(),
            'path_completed': all_completed
        }
        emit_coach_notification(user.tenant_id, notification_data)
        
        return jsonify({
            'success': True,
            'message': 'Milestone completed successfully',
            'milestone_id': milestone_id,
            'path_completed': all_completed
        })
        
    except ValidationError as e:
        return jsonify({
            'success': False,
            'error': str(e)
        }), 400
    except Exception as e:
        db.rollback()
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500


@learning_paths_bp.route('/milestones/<int:milestone_id>/progress', methods=['PATCH'])
@require_auth
def update_milestone_progress(milestone_id: int):
    """Update milestone progress."""
    user = get_current_user()
    db = get_db()
    data = request.get_json()
    
    try:
        milestone = db.query(LearningMilestone).get(milestone_id)
        if not milestone:
            raise NotFoundError("Milestone not found")
        
        # Check if user has access to this milestone
        if milestone.learning_path.user_id != user.id:
            raise NotFoundError("Milestone not found")
        
        # Get or create progress record
        progress = db.query(MilestoneProgress).filter(
            MilestoneProgress.milestone_id == milestone_id,
            MilestoneProgress.user_id == user.id
        ).first()
        
        if not progress:
            progress = MilestoneProgress(
                milestone_id=milestone_id,
                user_id=user.id,
                tenant_id=user.tenant_id,
                status='in_progress',
                started_at=datetime.utcnow()
            )
            db.add(progress)
        
        # Update progress
        if 'progress' in data:
            progress.progress_percentage = min(100, max(0, data['progress']))
        
        if 'completed_activities' in data:
            progress.completed_activities = data['completed_activities']
        
        db.commit()
        
        return jsonify({
            'success': True,
            'message': 'Progress updated successfully',
            'progress': progress.progress_percentage
        })
        
    except Exception as e:
        db.rollback()
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500


@learning_paths_bp.route('/milestones/<int:milestone_id>/help', methods=['POST'])
@require_auth
def request_milestone_help(milestone_id: int):
    """Request help for a milestone."""
    user = get_current_user()
    db = get_db()
    data = request.get_json()
    
    try:
        milestone = db.query(LearningMilestone).get(milestone_id)
        if not milestone:
            raise NotFoundError("Milestone not found")
        
        # Check if user has access to this milestone
        if milestone.learning_path.user_id != user.id:
            raise NotFoundError("Milestone not found")
        
        # Get progress record
        progress = db.query(MilestoneProgress).filter(
            MilestoneProgress.milestone_id == milestone_id,
            MilestoneProgress.user_id == user.id
        ).first()
        
        if not progress:
            raise ValidationError("Milestone not started")
        
        # Update help request
        progress.help_requested = True
        progress.help_message = data.get('message', '')
        progress.help_requested_at = datetime.utcnow()
        
        db.commit()
        
        # Send real-time notification to coaches
        notification_data = {
            'type': 'help_request',
            'student_id': user.id,
            'student_name': user.name,
            'milestone_id': milestone_id,
            'milestone_title': milestone.title,
            'learning_path_title': milestone.learning_path.title,
            'message': data.get('message', ''),
            'timestamp': datetime.utcnow().isoformat(),
            'priority': 'high'
        }
        emit_coach_notification(user.tenant_id, notification_data)
        
        return jsonify({
            'success': True,
            'message': 'Help request sent successfully'
        })
        
    except ValidationError as e:
        return jsonify({
            'success': False,
            'error': str(e)
        }), 400
    except Exception as e:
        db.rollback()
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500


@learning_paths_bp.route('/statistics', methods=['GET'])
@require_auth
def get_learning_path_statistics():
    """Get learning path statistics for the current user"""
    user = get_current_user()
    
    # Get all user's paths
    paths = learning_path_service.get_user_learning_paths(
        user_id=user.id,
        tenant_id=user.tenant_id
    )
    
    # Calculate statistics
    stats = {
        'total_paths': len(paths),
        'active_paths': len([p for p in paths if p.status == 'accepted']),
        'completed_paths': len([p for p in paths if p.status == 'completed']),
        'total_milestones': sum(p.total_milestones for p in paths),
        'completed_milestones': sum(p.completed_milestones for p in paths),
        'average_progress': sum(p.overall_progress for p in paths) / len(paths) if paths else 0,
        'by_status': {}
    }
    
    # Count by status
    for path in paths:
        if path.status not in stats['by_status']:
            stats['by_status'][path.status] = 0
        stats['by_status'][path.status] += 1
    
    return jsonify(stats)