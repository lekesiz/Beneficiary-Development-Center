"""API endpoints for Course management."""

from flask import Blueprint, request, jsonify, Response
from flask_jwt_extended import jwt_required, get_jwt_identity, get_jwt
from marshmallow import ValidationError
from app.services.course_service import CourseService
from app.models.course import Course, CourseStatus, CourseFormat, DifficultyLevel
from app.models.user import User
from app.models.course_session import CourseSession
from app.schemas.course import (
    CourseCreateSchema,
    CourseUpdateSchema,
    CourseResponseSchema,
    CourseListSchema,
    CourseOrderUpdateSchema,
    CourseDuplicateSchema,
    CourseSessionAddSchema,
)
from app.core.decorators import require_tenant, check_role
from app.extensions import db
from app.core.logging import logger
from app.core.exceptions import NotFoundError, BadRequestError, ForbiddenError
from app.utils.calendar import generate_session_ics

bp = Blueprint("courses", __name__)

# Schema instances
course_create_schema = CourseCreateSchema()
course_update_schema = CourseUpdateSchema()
course_response_schema = CourseResponseSchema()
course_list_schema = CourseListSchema()
course_order_schema = CourseOrderUpdateSchema()
course_duplicate_schema = CourseDuplicateSchema()
course_session_schema = CourseSessionAddSchema()


@bp.route("", methods=["GET"])
@jwt_required()
@require_tenant()
def get_courses(program_id):
    """Get all courses for a program."""
    try:
        jwt_payload = get_jwt()
        tenant_id = jwt_payload.get("tenant_id")
        user_id = get_jwt_identity()

        # Get current user
        user = db.session.query(User).filter_by(id=user_id).first()
        if not user:
            return jsonify({"error": "User not found"}), 404

        # Get query parameters
        page = int(request.args.get("page", 1))
        per_page = int(request.args.get("per_page", 20))
        status = request.args.get("status")
        format = request.args.get("format")
        difficulty = request.args.get("difficulty")
        instructor_id = request.args.get("instructor_id", type=int)
        search = request.args.get("search")
        sort_by = request.args.get("sort_by", "created_at")
        sort_order = request.args.get("sort_order", "desc")

        # Convert string parameters to enums
        if status:
            try:
                status = CourseStatus(status)
            except ValueError:
                return jsonify({"error": f"Invalid status: {status}"}), 400

        if format:
            try:
                format = CourseFormat(format)
            except ValueError:
                return jsonify({"error": f"Invalid format: {format}"}), 400

        if difficulty:
            try:
                difficulty = DifficultyLevel(difficulty)
            except ValueError:
                return jsonify({"error": f"Invalid difficulty: {difficulty}"}), 400

        # Get courses
        service = CourseService(db.session)
        courses = service.get_all_by_program(
            tenant_id=tenant_id,
            program_id=program_id,
            user=user,
            skip=(page - 1) * per_page,
            limit=per_page,
            status=status,
            format=format,
            difficulty=difficulty,
            instructor_id=instructor_id,
            search=search,
            sort_by=sort_by,
            sort_order=sort_order,
        )

        # Get total count for pagination
        total_query = db.session.query(Course).filter(
            Course.program_id == program_id, Course.tenant_id == tenant_id, Course.deleted_at.is_(None)
        )

        if status:
            total_query = total_query.filter(Course.status == status)
        if format:
            total_query = total_query.filter(Course.format == format)
        if difficulty:
            total_query = total_query.filter(Course.difficulty_level == difficulty)
        if instructor_id:
            total_query = total_query.filter(Course.instructor_id == instructor_id)

        total = total_query.count()

        # Serialize courses
        courses_data = [course_response_schema.dump(c.to_dict(include_related=True)) for c in courses]

        return (
            jsonify(
                {
                    "courses": courses_data,
                    "pagination": {
                        "page": page,
                        "per_page": per_page,
                        "total": total,
                        "pages": (total + per_page - 1) // per_page,
                    },
                }
            ),
            200,
        )

    except NotFoundError as e:
        return jsonify({"error": str(e)}), 404
    except Exception as e:
        logger.error(f"Error fetching courses: {str(e)}")
        return jsonify({"error": "Failed to fetch courses"}), 500


@bp.route("/<int:course_id>", methods=["GET"])
@jwt_required()
@require_tenant()
def get_course(program_id, course_id):
    """Get a specific course."""
    try:
        jwt_payload = get_jwt()
        tenant_id = jwt_payload.get("tenant_id")
        user_id = get_jwt_identity()

        # Get current user
        user = db.session.query(User).filter_by(id=user_id).first()
        if not user:
            return jsonify({"error": "User not found"}), 404

        # Get course
        service = CourseService(db.session)
        course = service.get_by_id(tenant_id, program_id, course_id, user)

        # Include sessions if requested
        include_sessions = request.args.get("include_sessions", "false").lower() == "true"
        data = course.to_dict(include_related=True)

        if include_sessions:
            data["sessions"] = [s.to_dict() for s in course.sessions]

        return jsonify(course_response_schema.dump(data)), 200

    except NotFoundError as e:
        return jsonify({"error": str(e)}), 404
    except Exception as e:
        logger.error(f"Error fetching course: {str(e)}")
        return jsonify({"error": "Failed to fetch course"}), 500


@bp.route("", methods=["POST"])
@jwt_required()
@require_tenant()
@check_role(["admin", "manager", "instructor"])
def create_course(program_id):
    """Create a new course."""
    try:
        jwt_payload = get_jwt()
        tenant_id = jwt_payload.get("tenant_id")
        user_id = get_jwt_identity()

        # Get current user
        user = db.session.query(User).filter_by(id=user_id).first()
        if not user:
            return jsonify({"error": "User not found"}), 404

        # Validate request data
        data = course_create_schema.load(request.json)

        # Convert string enum values to actual enums
        if 'status' in data and isinstance(data['status'], str):
            try:
                data['status'] = CourseStatus(data['status'])
            except ValueError:
                return jsonify({"error": f"Invalid status: {data['status']}"}), 400
        
        if 'format' in data and isinstance(data['format'], str):
            try:
                data['format'] = CourseFormat(data['format'])
            except ValueError:
                return jsonify({"error": f"Invalid format: {data['format']}"}), 400
        
        if 'difficulty_level' in data and isinstance(data['difficulty_level'], str):
            try:
                data['difficulty_level'] = DifficultyLevel(data['difficulty_level'])
            except ValueError:
                return jsonify({"error": f"Invalid difficulty_level: {data['difficulty_level']}"}), 400

        # Create course
        service = CourseService(db.session)
        course = service.create(tenant_id, program_id, data, user)

        return jsonify(course_response_schema.dump(course.to_dict(include_related=True))), 201

    except ValidationError as e:
        return jsonify({"error": "Validation error", "details": e.messages}), 400
    except NotFoundError as e:
        return jsonify({"error": str(e)}), 404
    except BadRequestError as e:
        return jsonify({"error": str(e)}), 400
    except ForbiddenError as e:
        return jsonify({"error": str(e)}), 403
    except Exception as e:
        logger.error(f"Error creating course: {str(e)}")
        return jsonify({"error": "Failed to create course"}), 500


@bp.route("/<int:course_id>", methods=["PUT"])
@jwt_required()
@require_tenant()
@check_role(["admin", "manager", "instructor"])
def update_course(program_id, course_id):
    """Update a course."""
    try:
        jwt_payload = get_jwt()
        tenant_id = jwt_payload.get("tenant_id")
        user_id = get_jwt_identity()

        # Get current user
        user = db.session.query(User).filter_by(id=user_id).first()
        if not user:
            return jsonify({"error": "User not found"}), 404

        # Validate request data
        data = course_update_schema.load(request.json)

        # Convert string enum values to actual enums
        if 'status' in data and isinstance(data['status'], str):
            try:
                data['status'] = CourseStatus(data['status'])
            except ValueError:
                return jsonify({"error": f"Invalid status: {data['status']}"}), 400
        
        if 'format' in data and isinstance(data['format'], str):
            try:
                data['format'] = CourseFormat(data['format'])
            except ValueError:
                return jsonify({"error": f"Invalid format: {data['format']}"}), 400
        
        if 'difficulty_level' in data and isinstance(data['difficulty_level'], str):
            try:
                data['difficulty_level'] = DifficultyLevel(data['difficulty_level'])
            except ValueError:
                return jsonify({"error": f"Invalid difficulty_level: {data['difficulty_level']}"}), 400

        # Update course
        service = CourseService(db.session)
        course = service.update(tenant_id, program_id, course_id, data, user)

        return jsonify(course_response_schema.dump(course.to_dict(include_related=True))), 200

    except ValidationError as e:
        return jsonify({"error": "Validation error", "details": e.messages}), 400
    except NotFoundError as e:
        return jsonify({"error": str(e)}), 404
    except BadRequestError as e:
        return jsonify({"error": str(e)}), 400
    except ForbiddenError as e:
        return jsonify({"error": str(e)}), 403
    except Exception as e:
        logger.error(f"Error updating course: {str(e)}")
        return jsonify({"error": "Failed to update course"}), 500


@bp.route("/<int:course_id>", methods=["DELETE"])
@jwt_required()
@require_tenant()
@check_role(["admin", "manager"])
def delete_course(program_id, course_id):
    """Delete a course."""
    try:
        jwt_payload = get_jwt()
        tenant_id = jwt_payload.get("tenant_id")
        user_id = get_jwt_identity()

        # Get current user
        user = db.session.query(User).filter_by(id=user_id).first()
        if not user:
            return jsonify({"error": "User not found"}), 404

        # Delete course
        service = CourseService(db.session)
        service.delete(tenant_id, program_id, course_id, user)

        return "", 204

    except NotFoundError as e:
        return jsonify({"error": str(e)}), 404
    except BadRequestError as e:
        return jsonify({"error": str(e)}), 400
    except ForbiddenError as e:
        return jsonify({"error": str(e)}), 403
    except Exception as e:
        logger.error(f"Error deleting course: {str(e)}")
        return jsonify({"error": "Failed to delete course"}), 500


@bp.route("/<int:course_id>/status", methods=["PUT"])
@jwt_required()
@require_tenant()
@check_role(["admin", "manager", "instructor"])
def update_course_status(program_id, course_id):
    """Update course status."""
    try:
        jwt_payload = get_jwt()
        tenant_id = jwt_payload.get("tenant_id")
        user_id = get_jwt_identity()

        # Get current user
        user = db.session.query(User).filter_by(id=user_id).first()
        if not user:
            return jsonify({"error": "User not found"}), 404

        # Get new status
        data = request.json
        if not data or "status" not in data:
            return jsonify({"error": "Status is required"}), 400

        try:
            new_status = CourseStatus(data["status"])
        except ValueError:
            return jsonify({"error": f'Invalid status: {data["status"]}'}), 400

        # Update status
        service = CourseService(db.session)
        course = service.update_status(tenant_id, program_id, course_id, new_status, user)

        return jsonify(course_response_schema.dump(course.to_dict(include_related=True))), 200

    except NotFoundError as e:
        return jsonify({"error": str(e)}), 404
    except BadRequestError as e:
        return jsonify({"error": str(e)}), 400
    except ForbiddenError as e:
        return jsonify({"error": str(e)}), 403
    except Exception as e:
        logger.error(f"Error updating course status: {str(e)}")
        return jsonify({"error": "Failed to update course status"}), 500


@bp.route("/reorder", methods=["PUT"])
@jwt_required()
@require_tenant()
@check_role(["admin", "manager"])
def reorder_courses(program_id):
    """Reorder courses within a program."""
    try:
        jwt_payload = get_jwt()
        tenant_id = jwt_payload.get("tenant_id")
        user_id = get_jwt_identity()

        # Get current user
        user = db.session.query(User).filter_by(id=user_id).first()
        if not user:
            return jsonify({"error": "User not found"}), 404

        # Get course orders
        data = request.json
        if not data or "course_orders" not in data:
            return jsonify({"error": "course_orders is required"}), 400

        course_orders = data["course_orders"]
        if not isinstance(course_orders, dict):
            return jsonify({"error": "course_orders must be a dictionary"}), 400

        # Convert keys to integers
        try:
            course_orders = {int(k): v for k, v in course_orders.items()}
        except (ValueError, TypeError):
            return jsonify({"error": "Invalid course_orders format"}), 400

        # Reorder courses
        service = CourseService(db.session)
        courses = service.reorder_courses(tenant_id, program_id, course_orders, user)

        courses_data = [course_response_schema.dump(c.to_dict(include_related=True)) for c in courses]

        return jsonify({"courses": courses_data}), 200

    except BadRequestError as e:
        return jsonify({"error": str(e)}), 400
    except ForbiddenError as e:
        return jsonify({"error": str(e)}), 403
    except Exception as e:
        logger.error(f"Error reordering courses: {str(e)}")
        return jsonify({"error": "Failed to reorder courses"}), 500


@bp.route("/<int:course_id>/duplicate", methods=["POST"])
@jwt_required()
@require_tenant()
@check_role(["admin", "manager"])
def duplicate_course(program_id, course_id):
    """Duplicate a course."""
    try:
        jwt_payload = get_jwt()
        tenant_id = jwt_payload.get("tenant_id")
        user_id = get_jwt_identity()

        # Get current user
        user = db.session.query(User).filter_by(id=user_id).first()
        if not user:
            return jsonify({"error": "User not found"}), 404

        # Validate request data
        data = course_duplicate_schema.load(request.json or {})

        # Duplicate course
        service = CourseService(db.session)
        duplicate = service.duplicate_course(
            tenant_id=tenant_id,
            program_id=program_id,
            course_id=course_id,
            new_program_id=data.get("program_id"),
            new_title=data.get("title"),
            user=user,
        )

        return jsonify(course_response_schema.dump(duplicate.to_dict(include_related=True))), 201

    except ValidationError as e:
        return jsonify({"error": "Validation error", "details": e.messages}), 400
    except NotFoundError as e:
        return jsonify({"error": str(e)}), 404
    except ForbiddenError as e:
        return jsonify({"error": str(e)}), 403
    except Exception as e:
        logger.error(f"Error duplicating course: {str(e)}")
        return jsonify({"error": "Failed to duplicate course"}), 500


@bp.route("/<int:course_id>/sessions", methods=["POST"])
@jwt_required()
@require_tenant()
@check_role(["admin", "manager", "instructor"])
def add_course_session(program_id, course_id):
    """Add a session to a course."""
    try:
        jwt_payload = get_jwt()
        tenant_id = jwt_payload.get("tenant_id")
        user_id = get_jwt_identity()

        # Get current user
        user = db.session.query(User).filter_by(id=user_id).first()
        if not user:
            return jsonify({"error": "User not found"}), 404

        # Validate request data
        data = course_session_schema.load(request.json)

        # Get course
        service = CourseService(db.session)
        course = service.get_by_id(tenant_id, program_id, course_id, user)

        # Check permissions
        if user.role == "instructor":
            if course.instructor_id != user.id and course.program.coordinator_id != user.id:
                return jsonify({"error": "You can only add sessions to courses you teach or coordinate"}), 403

        # Add session
        session_data = {"created_by": user.id, **data}
        course.add_session(session_data)

        # Return the newly added session
        new_session = course.sessions[-1]
        return jsonify(new_session.to_dict()), 201

    except ValidationError as e:
        return jsonify({"error": "Validation error", "details": e.messages}), 400
    except NotFoundError as e:
        return jsonify({"error": str(e)}), 404
    except ForbiddenError as e:
        return jsonify({"error": str(e)}), 403
    except Exception as e:
        logger.error(f"Error adding session: {str(e)}")
        return jsonify({"error": "Failed to add session"}), 500


@bp.route("/statistics", methods=["GET"])
@jwt_required()
@require_tenant()
def get_course_statistics(program_id):
    """Get course statistics for a program."""
    try:
        jwt_payload = get_jwt()
        tenant_id = jwt_payload.get("tenant_id")
        user_id = get_jwt_identity()

        # Get current user
        user = db.session.query(User).filter_by(id=user_id).first()
        if not user:
            return jsonify({"error": "User not found"}), 404

        # Get statistics
        service = CourseService(db.session)
        stats = service.get_statistics(tenant_id, program_id, user)

        return jsonify(stats), 200

    except NotFoundError as e:
        return jsonify({"error": str(e)}), 404
    except Exception as e:
        logger.error(f"Error fetching statistics: {str(e)}")
        return jsonify({"error": "Failed to fetch statistics"}), 500


@bp.route("/<int:course_id>/sessions/<int:session_id>/calendar", methods=["GET"])
@jwt_required()
@require_tenant()
def download_session_calendar(program_id, course_id, session_id):
    """Download calendar file (.ics) for a specific session."""
    try:
        jwt_payload = get_jwt()
        tenant_id = jwt_payload.get("tenant_id")
        user_id = get_jwt_identity()

        # Get current user
        user = db.session.query(User).filter_by(id=user_id).first()
        if not user:
            return jsonify({"error": "User not found"}), 404

        # Get course
        service = CourseService(db.session)
        course = service.get_by_id(tenant_id, program_id, course_id, user)

        # Get session
        session = db.session.query(CourseSession).filter_by(
            id=session_id, 
            course_id=course_id,
            tenant_id=tenant_id,
            deleted_at=None
        ).first()
        
        if not session:
            return jsonify({"error": "Session not found"}), 404

        # Get timezone from request or use default
        timezone = request.args.get("timezone", "UTC")

        # Generate session data for ICS
        session_data = session.to_dict(include_related=True)
        
        # Add instructor name if available
        if session.instructor:
            session_data["instructor_name"] = session.instructor.full_name

        # Generate ICS content
        ics_content = generate_session_ics(
            session=session_data,
            course_title=course.title,
            timezone=timezone
        )

        # Create response with ICS file
        response = Response(
            ics_content,
            mimetype="text/calendar",
            headers={
                "Content-Disposition": f'attachment; filename="session_{session.uuid}.ics"',
                "Content-Type": "text/calendar; charset=utf-8"
            }
        )

        return response

    except NotFoundError as e:
        return jsonify({"error": str(e)}), 404
    except Exception as e:
        logger.error(f"Error generating calendar file: {str(e)}")
        return jsonify({"error": "Failed to generate calendar file"}), 500


@bp.route("/<int:course_id>/sessions", methods=["GET"])
@jwt_required()
@require_tenant()
def get_course_sessions(program_id, course_id):
    """Get all sessions for a course."""
    try:
        jwt_payload = get_jwt()
        tenant_id = jwt_payload.get("tenant_id")
        user_id = get_jwt_identity()

        # Get current user
        user = db.session.query(User).filter_by(id=user_id).first()
        if not user:
            return jsonify({"error": "User not found"}), 404

        # Get course
        service = CourseService(db.session)
        course = service.get_by_id(tenant_id, program_id, course_id, user)

        # Get query parameters
        include_past = request.args.get("include_past", "true").lower() == "true"
        include_cancelled = request.args.get("include_cancelled", "false").lower() == "true"

        # Query sessions
        sessions_query = db.session.query(CourseSession).filter_by(
            course_id=course_id,
            tenant_id=tenant_id,
            deleted_at=None
        )

        # Filter by date if needed
        if not include_past:
            from datetime import datetime
            sessions_query = sessions_query.filter(
                CourseSession.session_date >= datetime.utcnow()
            )

        # Filter cancelled sessions
        if not include_cancelled:
            sessions_query = sessions_query.filter(
                CourseSession.is_cancelled == False
            )

        # Order by date
        sessions = sessions_query.order_by(CourseSession.session_date).all()

        # Serialize sessions
        sessions_data = []
        for session in sessions:
            session_dict = session.to_dict(include_related=True)
            # Add calendar download URL
            session_dict["calendar_url"] = f"/api/v1/programs/{program_id}/courses/{course_id}/sessions/{session.id}/calendar"
            sessions_data.append(session_dict)

        return jsonify({
            "sessions": sessions_data,
            "course": {
                "id": course.id,
                "title": course.title,
                "code": course.code
            }
        }), 200

    except NotFoundError as e:
        return jsonify({"error": str(e)}), 404
    except Exception as e:
        logger.error(f"Error fetching sessions: {str(e)}")
        return jsonify({"error": "Failed to fetch sessions"}), 500
