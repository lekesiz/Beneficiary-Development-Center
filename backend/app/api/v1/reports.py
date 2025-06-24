"""
Development Reports API endpoints
"""
from flask import Blueprint, request, jsonify, send_file
from app.services.report_service import report_service
from app.services.reports_overview_service import reports_overview_service
from app.services.student_profile_service import student_profile_service
from app.core.auth import require_auth, get_current_user
from app.core.database import get_db
from app.core.exceptions import ValidationError
import io
import json
from datetime import datetime

reports_bp = Blueprint('reports', __name__, url_prefix='/api/reports')


@reports_bp.route('/development/<int:user_id>', methods=['GET'])
@require_auth
def get_development_report(user_id: int):
    """
    Generate a development report for a specific user.
    
    Query Parameters:
    - days: Number of days to include in the report (default: 30)
    """
    user = get_current_user()
    db = get_db()
    
    # Get date range from query params
    date_range_days = request.args.get('days', 30, type=int)
    
    # Generate report
    report = report_service.generate_development_report(
        user_id=user_id,
        tenant_id=user.tenant_id,
        requesting_user=user,
        date_range_days=date_range_days
    )
    
    return jsonify(report)


@reports_bp.route('/development/batch', methods=['POST'])
@require_auth
def get_batch_development_reports():
    """
    Generate development reports for multiple users.
    
    Request Body:
    {
        "user_ids": [1, 2, 3],
        "days": 30
    }
    """
    user = get_current_user()
    db = get_db()
    data = request.get_json()
    
    if not data or 'user_ids' not in data:
        raise ValidationError("user_ids is required")
    
    user_ids = data['user_ids']
    date_range_days = data.get('days', 30)
    
    # Generate batch reports
    reports = report_service.get_batch_reports(
        user_ids=user_ids,
        tenant_id=user.tenant_id,
        requesting_user=user,
        date_range_days=date_range_days
    )
    
    return jsonify({
        'reports': reports,
        'total': len(reports),
        'successful': len([r for r in reports if 'error' not in r])
    })


@reports_bp.route('/development/<int:user_id>/download', methods=['GET'])
@require_auth
def download_development_report(user_id: int):
    """
    Download a development report as JSON file.
    
    Query Parameters:
    - days: Number of days to include in the report (default: 30)
    - format: File format (json or pdf) - currently only json is supported
    """
    user = get_current_user()
    db = get_db()
    
    # Get parameters
    date_range_days = request.args.get('days', 30, type=int)
    file_format = request.args.get('format', 'json')
    
    if file_format not in ['json']:
        raise ValidationError("Only JSON format is currently supported")
    
    # Generate report
    report = report_service.generate_development_report(
        user_id=user_id,
        tenant_id=user.tenant_id,
        requesting_user=user,
        date_range_days=date_range_days
    )
    
    # Create file
    if file_format == 'json':
        # Convert to pretty JSON
        json_data = json.dumps(report, indent=2, ensure_ascii=False)
        file_data = io.BytesIO(json_data.encode('utf-8'))
        
        # Generate filename
        timestamp = datetime.utcnow().strftime('%Y%m%d_%H%M%S')
        filename = f"development_report_{user_id}_{timestamp}.json"
        
        return send_file(
            file_data,
            mimetype='application/json',
            as_attachment=True,
            download_name=filename
        )


@reports_bp.route('/my-development', methods=['GET'])
@require_auth
def get_my_development_report():
    """
    Generate a development report for the current user.
    
    Query Parameters:
    - days: Number of days to include in the report (default: 30)
    """
    user = get_current_user()
    db = get_db()
    
    # Get date range from query params
    date_range_days = request.args.get('days', 30, type=int)
    
    # Generate report for current user
    report = report_service.generate_development_report(
        user_id=user.id,
        tenant_id=user.tenant_id,
        requesting_user=user,
        date_range_days=date_range_days
    )
    
    return jsonify(report)


@reports_bp.route('/insights/summary', methods=['GET'])
@require_auth
def get_insights_summary():
    """
    Get a quick insights summary for the current user.
    This is a lighter version of the full development report.
    """
    user = get_current_user()
    db = get_db()
    
    # Generate full report
    report = report_service.generate_development_report(
        user_id=user.id,
        tenant_id=user.tenant_id,
        requesting_user=user,
        date_range_days=7  # Last 7 days for quick summary
    )
    
    # Extract summary data
    summary = {
        'student_name': report.get('student_name'),
        'progress_summary': report.get('progress_summary'),
        'summary_score': report.get('summary_score'),
        'immediate_actions': report.get('recommendations', {}).get('immediate_actions', []),
        'performance_trend': report.get('visualization_data', {}).get('performance_trend', [])[-5:],
        'generated_at': report.get('metadata', {}).get('generated_at')
    }
    
    return jsonify(summary)


# Coach Dashboard Endpoints

@reports_bp.route('/overview', methods=['GET'])
@require_auth
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
    user = get_current_user()
    db = get_db()
    
    # Get filters from query params
    filters = {
        'page': request.args.get('page', 1, type=int),
        'per_page': request.args.get('per_page', 20, type=int),
        'risk': request.args.get('risk'),
        'min_performance': request.args.get('min_performance', type=float),
        'max_performance': request.args.get('max_performance', type=float),
        'program_id': request.args.get('program_id', type=int),
        'course_id': request.args.get('course_id', type=int),
        'search': request.args.get('search'),
        'sort_by': request.args.get('sort_by', 'risk_score'),
        'sort_desc': request.args.get('sort_desc', 'true')
    }
    
    # Get overview
    overview = reports_overview_service.get_students_overview(
        tenant_id=user.tenant_id,
        requesting_user=user,
        filters=filters
    )
    
    return jsonify(overview)


@reports_bp.route('/students/<int:student_id>/note', methods=['POST'])
@require_auth
def add_coach_note(student_id: int):
    """
    Add a coach note for a student.
    
    Request Body:
    {
        "note": "Coach's observation or recommendation"
    }
    """
    user = get_current_user()
    db = get_db()
    data = request.get_json()
    
    if not data or 'note' not in data:
        raise ValidationError("note is required")
    
    # Add note
    result = reports_overview_service.add_coach_note(
        student_id=student_id,
        tenant_id=user.tenant_id,
        requesting_user=user,
        note=data['note']
    )
    
    return jsonify(result), 201


@reports_bp.route('/export/batch', methods=['POST'])
@require_auth
def export_reports_batch():
    """
    Export multiple student reports.
    
    Request Body:
    {
        "student_ids": [1, 2, 3],
        "format": "json"  // or "pdf" (future)
    }
    """
    user = get_current_user()
    db = get_db()
    data = request.get_json()
    
    if not data or 'student_ids' not in data:
        raise ValidationError("student_ids is required")
    
    student_ids = data['student_ids']
    export_format = data.get('format', 'json')
    
    if export_format not in ['json']:
        raise ValidationError("Only JSON format is currently supported")
    
    # Export reports
    export_data = reports_overview_service.export_reports_batch(
        student_ids=student_ids,
        tenant_id=user.tenant_id,
        requesting_user=user,
        format=export_format
    )
    
    # For JSON format, return as downloadable file
    if export_format == 'json':
        json_data = json.dumps(export_data, indent=2, ensure_ascii=False)
        file_data = io.BytesIO(json_data.encode('utf-8'))
        
        timestamp = datetime.utcnow().strftime('%Y%m%d_%H%M%S')
        filename = f"student_reports_batch_{timestamp}.json"
        
        return send_file(
            file_data,
            mimetype='application/json',
            as_attachment=True,
            download_name=filename
        )
    
    return jsonify(export_data)


# Student Profile Endpoints

@reports_bp.route('/profile/<int:student_id>', methods=['GET'])
@require_auth
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
    user = get_current_user()
    db = get_db()
    
    # Get student profile
    profile = student_profile_service.get_student_profile(
        student_id=student_id,
        tenant_id=user.tenant_id,
        requesting_user=user
    )
    
    return jsonify(profile)


@reports_bp.route('/profile/<int:student_id>/notes', methods=['POST'])
@require_auth
def add_profile_note(student_id: int):
    """
    Add a coach note to student profile.
    
    Request Body:
    {
        "note": "Coach observation or recommendation",
        "category": "general/academic/behavioral/other"
    }
    """
    user = get_current_user()
    db = get_db()
    data = request.get_json()
    
    if not data or 'note' not in data:
        raise ValidationError("note is required")
    
    # Add note
    result = student_profile_service.add_coach_note(
        student_id=student_id,
        tenant_id=user.tenant_id,
        coach_id=user.id,
        note=data['note'],
        category=data.get('category', 'general')
    )
    
    return jsonify(result), 201


@reports_bp.route('/profile/<int:student_id>/export', methods=['GET'])
@require_auth
def export_student_profile(student_id: int):
    """
    Export student profile as JSON or PDF.
    
    Query Parameters:
    - format: Export format (json/pdf) - currently only json is supported
    """
    user = get_current_user()
    db = get_db()
    
    export_format = request.args.get('format', 'json')
    
    if export_format not in ['json']:
        raise ValidationError("Only JSON format is currently supported")
    
    # Get profile data
    profile = student_profile_service.get_student_profile(
        student_id=student_id,
        tenant_id=user.tenant_id,
        requesting_user=user
    )
    
    # Create file
    if export_format == 'json':
        # Convert to pretty JSON
        json_data = json.dumps(profile, indent=2, ensure_ascii=False)
        file_data = io.BytesIO(json_data.encode('utf-8'))
        
        # Generate filename
        timestamp = datetime.utcnow().strftime('%Y%m%d_%H%M%S')
        student_name = profile['student_info']['name'].replace(' ', '_')
        filename = f"student_profile_{student_name}_{timestamp}.json"
        
        return send_file(
            file_data,
            mimetype='application/json',
            as_attachment=True,
            download_name=filename
        )


@reports_bp.route('/profile/<int:student_id>/recommendations', methods=['GET'])
@require_auth
def get_profile_recommendations(student_id: int):
    """
    Get specific recommendations for next evaluation and learning activities.
    """
    user = get_current_user()
    db = get_db()
    
    # Get profile to extract recommendations
    profile = student_profile_service.get_student_profile(
        student_id=student_id,
        tenant_id=user.tenant_id,
        requesting_user=user
    )
    
    # Extract relevant recommendation data
    recommendations = {
        'next_evaluation': profile.get('next_recommendations', {}).get('next_evaluation'),
        'suggested_courses': profile.get('next_recommendations', {}).get('suggested_courses', []),
        'improvement_areas': profile.get('next_recommendations', {}).get('improvement_areas', []),
        'action_items': profile.get('next_recommendations', {}).get('action_items', []),
        'ai_recommendations': profile.get('ai_analysis', {}).get('recommendations', []),
        'intervention_suggestions': profile.get('ai_analysis', {}).get('intervention_suggestions', [])
    }
    
    return jsonify(recommendations)