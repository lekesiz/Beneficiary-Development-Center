"""
Development Reports API endpoints
"""

from flask import Blueprint, request, jsonify, send_file
from app.services.report_service import ReportService
from app.services.reports_overview_service import ReportsOverviewService
from app.services.student_profile_service import StudentProfileService
from flask_jwt_extended import jwt_required, get_jwt_identity
from app.models.user import User
from app.core.database import get_db
from app.core.exceptions import ValidationError
from app.extensions import db
import io
import json
from datetime import datetime

reports_bp = Blueprint("reports", __name__, url_prefix="/api/v1/reports")


@reports_bp.route("", methods=["GET"])
@jwt_required()
def list_reports():
    """List available reports."""
    from app.core.jwt_utils import get_current_user_id
    
    try:
        user_id = get_current_user_id()
        current_user = db.session.query(User).filter_by(id=user_id).first()
        
        if not current_user:
            return jsonify({"error": "User not found"}), 404
        
        # Return list of available report types
        available_reports = [
            {
                "id": "development",
                "name": "Development Report",
                "description": "Comprehensive report on user development progress",
                "endpoint": "/api/v1/reports/development/{user_id}",
                "formats": ["json", "pdf"]
            },
            {
                "id": "overview",
                "name": "Reports Overview",
                "description": "Overview of all available reports and statistics",
                "endpoint": "/api/v1/reports/overview",
                "formats": ["json"]
            },
            {
                "id": "student_profile",
                "name": "Student Profile Report",
                "description": "Detailed student profile information",
                "endpoint": "/api/v1/reports/student-profile/{user_id}",
                "formats": ["json", "pdf"]
            }
        ]
        
        return jsonify({
            "reports": available_reports,
            "total": len(available_reports)
        }), 200
        
    except Exception as e:
        return jsonify({"error": str(e)}), 500


@reports_bp.route("/development/<int:user_id>", methods=["GET"])
@jwt_required()
def get_development_report(user_id: int):
    """
    Generate a development report for a specific user.

    Query Parameters:
    - days: Number of days to include in the report (default: 30)
    """
    current_user_id = get_jwt_identity()
    db_session = get_db()
    
    try:
        current_user = db_session.query(User).filter_by(id=int(current_user_id)).first()
        if not current_user:
            return jsonify({"error": "User not found"}), 404

        # Get date range from query params
        date_range_days = request.args.get("days", 30, type=int)

        # Generate report
        report_service = ReportService(db_session=db_session)
        report = report_service.generate_development_report(
            user_id=user_id, tenant_id=current_user.tenant_id, requesting_user=current_user, date_range_days=date_range_days
        )

        return jsonify(report)
    
    finally:
        db_session.close()


@reports_bp.route("/development/batch", methods=["POST"])
@jwt_required()
def get_batch_development_reports():
    """
    Generate development reports for multiple users.

    Request Body:
    {
        "user_ids": [1, 2, 3],
        "days": 30
    }
    """
    current_user_id = get_jwt_identity()
    db_session = get_db()
    
    try:
        current_user = db_session.query(User).filter_by(id=int(current_user_id)).first()
        if not current_user:
            return jsonify({"error": "User not found"}), 404
        data = request.get_json()

        if not data or "user_ids" not in data:
            return jsonify({"error": "user_ids is required"}), 400

        user_ids = data["user_ids"]
        date_range_days = data.get("days", 30)

        # Generate batch reports
        report_service = ReportService(db_session=db_session)
        reports = report_service.get_batch_reports(
            user_ids=user_ids, tenant_id=current_user.tenant_id, requesting_user=current_user, date_range_days=date_range_days
        )

        return jsonify(
            {"reports": reports, "total": len(reports), "successful": len([r for r in reports if "error" not in r])}
        )
    
    finally:
        db_session.close()


@reports_bp.route("/development/<int:user_id>/download", methods=["GET"])
@jwt_required()
def download_development_report(user_id: int):
    """
    Download a development report as JSON file.

    Query Parameters:
    - days: Number of days to include in the report (default: 30)
    - format: File format (json or pdf) - currently only json is supported
    """
    current_user_id = get_jwt_identity()
    db_session = get_db()
    
    try:
        current_user = db_session.query(User).filter_by(id=int(current_user_id)).first()
        if not current_user:
            return jsonify({"error": "User not found"}), 404

        # Get parameters
        date_range_days = request.args.get("days", 30, type=int)
        file_format = request.args.get("format", "json")

        if file_format not in ["json"]:
            return jsonify({"error": "Only JSON format is currently supported"}), 400

        # Generate report
        report_service = ReportService(db_session=db_session)
        report = report_service.generate_development_report(
            user_id=user_id, tenant_id=current_user.tenant_id, requesting_user=current_user, date_range_days=date_range_days
        )

        # Create file
        if file_format == "json":
            # Convert to pretty JSON
            json_data = json.dumps(report, indent=2, ensure_ascii=False)
            file_data = io.BytesIO(json_data.encode("utf-8"))

            # Generate filename
            timestamp = datetime.utcnow().strftime("%Y%m%d_%H%M%S")
            filename = f"development_report_{user_id}_{timestamp}.json"

            return send_file(file_data, mimetype="application/json", as_attachment=True, download_name=filename)
    
    finally:
        db_session.close()


@reports_bp.route("/my-development", methods=["GET"])
@jwt_required()
def get_my_development_report():
    """
    Generate a development report for the current user.

    Query Parameters:
    - days: Number of days to include in the report (default: 30)
    """
    current_user_id = get_jwt_identity()
    db_session = get_db()
    
    try:
        current_user = db_session.query(User).filter_by(id=int(current_user_id)).first()
        if not current_user:
            return jsonify({"error": "User not found"}), 404

        # Get date range from query params
        date_range_days = request.args.get("days", 30, type=int)

        # Generate report for current user
        report_service = ReportService(db_session=db_session)
        report = report_service.generate_development_report(
            user_id=current_user.id, tenant_id=current_user.tenant_id, requesting_user=current_user, date_range_days=date_range_days
        )

        return jsonify(report)
    
    finally:
        db_session.close()


@reports_bp.route("/insights/summary", methods=["GET"])
@jwt_required()
def get_insights_summary():
    """
    Get a quick insights summary for the current user.
    This is a lighter version of the full development report.
    """
    current_user_id = get_jwt_identity()
    db_session = get_db()
    
    try:
        current_user = db_session.query(User).filter_by(id=int(current_user_id)).first()
        if not current_user:
            return jsonify({"error": "User not found"}), 404

        # Generate full report
        report_service = ReportService(db_session=db_session)
        report = report_service.generate_development_report(
            user_id=current_user.id,
            tenant_id=current_user.tenant_id,
            requesting_user=current_user,
            date_range_days=7,  # Last 7 days for quick summary
        )

        # Extract summary data
        summary = {
            "student_name": report.get("student_name"),
            "progress_summary": report.get("progress_summary"),
            "summary_score": report.get("summary_score"),
            "immediate_actions": report.get("recommendations", {}).get("immediate_actions", []),
            "performance_trend": report.get("visualization_data", {}).get("performance_trend", [])[-5:],
            "generated_at": report.get("metadata", {}).get("generated_at"),
        }

        return jsonify(summary)
    
    finally:
        db_session.close()


# Coach Dashboard Endpoints


@reports_bp.route("/overview", methods=["GET"])
@jwt_required()
def get_reports_overview():
    """
    Get overview of all students' development reports for coaches.

    Query Parameters:
    - page: Page number (default: 1)
    - per_page: Items per page (default: 20)
    - risk: Filter by risk level (Low/Medium/High)
    - min_performance: Minimum performance score
    - max_performance: Maximum performance score
    - program_id: Filter by program
    - course_id: Filter by course
    - search: Search by student name or email
    - sort_by: Sort field (risk_score/performance/name)
    - sort_desc: Sort descending (true/false)
    """
    current_user_id = get_jwt_identity()
    db_session = get_db()
    
    try:
        current_user = db_session.query(User).filter_by(id=int(current_user_id)).first()
        if not current_user:
            return jsonify({"error": "User not found"}), 404

        # Get filters from query params
        filters = {
            "page": request.args.get("page", 1, type=int),
            "per_page": request.args.get("per_page", 20, type=int),
            "risk": request.args.get("risk"),
            "min_performance": request.args.get("min_performance", type=float),
            "max_performance": request.args.get("max_performance", type=float),
            "program_id": request.args.get("program_id", type=int),
            "course_id": request.args.get("course_id", type=int),
            "search": request.args.get("search"),
            "sort_by": request.args.get("sort_by", "risk_score"),
            "sort_desc": request.args.get("sort_desc", "true"),
        }

        # Get overview
        reports_overview_service = ReportsOverviewService(db_session=db_session)
        overview = reports_overview_service.get_students_overview(
            tenant_id=current_user.tenant_id, requesting_user=current_user, filters=filters
        )

        return jsonify(overview)
    
    finally:
        db_session.close()


@reports_bp.route("/students/<int:student_id>/note", methods=["POST"])
@jwt_required()
def add_coach_note(student_id: int):
    """
    Add a coach note for a student.

    Request Body:
    {
        "note": "Coach's observation or recommendation"
    }
    """
    current_user_id = get_jwt_identity()
    db_session = get_db()
    
    try:
        current_user = db_session.query(User).filter_by(id=int(current_user_id)).first()
        if not current_user:
            return jsonify({"error": "User not found"}), 404
        data = request.get_json()

        if not data or "note" not in data:
            return jsonify({"error": "note is required"}), 400

        # Add note
        reports_overview_service = ReportsOverviewService(db_session=db_session)
        result = reports_overview_service.add_coach_note(
            student_id=student_id, tenant_id=current_user.tenant_id, requesting_user=current_user, note=data["note"]
        )

        return jsonify(result), 201
    
    finally:
        db_session.close()


@reports_bp.route("/export/batch", methods=["POST"])
@jwt_required()
def export_reports_batch():
    """
    Export multiple student reports.

    Request Body:
    {
        "student_ids": [1, 2, 3],
        "format": "json"  // or "pdf" (future)
    }
    """
    current_user_id = get_jwt_identity()
    db_session = get_db()
    
    try:
        current_user = db_session.query(User).filter_by(id=int(current_user_id)).first()
        if not current_user:
            return jsonify({"error": "User not found"}), 404
        data = request.get_json()

        if not data or "student_ids" not in data:
            return jsonify({"error": "student_ids is required"}), 400

        student_ids = data["student_ids"]
        export_format = data.get("format", "json")

        if export_format not in ["json"]:
            return jsonify({"error": "Only JSON format is currently supported"}), 400

        # Export reports
        reports_overview_service = ReportsOverviewService(db_session=db_session)
        export_data = reports_overview_service.export_reports_batch(
            student_ids=student_ids, tenant_id=current_user.tenant_id, requesting_user=current_user, format=export_format
        )

        # For JSON format, return as downloadable file
        if export_format == "json":
            json_data = json.dumps(export_data, indent=2, ensure_ascii=False)
            file_data = io.BytesIO(json_data.encode("utf-8"))

            timestamp = datetime.utcnow().strftime("%Y%m%d_%H%M%S")
            filename = f"student_reports_batch_{timestamp}.json"

            return send_file(file_data, mimetype="application/json", as_attachment=True, download_name=filename)

        return jsonify(export_data)
    
    finally:
        db_session.close()


# Student Profile Endpoints


@reports_bp.route("/profile/<int:student_id>", methods=["GET"])
@jwt_required()
def get_student_profile(student_id: int):
    """
    Get comprehensive student development profile.

    Returns detailed analysis including:
    - Student info
    - Development scores
    - Recent activities
    - AI analysis
    - Visualization data
    - Coach notes
    - Recommendations
    """
    current_user_id = get_jwt_identity()
    db_session = get_db()
    
    try:
        current_user = db_session.query(User).filter_by(id=int(current_user_id)).first()
        if not current_user:
            return jsonify({"error": "User not found"}), 404

        # Get student profile
        student_profile_service = StudentProfileService(db_session=db_session)
        profile = student_profile_service.get_student_profile(
            student_id=student_id, tenant_id=current_user.tenant_id, requesting_user=current_user
        )

        return jsonify(profile)
    
    finally:
        db_session.close()


@reports_bp.route("/profile/<int:student_id>/notes", methods=["POST"])
@jwt_required()
def add_profile_note(student_id: int):
    """
    Add a coach note to student profile.

    Request Body:
    {
        "note": "Coach observation or recommendation",
        "category": "general/academic/behavioral/other"
    }
    """
    current_user_id = get_jwt_identity()
    db_session = get_db()
    
    try:
        current_user = db_session.query(User).filter_by(id=int(current_user_id)).first()
        if not current_user:
            return jsonify({"error": "User not found"}), 404
        data = request.get_json()

        if not data or "note" not in data:
            return jsonify({"error": "note is required"}), 400

        # Add note
        student_profile_service = StudentProfileService(db_session=db_session)
        result = student_profile_service.add_coach_note(
            student_id=student_id,
            tenant_id=current_user.tenant_id,
            coach_id=current_user.id,
            note=data["note"],
            category=data.get("category", "general"),
        )

        return jsonify(result), 201
    
    finally:
        db_session.close()


@reports_bp.route("/profile/<int:student_id>/export", methods=["GET"])
@jwt_required()
def export_student_profile(student_id: int):
    """
    Export student profile as JSON or PDF.

    Query Parameters:
    - format: Export format (json/pdf) - currently only json is supported
    """
    current_user_id = get_jwt_identity()
    db_session = get_db()
    
    try:
        current_user = db_session.query(User).filter_by(id=int(current_user_id)).first()
        if not current_user:
            return jsonify({"error": "User not found"}), 404

        export_format = request.args.get("format", "json")

        if export_format not in ["json"]:
            return jsonify({"error": "Only JSON format is currently supported"}), 400

        # Get profile data
        student_profile_service = StudentProfileService(db_session=db_session)
        profile = student_profile_service.get_student_profile(
            student_id=student_id, tenant_id=current_user.tenant_id, requesting_user=current_user
        )

        # Create file
        if export_format == "json":
            # Convert to pretty JSON
            json_data = json.dumps(profile, indent=2, ensure_ascii=False)
            file_data = io.BytesIO(json_data.encode("utf-8"))

            # Generate filename
            timestamp = datetime.utcnow().strftime("%Y%m%d_%H%M%S")
            student_name = profile["student_info"]["name"].replace(" ", "_")
            filename = f"student_profile_{student_name}_{timestamp}.json"

            return send_file(file_data, mimetype="application/json", as_attachment=True, download_name=filename)
    
    finally:
        db_session.close()


@reports_bp.route("/profile/<int:student_id>/recommendations", methods=["GET"])
@jwt_required()
def get_profile_recommendations(student_id: int):
    """
    Get specific recommendations for next evaluation and learning activities.
    """
    current_user_id = get_jwt_identity()
    db_session = get_db()
    
    try:
        current_user = db_session.query(User).filter_by(id=int(current_user_id)).first()
        if not current_user:
            return jsonify({"error": "User not found"}), 404

        # Get profile to extract recommendations
        student_profile_service = StudentProfileService(db_session=db_session)
        profile = student_profile_service.get_student_profile(
            student_id=student_id, tenant_id=current_user.tenant_id, requesting_user=current_user
        )

        # Extract relevant recommendation data
        recommendations = {
            "next_evaluation": profile.get("next_recommendations", {}).get("next_evaluation"),
            "suggested_courses": profile.get("next_recommendations", {}).get("suggested_courses", []),
            "improvement_areas": profile.get("next_recommendations", {}).get("improvement_areas", []),
            "action_items": profile.get("next_recommendations", {}).get("action_items", []),
            "ai_recommendations": profile.get("ai_analysis", {}).get("recommendations", []),
            "intervention_suggestions": profile.get("ai_analysis", {}).get("intervention_suggestions", []),
        }

        return jsonify(recommendations)
    
    finally:
        db_session.close()
