"""API endpoints for Course management."""
from flask import Blueprint, request, jsonify
from flask_jwt_extended import jwt_required, get_jwt_identity, get_jwt
from marshmallow import Schema, fields, validate, ValidationError
from datetime import datetime
from app.services.course_service import CourseService
from app.models.course import CourseStatus, CourseFormat, DifficultyLevel
from app.models.user import User
from app.core.decorators import require_tenant, check_role
from app.extensions import db
from app.core.logging import logger
from app.core.exceptions import NotFoundError, BadRequestError, ForbiddenError

bp = Blueprint('courses', __name__, url_prefix='/api/v1/courses')


class CourseSchema(Schema):
    """Schema for course validation."""
    code = fields.String(required=False, validate=validate.Length(max=50))
    title = fields.String(required=True, validate=validate.Length(min=1, max=200))
    subtitle = fields.String(required=False, validate=validate.Length(max=300))
    description = fields.String(required=False)
    program_id = fields.Integer(required=True)
    status = fields.String(
        required=False,
        validate=validate.OneOf([s.value for s in CourseStatus])
    )
    format = fields.String(
        required=False,
        validate=validate.OneOf([f.value for f in CourseFormat])
    )
    difficulty_level = fields.String(
        required=False,
        validate=validate.OneOf([d.value for d in DifficultyLevel])
    )
    duration_hours = fields.Float(required=False, validate=validate.Range(min=0))
    duration_weeks = fields.Integer(required=False, validate=validate.Range(min=1))
    order_index = fields.Integer(required=False, validate=validate.Range(min=0))
    objectives = fields.List(fields.String(), required=False)
    outline = fields.List(fields.Dict(), required=False)
    prerequisites = fields.List(fields.String(), required=False)
    materials = fields.List(fields.String(), required=False)
    content_url = fields.String(required=False, validate=validate.Length(max=500))
    video_url = fields.String(required=False, validate=validate.Length(max=500))
    resources = fields.List(fields.Dict(), required=False)
    assignments = fields.List(fields.Dict(), required=False)
    has_assessment = fields.Boolean(required=False)
    assessment_type = fields.String(required=False, validate=validate.Length(max=50))
    passing_score = fields.Float(required=False, validate=validate.Range(min=0, max=100))
    max_attempts = fields.Integer(required=False, validate=validate.Range(min=1))
    min_participants = fields.Integer(required=False, validate=validate.Range(min=1))
    max_participants = fields.Integer(required=False, validate=validate.Range(min=1))
    tags = fields.List(fields.String(), required=False)
    metadata = fields.Dict(required=False)
    thumbnail_url = fields.String(required=False, validate=validate.Length(max=500))
    instructor_id = fields.Integer(required=False)


class SessionSchema(Schema):
    """Schema for course session validation."""
    title = fields.String(required=True, validate=validate.Length(min=1, max=200))
    description = fields.String(required=False)
    session_date = fields.DateTime(required=True)
    duration_hours = fields.Float(required=False, validate=validate.Range(min=0))
    location = fields.String(required=False, validate=validate.Length(max=200))
    room_number = fields.String(required=False, validate=validate.Length(max=50))
    is_online = fields.Boolean(required=False)
    online_link = fields.String(required=False, validate=validate.Length(max=500))
    instructor_id = fields.Integer(required=False)
    is_mandatory = fields.Boolean(required=False)
    materials_url = fields.String(required=False, validate=validate.Length(max=500))


course_schema = CourseSchema()
session_schema = SessionSchema()


@bp.route('', methods=['GET'])
@jwt_required()
@require_tenant()
def get_courses():
    """Get all courses for the tenant."""
    try:
        jwt_payload = get_jwt()
        tenant_id = jwt_payload.get('tenant_id')
        user_id = get_jwt_identity()
        
        # Get current user
        user = db.session.query(User).filter_by(id=user_id).first()
        if not user:
            return jsonify({'error': 'User not found'}), 404
        
        # Get query parameters
        page = int(request.args.get('page', 1))
        per_page = int(request.args.get('per_page', 20))
        program_id = request.args.get('program_id', type=int)
        status = request.args.get('status')
        format = request.args.get('format')
        difficulty = request.args.get('difficulty')
        search = request.args.get('search')
        instructor_id = request.args.get('instructor_id', type=int)
        
        # Convert string parameters to enums
        if status:
            try:
                status = CourseStatus(status)
            except ValueError:
                return jsonify({'error': f'Invalid status: {status}'}), 400
        
        if format:
            try:
                format = CourseFormat(format)
            except ValueError:
                return jsonify({'error': f'Invalid format: {format}'}), 400
        
        if difficulty:
            try:
                difficulty = DifficultyLevel(difficulty)
            except ValueError:
                return jsonify({'error': f'Invalid difficulty: {difficulty}'}), 400
        
        # Get courses
        service = CourseService(db.session)
        courses = service.get_all(
            tenant_id=tenant_id,
            user=user,
            program_id=program_id,
            skip=(page - 1) * per_page,
            limit=per_page,
            status=status,
            format=format,
            difficulty=difficulty,
            search=search,
            instructor_id=instructor_id
        )
        
        # Get total count for pagination
        from app.models.course import Course
        total_query = db.session.query(Course).filter(
            Course.tenant_id == tenant_id,
            Course.deleted_at.is_(None)
        )
        
        if program_id:
            total_query = total_query.filter(Course.program_id == program_id)
        if status:
            total_query = total_query.filter(Course.status == status)
        if format:
            total_query = total_query.filter(Course.format == format)
        if difficulty:
            total_query = total_query.filter(Course.difficulty_level == difficulty)
        
        total = total_query.count()
        
        return jsonify({
            'courses': [c.to_dict(include_related=True) for c in courses],
            'pagination': {
                'page': page,
                'per_page': per_page,
                'total': total,
                'pages': (total + per_page - 1) // per_page
            }
        }), 200
        
    except Exception as e:
        logger.error(f"Error fetching courses: {str(e)}")
        return jsonify({'error': 'Failed to fetch courses'}), 500


@bp.route('/<int:course_id>', methods=['GET'])
@jwt_required()
@require_tenant()
def get_course(course_id):
    """Get a specific course."""
    try:
        jwt_payload = get_jwt()
        tenant_id = jwt_payload.get('tenant_id')
        user_id = get_jwt_identity()
        
        # Get current user
        user = db.session.query(User).filter_by(id=user_id).first()
        if not user:
            return jsonify({'error': 'User not found'}), 404
        
        # Get course
        service = CourseService(db.session)
        course = service.get_by_id(tenant_id, course_id, user)
        
        # Include sessions if requested
        include_sessions = request.args.get('include_sessions', 'false').lower() == 'true'
        data = course.to_dict(include_related=True)
        
        if include_sessions:
            data['sessions'] = [s.to_dict() for s in course.sessions if not s.is_cancelled]
        
        return jsonify(data), 200
        
    except NotFoundError as e:
        return jsonify({'error': str(e)}), 404
    except Exception as e:
        logger.error(f"Error fetching course: {str(e)}")
        return jsonify({'error': 'Failed to fetch course'}), 500


@bp.route('', methods=['POST'])
@jwt_required()
@require_tenant()
@check_role(['admin', 'manager', 'instructor'])
def create_course():
    """Create a new course."""
    try:
        jwt_payload = get_jwt()
        tenant_id = jwt_payload.get('tenant_id')
        user_id = get_jwt_identity()
        
        # Get current user
        user = db.session.query(User).filter_by(id=user_id).first()
        if not user:
            return jsonify({'error': 'User not found'}), 404
        
        # Validate request data
        data = course_schema.load(request.json)
        
        # Create course
        service = CourseService(db.session)
        course = service.create(tenant_id, data, user)
        
        return jsonify(course.to_dict(include_related=True)), 201
        
    except ValidationError as e:
        return jsonify({'error': 'Validation error', 'details': e.messages}), 400
    except NotFoundError as e:
        return jsonify({'error': str(e)}), 404
    except BadRequestError as e:
        return jsonify({'error': str(e)}), 400
    except ForbiddenError as e:
        return jsonify({'error': str(e)}), 403
    except Exception as e:
        logger.error(f"Error creating course: {str(e)}")
        return jsonify({'error': 'Failed to create course'}), 500


@bp.route('/<int:course_id>', methods=['PUT'])
@jwt_required()
@require_tenant()
def update_course(course_id):
    """Update a course."""
    try:
        jwt_payload = get_jwt()
        tenant_id = jwt_payload.get('tenant_id')
        user_id = get_jwt_identity()
        
        # Get current user
        user = db.session.query(User).filter_by(id=user_id).first()
        if not user:
            return jsonify({'error': 'User not found'}), 404
        
        # Validate request data
        data = course_schema.load(request.json, partial=True)
        
        # Update course
        service = CourseService(db.session)
        course = service.update(tenant_id, course_id, data, user)
        
        return jsonify(course.to_dict(include_related=True)), 200
        
    except ValidationError as e:
        return jsonify({'error': 'Validation error', 'details': e.messages}), 400
    except NotFoundError as e:
        return jsonify({'error': str(e)}), 404
    except BadRequestError as e:
        return jsonify({'error': str(e)}), 400
    except ForbiddenError as e:
        return jsonify({'error': str(e)}), 403
    except Exception as e:
        logger.error(f"Error updating course: {str(e)}")
        return jsonify({'error': 'Failed to update course'}), 500


@bp.route('/<int:course_id>', methods=['DELETE'])
@jwt_required()
@require_tenant()
@check_role(['admin'])
def delete_course(course_id):
    """Delete a course."""
    try:
        jwt_payload = get_jwt()
        tenant_id = jwt_payload.get('tenant_id')
        user_id = get_jwt_identity()
        
        # Get current user
        user = db.session.query(User).filter_by(id=user_id).first()
        if not user:
            return jsonify({'error': 'User not found'}), 404
        
        # Delete course
        service = CourseService(db.session)
        service.delete(tenant_id, course_id, user)
        
        return '', 204
        
    except NotFoundError as e:
        return jsonify({'error': str(e)}), 404
    except BadRequestError as e:
        return jsonify({'error': str(e)}), 400
    except ForbiddenError as e:
        return jsonify({'error': str(e)}), 403
    except Exception as e:
        logger.error(f"Error deleting course: {str(e)}")
        return jsonify({'error': 'Failed to delete course'}), 500


@bp.route('/<int:course_id>/sessions', methods=['POST'])
@jwt_required()
@require_tenant()
def add_session(course_id):
    """Add a session to a course."""
    try:
        jwt_payload = get_jwt()
        tenant_id = jwt_payload.get('tenant_id')
        user_id = get_jwt_identity()
        
        # Get current user
        user = db.session.query(User).filter_by(id=user_id).first()
        if not user:
            return jsonify({'error': 'User not found'}), 404
        
        # Validate request data
        data = session_schema.load(request.json)
        
        # Add session
        service = CourseService(db.session)
        course = service.add_session(tenant_id, course_id, data, user)
        
        # Return the newly added session
        new_session = course.sessions[-1]
        return jsonify(new_session.to_dict(include_related=True)), 201
        
    except ValidationError as e:
        return jsonify({'error': 'Validation error', 'details': e.messages}), 400
    except NotFoundError as e:
        return jsonify({'error': str(e)}), 404
    except ForbiddenError as e:
        return jsonify({'error': str(e)}), 403
    except Exception as e:
        logger.error(f"Error adding session: {str(e)}")
        return jsonify({'error': 'Failed to add session'}), 500


@bp.route('/<int:course_id>/duplicate', methods=['POST'])
@jwt_required()
@require_tenant()
@check_role(['admin', 'manager'])
def duplicate_course(course_id):
    """Duplicate a course."""
    try:
        jwt_payload = get_jwt()
        tenant_id = jwt_payload.get('tenant_id')
        user_id = get_jwt_identity()
        
        # Get current user
        user = db.session.query(User).filter_by(id=user_id).first()
        if not user:
            return jsonify({'error': 'User not found'}), 404
        
        # Get target program ID if provided
        data = request.json or {}
        target_program_id = data.get('target_program_id')
        
        # Duplicate course
        service = CourseService(db.session)
        new_course = service.duplicate(tenant_id, course_id, target_program_id, user)
        
        return jsonify(new_course.to_dict(include_related=True)), 201
        
    except NotFoundError as e:
        return jsonify({'error': str(e)}), 404
    except ForbiddenError as e:
        return jsonify({'error': str(e)}), 403
    except Exception as e:
        logger.error(f"Error duplicating course: {str(e)}")
        return jsonify({'error': 'Failed to duplicate course'}), 500


@bp.route('/<int:course_id>/reorder', methods=['PUT'])
@jwt_required()
@require_tenant()
@check_role(['admin', 'manager'])
def reorder_course(course_id):
    """Reorder a course within its program."""
    try:
        jwt_payload = get_jwt()
        tenant_id = jwt_payload.get('tenant_id')
        user_id = get_jwt_identity()
        
        # Get current user
        user = db.session.query(User).filter_by(id=user_id).first()
        if not user:
            return jsonify({'error': 'User not found'}), 404
        
        # Get new order
        data = request.json
        if not data or 'order_index' not in data:
            return jsonify({'error': 'order_index is required'}), 400
        
        new_order = data['order_index']
        if not isinstance(new_order, int) or new_order < 0:
            return jsonify({'error': 'order_index must be a non-negative integer'}), 400
        
        # Reorder course
        service = CourseService(db.session)
        course = service.reorder(tenant_id, course_id, new_order, user)
        
        return jsonify(course.to_dict(include_related=True)), 200
        
    except NotFoundError as e:
        return jsonify({'error': str(e)}), 404
    except ForbiddenError as e:
        return jsonify({'error': str(e)}), 403
    except Exception as e:
        logger.error(f"Error reordering course: {str(e)}")
        return jsonify({'error': 'Failed to reorder course'}), 500


@bp.route('/statistics', methods=['GET'])
@jwt_required()
@require_tenant()
@check_role(['admin', 'manager', 'instructor'])
def get_course_statistics():
    """Get course statistics."""
    try:
        jwt_payload = get_jwt()
        tenant_id = jwt_payload.get('tenant_id')
        user_id = get_jwt_identity()
        
        # Get current user
        user = db.session.query(User).filter_by(id=user_id).first()
        if not user:
            return jsonify({'error': 'User not found'}), 404
        
        # Get program ID filter if provided
        program_id = request.args.get('program_id', type=int)
        
        # Get statistics
        service = CourseService(db.session)
        stats = service.get_statistics(tenant_id, program_id, user)
        
        return jsonify(stats), 200
        
    except ForbiddenError as e:
        return jsonify({'error': str(e)}), 403
    except Exception as e:
        logger.error(f"Error fetching statistics: {str(e)}")
        return jsonify({'error': 'Failed to fetch statistics'}), 500