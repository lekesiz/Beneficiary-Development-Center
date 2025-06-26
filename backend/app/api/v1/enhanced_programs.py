"""
Enhanced Program API endpoints with comprehensive CRUD operations, validation, and error handling
"""

from flask import Blueprint, request, jsonify, current_app
from flask_jwt_extended import jwt_required, get_jwt_identity, get_jwt
from marshmallow import ValidationError
from datetime import datetime
from typing import Dict, Any, Tuple
import logging

from app.services.program_service import ProgramService
from app.models.program import Program, ProgramStatus, ProgramType
from app.models.user import User
from app.core.decorators import require_tenant, check_role, rate_limit, audit_log
from app.extensions import db, cache
from app.core.logging import logger
from app.core.exceptions import (
    NotFoundError, BadRequestError, ForbiddenError,
    ConflictError, BusinessLogicError, InvalidStateError
)
from app.core.error_handlers import ErrorResponse
from app.schemas.enhanced_program import (
    ProgramCreateSchema, ProgramUpdateSchema, ProgramQuerySchema,
    ProgramResponseSchema, ProgramBatchOperationSchema,
    ProgramStatisticsResponseSchema
)

bp = Blueprint("enhanced_programs", __name__)

# Initialize schemas
program_create_schema = ProgramCreateSchema()
program_update_schema = ProgramUpdateSchema()
program_query_schema = ProgramQuerySchema()
program_response_schema = ProgramResponseSchema()
program_batch_schema = ProgramBatchOperationSchema()
program_stats_schema = ProgramStatisticsResponseSchema()


# Helper functions
def get_current_user() -> User:
    """Get the current authenticated user"""
    user_id = get_jwt_identity()
    user = db.session.query(User).filter_by(id=user_id).first()
    if not user:
        raise NotFoundError("User not found")
    return user


def serialize_program(program: Program, include_stats: bool = False) -> Dict[str, Any]:
    """Serialize a program with optional statistics"""
    data = program_response_schema.dump(program.to_dict(include_related=True))
    
    if include_stats:
        # Add real-time statistics
        data['current_participants'] = program.get_enrollment_count()
        data['available_seats'] = program.get_available_spots()
        data['is_enrollment_open'] = program.is_enrollment_open
        data['progress_percentage'] = program.get_progress_percentage()
    
    return data


# Main CRUD endpoints
@bp.route("", methods=["GET"])
@jwt_required()
@require_tenant()
@rate_limit(calls=100, period=60)  # 100 calls per minute
def list_programs():
    """
    List all programs with advanced filtering, sorting, and pagination
    
    Query Parameters:
    - page: Page number (default: 1)
    - per_page: Items per page (default: 20, max: 100)
    - status: Filter by status
    - program_type: Filter by type
    - search: Search in title, description, code
    - upcoming_only: Show only upcoming programs
    - active_only: Show only active programs
    - has_seats: Show only programs with available seats
    - min_price: Minimum price filter
    - max_price: Maximum price filter
    - coordinator_id: Filter by coordinator
    - tags: Filter by tags (comma-separated)
    - start_date_from: Start date range from
    - start_date_to: Start date range to
    - sort_by: Sort field (default: created_at)
    - sort_order: Sort order (asc/desc, default: desc)
    - include_stats: Include real-time statistics
    """
    try:
        # Parse and validate query parameters
        try:
            filters = program_query_schema.load(request.args)
        except ValidationError as e:
            return jsonify({"error": "Invalid query parameters", "details": e.messages}), 400
        
        # Get tenant and user info
        jwt_payload = get_jwt()
        tenant_id = jwt_payload.get("tenant_id")
        user = get_current_user()
        
        # Extract filters
        page = filters.get('page', 1)
        per_page = filters.get('per_page', 20)
        include_stats = request.args.get('include_stats', 'false').lower() == 'true'
        
        # Check cache for non-filtered results
        cache_key = f"programs:{tenant_id}:{page}:{per_page}:{hash(frozenset(filters.items()))}"
        cached_result = cache.get(cache_key) if not include_stats else None
        
        if cached_result:
            logger.info(f"Returning cached programs for tenant {tenant_id}")
            return jsonify(cached_result), 200
        
        # Get programs from service
        service = ProgramService(db.session)
        
        # Filter out parameters that the service doesn't support
        supported_params = ['status', 'program_type', 'search', 'upcoming_only', 'active_only', 'sort_by', 'sort_order']
        service_params = {k: v for k, v in filters.items() if k in supported_params}
        
        programs = service.get_all(
            tenant_id=tenant_id,
            user=user,
            skip=(page - 1) * per_page,
            limit=per_page,
            **service_params
        )
        
        # Get total count for pagination
        total = service.count(tenant_id=tenant_id, filters=filters)
        
        # Serialize programs
        programs_data = [serialize_program(p, include_stats) for p in programs]
        
        # Build response
        response = {
            "programs": programs_data,
            "pagination": {
                "page": page,
                "per_page": per_page,
                "total": total,
                "pages": (total + per_page - 1) // per_page,
                "has_next": page * per_page < total,
                "has_prev": page > 1
            },
            "filters_applied": {k: v for k, v in filters.items() if v is not None}
        }
        
        # Cache the result for 5 minutes (if not including stats)
        if not include_stats:
            cache.set(cache_key, response, timeout=300)
        
        logger.info(f"Retrieved {len(programs)} programs for tenant {tenant_id}")
        return jsonify(response), 200
        
    except Exception as e:
        logger.error(f"Error listing programs: {str(e)}")
        error_response, status_code = ErrorResponse.create(
            error="InternalError",
            message="Failed to retrieve programs",
            status_code=500
        )
        return jsonify(error_response), status_code


@bp.route("/<int:program_id>", methods=["GET"])
@jwt_required()
@require_tenant()
@rate_limit(calls=200, period=60)
def get_program(program_id: int):
    """
    Get a specific program by ID
    
    Query Parameters:
    - include_courses: Include course list (default: false)
    - include_stats: Include real-time statistics (default: false)
    - include_enrollments: Include enrollment details (default: false)
    """
    try:
        jwt_payload = get_jwt()
        tenant_id = jwt_payload.get("tenant_id")
        user = get_current_user()
        
        # Parse query parameters
        include_courses = request.args.get('include_courses', 'false').lower() == 'true'
        include_stats = request.args.get('include_stats', 'false').lower() == 'true'
        include_enrollments = request.args.get('include_enrollments', 'false').lower() == 'true'
        
        # Get program
        service = ProgramService(db.session)
        program = service.get_by_id(tenant_id, program_id, user)
        
        # Serialize program
        data = serialize_program(program, include_stats)
        
        # Add optional data
        if include_courses:
            data['courses'] = [
                {
                    'id': c.id,
                    'code': c.code,
                    'title': c.title,
                    'status': c.status.value,
                    'duration_hours': c.duration_hours,
                    'instructor_name': c.instructor.full_name if c.instructor else None
                }
                for c in program.courses if not c.deleted_at
            ]
        
        if include_enrollments and user.role in ['admin', 'manager']:
            data['enrollments'] = {
                'total': len(program.enrollments),
                'active': len([e for e in program.enrollments if e.status in ['enrolled', 'in_progress']]),
                'completed': len([e for e in program.enrollments if e.status == 'completed'])
            }
        
        logger.info(f"Retrieved program {program_id} for user {user.id}")
        return jsonify(data), 200
        
    except NotFoundError as e:
        return ErrorResponse.create(
            error="NotFound",
            message=str(e),
            status_code=404,
            error_code="PROGRAM_NOT_FOUND"
        )
    except Exception as e:
        logger.error(f"Error retrieving program {program_id}: {str(e)}")
        return ErrorResponse.create(
            error="InternalError",
            message="Failed to retrieve program",
            status_code=500
        )


@bp.route("", methods=["POST"])
@jwt_required()
@require_tenant()
@check_role(["admin", "manager"])
@rate_limit(calls=20, period=60)
@audit_log(action="create_program")
def create_program():
    """
    Create a new program
    
    Request Body: ProgramCreateSchema
    """
    try:
        jwt_payload = get_jwt()
        tenant_id = jwt_payload.get("tenant_id")
        user = get_current_user()
        
        # Validate request data
        try:
            data = program_create_schema.load(request.json)
        except ValidationError as e:
            return jsonify({"error": "Validation error", "details": e.messages}), 400
        
        # Check for duplicate code
        existing = db.session.query(Program).filter_by(
            tenant_id=tenant_id,
            code=data.get('code'),
            deleted_at=None
        ).first()
        
        if existing:
            raise ConflictError(f"Program with code '{data.get('code')}' already exists")
        
        # Create program
        service = ProgramService(db.session)
        program = service.create(tenant_id, data, user)
        
        # Return created program
        response_data = serialize_program(program, include_stats=True)
        
        logger.info(f"Created program {program.code} by user {user.id}")
        return jsonify(response_data), 201
        
    except ValidationError as e:
        return jsonify({"error": "Validation error", "details": e.messages}), 400
    except ConflictError as e:
        return ErrorResponse.create(
            error="Conflict",
            message=str(e),
            status_code=409,
            error_code="DUPLICATE_PROGRAM"
        )
    except BusinessLogicError as e:
        return ErrorResponse.create(
            error="BusinessLogicError",
            message=str(e),
            status_code=400,
            error_code="BUSINESS_RULE_VIOLATION"
        )
    except Exception as e:
        logger.error(f"Error creating program: {str(e)}")
        db.session.rollback()
        return ErrorResponse.create(
            error="InternalError",
            message="Failed to create program",
            status_code=500
        )


@bp.route("/<int:program_id>", methods=["PUT", "PATCH"])
@jwt_required()
@require_tenant()
@check_role(["admin", "manager"])
@rate_limit(calls=50, period=60)
@audit_log(action="update_program")
def update_program(program_id: int):
    """
    Update a program (PUT for full update, PATCH for partial update)
    
    Request Body: ProgramUpdateSchema
    """
    try:
        jwt_payload = get_jwt()
        tenant_id = jwt_payload.get("tenant_id")
        user = get_current_user()
        
        # Determine if partial update
        partial = request.method == 'PATCH'
        
        # Validate request data
        try:
            data = program_update_schema.load(request.json, partial=partial)
        except ValidationError as e:
            return jsonify({"error": "Validation error", "details": e.messages}), 400
        
        # Check if trying to update code to existing one
        if 'code' in data:
            existing = db.session.query(Program).filter_by(
                tenant_id=tenant_id,
                code=data['code'],
                deleted_at=None
            ).filter(Program.id != program_id).first()
            
            if existing:
                raise ConflictError(f"Program with code '{data['code']}' already exists")
        
        # Update program
        service = ProgramService(db.session)
        program = service.update(tenant_id, program_id, data, user)
        
        # Return updated program
        response_data = serialize_program(program, include_stats=True)
        
        logger.info(f"Updated program {program_id} by user {user.id}")
        return jsonify(response_data), 200
        
    except NotFoundError as e:
        return ErrorResponse.create(
            error="NotFound",
            message=str(e),
            status_code=404,
            error_code="PROGRAM_NOT_FOUND"
        )
    except ConflictError as e:
        return ErrorResponse.create(
            error="Conflict",
            message=str(e),
            status_code=409,
            error_code="DUPLICATE_PROGRAM"
        )
    except InvalidStateError as e:
        return ErrorResponse.create(
            error="InvalidState",
            message=str(e),
            status_code=400,
            error_code="INVALID_PROGRAM_STATE"
        )
    except Exception as e:
        logger.error(f"Error updating program {program_id}: {str(e)}")
        db.session.rollback()
        return ErrorResponse.create(
            error="InternalError",
            message="Failed to update program",
            status_code=500
        )


@bp.route("/<int:program_id>", methods=["DELETE"])
@jwt_required()
@require_tenant()
@check_role(["admin"])
@rate_limit(calls=10, period=60)
@audit_log(action="delete_program")
def delete_program(program_id: int):
    """
    Delete a program (soft delete)
    
    Query Parameters:
    - force: Force delete even with active enrollments (admin only)
    """
    try:
        jwt_payload = get_jwt()
        tenant_id = jwt_payload.get("tenant_id")
        user = get_current_user()
        
        force_delete = request.args.get('force', 'false').lower() == 'true'
        
        # Only super admins can force delete
        if force_delete and user.role != 'admin':
            raise ForbiddenError("Only administrators can force delete programs")
        
        # Delete program
        service = ProgramService(db.session)
        
        # Check if program has active enrollments
        program = service.get_by_id(tenant_id, program_id, user)
        active_enrollments = [e for e in program.enrollments if e.status in ['enrolled', 'in_progress']]
        
        if active_enrollments and not force_delete:
            return ErrorResponse.create(
                error="Conflict",
                message=f"Cannot delete program with {len(active_enrollments)} active enrollments",
                status_code=409,
                error_code="ACTIVE_ENROLLMENTS_EXIST",
                details={"active_enrollments": len(active_enrollments)}
            )
        
        service.delete(tenant_id, program_id, user)
        
        logger.info(f"Deleted program {program_id} by user {user.id}")
        return '', 204
        
    except NotFoundError as e:
        return ErrorResponse.create(
            error="NotFound",
            message=str(e),
            status_code=404,
            error_code="PROGRAM_NOT_FOUND"
        )
    except ForbiddenError as e:
        return ErrorResponse.create(
            error="Forbidden",
            message=str(e),
            status_code=403,
            error_code="INSUFFICIENT_PERMISSIONS"
        )
    except Exception as e:
        logger.error(f"Error deleting program {program_id}: {str(e)}")
        db.session.rollback()
        return ErrorResponse.create(
            error="InternalError",
            message="Failed to delete program",
            status_code=500
        )


# Additional endpoints
@bp.route("/<int:program_id>/status", methods=["PUT"])
@jwt_required()
@require_tenant()
@check_role(["admin", "manager"])
@rate_limit(calls=30, period=60)
@audit_log(action="update_program_status")
def update_program_status(program_id: int):
    """
    Update program status with validation
    
    Request Body:
    {
        "status": "draft|published|active|completed|archived",
        "reason": "Optional reason for status change"
    }
    """
    try:
        jwt_payload = get_jwt()
        tenant_id = jwt_payload.get("tenant_id")
        user = get_current_user()
        
        # Get request data
        data = request.json
        if not data or 'status' not in data:
            raise BadRequestError("Status is required")
        
        try:
            new_status = ProgramStatus(data['status'])
        except ValueError:
            raise BadRequestError(f"Invalid status: {data['status']}")
        
        reason = data.get('reason')
        
        # Update status
        service = ProgramService(db.session)
        program = service.update_status(tenant_id, program_id, new_status, user)
        
        # Log status change
        logger.info(f"Updated program {program_id} status to {new_status.value} by user {user.id}. Reason: {reason}")
        
        return jsonify(serialize_program(program, include_stats=True)), 200
        
    except NotFoundError as e:
        return ErrorResponse.create(
            error="NotFound",
            message=str(e),
            status_code=404,
            error_code="PROGRAM_NOT_FOUND"
        )
    except InvalidStateError as e:
        return ErrorResponse.create(
            error="InvalidState",
            message=str(e),
            status_code=400,
            error_code="INVALID_STATUS_TRANSITION"
        )
    except Exception as e:
        logger.error(f"Error updating program status: {str(e)}")
        db.session.rollback()
        return ErrorResponse.create(
            error="InternalError",
            message="Failed to update program status",
            status_code=500
        )


@bp.route("/batch", methods=["POST"])
@jwt_required()
@require_tenant()
@check_role(["admin"])
@rate_limit(calls=5, period=60)
@audit_log(action="batch_program_operation")
def batch_program_operation():
    """
    Perform batch operations on multiple programs
    
    Request Body: ProgramBatchOperationSchema
    """
    try:
        jwt_payload = get_jwt()
        tenant_id = jwt_payload.get("tenant_id")
        user = get_current_user()
        
        # Validate request
        try:
            data = program_batch_schema.load(request.json)
        except ValidationError as e:
            return jsonify({"error": "Validation error", "details": e.messages}), 400
        
        if not data['confirm']:
            raise BadRequestError("Confirmation is required for batch operations")
        
        program_ids = data['program_ids']
        operation = data['operation']
        reason = data.get('reason')
        
        # Perform batch operation
        service = ProgramService(db.session)
        results = {
            'success': [],
            'failed': []
        }
        
        for program_id in program_ids:
            try:
                if operation == 'archive':
                    service.update_status(tenant_id, program_id, ProgramStatus.ARCHIVED, user)
                elif operation == 'delete':
                    service.delete(tenant_id, program_id, user)
                elif operation == 'publish':
                    service.update_status(tenant_id, program_id, ProgramStatus.PUBLISHED, user)
                elif operation == 'activate':
                    service.update_status(tenant_id, program_id, ProgramStatus.ACTIVE, user)
                
                results['success'].append(program_id)
                
            except Exception as e:
                results['failed'].append({
                    'program_id': program_id,
                    'error': str(e)
                })
        
        # Commit all changes
        db.session.commit()
        
        logger.info(f"Batch operation '{operation}' on {len(program_ids)} programs by user {user.id}. "
                   f"Success: {len(results['success'])}, Failed: {len(results['failed'])}")
        
        return jsonify({
            'operation': operation,
            'total': len(program_ids),
            'success_count': len(results['success']),
            'failed_count': len(results['failed']),
            'results': results
        }), 200
        
    except BadRequestError as e:
        return ErrorResponse.create(
            error="BadRequest",
            message=str(e),
            status_code=400
        )
    except Exception as e:
        logger.error(f"Error in batch operation: {str(e)}")
        db.session.rollback()
        return ErrorResponse.create(
            error="InternalError",
            message="Failed to perform batch operation",
            status_code=500
        )


@bp.route("/statistics", methods=["GET"])
@jwt_required()
@require_tenant()
@check_role(["admin", "manager"])
@rate_limit(calls=50, period=60)
def get_program_statistics():
    """
    Get comprehensive program statistics
    
    Query Parameters:
    - start_date: Start date for statistics
    - end_date: End date for statistics
    - group_by: Group statistics by (month|quarter|year)
    """
    try:
        jwt_payload = get_jwt()
        tenant_id = jwt_payload.get("tenant_id")
        user = get_current_user()
        
        # Parse query parameters
        start_date = request.args.get('start_date')
        end_date = request.args.get('end_date')
        group_by = request.args.get('group_by', 'month')
        
        # Get statistics
        service = ProgramService(db.session)
        stats = service.get_statistics(
            tenant_id=tenant_id,
            user=user,
            start_date=start_date,
            end_date=end_date,
            group_by=group_by
        )
        
        # Add additional computed statistics
        stats['generated_at'] = datetime.utcnow()
        
        return jsonify(program_stats_schema.dump(stats)), 200
        
    except Exception as e:
        logger.error(f"Error fetching program statistics: {str(e)}")
        return ErrorResponse.create(
            error="InternalError",
            message="Failed to fetch statistics",
            status_code=500
        )


@bp.route("/search", methods=["POST"])
@jwt_required()
@require_tenant()
@rate_limit(calls=100, period=60)
def search_programs():
    """
    Advanced search endpoint with full-text search capabilities
    
    Request Body:
    {
        "query": "search terms",
        "filters": {...},
        "facets": ["status", "type", "tags"],
        "highlight": true
    }
    """
    try:
        jwt_payload = get_jwt()
        tenant_id = jwt_payload.get("tenant_id")
        user = get_current_user()
        
        data = request.json or {}
        query = data.get('query', '')
        filters = data.get('filters', {})
        facets = data.get('facets', [])
        highlight = data.get('highlight', False)
        
        # Perform search
        service = ProgramService(db.session)
        results = service.search(
            tenant_id=tenant_id,
            user=user,
            query=query,
            filters=filters,
            facets=facets,
            highlight=highlight
        )
        
        return jsonify(results), 200
        
    except Exception as e:
        logger.error(f"Error searching programs: {str(e)}")
        return ErrorResponse.create(
            error="InternalError",
            message="Failed to search programs",
            status_code=500
        )


@bp.route("/export", methods=["GET"])
@jwt_required()
@require_tenant()
@check_role(["admin", "manager"])
@rate_limit(calls=10, period=60)
def export_programs():
    """
    Export programs data in various formats
    
    Query Parameters:
    - format: Export format (csv|excel|json)
    - fields: Comma-separated list of fields to export
    - filters: Apply same filters as list endpoint
    """
    try:
        jwt_payload = get_jwt()
        tenant_id = jwt_payload.get("tenant_id")
        user = get_current_user()
        
        export_format = request.args.get('format', 'csv')
        fields = request.args.get('fields', '').split(',') if request.args.get('fields') else None
        
        # Apply filters
        filters = program_query_schema.load(request.args)
        
        # Generate export
        service = ProgramService(db.session)
        export_data = service.export(
            tenant_id=tenant_id,
            user=user,
            format=export_format,
            fields=fields,
            filters=filters
        )
        
        # Return appropriate response based on format
        if export_format == 'json':
            return jsonify(export_data), 200
        else:
            # For CSV/Excel, return file response
            from flask import Response
            return Response(
                export_data,
                mimetype='text/csv' if export_format == 'csv' else 'application/vnd.openxmlformats-officedocument.spreadsheetml.sheet',
                headers={
                    'Content-Disposition': f'attachment; filename=programs_export_{datetime.utcnow().strftime("%Y%m%d_%H%M%S")}.{export_format}'
                }
            )
            
    except Exception as e:
        logger.error(f"Error exporting programs: {str(e)}")
        return ErrorResponse.create(
            error="InternalError",
            message="Failed to export programs",
            status_code=500
        )


# Health check endpoint
@bp.route("/health", methods=["GET"])
def health_check():
    """API health check endpoint"""
    return jsonify({
        "status": "healthy",
        "service": "programs-api",
        "version": "1.0.0",
        "timestamp": datetime.utcnow().isoformat()
    }), 200