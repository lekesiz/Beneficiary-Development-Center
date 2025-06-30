"""Flask application factory."""

import os
import logging
from logging.handlers import RotatingFileHandler
from flask import Flask, g
from app.extensions import db, migrate, jwt, cors, cache, socketio, mail, limiter
from app.core.socketio import init_socketio as setup_socketio
from app.core.security import init_security_middleware
from app.core.monitoring import init_monitoring
from app.core.logging_config import security_logger, performance_logger, business_logger
import sentry_sdk
from sentry_sdk.integrations.flask import FlaskIntegration
from config.config import get_config


def create_app(config_name=None):
    """Create Flask application."""
    app = Flask(__name__)

    # Load configuration
    config = get_config(config_name)
    app.config.from_object(config)
    
    # Load secrets from Google Secret Manager in production
    if config_name == 'production' and not app.config.get('TESTING'):
        try:
            from app.core.secrets_manager import init_app_secrets
            init_app_secrets(app)
        except Exception as e:
            app.logger.warning(f"Failed to initialize secrets: {str(e)}")

    # Initialize Sentry for error tracking
    if app.config.get("SENTRY_DSN"):
        sentry_sdk.init(
            dsn=app.config["SENTRY_DSN"],
            integrations=[FlaskIntegration()],
            traces_sample_rate=1.0,
            profiles_sample_rate=1.0,
        )

    # Initialize extensions
    db.init_app(app)
    migrate.init_app(app, db)

    # Setup structured logging
    from app.core.logging_config import setup_logging as setup_structured_logging
    setup_structured_logging(app)
    jwt.init_app(app)
    cors.init_app(
        app,
        origins=app.config["CORS_ORIGINS"],
        supports_credentials=True,
        allow_headers=["Content-Type", "Authorization", "X-Tenant-ID"],
        methods=["GET", "POST", "PUT", "DELETE", "OPTIONS"],
        expose_headers=["X-Total-Count", "X-Page-Count"]
    )
    cache.init_app(app)
    
    # Configure rate limiter with custom settings
    from app.core.rate_limiting import get_rate_limit_key, configure_endpoint_limits
    app.config['RATELIMIT_KEY_FUNC'] = get_rate_limit_key
    app.config['RATELIMIT_DEFAULT'] = "1000 per hour"
    app.config['RATELIMIT_STORAGE_URL'] = app.config.get('RATELIMIT_STORAGE_URL', 'memory://')
    app.config['RATELIMIT_STRATEGY'] = 'fixed-window'
    app.config['RATELIMIT_HEADERS_ENABLED'] = True
    app.config['RATELIMIT_SWALLOW_ERRORS'] = True
    limiter.init_app(app)
    # TODO: Fix endpoint limits configuration for flask-limiter 3.x
    # configure_endpoint_limits(limiter)
    
    # Initialize Socket.IO with custom handlers
    setup_socketio(app)
    mail.init_app(app)

    # Initialize security middleware
    init_security_middleware(app)
    
    # Initialize Google App Engine handlers if running on GAE
    if os.environ.get('GAE_ENV'):
        from app.core.gae_handlers import init_gae_handlers
        init_gae_handlers(app)
    
    # Initialize JWT debug middleware (only in development)
    if app.config.get("DEBUG"):
        from app.core.jwt_debug import init_jwt_debug_middleware
        init_jwt_debug_middleware(app)

    # Initialize monitoring and health checks
    init_monitoring(app)

    # Register blueprints
    register_blueprints(app)

    # Register error handlers
    register_error_handlers(app)

    # Register JWT callbacks
    register_jwt_callbacks(jwt)

    # Register before/after request handlers
    register_request_handlers(app)

    # Register CLI commands
    register_cli_commands(app)

    # Create upload folder
    os.makedirs(app.config["UPLOAD_FOLDER"], exist_ok=True)
    
    # Import all models to ensure they are registered with SQLAlchemy
    # This is important for migrations to detect all models
    with app.app_context():
        from app import models

    return app


def register_blueprints(app):
    """Register Flask blueprints."""
    from app.api.v1 import api_v1_bp
    from app.api.v1.auth import auth_bp
    from app.api.v1.users import users_bp
    from app.api.v1.beneficiaries import bp as beneficiaries_bp

    # Import enhanced blueprints (replacing old ones)
    # from app.api.v1.enhanced_programs import bp as programs_bp
    # from app.api.v1.enhanced_courses import bp as courses_bp
    # from app.api.v1.enhanced_evaluations import bp as evaluations_bp

    # Old blueprints (commented out - now using enhanced versions)
    from app.api.v1.programs import bp as programs_bp
    from app.api.v1.courses import bp as courses_bp
    from app.api.v1.evaluations import evaluations_bp

    from app.api.v1.ai import ai_bp
    from app.api.v1.dashboard import dashboard_bp
    from app.api.v1.reports import reports_bp
    from app.api.v1.coach_notes import coach_notes_bp
    from app.api.v1.analytics import analytics_bp
    from app.api.v1.notifications import notifications_bp
    from app.api.health import health_bp
    
    # Bilan de Compétence API blueprints
    from app.api.v1.assessments import bp as assessments_bp
    from app.api.v1.career import bp as career_bp
    from app.api.v1.compliance import bp as compliance_bp
    from app.api.v1.learning_advanced import bp as learning_advanced_bp
    from app.api.v1.bilan_dashboard import bp as bilan_dashboard_bp

    # Register health check endpoints (no prefix for easier access)
    app.register_blueprint(health_bp)

    # Register API v1 blueprints
    app.register_blueprint(api_v1_bp, url_prefix="/api/v1")
    app.register_blueprint(auth_bp, url_prefix="/api/v1/auth")
    app.register_blueprint(users_bp, url_prefix="/api/v1/users")
    app.register_blueprint(beneficiaries_bp, url_prefix="/api/v1/beneficiaries")

    # Enhanced blueprints with proper URL prefixes
    app.register_blueprint(programs_bp, url_prefix="/api/v1/programs")
    # Register courses under programs route (RESTful nested resource)
    app.register_blueprint(courses_bp, url_prefix="/api/v1/programs/<int:program_id>/courses")
    # Also register the courses adapter for backward compatibility
    # TODO: Remove this once all tests and frontend are updated
    from app.api.v1.courses_adapter import bp as courses_adapter_bp

    app.register_blueprint(courses_adapter_bp, url_prefix="/api/v1/courses")
    app.register_blueprint(evaluations_bp, url_prefix="/api/v1/evaluations")

    app.register_blueprint(ai_bp, url_prefix="/api/v1/ai")
    
    # Register additional API blueprints
    app.register_blueprint(dashboard_bp)  # Uses its own prefix /api/dashboard
    app.register_blueprint(reports_bp)    # Uses its own prefix /api/reports
    app.register_blueprint(coach_notes_bp)  # Uses its own prefix /api/coach-notes
    app.register_blueprint(analytics_bp)    # Uses its own prefix /api/analytics
    app.register_blueprint(notifications_bp)  # Uses its own prefix /api/notifications
    
    # Register Bilan de Compétence API blueprints
    app.register_blueprint(assessments_bp)    # /api/v1/assessments
    app.register_blueprint(career_bp)         # /api/v1/career
    app.register_blueprint(compliance_bp)     # /api/v1/compliance
    app.register_blueprint(learning_advanced_bp)  # /api/v1/learning
    app.register_blueprint(bilan_dashboard_bp)    # /api/v1/bilan

    # Initialize Swagger documentation
    from app.core.swagger import init_swagger

    init_swagger(app)


def register_error_handlers(app):
    """Register error handlers."""
    # Use the new comprehensive error handling system
    from app.core.error_handlers import register_error_handlers as register_enhanced_error_handlers

    # Register all enhanced error handlers
    register_enhanced_error_handlers(app)

    # Keep the old error handlers commented for reference
    # from app.core.exceptions import APIException, ValidationError

    # @app.errorhandler(APIException)
    # def handle_api_exception(error):
    #     """Handle API exceptions."""
    #     return error.to_dict(), error.status_code

    # @app.errorhandler(ValidationError)
    # def handle_validation_error(error):
    #     """Handle validation errors."""
    #     return {"message": str(error), "errors": error.errors}, 400

    # @app.errorhandler(404)
    # def handle_not_found(error):
    #     """Handle 404 errors."""
    #     return {"message": "Resource not found"}, 404

    # @app.errorhandler(500)
    # def handle_internal_error(error):
    #     """Handle 500 errors."""
    #     db.session.rollback()
    #     return {"message": "Internal server error"}, 500


def register_jwt_callbacks(jwt_manager):
    """Register JWT callbacks."""
    from app.models.user import User
    from app.core.jwt_error_handler import register_jwt_error_handlers

    # Register detailed error handlers
    register_jwt_error_handlers(jwt_manager)

    @jwt_manager.user_lookup_loader
    def user_lookup_callback(_jwt_header, jwt_data):
        """Load user from JWT."""
        identity = jwt_data["sub"]
        # Convert string identity back to integer
        try:
            user_id = int(identity)
        except (ValueError, TypeError):
            return None
        return db.session.query(User).filter_by(id=user_id).first()

    @jwt_manager.token_in_blocklist_loader
    def check_if_token_revoked(jwt_header, jwt_payload):
        """Check if token is blacklisted."""
        try:
            jti = jwt_payload["jti"]
            token_in_redis = cache.get(f"blacklist_{jti}")
            return token_in_redis is not None
        except Exception as e:
            # If Redis is not available, tokens are not blacklisted
            import logging
            logging.warning(f"JWT blocklist check failed: {str(e)}")
            return False


def register_request_handlers(app):
    """Register before/after request handlers."""

    @app.before_request
    def before_request():
        """Before request handler."""
        # Set tenant ID from header
        from flask import request

        tenant_header = app.config.get("TENANT_HEADER", "X-Tenant-ID")
        tenant_id = request.headers.get(tenant_header)

        if tenant_id:
            g.tenant_id = int(tenant_id)
        else:
            g.tenant_id = app.config.get("DEFAULT_TENANT_ID", 1)

    @app.after_request
    def after_request(response):
        """After request handler."""
        # Add security headers
        response.headers["X-Content-Type-Options"] = "nosniff"
        response.headers["X-Frame-Options"] = "DENY"
        response.headers["X-XSS-Protection"] = "1; mode=block"
        response.headers["Strict-Transport-Security"] = "max-age=31536000; includeSubDomains"
        return response


def register_cli_commands(app):
    """Register CLI commands."""

    @app.cli.command()
    def init_db():
        """Initialize the database."""
        db.create_all()
        print("Database initialized!")

    @app.cli.command()
    def seed_db():
        """Seed the database with initial data."""
        from app.utils.seed import seed_database

        seed_database()
        print("Database seeded!")

    @app.cli.command()
    def create_admin():
        """Create admin user."""
        from app.services.user_service import UserService

        email = input("Enter admin email: ")
        password = input("Enter admin password: ")

        user_data = {
            "email": email,
            "password": password,
            "first_name": "Admin",
            "last_name": "User",
            "role": "super_admin",
            "tenant_id": 1,
        }

        user = UserService.create_user(user_data)
        print(f"Admin user created: {user.email}")


# The setup_logging function has been moved to app.core.logging_config
# and is now called setup_structured_logging
