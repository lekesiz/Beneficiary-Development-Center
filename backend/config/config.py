"""Application configuration."""

import secrets
import os
from datetime import timedelta
from dotenv import load_dotenv

# Load environment variables
load_dotenv()


class Config:
    """Base configuration with security hardening."""

    # SECURE SECRET GENERATION
    SECRET_KEY = os.environ.get("SECRET_KEY") or secrets.token_urlsafe(32)
    DEBUG = False
    TESTING = False

    # SECURITY HEADERS
    SECURITY_HEADERS = {
        'Strict-Transport-Security': 'max-age=31536000; includeSubDomains; preload',
        'Content-Security-Policy': "default-src 'self'; script-src 'self' 'unsafe-inline'",
        'X-Content-Type-Options': 'nosniff',
        'X-Frame-Options': 'DENY',
        'X-XSS-Protection': '1; mode=block',
        'Referrer-Policy': 'strict-origin-when-cross-origin'
    }

    # ENHANCED DATABASE SECURITY
    SQLALCHEMY_DATABASE_URI = os.environ.get("DATABASE_URL", "sqlite:///bdc.db")
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    SQLALCHEMY_ENGINE_OPTIONS = {
        "pool_size": 20,
        "pool_recycle": 1800,
        "pool_pre_ping": True,
        "pool_timeout": 30,
        "max_overflow": 30
    }

    # JWT
    JWT_SECRET_KEY = os.environ.get("JWT_SECRET_KEY") or secrets.token_urlsafe(32)
    JWT_ACCESS_TOKEN_EXPIRES = timedelta(seconds=int(os.environ.get("JWT_ACCESS_TOKEN_EXPIRES", 3600)))
    JWT_REFRESH_TOKEN_EXPIRES = timedelta(seconds=int(os.environ.get("JWT_REFRESH_TOKEN_EXPIRES", 2592000)))
    JWT_TOKEN_LOCATION = ["headers", "cookies"]
    JWT_COOKIE_SECURE = True
    JWT_COOKIE_HTTPONLY = True
    JWT_COOKIE_SAMESITE = "Lax"
    JWT_COOKIE_CSRF_PROTECT = True
    JWT_ERROR_MESSAGE_KEY = "message"

    # Redis
    REDIS_URL = os.environ.get("REDIS_URL", "redis://localhost:6379/0")
    CACHE_TYPE = "redis"
    CACHE_REDIS_URL = os.environ.get("CACHE_REDIS_URL", "redis://localhost:6379/1")
    CACHE_DEFAULT_TIMEOUT = 300

    # Celery
    CELERY_BROKER_URL = os.environ.get("CELERY_BROKER_URL", "redis://localhost:6379/2")
    CELERY_RESULT_BACKEND = os.environ.get("CELERY_RESULT_BACKEND", "redis://localhost:6379/3")
    CELERY_TASK_SERIALIZER = "json"
    CELERY_RESULT_SERIALIZER = "json"
    CELERY_ACCEPT_CONTENT = ["json"]
    CELERY_TIMEZONE = "UTC"
    CELERY_ENABLE_UTC = True

    # OpenAI
    OPENAI_API_KEY = os.environ.get("OPENAI_API_KEY")
    OPENAI_ORGANIZATION = os.environ.get("OPENAI_ORGANIZATION")
    OPENAI_MODEL_GPT4 = "gpt-4-1106-preview"
    OPENAI_MODEL_GPT35 = "gpt-3.5-turbo-1106"
    OPENAI_MODEL_EMBEDDING = "text-embedding-3-small"

    # CORS SECURITY
    CORS_ORIGINS = os.environ.get("CORS_ORIGINS", "http://localhost:3000").split(",")
    CORS_SUPPORTS_CREDENTIALS = True
    CORS_ALLOW_HEADERS = ["Content-Type", "Authorization", "X-Tenant-ID"]
    CORS_EXPOSE_HEADERS = ["X-Total-Count", "X-Page-Count"]

    # Security
    BCRYPT_LOG_ROUNDS = 12
    WTF_CSRF_ENABLED = True
    WTF_CSRF_TIME_LIMIT = None

    # File Upload
    MAX_CONTENT_LENGTH = int(os.environ.get("MAX_CONTENT_LENGTH", 16 * 1024 * 1024))  # 16MB
    UPLOAD_FOLDER = os.environ.get("UPLOAD_FOLDER", "uploads")
    ALLOWED_EXTENSIONS = set(
        os.environ.get("ALLOWED_EXTENSIONS", "pdf,doc,docx,xls,xlsx,jpg,jpeg,png,gif,txt,csv").split(",")
    )

    # Email
    MAIL_SERVER = os.environ.get("MAIL_SERVER", "smtp.gmail.com")
    MAIL_PORT = int(os.environ.get("MAIL_PORT", 587))
    MAIL_USE_TLS = os.environ.get("MAIL_USE_TLS", "True").lower() == "true"
    MAIL_USE_SSL = os.environ.get("MAIL_USE_SSL", "False").lower() == "true"
    MAIL_USERNAME = os.environ.get("MAIL_USERNAME")
    MAIL_PASSWORD = os.environ.get("MAIL_PASSWORD")
    MAIL_DEFAULT_SENDER = os.environ.get("MAIL_DEFAULT_SENDER", "noreply@bdc.com")

    # Logging
    LOG_LEVEL = os.environ.get("LOG_LEVEL", "INFO")
    LOG_FILE = os.environ.get("LOG_FILE", "bdc.log")

    # Rate Limiting
    RATELIMIT_STORAGE_URL = os.environ.get("RATELIMIT_STORAGE_URL", "redis://localhost:6379/4")
    RATELIMIT_DEFAULT = "100 per hour"
    RATELIMIT_HEADERS_ENABLED = True

    # Multi-tenant
    TENANT_HEADER = os.environ.get("TENANT_HEADER", "X-Tenant-ID")
    DEFAULT_TENANT_ID = int(os.environ.get("DEFAULT_TENANT_ID", 1))

    # Pagination
    DEFAULT_PAGE_SIZE = int(os.environ.get("DEFAULT_PAGE_SIZE", 20))
    MAX_PAGE_SIZE = int(os.environ.get("MAX_PAGE_SIZE", 100))

    # Frontend
    FRONTEND_URL = os.environ.get("FRONTEND_URL", "http://localhost:3000")

    # API Documentation
    API_TITLE = "BDC API"
    API_VERSION = "v1"
    OPENAPI_VERSION = "3.0.2"
    OPENAPI_URL_PREFIX = "/api/docs"
    OPENAPI_SWAGGER_UI_PATH = "/swagger"
    OPENAPI_SWAGGER_UI_URL = "https://cdn.jsdelivr.net/npm/swagger-ui-dist/"

    # Session
    SESSION_TYPE = "redis"
    SESSION_REDIS = None  # Will be set in app initialization
    SESSION_PERMANENT = False
    SESSION_USE_SIGNER = True
    SESSION_KEY_PREFIX = "bdc_session:"
    PERMANENT_SESSION_LIFETIME = timedelta(hours=24)


class DevelopmentConfig(Config):
    """Development configuration."""

    DEBUG = True
    SQLALCHEMY_ECHO = True
    JWT_COOKIE_SECURE = False  # Allow non-HTTPS in development


class TestingConfig(Config):
    """Testing configuration."""

    TESTING = True
    SQLALCHEMY_DATABASE_URI = "sqlite:///:memory:"
    WTF_CSRF_ENABLED = False
    JWT_COOKIE_SECURE = False
    # SQLite doesn't support these options
    SQLALCHEMY_ENGINE_OPTIONS = {}
    # Disable rate limiting for tests
    RATELIMIT_ENABLED = False


class ProductionConfig(Config):
    """Production configuration."""

    DEBUG = False
    
    def __init__(self):
        super().__init__()
        
        # Check if running on Google App Engine
        if os.environ.get("GAE_ENV", "").startswith("standard"):
            # Running on App Engine, try to get secrets
            try:
                from google.cloud import secretmanager
                client = secretmanager.SecretManagerServiceClient()
                project_id = os.environ.get("GOOGLE_CLOUD_PROJECT")
                
                # Get secrets from Secret Manager
                def get_secret(secret_id):
                    try:
                        name = f"projects/{project_id}/secrets/{secret_id}/versions/latest"
                        response = client.access_secret_version(request={"name": name})
                        return response.payload.data.decode("UTF-8")
                    except Exception as e:
                        print(f"Warning: Could not access secret {secret_id}: {e}")
                        return None
                
                # Override with secrets from Secret Manager
                secret_key = get_secret("SECRET_KEY")
                if secret_key:
                    self.SECRET_KEY = secret_key
                    
                jwt_secret = get_secret("JWT_SECRET_KEY")
                if jwt_secret:
                    self.JWT_SECRET_KEY = jwt_secret
                    
                db_password = get_secret("DB_PASSWORD")
                if db_password:
                    db_name = os.environ.get("DB_NAME", "bdc_production")
                    db_user = os.environ.get("DB_USER", "bdc_user")
                    cloud_sql_connection = os.environ.get("CLOUD_SQL_CONNECTION_NAME")
                    self.SQLALCHEMY_DATABASE_URI = f"postgresql://{db_user}:{db_password}@/{db_name}?host=/cloudsql/{cloud_sql_connection}"
                
            except ImportError:
                print("Warning: google-cloud-secret-manager not installed")
        else:
            # Not on App Engine, use environment variables
            self.SQLALCHEMY_DATABASE_URI = os.environ.get("DATABASE_URL", "postgresql://bdc_user:bdc_password@localhost:5432/bdc_db")
        
        # In production, ensure these are set
        assert self.SECRET_KEY != Config.SECRET_KEY, "SECRET_KEY must be set in production"
        assert self.JWT_SECRET_KEY != Config.JWT_SECRET_KEY, "JWT_SECRET_KEY must be set in production"
        assert hasattr(self, 'SQLALCHEMY_DATABASE_URI'), "DATABASE_URL must be configured"


# Configuration dictionary
config = {
    "development": DevelopmentConfig,
    "testing": TestingConfig,
    "production": ProductionConfig,
    "default": DevelopmentConfig,
}


def get_config(config_name=None):
    """Get configuration based on environment."""
    if config_name:
        env = config_name
    else:
        env = os.environ.get("FLASK_ENV", "development")
    return config.get(env, config["default"])
