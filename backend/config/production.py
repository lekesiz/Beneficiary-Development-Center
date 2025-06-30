"""
Production configuration for BDC Platform
Optimized for Google App Engine with Cloud SQL
"""

import os
import secrets
from datetime import timedelta
from urllib.parse import quote_plus
from dotenv import load_dotenv
from .config import Config

load_dotenv()


class ProductionConfig(Config):
    """Production configuration with enterprise-grade settings for Google App Engine."""
    
    DEBUG = False
    TESTING = False
    ENV = 'production'
    
    # Prevent SQLAlchemy from creating instance folder on read-only filesystem
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    
    # Enhanced secret generation for production - using Secret Manager in production
    SECRET_KEY = os.environ.get("SECRET_KEY") or secrets.token_urlsafe(64)
    JWT_SECRET_KEY = os.environ.get("JWT_SECRET_KEY") or secrets.token_urlsafe(64)
    
    # Cloud SQL Configuration
    @property
    def SQLALCHEMY_DATABASE_URI(self):
        """Build database URI for Cloud SQL"""
        # Check if running on App Engine
        if os.environ.get('GAE_ENV', '').startswith('standard'):
            # Running on App Engine, use Unix socket
            db_user = os.environ.get('DB_USER', 'bdc_user')
            db_pass = quote_plus(os.environ.get('DB_PASS', ''))
            db_name = os.environ.get('DB_NAME', 'bdc_production')
            cloud_sql_connection = os.environ.get('CLOUD_SQL_CONNECTION_NAME', '')
            
            # For now, use SQLite in production until PostgreSQL is set up
            if not cloud_sql_connection or cloud_sql_connection == 'bilan-competence-449414:europe-west1:bdc-db':
                # Use SQLite temporarily
                return 'sqlite:////tmp/bdc.db'
            
            return f"postgresql://{db_user}:{db_pass}@/{db_name}?host=/cloudsql/{cloud_sql_connection}"
        else:
            # Running locally or in other environments
            return os.environ.get(
                'DATABASE_URL',
                'postgresql://localhost/bdc_production'
            )
    
    # Database pool configuration optimized for App Engine
    SQLALCHEMY_ENGINE_OPTIONS = {
        "pool_size": 10,
        "pool_recycle": 3600,
        "pool_pre_ping": True,
        "pool_timeout": 10,
        "max_overflow": 20,
        "echo": False,
        "pool_reset_on_return": "commit",
        "connect_args": {
            'connect_timeout': 10,
            'options': '-c statement_timeout=30000'  # 30 seconds
        }
    }
    
    # Redis configuration (Google Memorystore)
    @property
    def REDIS_URL(self):
        """Get Redis URL from environment"""
        if os.environ.get('GAE_ENV', '').startswith('standard'):
            # Use VPC connector to access Memorystore
            redis_host = os.environ.get('REDIS_HOST', '10.0.0.3')
            redis_port = os.environ.get('REDIS_PORT', '6379')
            redis_password = os.environ.get('REDIS_PASSWORD', '')
            
            if redis_password:
                return f"redis://:{redis_password}@{redis_host}:{redis_port}/0"
            return f"redis://{redis_host}:{redis_port}/0"
        else:
            return os.environ.get('REDIS_URL', 'redis://localhost:6379/0')
    
    # Cache configuration
    CACHE_TYPE = 'redis'
    CACHE_REDIS_URL = property(lambda self: self.REDIS_URL)
    CACHE_DEFAULT_TIMEOUT = 300
    CACHE_KEY_PREFIX = 'bdc_prod:'
    
    # Rate limiting
    RATELIMIT_ENABLED = True
    RATELIMIT_STORAGE_URL = property(lambda self: self.REDIS_URL)
    RATELIMIT_STRATEGY = 'fixed-window-elastic-expiry'
    
    # Enhanced security for production
    SESSION_COOKIE_SECURE = True
    SESSION_COOKIE_HTTPONLY = True
    SESSION_COOKIE_SAMESITE = 'Lax'
    JWT_COOKIE_SECURE = True
    JWT_COOKIE_HTTPONLY = True
    JWT_COOKIE_SAMESITE = 'Lax'
    WTF_CSRF_ENABLED = True
    
    # Performance settings
    SEND_FILE_MAX_AGE_DEFAULT = 31536000  # 1 year cache
    
    # Rate limiting for production
    RATELIMIT_DEFAULT = "1000 per hour"
    RATELIMIT_HEADERS_ENABLED = True
    
    # Enhanced CORS security
    CORS_ORIGINS = os.environ.get(
        'CORS_ORIGINS', 
        'https://bdc-platform.appspot.com,https://www.bdc-platform.com'
    ).split(',')
    CORS_SUPPORTS_CREDENTIALS = True
    CORS_ALLOW_HEADERS = ["Content-Type", "Authorization", "X-Tenant-ID", "X-Request-ID"]
    CORS_EXPOSE_HEADERS = ["X-Total-Count", "X-Page-Count", "X-Request-ID", "Content-Range", "X-Content-Range"]
    
    # Logging configuration
    LOG_LEVEL = "INFO"
    LOG_FORMAT = "json"
    
    # Email configuration (SendGrid for production)
    MAIL_SERVER = os.environ.get("MAIL_SERVER", "smtp.sendgrid.net")
    MAIL_PORT = int(os.environ.get("MAIL_PORT", 587))
    MAIL_USE_TLS = True
    MAIL_USE_SSL = False
    MAIL_USERNAME = 'apikey'
    MAIL_PASSWORD = os.environ.get("SENDGRID_API_KEY")
    MAIL_DEFAULT_SENDER = os.environ.get('MAIL_DEFAULT_SENDER', 'noreply@bdc-platform.com')
    MAIL_MAX_EMAILS = 100
    MAIL_SUPPRESS_SEND = False
    
    # OpenAI settings
    OPENAI_API_KEY = os.environ.get("OPENAI_API_KEY")
    OPENAI_ORGANIZATION = os.environ.get("OPENAI_ORGANIZATION")
    
    # Sentry for error tracking
    SENTRY_DSN = os.environ.get("SENTRY_DSN")
    
    # File upload configuration (Cloud Storage)
    MAX_CONTENT_LENGTH = 100 * 1024 * 1024  # 100MB for production
    UPLOAD_FOLDER = '/tmp/uploads'  # Temporary folder for processing
    ALLOWED_EXTENSIONS = {
        'txt', 'pdf', 'png', 'jpg', 'jpeg', 'gif', 
        'doc', 'docx', 'xls', 'xlsx', 'csv', 'zip'
    }
    
    # Cloud Storage configuration
    GCS_BUCKET_NAME = os.environ.get('GCS_BUCKET_NAME', 'bdc-platform-uploads')
    GCS_PROJECT_ID = os.environ.get('GOOGLE_CLOUD_PROJECT')
    GCS_CREDENTIALS_PATH = os.environ.get('GOOGLE_APPLICATION_CREDENTIALS')
    
    # Production security headers
    SECURITY_HEADERS = {
        'Strict-Transport-Security': 'max-age=31536000; includeSubDomains',
        'X-Content-Type-Options': 'nosniff',
        'X-Frame-Options': 'DENY',
        'X-XSS-Protection': '1; mode=block',
        'Referrer-Policy': 'strict-origin-when-cross-origin',
        'Content-Security-Policy': (
            "default-src 'self'; "
            "script-src 'self' 'unsafe-inline' https://www.googletagmanager.com; "
            "style-src 'self' 'unsafe-inline'; "
            "img-src 'self' data: https:; "
            "font-src 'self' data:; "
            "connect-src 'self' https://api.bdc-platform.com; "
            "frame-ancestors 'none';"
        )
    }
    
    # Feature flags
    FEATURE_FLAGS = {
        'ENABLE_AI_INSIGHTS': True,
        'ENABLE_ADVANCED_ANALYTICS': True,
        'ENABLE_EXPORT_FUNCTIONALITY': True,
        'ENABLE_BULK_OPERATIONS': True,
        'ENABLE_WEBHOOKS': True,
        'ENABLE_API_VERSIONING': True,
        'ENABLE_AUDIT_LOGS': True,
        'ENABLE_DATA_ENCRYPTION': True
    }
    
    # Cloud Tasks configuration
    CLOUD_TASKS_QUEUE_NAME = os.environ.get(
        'CLOUD_TASKS_QUEUE_NAME',
        'projects/{}/locations/us-central1/queues/bdc-tasks'.format(
            os.environ.get('GOOGLE_CLOUD_PROJECT')
        )
    )
    
    # Monitoring and observability
    OPENTELEMETRY_ENABLED = True
    OPENTELEMETRY_SERVICE_NAME = 'bdc-platform'
    OPENTELEMETRY_EXPORTER_ENDPOINT = os.environ.get(
        'OTEL_EXPORTER_ENDPOINT',
        'https://otel-collector.monitoring.svc.cluster.local:4317'
    )
    
    @classmethod
    def init_app(cls, app):
        """Initialize production app configuration"""
        Config.init_app(app)
        
        # Configure production logging
        import logging
        from logging.handlers import RotatingFileHandler
        
        # Setup Google Cloud Logging
        if os.environ.get('GAE_ENV', '').startswith('standard'):
            try:
                import google.cloud.logging
                client = google.cloud.logging.Client()
                client.setup_logging(log_level=logging.INFO)
            except Exception as e:
                app.logger.warning(f"Failed to setup Google Cloud Logging: {e}")
        
        # Setup file logging as backup
        if not os.path.exists('logs'):
            os.mkdir('logs')
        
        file_handler = RotatingFileHandler(
            'logs/bdc-platform.log',
            maxBytes=10485760,  # 10MB
            backupCount=10
        )
        file_handler.setFormatter(logging.Formatter(
            '%(asctime)s %(levelname)s: %(message)s [in %(pathname)s:%(lineno)d]'
        ))
        file_handler.setLevel(logging.INFO)
        app.logger.addHandler(file_handler)
        
        app.logger.setLevel(logging.INFO)
        app.logger.info('BDC Platform startup in production mode')
        
        # Initialize Sentry for error tracking
        if cls.SENTRY_DSN:
            try:
                import sentry_sdk
                from sentry_sdk.integrations.flask import FlaskIntegration
                from sentry_sdk.integrations.sqlalchemy import SqlalchemyIntegration
                
                sentry_sdk.init(
                    dsn=cls.SENTRY_DSN,
                    integrations=[
                        FlaskIntegration(transaction_style='endpoint'),
                        SqlalchemyIntegration()
                    ],
                    traces_sample_rate=0.1,
                    environment='production',
                    release=os.environ.get('GAE_VERSION', 'unknown')
                )
            except Exception as e:
                app.logger.warning(f"Failed to initialize Sentry: {e}")


class StagingConfig(ProductionConfig):
    """Staging configuration - similar to production but with debugging."""
    
    DEBUG = False
    TESTING = False
    
    # Staging-specific settings
    LOG_LEVEL = "DEBUG"
    SQLALCHEMY_ENGINE_OPTIONS = {
        **ProductionConfig.SQLALCHEMY_ENGINE_OPTIONS,
        "echo": True,  # Enable SQL logging in staging
        "pool_size": 20,  # Smaller pool for staging
        "max_overflow": 30
    }
    
    # Less strict CORS for staging
    CORS_ORIGINS = os.environ.get("CORS_ORIGINS", "http://localhost:3000,https://staging.yourdomain.com").split(",")
    
    # Staging-specific CSP (more permissive)
    SECURITY_HEADERS = {
        **ProductionConfig.SECURITY_HEADERS,
        'Content-Security-Policy': "default-src 'self' 'unsafe-inline' 'unsafe-eval'; connect-src 'self' ws: wss: http: https:",
        'X-Robots-Tag': 'noindex, nofollow'
    }


# Export configurations
production_config = ProductionConfig
staging_config = StagingConfig