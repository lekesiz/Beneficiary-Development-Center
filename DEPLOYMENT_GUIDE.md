# BDC Platform - Enterprise Deployment Guide

## Overview

This guide documents the enterprise-grade deployment configuration for the BDC (Beneficiary Development Center) platform on Google App Engine. The platform has been transformed from 75% production-ready to enterprise-grade with comprehensive security, scalability, and monitoring features.

## Table of Contents

1. [Google App Engine Configuration](#google-app-engine-configuration)
2. [CI/CD Pipeline](#cicd-pipeline)
3. [Cloud SQL Configuration](#cloud-sql-configuration)
4. [Cloud Storage Integration](#cloud-storage-integration)
5. [Secrets Management](#secrets-management)
6. [Security Features](#security-features)
7. [Rate Limiting](#rate-limiting)
8. [Deployment Steps](#deployment-steps)
9. [Monitoring and Observability](#monitoring-and-observability)
10. [Troubleshooting](#troubleshooting)

## Google App Engine Configuration

### app.yaml Configuration

The `app.yaml` file configures the application for Google App Engine deployment:

```yaml
runtime: python312
instance_class: F2

automatic_scaling:
  min_instances: 2
  max_instances: 10
  target_cpu_utilization: 0.65
```

Key features:
- Auto-scaling from 2 to 10 instances
- VPC connector for secure Cloud SQL access
- Optimized static file serving with caching
- Security headers for all responses
- Health check and warmup endpoints

### Environment Variables

Critical environment variables are set in `app.yaml`:
- `DATABASE_URL`: Cloud SQL connection string
- `REDIS_URL`: Memorystore connection
- `CORS_ORIGINS`: Allowed origins for CORS
- Feature flags for enabling/disabling features

## CI/CD Pipeline

### Cloud Build Configuration

The `cloudbuild.yaml` defines a comprehensive CI/CD pipeline:

1. **Testing Phase**
   - Run unit tests and integration tests
   - Security scanning with Bandit and Safety
   - Code quality checks

2. **Build Phase**
   - Frontend build with optimization
   - Backend container build
   - Multi-stage Docker builds for efficiency

3. **Deployment Phase**
   - Database migrations
   - App Engine deployment
   - Smoke tests
   - Traffic migration

4. **Post-Deployment**
   - CDN cache invalidation
   - Deployment notifications

### Triggering Deployments

```bash
# Manual deployment
gcloud builds submit --config=cloudbuild.yaml

# Automatic deployment on push to main
# Configure in Cloud Console > Cloud Build > Triggers
```

## Cloud SQL Configuration

### Production Configuration

The production configuration (`backend/config/production.py`) automatically detects the environment:

```python
# Automatic Cloud SQL connection on App Engine
if os.environ.get('GAE_ENV', '').startswith('standard'):
    # Uses Unix socket connection
    DATABASE_URL = f"postgresql://{user}:{password}@/{database}?host=/cloudsql/{connection_name}"
```

### Database Pool Settings

Optimized for App Engine:
- Pool size: 10 connections
- Max overflow: 20 connections
- Connection timeout: 10 seconds
- Statement timeout: 30 seconds

## Cloud Storage Integration

### Storage Manager Features

The `CloudStorageManager` class provides:
- Multi-tenant file isolation
- Signed URLs for secure access
- File versioning and soft deletes
- Lifecycle management
- CORS configuration
- CDN integration

### Usage Example

```python
from app.core.cloud_storage import get_storage_manager

storage = get_storage_manager()

# Upload file
result = storage.upload_file(
    file=file_object,
    path='documents/',
    tenant_id=1,
    user_id=123
)

# Get signed URL
url = storage.get_file_url(path, expires_in=3600)
```

### API Endpoints

- `POST /api/v1/files/upload` - Upload files
- `GET /api/v1/files/<path>` - Download files
- `DELETE /api/v1/files/<path>` - Delete files
- `GET /api/v1/files/` - List files
- `POST /api/v1/files/upload-url` - Get direct upload URL

## Secrets Management

### Secret Manager Integration

The platform uses Google Secret Manager for sensitive configuration:

```python
from app.core.secrets_manager import get_secret

# Automatic fallback to environment variables
database_url = get_database_url()
jwt_secret = get_jwt_secret()
```

### Managing Secrets

Use the provided CLI tool:

```bash
# Initialize all required secrets
python backend/scripts/manage_secrets.py init

# Create a new secret
python backend/scripts/manage_secrets.py create my-secret --value "secret-value"

# List all secrets
python backend/scripts/manage_secrets.py list

# Validate all required secrets exist
python backend/scripts/manage_secrets.py validate
```

### Required Secrets

- `app-secret-key` - Flask session key
- `jwt-secret-key` - JWT signing key
- `database-url` - PostgreSQL connection string
- `redis-url` - Redis/Memorystore URL
- `sendgrid-api-key` - Email service
- `cloud-sql-connection` - Cloud SQL instance

## Security Features

### Security Headers

Comprehensive security headers are automatically applied:

- `Strict-Transport-Security` - Force HTTPS
- `X-Content-Type-Options` - Prevent MIME sniffing
- `X-Frame-Options` - Prevent clickjacking
- `Content-Security-Policy` - Control resource loading
- `X-XSS-Protection` - XSS protection

### Request Validation

The security middleware provides:

- SQL injection detection
- XSS attempt detection
- Request size validation
- Content type validation
- IP-based access control

### Security Decorators

```python
from app.core.security import (
    require_https,
    validate_api_key,
    validate_ip_whitelist,
    rate_limit_by_ip
)

@require_https
@validate_api_key
@rate_limit_by_ip(max_requests=100, window=3600)
def sensitive_endpoint():
    pass
```

## Rate Limiting

### Tiered Rate Limits

Rate limits are automatically adjusted based on user role:

- **Admin**: 10,000 requests/hour
- **Trainer**: 5,000 requests/hour
- **Student**: 1,000 requests/hour
- **Anonymous**: 100 requests/hour

### Endpoint-Specific Limits

Critical endpoints have specific limits:

```python
# Authentication
'api_v1.auth.login': '5 per minute, 20 per hour'
'api_v1.auth.register': '3 per hour, 10 per day'

# File operations
'api_v1.files.upload_file': '10 per hour, 50 per day'

# Exports
'api_v1.reports.export': '5 per hour'
```

### Custom Rate Limiting

```python
from app.extensions import limiter

@app.route('/api/endpoint')
@limiter.limit("10 per minute")
def rate_limited_endpoint():
    pass
```

## Deployment Steps

### Prerequisites

1. Install Google Cloud SDK
2. Authenticate: `gcloud auth login`
3. Set project: `gcloud config set project YOUR_PROJECT_ID`
4. Enable required APIs:
   ```bash
   gcloud services enable \
     appengine.googleapis.com \
     cloudbuild.googleapis.com \
     secretmanager.googleapis.com \
     sqladmin.googleapis.com \
     storage.googleapis.com
   ```

### Initial Setup

1. **Create Cloud SQL Instance**
   ```bash
   gcloud sql instances create bdc-db-prod \
     --database-version=POSTGRES_15 \
     --tier=db-n1-standard-2 \
     --region=us-central1
   ```

2. **Create Storage Bucket**
   ```bash
   gsutil mb -c standard -l us-central1 gs://bdc-platform-uploads
   ```

3. **Initialize Secrets**
   ```bash
   python backend/scripts/manage_secrets.py init
   ```

4. **Configure VPC Connector**
   ```bash
   gcloud compute networks vpc-access connectors create bdc-connector \
     --region=us-central1 \
     --subnet=default \
     --subnet-project=YOUR_PROJECT_ID \
     --min-instances=2 \
     --max-instances=10
   ```

### Deployment

1. **Deploy with Cloud Build**
   ```bash
   gcloud builds submit --config=cloudbuild.yaml
   ```

2. **Or direct deployment**
   ```bash
   gcloud app deploy app.yaml
   ```

3. **Monitor deployment**
   ```bash
   gcloud app logs tail -s default
   ```

## Monitoring and Observability

### Health Checks

- `/_ah/health` - App Engine health check
- `/api/v1/admin/health/detailed` - Detailed health status

### Logging

Structured logging with Google Cloud Logging:
- Request/response logging
- Security event logging
- Performance metrics
- Error tracking with Sentry

### Metrics

Key metrics to monitor:
- Request latency
- Error rates
- Database connection pool
- Cache hit rates
- Rate limit violations

## Troubleshooting

### Common Issues

1. **Database Connection Errors**
   - Check Cloud SQL proxy connection
   - Verify VPC connector configuration
   - Check connection pool settings

2. **Rate Limiting Issues**
   - Check Redis/Memorystore connectivity
   - Verify rate limit configuration
   - Monitor rate limit headers in responses

3. **File Upload Failures**
   - Check bucket permissions
   - Verify CORS configuration
   - Check file size limits

### Debug Commands

```bash
# View application logs
gcloud app logs read --limit=50

# SSH into instance (if enabled)
gcloud app instances ssh INSTANCE_ID --service=default

# View Cloud Build logs
gcloud builds log BUILD_ID

# Test health endpoint
curl https://YOUR_PROJECT.appspot.com/_ah/health
```

### Support

For issues or questions:
- Check logs in Cloud Console
- Review error tracking in Sentry
- Contact platform administrators

## Security Best Practices

1. **Regular Updates**
   - Keep dependencies updated
   - Review security advisories
   - Run security scans regularly

2. **Access Control**
   - Use principle of least privilege
   - Regularly audit admin access
   - Monitor failed login attempts

3. **Data Protection**
   - Enable encryption at rest
   - Use signed URLs for file access
   - Implement proper data retention

4. **Monitoring**
   - Set up alerts for anomalies
   - Review security logs regularly
   - Monitor rate limit violations

## Next Steps

1. Configure custom domain
2. Set up SSL certificates
3. Configure backup strategies
4. Implement disaster recovery plan
5. Set up monitoring dashboards
6. Configure alert policies
7. Plan for scaling strategies