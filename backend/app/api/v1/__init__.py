"""API v1 blueprint initialization."""
from flask import Blueprint

# Create main API v1 blueprint
api_v1_bp = Blueprint('api_v1', __name__)

# Import and register sub-blueprints
from app.api.v1 import auth, beneficiaries, programs, courses, evaluations, learning_paths, reports, dashboard

api_v1_bp.register_blueprint(auth.bp, url_prefix='/auth')
api_v1_bp.register_blueprint(beneficiaries.bp, url_prefix='/beneficiaries')
api_v1_bp.register_blueprint(programs.bp, url_prefix='/programs')
api_v1_bp.register_blueprint(courses.bp, url_prefix='/courses')
api_v1_bp.register_blueprint(evaluations.evaluations_bp)
api_v1_bp.register_blueprint(learning_paths.learning_paths_bp)
api_v1_bp.register_blueprint(reports.reports_bp)
api_v1_bp.register_blueprint(dashboard.dashboard_bp)

# API metadata
API_VERSION = '1.0.0'
API_DESCRIPTION = 'BDC REST API v1'

@api_v1_bp.route('/')
def api_info():
    """Get API information."""
    return {
        'version': API_VERSION,
        'description': API_DESCRIPTION,
        'endpoints': {
            'auth': '/api/v1/auth',
            'users': '/api/v1/users',
            'beneficiaries': '/api/v1/beneficiaries',
            'programs': '/api/v1/programs',
            'evaluations': '/api/v1/evaluations',
            'ai': '/api/v1/ai'
        }
    }