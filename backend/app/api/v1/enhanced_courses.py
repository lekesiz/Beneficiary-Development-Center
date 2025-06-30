"""
Enhanced Course API endpoints with comprehensive CRUD operations, validation, and error handling
"""

from flask import Blueprint, request, jsonify, Response
from flask_jwt_extended import jwt_required, get_jwt_identity, get_jwt
from marshmallow import ValidationError
from datetime import datetime
from typing import Dict, Any, List, Optional
import logging

from app.services.course_service import CourseService
from app.models.course import Course, CourseStatus, CourseFormat, DifficultyLevel
from app.models.user import User
from app.models.course_session import CourseSession
from app.core.decorators import require_tenant, check_role, rate_limit, audit_log
from app.extensions import db, cache
from app.core.logging import logger
from app.core.exceptions import (
    NotFoundError,
    BadRequestError,
    ForbiddenError,
    ConflictError,
    BusinessLogicError,
    InvalidStateError,
)
from app.core.error_handlers import ErrorResponse
from app.schemas.enhanced_course import (
    CourseCreateSchema,
    CourseUpdateSchema,
    CourseQuerySchema,
    CourseResponseSchema,
    CourseSessionSchema,
    CourseReorderSchema,
    CourseDuplicateSchema,
    CourseStatisticsResponseSchema,
)
from app.utils.calendar import generate_session_ics

bp = Blueprint("enhanced_courses", __name__)

# Initialize schemas
course_create_schema = CourseCreateSchema()
course_update_schema = CourseUpdateSchema()
course_query_schema = CourseQuerySchema()
course_response_schema = CourseResponseSchema()
course_session_schema = CourseSessionSchema()
course_reorder_schema = CourseReorderSchema()
course_duplicate_schema = CourseDuplicateSchema()
course_stats_schema = CourseStatisticsResponseSchema()


# Helper functions
def get_current_user() -> User:
    """Get the current authenticated user"""
    user_id = get_jwt_identity()
    user = db.session.query(User).filter_by(id=user_id).first()
    if not user:
        raise NotFoundError("User not found")
    return user


def serialize_course(course: Course, include_sessions: bool = False) -> Dict[str, Any]:
    """Serialize a course with optional sessions"""
    try:
        # Start with basic course data
        data = course.to_dict(exclude=None, include_related=False)

        # Safely add computed fields
        try:
            data["participant_count"] = course.get_participant_count()
        except:
            data["participant_count"] = 0

        try:
            data["available_spots"] = course.get_available_spots()
        except:
            data["available_spots"] = 0

        try:
            data["completion_rate"] = course.get_completion_rate()
        except:
            data["completion_rate"] = 0

        try:
            data["average_score"] = course.get_average_score()
        except:
            data["average_score"] = None

        data["session_count"] = len(course.sessions) if course.sessions else 0

        # Add instructor info safely
        if hasattr(course, "instructor") and course.instructor:
            data["instructor_name"] = course.instructor.full_name
            data["instructor"] = {
                "id": course.instructor.id,
                "name": course.instructor.full_name,
                "email": getattr(course.instructor, "email", None),
            }
        else:
            data["instructor_name"] = None
            data["instructor"] = None

        # Add program info safely
        if hasattr(course, "program") and course.program:
            data["program_title"] = course.program.title
            data["program_code"] = getattr(course.program, "code", None)
            data["program"] = {
                "id": course.program.id,
                "title": course.program.title,
                "code": getattr(course.program, "code", None),
            }
        else:
            data["program"] = None

        if include_sessions:
            if course.sessions:
                data["sessions"] = [
                    {
                        "id": s.id,
                        "title": s.title,
                        "session_date": s.session_date.isoformat() if s.session_date else None,
                        "duration_hours": s.duration_hours,
                        "start_time": s.session_date.strftime("%H:%M") if s.session_date else None,
                        "end_time": s.end_time.strftime("%H:%M") if s.end_time else None,
                        "location": getattr(s, "location", None),
                        "online_link": getattr(s, "online_link", None),
                        "is_online": getattr(s, "is_online", False),
                        "instructor_name": (
                            s.instructor.full_name if hasattr(s, "instructor") and s.instructor else None
                        ),
                        "instructor_id": getattr(s, "instructor_id", None),
                        "is_cancelled": getattr(s, "is_cancelled", False),
                        "is_mandatory": getattr(s, "is_mandatory", True),
                    }
                    for s in course.sessions
                ]
            else:
                data["sessions"] = []

        return data
    except Exception as e:
        # Fallback to minimal serialization
        logger.error(f"Error serializing course {course.id}: {str(e)}")
        return {
            "id": course.id,
            "title": course.title,
            "code": getattr(course, "code", None),
            "status": course.status.value if course.status else None,
            "description": getattr(course, "description", None),
        }


# Main CRUD endpoints
@bp.route("", methods=["GET"])
@jwt_required()
@require_tenant()
@rate_limit(calls=100, period=60)
def list_courses(program_id):
    """
    List all courses for a program with filtering and pagination

    Query Parameters:
    - page: Page number (default: 1)
    - per_page: Items per page (default: 20)
    - status: Filter by status
    - format: Filter by format
    - difficulty_level: Filter by difficulty
    - instructor_id: Filter by instructor
    - search: Search in title, description
    - has_assessment: Filter courses with assessment
    - has_sessions: Filter courses with sessions
    - min_duration_hours: Minimum duration filter
    - max_duration_hours: Maximum duration filter
    - tags: Filter by tags
    - sort_by: Sort field
    - sort_order: Sort order
    - include_sessions: Include session details
    """
    try:
        # Validate query parameters
        try:
            filters = course_query_schema.load(request.args)
        except ValidationError as e:
            return jsonify({"error": "Invalid query parameters", "details": e.messages}), 400

        jwt_payload = get_jwt()
        tenant_id = jwt_payload.get("tenant_id")
        user = get_current_user()

        # Extract pagination
        page = filters.get("page", 1)
        per_page = filters.get("per_page", 20)
        include_sessions = request.args.get("include_sessions", "false").lower() == "true"

        logger.info(f"Processing list_courses request: program_id={program_id}, user={user.id}, tenant_id={tenant_id}")

        # Get courses
        service = CourseService(db.session)

        # Extract filter parameters for the service
        service_filters = {}
        for key in ["status", "format", "difficulty_level", "instructor_id", "search", "sort_by", "sort_order"]:
            if key in filters:
                # Map API field names to service parameter names
                if key == "difficulty_level":
                    service_filters["difficulty"] = filters[key]
                else:
                    service_filters[key] = filters[key]

        courses = service.get_all_by_program(
            tenant_id=tenant_id,
            program_id=program_id,
            user=user,
            skip=(page - 1) * per_page,
            limit=per_page,
            **service_filters,
        )

        # Get total count
        total = service.count_by_program(tenant_id, program_id, dict(filters))

        # Serialize courses
        courses_data = [serialize_course(c, include_sessions) for c in courses]

        # Build response
        response = {
            "data": courses_data,
            "meta": {
                "page": page,
                "per_page": per_page,
                "total": total,
                "pages": (total + per_page - 1) // per_page,
                "has_next": page * per_page < total,
                "has_prev": page > 1,
            },
        }

        logger.info(f"Retrieved {len(courses)} courses for program {program_id}")
        return jsonify(response), 200

    except NotFoundError as e:
        return ErrorResponse.create(error="NotFound", message=str(e), status_code=404, error_code="PROGRAM_NOT_FOUND")
    except Exception as e:
        logger.error(f"Error listing courses: {str(e)}")
        return ErrorResponse.create(error="InternalError", message="Failed to retrieve courses", status_code=500)


@bp.route("/<int:course_id>", methods=["GET"])
@jwt_required()
@require_tenant()
@rate_limit(calls=200, period=60)
def get_course(program_id, course_id):
    """
    Get a specific course by ID

    Query Parameters:
    - include_sessions: Include session list
    - include_progress: Include user progress (for students)
    - include_materials: Include course materials
    """
    try:
        jwt_payload = get_jwt()
        tenant_id = jwt_payload.get("tenant_id")
        user = get_current_user()

        # Parse query parameters
        include_sessions = request.args.get(
            "include_sessions", "false"
        ).lower() == "true" or "sessions" in request.args.get("include", "").split(",")
        include_progress = request.args.get(
            "include_progress", "false"
        ).lower() == "true" or "progress" in request.args.get("include", "").split(",")
        include_materials = request.args.get(
            "include_materials", "false"
        ).lower() == "true" or "materials" in request.args.get("include", "").split(",")

        # Get course
        service = CourseService(db.session)
        course = service.get_by_id(tenant_id, program_id, course_id, user)

        # Serialize course
        data = serialize_course(course, include_sessions)

        # Add user progress if requested
        if include_progress and user.role == "student":
            progress = service.get_user_progress(course_id, user.id)
            data["user_progress"] = progress

        # Add materials if requested
        if include_materials:
            data["materials_detail"] = course.materials or []
            data["resources_detail"] = course.resources or []
            data["assignments_detail"] = course.assignments or []

        logger.info(f"Retrieved course {course_id} for user {user.id}")
        return jsonify({"data": data}), 200

    except NotFoundError as e:
        return ErrorResponse.create(error="NotFound", message=str(e), status_code=404, error_code="COURSE_NOT_FOUND")
    except Exception as e:
        logger.error(f"Error retrieving course {course_id}: {str(e)}")
        return ErrorResponse.create(error="InternalError", message="Failed to retrieve course", status_code=500)


@bp.route("", methods=["POST"])
@jwt_required()
@require_tenant()
@check_role(["admin", "manager", "instructor"])
@rate_limit(calls=20, period=60)
@audit_log(action="create_course")
def create_course(program_id):
    """
    Create a new course in a program

    Request Body: CourseCreateSchema
    """
    try:
        jwt_payload = get_jwt()
        tenant_id = jwt_payload.get("tenant_id")
        user = get_current_user()

        # Get request data and set program_id from URL
        request_data = request.json or {}
        request_data["program_id"] = program_id

        # Validate request data
        try:
            data = course_create_schema.load(request_data)
        except ValidationError as e:
            return jsonify({"error": "Validation error", "details": e.messages}), 400

        # Check for duplicate code within program
        if "code" in data:
            existing = (
                db.session.query(Course)
                .filter_by(tenant_id=tenant_id, program_id=program_id, code=data["code"], deleted_at=None)
                .first()
            )

            if existing:
                raise ConflictError(f"Course with code '{data['code']}' already exists in this program")

        # Create course
        service = CourseService(db.session)
        course = service.create_for_program(tenant_id, program_id, data, user)

        # Return created course
        response_data = serialize_course(course)

        logger.info(f"Created course {course.code} in program {program_id} by user {user.id}")
        return jsonify({"data": response_data}), 201

    except NotFoundError as e:
        return ErrorResponse.create(error="NotFound", message=str(e), status_code=404, error_code="PROGRAM_NOT_FOUND")
    except ConflictError as e:
        return ErrorResponse.create(error="Conflict", message=str(e), status_code=409, error_code="DUPLICATE_COURSE")
    except ForbiddenError as e:
        return ErrorResponse.create(
            error="Forbidden", message=str(e), status_code=403, error_code="INSUFFICIENT_PERMISSIONS"
        )
    except BusinessLogicError as e:
        return ErrorResponse.create(
            error="BusinessLogicError", message=str(e), status_code=400, error_code="BUSINESS_RULE_VIOLATION"
        )
    except Exception as e:
        logger.error(f"Error creating course: {str(e)}")
        db.session.rollback()
        return ErrorResponse.create(error="InternalError", message="Failed to create course", status_code=500)


@bp.route("/<int:course_id>", methods=["PUT", "PATCH"])
@jwt_required()
@require_tenant()
@check_role(["admin", "manager", "instructor"])
@rate_limit(calls=50, period=60)
@audit_log(action="update_course")
def update_course(program_id, course_id):
    """
    Update a course

    Request Body: CourseUpdateSchema
    """
    try:
        jwt_payload = get_jwt()
        tenant_id = jwt_payload.get("tenant_id")
        user = get_current_user()

        # Check instructor permissions
        if user.role == "instructor":
            course = (
                db.session.query(Course).filter_by(id=course_id, tenant_id=tenant_id, program_id=program_id).first()
            )

            if not course:
                raise NotFoundError("Course not found")

            # Check if instructor can update this course
            is_course_instructor = course.instructor_id == user.id
            is_program_coordinator = course.program and course.program.coordinator_id == user.id

            if not (is_course_instructor or is_program_coordinator):
                raise ForbiddenError("You can only update courses you teach or coordinate")

        # Validate request data
        partial = request.method == "PATCH"
        try:
            data = course_update_schema.load(request.json, partial=partial)
        except ValidationError as e:
            return jsonify({"error": "Validation error", "details": e.messages}), 400

        # Update course
        service = CourseService(db.session)
        course = service.update(tenant_id, course_id, data, user)

        # Return updated course
        response_data = serialize_course(course)

        logger.info(f"Updated course {course_id} by user {user.id}")
        return jsonify({"data": response_data}), 200

    except NotFoundError as e:
        return ErrorResponse.create(error="NotFound", message=str(e), status_code=404, error_code="COURSE_NOT_FOUND")
    except ForbiddenError as e:
        return ErrorResponse.create(
            error="Forbidden", message=str(e), status_code=403, error_code="INSUFFICIENT_PERMISSIONS"
        )
    except Exception as e:
        logger.error(f"Error updating course {course_id}: {str(e)}")
        db.session.rollback()
        return ErrorResponse.create(error="InternalError", message="Failed to update course", status_code=500)


@bp.route("/<int:course_id>", methods=["DELETE"])
@jwt_required()
@require_tenant()
@check_role(["admin", "manager"])
@rate_limit(calls=10, period=60)
@audit_log(action="delete_course")
def delete_course(program_id, course_id):
    """
    Delete a course (soft delete)
    """
    try:
        jwt_payload = get_jwt()
        tenant_id = jwt_payload.get("tenant_id")
        user = get_current_user()

        # Delete course
        service = CourseService(db.session)
        service.delete(tenant_id, program_id, course_id, user)

        logger.info(f"Deleted course {course_id} by user {user.id}")
        return "", 204

    except NotFoundError as e:
        return ErrorResponse.create(error="NotFound", message=str(e), status_code=404, error_code="COURSE_NOT_FOUND")
    except InvalidStateError as e:
        return ErrorResponse.create(
            error="InvalidState", message=str(e), status_code=400, error_code="CANNOT_DELETE_COURSE"
        )
    except Exception as e:
        logger.error(f"Error deleting course {course_id}: {str(e)}")
        db.session.rollback()
        return ErrorResponse.create(error="InternalError", message="Failed to delete course", status_code=500)


# Course session endpoints
@bp.route("/<int:course_id>/sessions", methods=["GET"])
@jwt_required()
@require_tenant()
@rate_limit(calls=100, period=60)
def list_course_sessions(program_id, course_id):
    """
    List all sessions for a course

    Query Parameters:
    - include_past: Include past sessions
    - include_cancelled: Include cancelled sessions
    - instructor_id: Filter by instructor
    - date_from: Filter sessions from date
    - date_to: Filter sessions to date
    """
    try:
        jwt_payload = get_jwt()
        tenant_id = jwt_payload.get("tenant_id")
        user = get_current_user()

        # Parse query parameters
        include_past = request.args.get("include_past", "true").lower() == "true"
        include_cancelled = request.args.get("include_cancelled", "false").lower() == "true"
        instructor_id = request.args.get("instructor_id", type=int)
        date_from = request.args.get("date_from")
        date_to = request.args.get("date_to")

        # Get course and sessions
        service = CourseService(db.session)
        course = service.get_by_id(tenant_id, program_id, course_id, user)
        sessions = service.get_sessions(
            course_id=course_id,
            include_past=include_past,
            include_cancelled=include_cancelled,
            instructor_id=instructor_id,
            date_from=date_from,
            date_to=date_to,
        )

        # Serialize sessions
        sessions_data = []
        for session in sessions:
            session_dict = {
                "id": session.id,
                "title": session.title,
                "description": session.description,
                "session_date": session.session_date.isoformat(),
                "start_time": session.start_time.strftime("%H:%M"),
                "end_time": session.end_time.strftime("%H:%M"),
                "duration_hours": session.duration_hours,
                "location": session.location,
                "online_link": session.online_link,
                "is_online": session.is_online,
                "instructor_id": session.instructor_id,
                "instructor_name": session.instructor.full_name if session.instructor else None,
                "max_participants": session.max_participants,
                "is_mandatory": session.is_mandatory,
                "is_recorded": session.is_recorded,
                "is_cancelled": session.is_cancelled,
                "cancellation_reason": session.cancellation_reason,
                "materials": session.materials or [],
                "calendar_url": f"/api/v1/programs/{program_id}/courses/{course_id}/sessions/{session.id}/calendar",
            }
            sessions_data.append(session_dict)

        return (
            jsonify(
                {
                    "sessions": sessions_data,
                    "course": {"id": course.id, "title": course.title, "code": course.code},
                    "total": len(sessions_data),
                }
            ),
            200,
        )

    except NotFoundError as e:
        return ErrorResponse.create(error="NotFound", message=str(e), status_code=404, error_code="COURSE_NOT_FOUND")
    except Exception as e:
        logger.error(f"Error fetching sessions: {str(e)}")
        return ErrorResponse.create(error="InternalError", message="Failed to fetch sessions", status_code=500)


@bp.route("/<int:course_id>/sessions", methods=["POST"])
@jwt_required()
@require_tenant()
@check_role(["admin", "manager", "instructor"])
@rate_limit(calls=30, period=60)
@audit_log(action="create_course_session")
def create_course_session(program_id, course_id):
    """
    Add a session to a course

    Request Body: CourseSessionSchema
    """
    try:
        jwt_payload = get_jwt()
        tenant_id = jwt_payload.get("tenant_id")
        user = get_current_user()

        # Validate request data
        try:
            data = course_session_schema.load(request.json)
        except ValidationError as e:
            return jsonify({"error": "Validation error", "details": e.messages}), 400

        # Get course
        service = CourseService(db.session)
        course = service.get_by_id(tenant_id, program_id, course_id, user)

        # Check permissions for instructor
        if user.role == "instructor":
            if course.instructor_id != user.id and course.program.coordinator_id != user.id:
                raise ForbiddenError("You can only add sessions to courses you teach or coordinate")

        # Check for session conflicts
        conflict = service.check_session_conflict(
            course_id=course_id,
            session_date=data["session_date"],
            start_time=data["start_time"],
            end_time=data["end_time"],
            location=data.get("location"),
            instructor_id=data.get("instructor_id"),
        )

        if conflict:
            return ErrorResponse.create(
                error="Conflict",
                message="Session conflicts with existing session",
                status_code=409,
                error_code="SESSION_CONFLICT",
                details={"conflicting_session": conflict},
            )

        # Add session
        session_data = {"created_by": user.id, **data}
        course.add_session(session_data)

        # Get the newly added session
        new_session = course.sessions[-1]

        logger.info(f"Added session to course {course_id} by user {user.id}")

        return (
            jsonify(
                {
                    "data": {
                        "id": new_session.id,
                        "title": new_session.title,
                        "session_date": new_session.session_date.isoformat(),
                        "start_time": new_session.start_time.strftime("%H:%M"),
                        "end_time": new_session.end_time.strftime("%H:%M"),
                        "course_id": course_id,
                        "instructor_id": new_session.instructor_id,
                        "message": "Session created successfully",
                    }
                }
            ),
            201,
        )

    except NotFoundError as e:
        return ErrorResponse.create(error="NotFound", message=str(e), status_code=404, error_code="COURSE_NOT_FOUND")
    except ForbiddenError as e:
        return ErrorResponse.create(
            error="Forbidden", message=str(e), status_code=403, error_code="INSUFFICIENT_PERMISSIONS"
        )
    except Exception as e:
        logger.error(f"Error adding session: {str(e)}")
        db.session.rollback()
        return ErrorResponse.create(error="InternalError", message="Failed to add session", status_code=500)


@bp.route("/<int:course_id>/sessions/<int:session_id>/calendar", methods=["GET"])
@jwt_required()
@require_tenant()
@rate_limit(calls=100, period=60)
def download_session_calendar(program_id, course_id, session_id):
    """
    Download calendar file (.ics) for a specific session

    Query Parameters:
    - timezone: Timezone for the calendar (default: UTC)
    """
    try:
        jwt_payload = get_jwt()
        tenant_id = jwt_payload.get("tenant_id")
        user = get_current_user()

        # Get course and session
        service = CourseService(db.session)
        course = service.get_by_id(tenant_id, program_id, course_id, user)

        session = (
            db.session.query(CourseSession)
            .filter_by(id=session_id, course_id=course_id, tenant_id=tenant_id, deleted_at=None)
            .first()
        )

        if not session:
            raise NotFoundError("Session not found")

        # Get timezone
        timezone = request.args.get("timezone", "UTC")

        # Generate session data for ICS
        session_data = {
            "id": session.id,
            "uuid": str(session.uuid),
            "title": session.title,
            "description": session.description,
            "session_date": session.session_date,
            "start_time": session.start_time,
            "end_time": session.end_time,
            "location": session.location,
            "online_link": session.online_link,
            "instructor_name": session.instructor.full_name if session.instructor else None,
        }

        # Generate ICS content
        ics_content = generate_session_ics(session=session_data, course_title=course.title, timezone=timezone)

        # Create response
        return Response(
            ics_content,
            mimetype="text/calendar",
            headers={
                "Content-Disposition": f'attachment; filename="session_{session.uuid}.ics"',
                "Content-Type": "text/calendar; charset=utf-8",
            },
        )

    except NotFoundError as e:
        return ErrorResponse.create(error="NotFound", message=str(e), status_code=404, error_code="SESSION_NOT_FOUND")
    except Exception as e:
        logger.error(f"Error generating calendar: {str(e)}")
        return ErrorResponse.create(error="InternalError", message="Failed to generate calendar file", status_code=500)


# Additional course operations
@bp.route("/reorder", methods=["PUT"])
@jwt_required()
@require_tenant()
@check_role(["admin", "manager"])
@rate_limit(calls=20, period=60)
@audit_log(action="reorder_courses")
def reorder_courses(program_id):
    """
    Reorder courses within a program

    Request Body: CourseReorderSchema
    """
    try:
        jwt_payload = get_jwt()
        tenant_id = jwt_payload.get("tenant_id")
        user = get_current_user()

        # Validate request
        try:
            data = course_reorder_schema.load(request.json)
        except ValidationError as e:
            return jsonify({"error": "Validation error", "details": e.messages}), 400

        # Reorder courses
        service = CourseService(db.session)
        courses = service.reorder_courses(tenant_id, program_id, data["course_orders"], user)

        # Return reordered courses
        courses_data = [serialize_course(c) for c in courses]

        logger.info(f"Reordered courses in program {program_id} by user {user.id}")
        return jsonify({"data": courses_data}), 200

    except BadRequestError as e:
        return ErrorResponse.create(error="BadRequest", message=str(e), status_code=400)
    except Exception as e:
        logger.error(f"Error reordering courses: {str(e)}")
        db.session.rollback()
        return ErrorResponse.create(error="InternalError", message="Failed to reorder courses", status_code=500)


@bp.route("/<int:course_id>/duplicate", methods=["POST"])
@jwt_required()
@require_tenant()
@check_role(["admin", "manager"])
@rate_limit(calls=10, period=60)
@audit_log(action="duplicate_course")
def duplicate_course(program_id, course_id):
    """
    Duplicate a course

    Request Body: CourseDuplicateSchema
    """
    try:
        jwt_payload = get_jwt()
        tenant_id = jwt_payload.get("tenant_id")
        user = get_current_user()

        # Validate request
        try:
            data = course_duplicate_schema.load(request.json or {})
        except ValidationError as e:
            return jsonify({"error": "Validation error", "details": e.messages}), 400

        # Duplicate course
        service = CourseService(db.session)
        duplicate = service.duplicate_course(
            tenant_id=tenant_id,
            program_id=program_id,
            course_id=course_id,
            new_program_id=data.get("program_id"),
            new_title=data.get("title"),
            include_sessions=data.get("include_sessions", False),
            include_materials=data.get("include_materials", True),
            include_assignments=data.get("include_assignments", True),
            user=user,
        )

        logger.info(f"Duplicated course {course_id} to {duplicate.id} by user {user.id}")
        return jsonify({"data": serialize_course(duplicate)}), 201

    except NotFoundError as e:
        return ErrorResponse.create(error="NotFound", message=str(e), status_code=404, error_code="COURSE_NOT_FOUND")
    except ConflictError as e:
        return ErrorResponse.create(
            error="Conflict", message=str(e), status_code=409, error_code="DUPLICATE_COURSE_CODE"
        )
    except Exception as e:
        logger.error(f"Error duplicating course: {str(e)}")
        db.session.rollback()
        return ErrorResponse.create(error="InternalError", message="Failed to duplicate course", status_code=500)


@bp.route("/<int:course_id>/statistics", methods=["GET"])
@jwt_required()
@require_tenant()
@check_role(["admin", "manager", "instructor"])
@rate_limit(calls=50, period=60)
def get_course_statistics(program_id, course_id):
    """
    Get detailed statistics for a course
    """
    try:
        jwt_payload = get_jwt()
        tenant_id = jwt_payload.get("tenant_id")
        user = get_current_user()

        # Get course
        service = CourseService(db.session)
        course = service.get_by_id(tenant_id, program_id, course_id, user)

        # Check permissions for instructor
        if user.role == "instructor":
            if course.instructor_id != user.id and course.program.coordinator_id != user.id:
                raise ForbiddenError("You can only view statistics for courses you teach or coordinate")

        # Get statistics
        stats = service.get_statistics(tenant_id, program_id, course_id, user)

        # Add metadata
        stats["generated_at"] = datetime.utcnow()

        return jsonify({"data": course_stats_schema.dump(stats)}), 200

    except NotFoundError as e:
        return ErrorResponse.create(error="NotFound", message=str(e), status_code=404, error_code="COURSE_NOT_FOUND")
    except ForbiddenError as e:
        return ErrorResponse.create(
            error="Forbidden", message=str(e), status_code=403, error_code="INSUFFICIENT_PERMISSIONS"
        )
    except Exception as e:
        logger.error(f"Error fetching course statistics: {str(e)}")
        return ErrorResponse.create(error="InternalError", message="Failed to fetch statistics", status_code=500)
