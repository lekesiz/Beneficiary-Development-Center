"""API endpoints for Program management."""

from flask import Blueprint, request, jsonify
from flask_jwt_extended import jwt_required, get_jwt_identity, get_jwt
from marshmallow import Schema, fields, validate, ValidationError
from datetime import datetime
from app.services.program_service import ProgramService
from app.models.program import Program, ProgramStatus, ProgramType
from app.models.user import User
from app.core.decorators import require_tenant, check_role
from app.extensions import db
from app.core.logging import logger
from app.core.exceptions import NotFoundError, BadRequestError, ForbiddenError

bp = Blueprint("programs", __name__, url_prefix="/api/v1/programs")


class ProgramSchema(Schema):
    """Schema for program validation."""

    code = fields.String(required=False, validate=validate.Length(max=50))
    title = fields.String(required=True, validate=validate.Length(min=1, max=200))
    description = fields.String(required=False)
    objectives = fields.List(fields.String(), required=False)
    program_type = fields.String(required=False, validate=validate.OneOf([t.value for t in ProgramType]))
    status = fields.String(required=False, validate=validate.OneOf([s.value for s in ProgramStatus]))
    start_date = fields.Date(required=True)
    end_date = fields.Date(required=True)
    enrollment_start = fields.Date(required=False)
    enrollment_end = fields.Date(required=False)
    min_participants = fields.Integer(required=False, validate=validate.Range(min=1))
    max_participants = fields.Integer(required=False, validate=validate.Range(min=1))
    requirements = fields.Dict(required=False)
    location = fields.String(required=False, validate=validate.Length(max=200))
    is_online = fields.Boolean(required=False)
    is_hybrid = fields.Boolean(required=False)
    online_link = fields.String(required=False, validate=validate.Length(max=500))
    price = fields.Integer(required=False, validate=validate.Range(min=0))
    currency = fields.String(required=False, validate=validate.Length(equal=3))
    tags = fields.List(fields.String(), required=False)
    metadata = fields.Dict(required=False)
    cover_image_url = fields.String(required=False, validate=validate.Length(max=500))
    resources = fields.List(fields.Dict(), required=False)
    coordinator_id = fields.Integer(required=False)


class CourseAddSchema(Schema):
    """Schema for adding course to program."""

    title = fields.String(required=True, validate=validate.Length(min=1, max=200))
    subtitle = fields.String(required=False, validate=validate.Length(max=300))
    description = fields.String(required=False)
    format = fields.String(required=False)
    difficulty_level = fields.String(required=False)
    duration_hours = fields.Float(required=False, validate=validate.Range(min=0))
    objectives = fields.List(fields.String(), required=False)
    instructor_id = fields.Integer(required=False)


program_schema = ProgramSchema()
course_add_schema = CourseAddSchema()


@bp.route("", methods=["GET"])
@jwt_required()
@require_tenant()
def get_programs():
    """Get all programs for the tenant."""
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
        program_type = request.args.get("type")
        search = request.args.get("search")
        upcoming_only = request.args.get("upcoming_only", "false").lower() == "true"
        active_only = request.args.get("active_only", "false").lower() == "true"
        sort_by = request.args.get("sort_by", "created_at")
        sort_order = request.args.get("sort_order", "desc")

        # Convert string parameters to enums
        if status:
            try:
                status = ProgramStatus(status)
            except ValueError:
                return jsonify({"error": f"Invalid status: {status}"}), 400

        if program_type:
            try:
                program_type = ProgramType(program_type)
            except ValueError:
                return jsonify({"error": f"Invalid program type: {program_type}"}), 400

        # Get programs
        service = ProgramService(db.session)
        programs = service.get_all(
            tenant_id=tenant_id,
            user=user,
            skip=(page - 1) * per_page,
            limit=per_page,
            status=status,
            program_type=program_type,
            search=search,
            upcoming_only=upcoming_only,
            active_only=active_only,
            sort_by=sort_by,
            sort_order=sort_order,
        )

        # Get total count for pagination
        total_query = db.session.query(Program).filter(Program.tenant_id == tenant_id, Program.deleted_at.is_(None))

        if status:
            total_query = total_query.filter(Program.status == status)
        if program_type:
            total_query = total_query.filter(Program.program_type == program_type)

        total = total_query.count()

        return (
            jsonify(
                {
                    "programs": [p.to_dict(include_related=True) for p in programs],
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

    except Exception as e:
        logger.error(f"Error fetching programs: {str(e)}")
        return jsonify({"error": "Failed to fetch programs"}), 500


@bp.route("/<int:program_id>", methods=["GET"])
@jwt_required()
@require_tenant()
def get_program(program_id):
    """Get a specific program."""
    try:
        jwt_payload = get_jwt()
        tenant_id = jwt_payload.get("tenant_id")
        user_id = get_jwt_identity()

        # Get current user
        user = db.session.query(User).filter_by(id=user_id).first()
        if not user:
            return jsonify({"error": "User not found"}), 404

        # Get program
        service = ProgramService(db.session)
        program = service.get_by_id(tenant_id, program_id, user)

        # Include courses if requested
        include_courses = request.args.get("include_courses", "false").lower() == "true"
        data = program.to_dict(include_related=True)

        if include_courses:
            data["courses"] = [c.to_dict() for c in program.courses if not c.deleted_at]

        return jsonify(data), 200

    except NotFoundError as e:
        return jsonify({"error": str(e)}), 404
    except Exception as e:
        logger.error(f"Error fetching program: {str(e)}")
        return jsonify({"error": "Failed to fetch program"}), 500


@bp.route("", methods=["POST"])
@jwt_required()
@require_tenant()
@check_role(["admin", "manager"])
def create_program():
    """Create a new program."""
    try:
        jwt_payload = get_jwt()
        tenant_id = jwt_payload.get("tenant_id")
        user_id = get_jwt_identity()

        # Get current user
        user = db.session.query(User).filter_by(id=user_id).first()
        if not user:
            return jsonify({"error": "User not found"}), 404

        # Validate request data
        data = program_schema.load(request.json)

        # Create program
        service = ProgramService(db.session)
        program = service.create(tenant_id, data, user)

        return jsonify(program.to_dict(include_related=True)), 201

    except ValidationError as e:
        return jsonify({"error": "Validation error", "details": e.messages}), 400
    except BadRequestError as e:
        return jsonify({"error": str(e)}), 400
    except ForbiddenError as e:
        return jsonify({"error": str(e)}), 403
    except Exception as e:
        logger.error(f"Error creating program: {str(e)}")
        return jsonify({"error": "Failed to create program"}), 500


@bp.route("/<int:program_id>", methods=["PUT"])
@jwt_required()
@require_tenant()
@check_role(["admin", "manager"])
def update_program(program_id):
    """Update a program."""
    try:
        jwt_payload = get_jwt()
        tenant_id = jwt_payload.get("tenant_id")
        user_id = get_jwt_identity()

        # Get current user
        user = db.session.query(User).filter_by(id=user_id).first()
        if not user:
            return jsonify({"error": "User not found"}), 404

        # Validate request data
        data = program_schema.load(request.json, partial=True)

        # Update program
        service = ProgramService(db.session)
        program = service.update(tenant_id, program_id, data, user)

        return jsonify(program.to_dict(include_related=True)), 200

    except ValidationError as e:
        return jsonify({"error": "Validation error", "details": e.messages}), 400
    except NotFoundError as e:
        return jsonify({"error": str(e)}), 404
    except BadRequestError as e:
        return jsonify({"error": str(e)}), 400
    except ForbiddenError as e:
        return jsonify({"error": str(e)}), 403
    except Exception as e:
        logger.error(f"Error updating program: {str(e)}")
        return jsonify({"error": "Failed to update program"}), 500


@bp.route("/<int:program_id>", methods=["DELETE"])
@jwt_required()
@require_tenant()
@check_role(["admin"])
def delete_program(program_id):
    """Delete a program."""
    try:
        jwt_payload = get_jwt()
        tenant_id = jwt_payload.get("tenant_id")
        user_id = get_jwt_identity()

        # Get current user
        user = db.session.query(User).filter_by(id=user_id).first()
        if not user:
            return jsonify({"error": "User not found"}), 404

        # Delete program
        service = ProgramService(db.session)
        service.delete(tenant_id, program_id, user)

        return "", 204

    except NotFoundError as e:
        return jsonify({"error": str(e)}), 404
    except BadRequestError as e:
        return jsonify({"error": str(e)}), 400
    except ForbiddenError as e:
        return jsonify({"error": str(e)}), 403
    except Exception as e:
        logger.error(f"Error deleting program: {str(e)}")
        return jsonify({"error": "Failed to delete program"}), 500


@bp.route("/<int:program_id>/status", methods=["PUT"])
@jwt_required()
@require_tenant()
@check_role(["admin", "manager"])
def update_program_status(program_id):
    """Update program status."""
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
            new_status = ProgramStatus(data["status"])
        except ValueError:
            return jsonify({"error": f'Invalid status: {data["status"]}'}), 400

        # Update status
        service = ProgramService(db.session)
        program = service.update_status(tenant_id, program_id, new_status, user)

        return jsonify(program.to_dict(include_related=True)), 200

    except NotFoundError as e:
        return jsonify({"error": str(e)}), 404
    except BadRequestError as e:
        return jsonify({"error": str(e)}), 400
    except ForbiddenError as e:
        return jsonify({"error": str(e)}), 403
    except Exception as e:
        logger.error(f"Error updating program status: {str(e)}")
        return jsonify({"error": "Failed to update program status"}), 500


@bp.route("/<int:program_id>/courses", methods=["POST"])
@jwt_required()
@require_tenant()
@check_role(["admin", "manager"])
def add_course_to_program(program_id):
    """Add a course to a program."""
    try:
        jwt_payload = get_jwt()
        tenant_id = jwt_payload.get("tenant_id")
        user_id = get_jwt_identity()

        # Get current user
        user = db.session.query(User).filter_by(id=user_id).first()
        if not user:
            return jsonify({"error": "User not found"}), 404

        # Validate request data
        data = course_add_schema.load(request.json)

        # Add course
        service = ProgramService(db.session)
        program = service.add_course(tenant_id, program_id, data, user)

        # Return the newly added course
        new_course = program.courses[-1]
        return jsonify(new_course.to_dict(include_related=True)), 201

    except ValidationError as e:
        return jsonify({"error": "Validation error", "details": e.messages}), 400
    except NotFoundError as e:
        return jsonify({"error": str(e)}), 404
    except ForbiddenError as e:
        return jsonify({"error": str(e)}), 403
    except Exception as e:
        logger.error(f"Error adding course: {str(e)}")
        return jsonify({"error": "Failed to add course"}), 500


@bp.route("/statistics", methods=["GET"])
@jwt_required()
@require_tenant()
@check_role(["admin", "manager"])
def get_program_statistics():
    """Get program statistics."""
    try:
        jwt_payload = get_jwt()
        tenant_id = jwt_payload.get("tenant_id")
        user_id = get_jwt_identity()

        # Get current user
        user = db.session.query(User).filter_by(id=user_id).first()
        if not user:
            return jsonify({"error": "User not found"}), 404

        # Get statistics
        service = ProgramService(db.session)
        stats = service.get_statistics(tenant_id, user)

        return jsonify(stats), 200

    except ForbiddenError as e:
        return jsonify({"error": str(e)}), 403
    except Exception as e:
        logger.error(f"Error fetching statistics: {str(e)}")
        return jsonify({"error": "Failed to fetch statistics"}), 500


# Register the courses blueprint
from app.api.v1 import courses

bp.register_blueprint(courses.bp)
