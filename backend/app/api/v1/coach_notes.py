from flask import Blueprint, request, jsonify
from flask_jwt_extended import jwt_required, get_jwt_identity
from sqlalchemy import and_, or_, desc
from sqlalchemy.orm import joinedload
from datetime import datetime

from app.models.coach_note import CoachNote
from app.models.user import User
from app.models.tenant import Tenant
from app.extensions import db
from app.core.jwt_utils import get_current_user_id
from app.core.decorators import require_permission, validate_json
from app.utils.response import success_response, error_response, validation_error_response
from app.core.rate_limiting import api_rate_limit
from app.extensions import limiter
from app.core.audit import audit_read, audit_create, audit_update, audit_delete, get_resource_id_from_url, get_resource_id_from_json

coach_notes_bp = Blueprint('coach_notes', __name__, url_prefix='/api/v1/coach-notes')

@coach_notes_bp.route('', methods=['GET'])
@jwt_required()
@require_permission(['admin', 'trainer'])
@limiter.limit(api_rate_limit)
@audit_read('coach_note')
def get_coach_notes():
    """
    Get coach notes with filtering and pagination
    
    Query Parameters:
    - page: Page number (default: 1)
    - per_page: Items per page (default: 20, max: 100)
    - student_id: Filter by student ID
    - coach_id: Filter by coach ID
    - category: Filter by category
    - priority: Filter by priority
    - is_archived: Filter by archived status (true/false)
    - search: Search in title and content
    - sort_by: Sort field (created_at, updated_at, title, priority)
    - sort_order: Sort order (asc, desc)
    """
    try:
        # Get query parameters
        page = request.args.get('page', 1, type=int)
        per_page = min(request.args.get('per_page', 20, type=int), 100)
        student_id = request.args.get('student_id', type=int)
        coach_id = request.args.get('coach_id', type=int)
        category = request.args.get('category')
        priority = request.args.get('priority')
        is_archived = request.args.get('is_archived')
        search = request.args.get('search', '').strip()
        sort_by = request.args.get('sort_by', 'created_at')
        sort_order = request.args.get('sort_order', 'desc')
        
        # Get current user and tenant
        current_user_id = get_current_user_id()
        tenant_id = request.headers.get('X-Tenant-ID')
        
        if not tenant_id:
            return error_response('Tenant ID is required', 400)
        
        # Build query
        query = CoachNote.query.filter(CoachNote.tenant_id == tenant_id)
        
        # Apply filters
        if student_id:
            query = query.filter(CoachNote.student_id == student_id)
        
        if coach_id:
            query = query.filter(CoachNote.coach_id == coach_id)
        
        if category:
            query = query.filter(CoachNote.category == category)
        
        if priority:
            query = query.filter(CoachNote.priority == priority)
        
        if is_archived is not None:
            archived_bool = is_archived.lower() == 'true'
            query = query.filter(CoachNote.is_archived == archived_bool)
        
        # Search in title and content
        if search:
            search_filter = or_(
                CoachNote.title.ilike(f'%{search}%'),
                CoachNote.content.ilike(f'%{search}%')
            )
            query = query.filter(search_filter)
        
        # Apply sorting
        sort_column = getattr(CoachNote, sort_by, CoachNote.created_at)
        if sort_order.lower() == 'desc':
            query = query.order_by(desc(sort_column))
        else:
            query = query.order_by(sort_column)
        
        # Execute paginated query
        paginated_notes = query.options(
            joinedload(CoachNote.student),
            joinedload(CoachNote.coach)
        ).paginate(
            page=page,
            per_page=per_page,
            error_out=False
        )
        
        # Prepare response
        notes_data = []
        for note in paginated_notes.items:
            note_dict = note.to_dict()
            notes_data.append(note_dict)
        
        return success_response({
            'notes': notes_data,
            'pagination': {
                'page': page,
                'per_page': per_page,
                'total': paginated_notes.total,
                'pages': paginated_notes.pages,
                'has_next': paginated_notes.has_next,
                'has_prev': paginated_notes.has_prev
            },
            'filters': {
                'student_id': student_id,
                'coach_id': coach_id,
                'category': category,
                'priority': priority,
                'is_archived': is_archived,
                'search': search
            }
        })
        
    except Exception as e:
        return error_response(f'Failed to fetch coach notes: {str(e)}', 500)

@coach_notes_bp.route('', methods=['POST'])
@jwt_required()
@require_permission(['admin', 'trainer'])
@validate_json(['student_id', 'title', 'content'])
@limiter.limit("10 per hour")  # More restrictive for create operations
@audit_create('coach_note', get_resource_id_from_json('student_id'))
def create_coach_note():
    """
    Create a new coach note
    
    Request Body:
    {
        "student_id": int,
        "title": str,
        "content": str,
        "category": str (optional, default: "general"),
        "priority": str (optional, default: "medium"),
        "is_private": bool (optional, default: false)
    }
    """
    try:
        data = request.get_json()
        current_user_id = get_current_user_id()
        tenant_id = request.headers.get('X-Tenant-ID')
        
        if not tenant_id:
            return error_response('Tenant ID is required', 400)
        
        # Validate student exists and belongs to tenant
        student = User.query.filter(
            and_(
                User.id == data['student_id'],
                User.tenant_id == tenant_id
            )
        ).first()
        
        if not student:
            return error_response('Student not found', 404)
        
        # Validate category and priority
        valid_categories = CoachNote.get_categories()
        category = data.get('category', 'general')
        if category not in valid_categories:
            return validation_error_response(f'Invalid category. Must be one of: {", ".join(valid_categories)}')
        
        valid_priorities = CoachNote.get_priorities()
        priority = data.get('priority', 'medium')
        if priority not in valid_priorities:
            return validation_error_response(f'Invalid priority. Must be one of: {", ".join(valid_priorities)}')
        
        # Create new coach note
        coach_note = CoachNote(
            student_id=data['student_id'],
            coach_id=current_user_id,
            tenant_id=tenant_id,
            title=data['title'].strip(),
            content=data['content'].strip(),
            category=category,
            priority=priority,
            is_private=data.get('is_private', False)
        )
        
        db.session.add(coach_note)
        db.session.commit()
        
        # Load relationships for response
        coach_note = CoachNote.query.options(
            joinedload(CoachNote.student),
            joinedload(CoachNote.coach)
        ).get(coach_note.id)
        
        return success_response({
            'note': coach_note.to_dict(),
            'message': 'Coach note created successfully'
        }, 201)
        
    except Exception as e:
        db.session.rollback()
        return error_response(f'Failed to create coach note: {str(e)}', 500)

@coach_notes_bp.route('/<int:note_id>', methods=['GET'])
@jwt_required()
@require_permission(['admin', 'trainer'])
@limiter.limit(api_rate_limit)
@audit_read('coach_note', get_resource_id_from_url('note_id'))
def get_coach_note(note_id):
    """Get a specific coach note by ID"""
    try:
        tenant_id = request.headers.get('X-Tenant-ID')
        current_user_id = get_current_user_id()
        
        if not tenant_id:
            return error_response('Tenant ID is required', 400)
        
        # Get note with relationships
        note = CoachNote.query.options(
            joinedload(CoachNote.student),
            joinedload(CoachNote.coach)
        ).filter(
            and_(
                CoachNote.id == note_id,
                CoachNote.tenant_id == tenant_id
            )
        ).first()
        
        if not note:
            return error_response('Coach note not found', 404)
        
        return success_response({
            'note': note.to_dict()
        })
        
    except Exception as e:
        return error_response(f'Failed to fetch coach note: {str(e)}', 500)

@coach_notes_bp.route('/<int:note_id>', methods=['PUT'])
@jwt_required()
@require_permission(['admin', 'trainer'])
@validate_json(['title', 'content'])
@limiter.limit("20 per hour")  # Moderate limit for updates
@audit_update('coach_note', get_resource_id_from_url('note_id'))
def update_coach_note(note_id):
    """
    Update a coach note
    
    Request Body:
    {
        "title": str,
        "content": str,
        "category": str (optional),
        "priority": str (optional),
        "is_private": bool (optional),
        "is_archived": bool (optional)
    }
    """
    try:
        data = request.get_json()
        tenant_id = request.headers.get('X-Tenant-ID')
        current_user_id = get_current_user_id()
        
        if not tenant_id:
            return error_response('Tenant ID is required', 400)
        
        # Get note
        note = CoachNote.query.filter(
            and_(
                CoachNote.id == note_id,
                CoachNote.tenant_id == tenant_id
            )
        ).first()
        
        if not note:
            return error_response('Coach note not found', 404)
        
        # Check permissions - only coach who created the note or admin can edit
        current_user = User.query.get(current_user_id)
        if current_user.role.name not in ['admin'] and note.coach_id != current_user_id:
            return error_response('You can only edit your own notes', 403)
        
        # Validate category and priority if provided
        if 'category' in data:
            valid_categories = CoachNote.get_categories()
            if data['category'] not in valid_categories:
                return validation_error_response(f'Invalid category. Must be one of: {", ".join(valid_categories)}')
        
        if 'priority' in data:
            valid_priorities = CoachNote.get_priorities()
            if data['priority'] not in valid_priorities:
                return validation_error_response(f'Invalid priority. Must be one of: {", ".join(valid_priorities)}')
        
        # Update fields
        note.title = data['title'].strip()
        note.content = data['content'].strip()
        note.updated_at = datetime.utcnow()
        
        if 'category' in data:
            note.category = data['category']
        if 'priority' in data:
            note.priority = data['priority']
        if 'is_private' in data:
            note.is_private = data['is_private']
        if 'is_archived' in data:
            note.is_archived = data['is_archived']
        
        db.session.commit()
        
        # Load relationships for response
        note = CoachNote.query.options(
            joinedload(CoachNote.student),
            joinedload(CoachNote.coach)
        ).get(note.id)
        
        return success_response({
            'note': note.to_dict(),
            'message': 'Coach note updated successfully'
        })
        
    except Exception as e:
        db.session.rollback()
        return error_response(f'Failed to update coach note: {str(e)}', 500)

@coach_notes_bp.route('/<int:note_id>', methods=['DELETE'])
@jwt_required()
@require_permission(['admin', 'trainer'])
@limiter.limit("5 per hour")  # Restrictive for delete operations
@audit_delete('coach_note', get_resource_id_from_url('note_id'))
def delete_coach_note(note_id):
    """Delete a coach note"""
    try:
        tenant_id = request.headers.get('X-Tenant-ID')
        current_user_id = get_current_user_id()
        
        if not tenant_id:
            return error_response('Tenant ID is required', 400)
        
        # Get note
        note = CoachNote.query.filter(
            and_(
                CoachNote.id == note_id,
                CoachNote.tenant_id == tenant_id
            )
        ).first()
        
        if not note:
            return error_response('Coach note not found', 404)
        
        # Check permissions - only coach who created the note or admin can delete
        current_user = User.query.get(current_user_id)
        if current_user.role.name not in ['admin'] and note.coach_id != current_user_id:
            return error_response('You can only delete your own notes', 403)
        
        db.session.delete(note)
        db.session.commit()
        
        return success_response({
            'message': 'Coach note deleted successfully'
        })
        
    except Exception as e:
        db.session.rollback()
        return error_response(f'Failed to delete coach note: {str(e)}', 500)

@coach_notes_bp.route('/categories', methods=['GET'])
@jwt_required()
def get_categories():
    """Get available coach note categories"""
    return success_response({
        'categories': CoachNote.get_categories()
    })

@coach_notes_bp.route('/priorities', methods=['GET'])
@jwt_required()
def get_priorities():
    """Get available coach note priorities"""
    return success_response({
        'priorities': CoachNote.get_priorities()
    })

@coach_notes_bp.route('/student/<int:student_id>', methods=['GET'])
@jwt_required()
@require_permission(['admin', 'trainer'])
def get_student_notes(student_id):
    """Get all notes for a specific student"""
    try:
        tenant_id = request.headers.get('X-Tenant-ID')
        
        if not tenant_id:
            return error_response('Tenant ID is required', 400)
        
        # Validate student exists
        student = User.query.filter(
            and_(
                User.id == student_id,
                User.tenant_id == tenant_id
            )
        ).first()
        
        if not student:
            return error_response('Student not found', 404)
        
        # Get notes for student
        notes = CoachNote.query.options(
            joinedload(CoachNote.coach)
        ).filter(
            and_(
                CoachNote.student_id == student_id,
                CoachNote.tenant_id == tenant_id,
                CoachNote.is_archived == False
            )
        ).order_by(desc(CoachNote.created_at)).all()
        
        notes_data = [note.to_dict() for note in notes]
        
        return success_response({
            'student': {
                'id': student.id,
                'name': f"{student.first_name} {student.last_name}",
                'email': student.email
            },
            'notes': notes_data,
            'total_notes': len(notes_data)
        })
        
    except Exception as e:
        return error_response(f'Failed to fetch student notes: {str(e)}', 500)

@coach_notes_bp.route('/coach/<int:coach_id>', methods=['GET'])
@jwt_required()
@require_permission(['admin'])
def get_coach_notes_by_coach(coach_id):
    """Get all notes created by a specific coach (admin only)"""
    try:
        tenant_id = request.headers.get('X-Tenant-ID')
        
        if not tenant_id:
            return error_response('Tenant ID is required', 400)
        
        # Validate coach exists
        coach = User.query.filter(
            and_(
                User.id == coach_id,
                User.tenant_id == tenant_id
            )
        ).first()
        
        if not coach:
            return error_response('Coach not found', 404)
        
        # Get notes by coach
        notes = CoachNote.query.options(
            joinedload(CoachNote.student)
        ).filter(
            and_(
                CoachNote.coach_id == coach_id,
                CoachNote.tenant_id == tenant_id
            )
        ).order_by(desc(CoachNote.created_at)).all()
        
        notes_data = [note.to_dict() for note in notes]
        
        return success_response({
            'coach': {
                'id': coach.id,
                'name': f"{coach.first_name} {coach.last_name}",
                'email': coach.email
            },
            'notes': notes_data,
            'total_notes': len(notes_data)
        })
        
    except Exception as e:
        return error_response(f'Failed to fetch coach notes: {str(e)}', 500)