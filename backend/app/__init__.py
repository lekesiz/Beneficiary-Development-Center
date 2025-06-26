"""Flask application factory."""

import os
import logging
from logging.handlers import RotatingFileHandler
from flask import Flask, g
from app.extensions import db, migrate, jwt, cors, cache, limiter, socketio, mail
from app.core.socketio import init_socketio as setup_socketio
import sentry_sdk
from sentry_sdk.integrations.flask import FlaskIntegration
from config.config import get_config


def create_app(config_name=None):
    """Create Flask application."""
    app = Flask(__name__)

    # Load configuration
    config = get_config(config_name)
    app.config.from_object(config)

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
    from app.core.logging import setup_logging

    setup_logging(app)
    jwt.init_app(app)
    cors.init_app(app, origins=app.config["CORS_ORIGINS"])
    cache.init_app(app)
    limiter.init_app(app)
    # Initialize Socket.IO with custom handlers
    setup_socketio(app)
    mail.init_app(app)

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
    from app.api.health import health_bp

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

    @jwt_manager.user_lookup_loader
    def user_lookup_callback(_jwt_header, jwt_data):
        """Load user from JWT."""
        identity = jwt_data["sub"]
        return db.session.query(User).filter_by(id=identity).first()

    @jwt_manager.expired_token_loader
    def expired_token_callback(jwt_header, jwt_payload):
        """Handle expired token."""
        return {"message": "Token has expired"}, 401

    @jwt_manager.invalid_token_loader
    def invalid_token_callback(error):
        """Handle invalid token."""
        return {"message": "Invalid token"}, 401

    @jwt_manager.unauthorized_loader
    def missing_token_callback(error):
        """Handle missing token."""
        return {"message": "Authorization required"}, 401


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


def setup_logging(app):
    """Setup application logging."""
    if not app.debug and not app.testing:
        # Create logs directory
        if not os.path.exists("logs"):
            os.mkdir("logs")

        # Setup file handler
        file_handler = RotatingFileHandler(f"logs/{app.config['LOG_FILE']}", maxBytes=10240000, backupCount=10)  # 10MB

        # Setup formatter
        formatter = logging.Formatter("%(asctime)s %(levelname)s: %(message)s " "[in %(pathname)s:%(lineno)d]")
        file_handler.setFormatter(formatter)

        # Set log level
        log_level = getattr(logging, app.config["LOG_LEVEL"].upper())
        file_handler.setLevel(log_level)
        app.logger.addHandler(file_handler)

        app.logger.setLevel(log_level)
        app.logger.info("BDC Application startup")
